/**
 * Realms of Myth - Player Data Persistence
 * Stores/retrieves player class, race, level via dynamic properties.
 * Race passives and Class Master set bonuses are applied here.
 */

import { world, system, Player } from '@minecraft/server';
import { RACES } from './classSystem.js';
import { CLASS_MASTER_BONUSES } from './config.js';

// ── Persistence helpers ─────────────────────────────────────────────

/**
 * Save player race/class/level to dynamic properties
 */
export function savePlayerData(player, data) {
    if (data.race) player.setDynamicProperty('rom:race', data.race);
    if (data.class) player.setDynamicProperty('rom:class', data.class);
    if (data.level !== undefined) player.setDynamicProperty('rom:level', data.level);
    player.setDynamicProperty('rom:has_chosen', true);
}

/**
 * Load player data — returns null if player hasn't chosen a class yet
 */
export function loadPlayerData(player) {
    const hasChosen = player.getDynamicProperty('rom:has_chosen');
    if (!hasChosen) {
        const race = player.getDynamicProperty('rom:race');
        const cls = player.getDynamicProperty('rom:class');
        // Backward compat: if race+class exist but no has_chosen flag
        if (race && cls) {
            player.setDynamicProperty('rom:has_chosen', true);
            return { race, class: cls, level: player.getDynamicProperty('rom:level') || 1 };
        }
        return null;
    }

    return {
        race: player.getDynamicProperty('rom:race'),
        class: player.getDynamicProperty('rom:class'),
        level: player.getDynamicProperty('rom:level') || 1
    };
}

/**
 * Reset a player's class/race — allows re-choosing
 */
export function resetPlayerData(player) {
    const props = [
        'rom:race', 'rom:class', 'rom:level', 'rom:has_chosen',
        'rom:bloodlust_active', 'rom:bloodlust_end',
        'rom:human_xp_bonus', 'rom:bow_damage_bonus', 'rom:human_skill_points',
        'rom:class_master_bonus', 'rom:master_bonus_announced', 'rom:troll_hp_applied'
    ];
    for (const key of props) {
        player.setDynamicProperty(key, undefined);
    }

    // Clear any class tokens from inventory
    const classes = ['mage', 'ranger', 'berserker', 'paladin', 'druid'];
    for (const c of classes) {
        player.runCommand(`clear @s realms:class_token_${c} 0`);
    }

    // Clear any persistent race / master-set effects
    // Covers all effects we apply (race + master bonus) plus common
    // debuffs that a player might have picked up and shouldn't carry
    // into the new character. `effect @s X 0` removes the effect entirely.
    try {
        const effectsToClear = [
            // Class/race persistent effects
            'night_vision', 'resistance', 'regeneration', 'speed', 'jump_boost',
            'luck', 'slow_falling', 'health_boost', 'absorption', 'fire_resistance',
            'invisibility', 'water_breathing', 'conduit_power',
            // Debuffs (we want a clean slate)
            'weakness', 'slowness', 'mining_fatigue', 'blindness', 'nausea',
            'hunger', 'poison', 'wither', 'levitation', 'darkness', 'oozing',
            'infested', 'wind_charged', 'weaving', 'trial_omen'
        ];
        for (const eff of effectsToClear) {
            try { player.runCommand(`effect @s ${eff} 0`); }
            catch (e2) { /* some effect names may not exist in older versions */ }
        }
    } catch (e) { /* commands may be disabled */ }

    player.sendMessage('§7Your destiny has been reset. Choose again.');
}

// ── Race trait application ──────────────────────────────────────────

/**
 * Apply race passive traits to a player. Called on every spawn/respawn so
 * the effects persist after death. Idempotent — safe to call repeatedly.
 */
export function applyRaceTraits(player) {
    const raceId = player.getDynamicProperty('rom:race');
    if (!raceId) return;

    const race = RACES[raceId];
    if (!race) return;

    const traits = race.traits;

    // Troll: +4 HP (permanent) + slow regeneration
    // Use health_boost (adds 4 HP = 2 hearts) so the bonus is a true +max,
    // not a transient currentValue tweak that gets clobbered on first hit.
    if (traits.bonusHealth) {
        const boostLevel = Math.max(1, Math.floor(traits.bonusHealth / 2));
        player.runCommand(`effect @s health_boost 999999 ${boostLevel} true`);
        // Also push current HP up to the new effective max so Troll spawns
        // at full HP on first apply.
        const health = player.getComponent('minecraft:health');
        if (health) {
            const target = (health.effectiveMax || 20) + traits.bonusHealth;
            if (health.currentValue < target) {
                health.setCurrentValue(target);
            }
        }
    }
    if (traits.slowRegeneration) {
        // regeneration level 0 = 1 HP / 30s — appropriate for "slow regen"
        player.runCommand('effect @s regeneration 999999 0 true');
    }

    // Elf: permanent night vision + bow damage bonus (read in abilities.js)
    if (traits.nightVision) {
        player.runCommand('effect @s night_vision 999999 0 true');
    }
    if (traits.bowDamageBonus) {
        player.setDynamicProperty('rom:bow_damage_bonus', traits.bowDamageBonus);
    }

    // Giant: knockback resistance (via resistance effect) + reach proxy via speed/jump
    if (traits.knockbackResistance) {
        const level = Math.round(traits.knockbackResistance * 5);
        player.runCommand(`effect @s resistance 999999 ${level} true`);
    }
    if (traits.reachBonus) {
        // True reach modifier is unavailable in the Bedrock scripting API.
        // Speed + jump boost is the documented proxy for "larger presence".
        player.runCommand(`effect @s speed 999999 0 true`);
        player.runCommand(`effect @s jump_boost 999999 0 true`);
    }

    // Human: +10% XP bonus (read in abilities.js entityDie handler) + skill point marker
    if (traits.xpBonus) {
        player.runCommand('effect @s luck 999999 0 true');
    }
    if (traits.bonusSkillPoint) {
        player.setDynamicProperty('rom:human_skill_points', traits.bonusSkillPoint);
    }
}

