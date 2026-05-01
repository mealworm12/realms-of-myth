/**
 * Realms of Myth - Ability Execution System
 * Handles ability activation, cooldowns, and visual effects via item usage
 */

import { world, system, Player } from '@minecraft/server';
import { CLASSES, getClassAbilities } from './classSystem.js';
import { loadPlayerData } from './playerData.js';

// Cooldowns: playerId -> { abilityId: remainingTicks }
const cooldowns = new Map();
// Track which players have bloodlust active: playerId -> endTick
const activeBloodlusts = new Map();

/**
 * Register ability triggers and cooldown processing.
 * Call once during mod initialization.
 */
export function registerAbilities() {
    const ABILITY_ITEMS = [
        'minecraft:nether_star',
        'minecraft:blaze_powder',
        'minecraft:ghast_tear'
    ];

    // ── Handle ability activation via item use ────────────
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

        // Check cooldown
        const playerCd = getCooldownMap(player.id);
        const remaining = playerCd.get(ability.id) || 0;
        if (remaining > 0) {
            player.sendMessage(`§c§l${ability.name} §ris on cooldown: §e${Math.ceil(remaining / 20)}s`);
            return;
        }

        // Set cooldown
        playerCd.set(ability.id, ability.cooldown);

        // Execute
        executeAbility(player, data.class, ability, data.race);

        player.sendMessage(`§a✨ §l${ability.name}§r §aactivated!`);
        player.playSound('random.orb');
    });

    // ── Cooldown tick processing ──────────────────────────
    let tickCounter = 0;
    system.runInterval(() => {
        tickCounter++;
        
        // Tick cooldowns every tick
        for (const [, cdMap] of cooldowns) {
            for (const [abilityId, ticks] of cdMap) {
                if (ticks > 0) cdMap.set(abilityId, ticks - 1);
            }
        }

        // Check bloodlust expiry every 10 ticks
        if (tickCounter % 10 === 0) {
            const currentTick = tickCounter;
            for (const [playerId, endTick] of activeBloodlusts) {
                if (currentTick >= endTick) {
                    activeBloodlusts.delete(playerId);
                }
            }
        }
    }, 1);

    // ── Lifesteal handler (bloodlust) ─────────────────────
    world.afterEvents.entityHurt.subscribe((event) => {
        if (!event.damageSource?.damagingEntity) return;
        const damager = event.damageSource.damagingEntity;
        if (!(damager instanceof Player)) return;

        if (!activeBloodlusts.has(damager.id)) return;

        const healAmount = Math.ceil(event.damage * 0.30);
        const health = damager.getComponent('minecraft:health');
        if (health) {
            health.setCurrentValue(Math.min(
                health.currentValue + healAmount,
                health.effectiveMax
            ));
        }
    });

    // ── Dragonslayer handler ──────────────────────────────
    world.afterEvents.entityHurt.subscribe((event) => {
        if (!event.damageSource?.damagingEntity) return;
        const damager = event.damageSource.damagingEntity;
        const victim = event.hurtEntity;
        if (!(damager instanceof Player)) return;

        // Check if victim is dragon-type
        const family = victim.getComponent('minecraft:type_family');
        if (!family || !family.hasType('dragon')) return;

        // Check for dragonslayer weapon
        const equippable = damager.getComponent('minecraft:equippable');
        if (!equippable) return;
        const weapon = equippable.getEquipment('Mainhand');
        if (!weapon || weapon.typeId !== 'realms:dragonslayer_spear') return;

        // Double damage
        const extraDamage = event.damage;
        const health = victim.getComponent('minecraft:health');
        if (health) {
            health.setCurrentValue(health.currentValue - extraDamage);
        }
        damager.sendMessage('§6⚔ Dragonslayer! Double damage dealt.');
    });
}

function getCooldownMap(playerId) {
    if (!cooldowns.has(playerId)) cooldowns.set(playerId, new Map());
    return cooldowns.get(playerId);
}

/**
 * Dispatch to the correct ability implementation
 */
