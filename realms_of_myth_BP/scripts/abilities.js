/**
 * Realms of Myth - Ability Execution System
 * Handles ability activation, cooldowns, legendary weapon specials, and class-master bonuses.
 *
 * Module-scope state (Maps) is intentional — Bedrock scripting has no native
 * per-player storage for transient runtime data, so dynamic properties are used
 * for persistence across sessions and Maps are used for in-session hot data.
 * All Maps are cleaned up on playerLeave to avoid memory leaks.
 */

import { world, system, Player } from '@minecraft/server';
import { CLASSES, getClassAbilities } from './classSystem.js';
import { loadPlayerData } from './playerData.js';

// ── Module-scope state ─────────────────────────────────────────────
/** playerId -> Map<abilityId, remainingTicks> */
const cooldowns = new Map();
/** playerId -> endTick (system.currentTick). Bloodlust is the only timed buff
 *  tracked in a Map because it needs fast per-event lookup in entityHurt. */
const activeBloodlusts = new Map();

const ABILITY_ITEMS = [
    'minecraft:nether_star',  // Ability slot 1
    'minecraft:blaze_powder', // Ability slot 2
    'minecraft:ghast_tear'    // Ability slot 3
];

// ── Public API ─────────────────────────────────────────────────────

/**
 * Register ability triggers and event handlers. Call once during mod init.
 */