// ── Lifecycle / Class Master bonuses ───────────────────────────────

/**
 * Restore player state on spawn/respawn — reapply traits, check Master set,
 * re-grant class token if missing.
 */
export function restorePlayerState(player) {
    const data = loadPlayerData(player);
    if (!data) return;

    applyRaceTraits(player);
    applyClassMasterBonuses(player);

    // Regive class token if missing
    if (data.class) {
        try {
            const inventory = player.getComponent('minecraft:inventory');
            if (inventory) {
                const container = inventory.container;
                let hasToken = false;
                if (container) {
                    for (let i = 0; i < container.size; i++) {
                        const item = container.getItem(i);
                        if (item && item.typeId === `realms:class_token_${data.class}`) {
                            hasToken = true;
                            break;
                        }
                    }
                }
                if (!hasToken) {
                    player.runCommand(`give @s realms:class_token_${data.class} 1`);
                }
            }
        } catch (e) { /* inventory may be transient on first spawn */ }
    }
}

/**
 * Check if a player is wearing a full Class Master armor set and apply bonuses.
 * Announcement is sent only ONCE per (re)equip (tracked via
 * `rom:master_bonus_announced` dynamic property) so respawns don't spam chat.
 */
export function applyClassMasterBonuses(player) {
    const data = loadPlayerData(player);
    if (!data || !data.class) return;

    const classId = data.class;
    const bonus = CLASS_MASTER_BONUSES[classId];
    if (!bonus) return;

    const equippable = player.getComponent('minecraft:equippable');
    if (!equippable) return;

    const slots = {
        head: equippable.getEquipment('Head'),
        chest: equippable.getEquipment('Chest'),
        legs: equippable.getEquipment('Legs'),
        feet: equippable.getEquipment('Feet')
    };

    const isFullSet = (
        slots.head && slots.head.typeId === `realms:${classId}_master_helmet` &&
        slots.chest && slots.chest.typeId === `realms:${classId}_master_chestplate` &&
        slots.legs && slots.legs.typeId === `realms:${classId}_master_leggings` &&
        slots.feet && slots.feet.typeId === `realms:${classId}_master_boots`
    );

    if (!isFullSet) {
        // Clear bonus state but DO NOT clear ranger/druid passive effects
        // that were set while the set was worn — they expire naturally.
        player.setDynamicProperty('rom:class_master_bonus', undefined);
        player.setDynamicProperty('rom:master_bonus_announced', undefined);
        return;
    }

    // Wearing the set — apply / refresh bonus
    player.setDynamicProperty('rom:class_master_bonus', classId);

    // Refresh persistent effects (ranger speed/slow_falling, druid regen)
    switch (classId) {
        case 'ranger':
            player.runCommand('effect @s speed 999999 1 true');
            player.runCommand('effect @s slow_falling 999999 1 true');
            break;
        case 'druid':
            player.runCommand('effect @s regeneration 999999 0 true');
            break;
    }

    // Announce ONCE per equip, not on every respawn
    const announced = player.getDynamicProperty('rom:master_bonus_announced');
    if (announced !== classId) {
        player.setDynamicProperty('rom:master_bonus_announced', classId);
        switch (classId) {
            case 'mage':
                player.sendMessage('§d✦ Arcane Amplification: +30% ability damage!'); break;
            case 'ranger':
                player.sendMessage('§a✦ Shadow\'s Grace: +15% speed, no fall damage!'); break;
            case 'berserker':
                player.sendMessage('§c✦ Blood Fury: +25% damage when below 50% HP!'); break;
            case 'paladin':
                player.sendMessage('§e✦ Radiant Aegis: 10% damage reflected!'); break;
            case 'druid':
                player.sendMessage('§2✦ Wildheart Vitality: permanent regeneration!'); break;
        }
        console.log(`[Realms of Myth] Applied ${bonus.name} to ${player.name}`);
    }
}