function executeAbility(player, classId, ability, raceId) {
    switch (ability.id) {
        // Mage
        case 'fireball':     spawnFireball(player, ability); break;
        case 'ice_shield':   applyShield(player, ability, 'resistance', 3); break;
        case 'arcane_teleport': teleportForward(player, ability); break;
        // Ranger
        case 'multi_shot':   spawnArrowSpread(player, ability); break;
        case 'shadow_step':  applyBuffs(player, ability, [
            ['invisibility', 0], ['speed', 2]
        ], 'mob.wither.spawn', 'minecraft:endrod'); break;
        case 'eagle_eye':    highlightNearby(player, ability); break;
        // Berserker
        case 'rage':         applyBuffs(player, ability, [
            ['strength', 2], ['speed', 1]
        ], 'mob.ravager.roar', 'minecraft:angry_villager'); break;
        case 'ground_slam':  doGroundSlam(player, ability); break;
        case 'bloodlust':    activateBloodlust(player, ability); break;
        // Paladin
        case 'holy_light':   healAOE(player, ability); break;
        case 'divine_shield': applyShield(player, ability, 'resistance', 10); break;
        case 'smite':         doSmite(player, ability); break;
        // Druid
        case 'wolf_form':    applyBuffs(player, ability, [
            ['speed', 2], ['strength', 1]
        ], 'mob.wolf.growl', 'minecraft:wolf_ambient'); break;
        case 'entangling_roots': rootEnemy(player, ability); break;
        case 'natures_blessing': applyHoT(player, ability); break;
    }
}

// ═══════════════════════════════════════════════════════════
// GENERIC ABILITY HELPERS
// ═══════════════════════════════════════════════════════════

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

// ═══════════════════════════════════════════════════════════
// MAGE
// ═══════════════════════════════════════════════════════════

function spawnFireball(player) {
    const head = player.getHeadLocation();
    const dir = player.getViewDirection();
    player.dimension.spawnEntity('minecraft:fireball', {
        x: head.x + dir.x * 1.5,
        y: head.y + dir.y * 1.5,
        z: head.z + dir.z * 1.5
    });
    player.playSound('mob.blaze.shoot');
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

// ═══════════════════════════════════════════════════════════
// RANGER
// ═══════════════════════════════════════════════════════════

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

// ═══════════════════════════════════════════════════════════
// BERSERKER
// ═══════════════════════════════════════════════════════════

function doGroundSlam(player, ability) {
    const dim = player.dimension;

    // Knockback: give enemies levitation burst then clear
    dim.runCommand(`effect @e[family=monster,r=${ability.radius}] levitation 5 0 true`);
    
    // Damage via instant_damage effect (works on all Bedrock versions)
    dim.runCommand(`effect @e[family=monster,r=${ability.radius}] instant_damage 1 ${Math.round(ability.damage / 3)} true`);

    dim.runCommand(`execute at @p run particle minecraft:large_explosion ~ ~ ~`);
    player.playSound('mob.irongolem.hit');
}

function activateBloodlust(player, ability) {
    // Small instant heal as burst
    player.runCommand('effect @s instant_health 1 1 true');
    player.playSound('mob.evocation_illager.prepare_summon');

    // Store player ID with tick-based expiry (not Date.now)
    const endTick = Math.floor(system.currentTick) + ability.duration;
    activeBloodlusts.set(player.id, endTick);
}

// ═══════════════════════════════════════════════════════════
// PALADIN
// ═══════════════════════════════════════════════════════════

function healAOE(player, ability) {
    const level = Math.round(ability.healAmount / 4);
    player.runCommand(`effect @s instant_health 1 ${level} true`);
    player.dimension.runCommand(`effect @e[family=player,r=${ability.radius}] instant_health 1 ${level} true`);
    player.dimension.runCommand(`execute at @p run particle minecraft:totem_of_undying ~ ~ ~`);
    player.playSound('random.orb');
}

function doSmite(player, ability) {
    // Damage nearest monsters via instant_damage (bypasses armor as magic)
    const dim = player.dimension;
    dim.runCommand(`effect @e[family=monster,c=1,r=8] instant_damage 1 ${Math.round(ability.damage / 3)} true`);
    player.playSound('ambient.weather.thunder');
    dim.runCommand(`execute at @p run particle minecraft:lightning_bolt ~ ~ ~`);
}

// ═══════════════════════════════════════════════════════════
// DRUID
// ═══════════════════════════════════════════════════════════

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

/**
 * Get remaining cooldown ticks for a player's ability
 */
export function getCooldown(playerId, abilityId) {
    const playerCd = cooldowns.get(playerId);
    if (!playerCd) return 0;
    return playerCd.get(abilityId) || 0;
}