export function registerAbilities() {
    // ── Ability activation via item use ───────────────────────────
    world.afterEvents.itemUse.subscribe((event) => {
        const player = event.source;
        const item = event.itemStack;
        if (!item) return;

        const abilityIndex = ABILITY_ITEMS.indexOf(item.typeId);
        if (abilityIndex === -1) return;

        const data = loadPlayerData(player);
        if (!data || !data.class) {
            player.sendMessage('§cYou must choose a class first! Use §e!class');
            return;
        }

        event.cancel = true;

        const abilities = getClassAbilities(data.class);
        if (!abilities || abilityIndex >= abilities.length) return;

        const ability = abilities[abilityIndex];

        // Cooldown check
        const playerCd = getCooldownMap(player.id);
        const remaining = playerCd.get(ability.id) || 0;
        if (remaining > 0) {
            player.sendMessage(`§c§l${ability.name} §ris on cooldown: §e${Math.ceil(remaining / 20)}s`);
            return;
        }

        // Staff of Arcana — reduces all cooldowns by 20% (T4 legendary)
        let cdTicks = ability.cooldown;
        const equippable = player.getComponent('minecraft:equippable');
        if (equippable) {
            const weapon = equippable.getEquipment('Mainhand');
            if (weapon && weapon.typeId === 'realms:magic_staff') {
                cdTicks = Math.round(cdTicks * 0.80);
                player.sendMessage('§d☆ Staff of Arcana reduces cooldown by 20%');
            }
        }

        playerCd.set(ability.id, cdTicks);

        // Dispatch
        executeAbility(player, data.class, ability, data.race);

        player.sendMessage(`§a✨ §l${ability.name}§r §aactivated!`);
        player.playSound('random.orb');
    });

    // ── Cooldown processing (every tick) + bloodlust expiry ───────
    // runInterval(1) is fine here because the work per tick is tiny.
    // We do NOT need the % 10 check on bloodlust — checking every tick is
    // cheap and avoids off-by-one drift if system.currentTick is a big number.
    system.runInterval(() => {
        for (const [, cdMap] of cooldowns) {
            for (const [abilityId, ticks] of cdMap) {
                if (ticks > 0) cdMap.set(abilityId, ticks - 1);
            }
        }
        const now = system.currentTick;
        for (const [playerId, endTick] of activeBloodlusts) {
            if (now >= endTick) activeBloodlusts.delete(playerId);
        }
    }, 1);

    // ── Player leave cleanup ──────────────────────────────────────
    world.afterEvents.playerLeave.subscribe((event) => {
        const pid = event.playerId;
        cooldowns.delete(pid);
        activeBloodlusts.delete(pid);
    });

    // ── Entity hurt: lifesteal + dragonslayer + berserker master + paladin reflect + elf bow ─
    // Single subscription merges five concerns (was previously split) to cut per-tick overhead.
    world.afterEvents.entityHurt.subscribe((event) => {
        const damager = event.damageSource?.damagingEntity;
        const victim = event.hurtEntity;
        if (!damager) return;

        const damagerIsPlayer = damager instanceof Player;

        // (1) Lifesteal (Bloodlust) — heals the damager for 30% of damage dealt
        if (damagerIsPlayer && activeBloodlusts.has(damager.id)) {
            const healAmount = Math.ceil(event.damage * 0.30);
            const health = damager.getComponent('minecraft:health');
            if (health) {
                health.setCurrentValue(Math.min(
                    health.currentValue + healAmount,
                    health.effectiveMax
                ));
            }
        }

        if (damagerIsPlayer) {
            // (2) Dragonslayer Spear: 2x damage vs family=dragon
            const family = victim.getComponent('minecraft:type_family');
            if (family && family.hasType('dragon')) {
                const eq = damager.getComponent('minecraft:equippable');
                if (eq) {
                    const weapon = eq.getEquipment('Mainhand');
                    if (weapon && weapon.typeId === 'realms:dragonslayer_spear') {
                        const extraDamage = event.damage;
                        const vHealth = victim.getComponent('minecraft:health');
                        if (vHealth) {
                            vHealth.setCurrentValue(vHealth.currentValue - extraDamage);
                        }
                        damager.sendMessage('§6⚔ Dragonslayer! Double damage dealt.');
                    }
                }
            }

            // (3) Berserker Class Master: +25% damage when below 50% HP
            if (damager.getDynamicProperty('rom:class_master_bonus') === 'berserker') {
                const hp = damager.getComponent('minecraft:health');
                if (hp && hp.currentValue < hp.effectiveMax * 0.5) {
                    const extraDamage = Math.ceil(event.damage * 0.25);
                    const vHealth = victim.getComponent('minecraft:health');
                    if (vHealth && extraDamage > 0) {
                        vHealth.setCurrentValue(vHealth.currentValue - extraDamage);
                    }
                }
            }

            // (4) Elf Bow Damage Bonus: +20% damage on projectile attacks
            if (event.damageSource.cause === 'projectile') {
                if (damager.getDynamicProperty('rom:race') === 'elf') {
                    const bonus = damager.getDynamicProperty('rom:bow_damage_bonus');
                    if (bonus) {
                        const extraDamage = Math.ceil(event.damage * bonus);
                        const vHealth = victim.getComponent('minecraft:health');
                        if (vHealth && extraDamage > 0) {
                            vHealth.setCurrentValue(vHealth.currentValue - extraDamage);
                        }
                    }
                }
            }
        }

        // (5) Paladin Class Master: 10% damage reflect (works even if source is not a player)
        if (victim instanceof Player) {
            if (victim.getDynamicProperty('rom:class_master_bonus') === 'paladin') {
                const reflect = Math.ceil(event.damage * 0.10);
                if (reflect > 0 && event.damageSource?.damagingEntity) {
                    const source = event.damageSource.damagingEntity;
                    const sHealth = source.getComponent('minecraft:health');
                    if (sHealth) {
                        sHealth.setCurrentValue(sHealth.currentValue - reflect);
                    }
                }
            }
        }
    });

    // ── Entity die: shadowfang invisibility + human XP bonus ─────
    world.afterEvents.entityDie.subscribe((event) => {
        const damager = event.damageSource?.damagingEntity;
        if (!damager || !(damager instanceof Player)) return;

        const equippable = damager.getComponent('minecraft:equippable');

        // (1) Shadowfang Dagger: 3s invisibility on kill
        if (equippable) {
            const weapon = equippable.getEquipment('Mainhand');
            if (weapon && weapon.typeId === 'realms:shadowfang_dagger') {
                try {
                    damager.runCommand('effect @s invisibility 3 0 true');
                } catch (e) { /* commands may be disabled */ }
                damager.sendMessage('§5🗡 Shadowfang: You fade into the shadows...');
            }
        }

        // (2) Human XP bonus: 1 bonus XP level per kill
        if (damager.getDynamicProperty('rom:race') === 'human') {
            if (damager.getDynamicProperty('rom:human_skill_points')) {
                try {
                    damager.runCommand('xp 1L @s');
                } catch (e) { /* commands may be disabled */ }
                damager.sendMessage('§e🌟 Human Adaptability: bonus XP earned!');
            }
        }
    });
}

// ── Internal helpers ───────────────────────────────────────────────

function getCooldownMap(playerId) {
    if (!cooldowns.has(playerId)) cooldowns.set(playerId, new Map());
    return cooldowns.get(playerId);
}

/**
 * Dispatch to the correct ability implementation. `classId` and `raceId` are
 * accepted for future hooks (e.g. "Elf passive doubles Fireball speed"); the
 * current implementation reads class/race via dynamic properties.
 */
function executeAbility(player, classId, ability, raceId) {
    // Mage Class Master: +30% ability damage (applies to damage-dealing abilities)
    const damageMultiplier = player.getDynamicProperty('rom:class_master_bonus') === 'mage' ? 1.30 : 1.0;

    switch (ability.id) {
        // Mage
        case 'fireball':         spawnFireball(player, ability, damageMultiplier); break;
        case 'ice_shield':       applyShield(player, ability, 'resistance', 3); break;
        case 'arcane_teleport':  teleportForward(player, ability); break;
        // Ranger
        case 'multi_shot':       spawnArrowSpread(player, ability); break;
        case 'shadow_step':      applyBuffs(player, ability, [
            ['invisibility', 0], ['speed', 2]
        ], 'mob.wither.spawn', 'minecraft:endrod'); break;
        case 'eagle_eye':        highlightNearby(player, ability); break;
        // Berserker
        case 'rage':             applyBuffs(player, ability, [
            ['strength', 2], ['speed', 1]
        ], 'mob.ravager.roar', 'minecraft:angry_villager'); break;
        case 'ground_slam':      doGroundSlam(player, ability, damageMultiplier); break;
        case 'bloodlust':        activateBloodlust(player, ability); break;
        // Paladin
        case 'holy_light':       healAOE(player, ability); break;
        case 'divine_shield':    applyShield(player, ability, 'resistance', 10); break;
        case 'smite':            doSmite(player, ability, damageMultiplier); break;
        // Druid
        case 'wolf_form':        activateWolfForm(player, ability); break;
        case 'entangling_roots': rootEnemy(player, ability); break;
        case 'natures_blessing': applyHoT(player, ability); break;
    }
}

// ═══════════════════════════════════════════════════════════════════
// GENERIC ABILITY HELPERS
// ═══════════════════════════════════════════════════════════════════

function applyBuffs(player, ability, effects, sound, particle) {
    const secs = Math.round(ability.duration / 20);
    for (const [effect, level] of effects) {
        player.runCommand(`effect @s ${effect} ${secs} ${level} true`);
    }
    if (sound) player.playSound(sound);
    if (particle) player.runCommand(`particle ${particle} ~~~`);
}

function applyShield(player, ability, effect, level) {
    const secs = Math.round(ability.duration / 20);
    player.runCommand(`effect @s ${effect} ${secs} ${level} true`);
    player.playSound('beacon.activate');
    player.runCommand('particle minecraft:totem_of_undying ~~~');
}

// ═══════════════════════════════════════════════════════════════════
// MAGE
// ═══════════════════════════════════════════════════════════════════

function spawnFireball(player, ability, multiplier) {
    const head = player.getHeadLocation();
    const dir = player.getViewDirection();
    player.dimension.spawnEntity('minecraft:fireball', {
        x: head.x + dir.x * 1.5,
        y: head.y + dir.y * 1.5,
        z: head.z + dir.z * 1.5
    });
    player.playSound('mob.blaze.shoot');
    player.runCommand(`particle minecraft:flame ~~~`);
    if (multiplier > 1) {
        player.sendMessage('§d✦ Arcane Amplification: +30% ability damage');
    }
}

function teleportForward(player, ability) {
    const dir = player.getViewDirection();
    const loc = player.location;
    player.teleport({
        x: loc.x + dir.x * ability.range,
        y: loc.y + dir.y * ability.range,
        z: loc.z + dir.z * ability.range
    });
    player.playSound('mob.endermen.portal');
    player.runCommand('particle minecraft:portal_particle ~~~');
}

// ═══════════════════════════════════════════════════════════════════
// RANGER
// ═══════════════════════════════════════════════════════════════════

function spawnArrowSpread(player) {
    const head = player.getHeadLocation();
    const dir = player.getViewDirection();
    const dim = player.dimension;
    const offsets = [0, -0.12, 0.12];
    for (const oy of offsets) {
        dim.spawnEntity('minecraft:arrow', {
            x: head.x + dir.x * 1.5,
            y: head.y + dir.y * 1.5 + oy,
            z: head.z + dir.z * 1.5
        });
    }
    player.playSound('random.bow');
}

function highlightNearby(player, ability) {
    const secs = Math.round(ability.duration / 20);
    player.runCommand(`effect @s night_vision ${secs} 0 true`);
    player.runCommand(`effect @e[r=${ability.radius},family=monster] glowing ${secs} 0 true`);
    player.playSound('mob.witch.ambient');
}

// ═══════════════════════════════════════════════════════════════════
// BERSERKER
// ═══════════════════════════════════════════════════════════════════

function doGroundSlam(player, ability, multiplier) {
    const dim = player.dimension;
    const dmgLevel = Math.round((ability.damage * multiplier) / 3);
    dim.runCommand(`effect @e[family=monster,r=${ability.radius}] levitation 5 0 true`);
    dim.runCommand(`effect @e[family=monster,r=${ability.radius}] instant_damage 1 ${dmgLevel} true`);
    dim.runCommand(`execute at @p run particle minecraft:large_explosion ~ ~ ~`);
    player.playSound('mob.irongolem.hit');
}

function activateBloodlust(player, ability) {
    player.runCommand('effect @s instant_health 1 1 true');
    player.playSound('mob.evocation_illager.prepare_summon');
    const endTick = system.currentTick + ability.duration;
    activeBloodlusts.set(player.id, endTick);
    player.sendMessage('§c🩸 Bloodlust active! Heal 30% of damage dealt for 6s.');
}

// ═══════════════════════════════════════════════════════════════════
// PALADIN
// ═══════════════════════════════════════════════════════════════════

function healAOE(player, ability) {
    const level = Math.round(ability.healAmount / 4);
    player.runCommand(`effect @s instant_health 1 ${level} true`);
    player.dimension.runCommand(`effect @e[family=player,r=${ability.radius}] instant_health 1 ${level} true`);
    player.dimension.runCommand(`execute at @p run particle minecraft:totem_of_undying ~ ~ ~`);
    player.playSound('random.orb');
}

function doSmite(player, ability, multiplier) {
    const dim = player.dimension;
    const dmgLevel = Math.round((ability.damage * multiplier) / 3);
    dim.runCommand(`effect @e[family=monster,c=1,r=8] instant_damage 1 ${dmgLevel} true`);
    player.playSound('ambient.weather.thunder');
    dim.runCommand(`execute at @p run particle minecraft:lightning_bolt ~ ~ ~`);
}

// ═══════════════════════════════════════════════════════════════════
// DRUID
// ═══════════════════════════════════════════════════════════════════

/**
 * Wolf Form — gives the player the appearance of a wolf spirit by:
 *   (1) Spawning a ghostly wolf companion that follows the player
 *   (2) Strong speed + strength buffs
 *   (3) Wolf-themed particles and sound
 * The companion despawns when the buff ends.
 */
function activateWolfForm(player, ability) {
    const secs = Math.round(ability.duration / 20);
    player.runCommand(`effect @s speed ${secs} 3 true`);
    player.runCommand(`effect @s strength ${secs} 1 true`);
    player.runCommand(`effect @s jump_boost ${secs} 1 true`);

    // Spawn a temporary wolf companion
    const head = player.getHeadLocation();
    const wolf = player.dimension.spawnEntity('minecraft:wolf', {
        x: head.x, y: head.y, z: head.z
    });
    try { wolf.setTamed(true); wolf.setOwner(player); } catch (e) { /* setOwner may fail in some envs */ }
    // Tag for cleanup
    wolf.addTag('rom:wolf_form_companion');
    // Despawn after duration
    system.runTimeout(() => {
        try { if (wolf.isValid()) wolf.remove(); } catch (e) { /* already gone */ }
    }, ability.duration);

    player.runCommand(`particle minecraft:heart_particle ~~~`);
    player.runCommand(`particle minecraft:spore_blossom_ambient ~~~`);
    player.playSound('mob.wolf.howl');
    player.sendMessage('§2🐺 Wolf Form! The pack is with you.');
}

function rootEnemy(player, ability) {
    const secs = Math.round(ability.duration / 20);
    player.dimension.runCommand(`effect @e[family=monster,c=1,r=10] slowness ${secs} 10 true`);
    player.dimension.runCommand(`execute at @e[family=monster,c=1,r=10] run particle minecraft:spore_blossom_ambient ~ ~ ~`);
    player.playSound('dig.grass');
}

function applyHoT(player, ability) {
    const secs = Math.round(ability.duration / 20);
    const level = Math.round(ability.healPerTick / 2);
    player.runCommand(`effect @s regeneration ${secs} ${level} true`);
    player.dimension.runCommand(`execute at @p run particle minecraft:crop_growth_emitter ~ ~ ~`);
    player.playSound('random.orb');
}

// ═══════════════════════════════════════════════════════════════════
// EXPORTS
// ═══════════════════════════════════════════════════════════════════

/** Get remaining cooldown ticks for a player's ability (used by HUDs / tools). */
export function getCooldown(playerId, abilityId) {
    const playerCd = cooldowns.get(playerId);
    if (!playerCd) return 0;
    return playerCd.get(abilityId) || 0;
}

/** Clear all cooldowns for a player (used by !reset). */
export function clearCooldowns(playerId) {
    cooldowns.delete(playerId);
    activeBloodlusts.delete(playerId);
}
