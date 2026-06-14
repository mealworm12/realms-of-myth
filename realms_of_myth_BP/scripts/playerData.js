/**
 * Realms of Myth - Player Data Persistence
 * Stores/retrieves player class, race, level via dynamic properties
 */

import { world, system, Player } from '@minecraft/server';
import { RACES } from './classSystem.js';
import { CLASS_MASTER_BONUSES } from './config.js';

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
    const props = ['rom:race', 'rom:class', 'rom:level', 'rom:has_chosen',
                   'rom:bloodlust_active', 'rom:bloodlust_end', 'rom:human_xp_bonus',
                   'rom:bow_damage_bonus', 'rom:human_skill_points',
                   'rom:master_bonus_announced', 'rom:troll_hp_applied'];
    for (const key of props) {
        player.setDynamicProperty(key, undefined);
    }

    // Clear any class tokens from inventory
    const classes = ['mage', 'ranger', 'berserker', 'paladin', 'druid'];
    for (const c of classes) {
        player.runCommand(`clear @s realms:class_token_${c} 0`);
    }

    // Clear any persistent race effects
    try {
        player.runCommand('effect @s night_vision 0');
        player.runCommand('effect @s resistance 0');
        player.runCommand('effect @s regeneration 0');
        player.runCommand('effect @s speed 0');
        player.runCommand('effect @s jump_boost 0');
        player.runCommand('effect @s luck 0');
    } catch (e) { /* ignore */ }

    player.sendMessage('§7Your destiny has been reset. Choose again.');
}

/**
 * Apply race passive traits to a player (called on spawn/respawn)
 */
export function applyRaceTraits(player) {
    const raceId = player.getDynamicProperty('rom:race');
    if (!raceId) return;

    const race = RACES[raceId];
    if (!race) return;

    const traits = race.traits;

    // Troll: bonus max HP + slow regeneration
    // Use health_boost effect (each level = +2 HP / +1 heart) for permanent +max HP.
    // health.setCurrentValue() is transient — lost on next heal/damage tick.
    if (traits.bonusHealth) {
        const health = player.getComponent('minecraft:health');
        if (health) {
            // health_boost: level N => +2*N HP added to effectiveMax
            const boostLevel = Math.ceil(traits.bonusHealth / 2);
            player.runCommand(`effect @s health_boost 999999 ${boostLevel} true`);
            // On first apply, clamp current HP up to the new effective max
            const announced = player.getDynamicProperty('rom:troll_hp_applied');
            if (announced !== raceId) {
                const newMax = health.effectiveMax + traits.bonusHealth;
                health.setCurrentValue(Math.min(newMax, health.currentValue + traits.bonusHealth));
                player.setDynamicProperty('rom:troll_hp_applied', raceId);
            }
        }
    }
    if (traits.slowRegeneration) {
        player.runCommand('effect @s regeneration 999999 0 true');
    }

    // Elf: permanent night vision
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
        // True reach modifier unavailable in scripting; use speed+jump as proxy
        player.runCommand(`effect @s speed 999999 0 true`);
        player.runCommand(`effect @s jump_boost 999999 0 true`);
    }

    // Human: +10% XP bonus (tracked via entityDie handler in main.js)
    // Apply luck as a visible indicator
    if (traits.xpBonus) {
        player.runCommand('effect @s luck 999999 0 true');
    }
    if (traits.bonusSkillPoint) {
        player.setDynamicProperty('rom:human_skill_points', traits.bonusSkillPoint);
    }

    console.log(`[Realms of Myth] Applied ${raceId} traits to ${player.name}`);
}

/**
 * Restore player state on spawn/respawn — reapply traits and class token
 */
export function restorePlayerState(player) {
    const data = loadPlayerData(player);
    if (!data) return;

    console.log(`[Realms of Myth] Restoring ${player.name}: ${data.race} ${data.class}`);

    applyRaceTraits(player);
    applyClassMasterBonuses(player);

    // Regive class token if missing
    if (data.class) {
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
    }
}

/**
 * Check if a player is wearing a full Class Master armor set and apply bonuses.
 * Run on spawn/respawn and re-check periodically.
 * 
 * Class Master bonus application:
 * - Mage: +30% ability damage (stored as dynamic property, checked in abilities.js)
 * - Ranger: +15% speed, no fall damage
 * - Berserker: +25% damage when below 50% HP
 * - Paladin: 10% damage reflect
 * - Druid: permanent regeneration
 */
export function applyClassMasterBonuses(player) {
    const data = loadPlayerData(player);
    if (!data || !data.class) return;

    const classId = data.class;
    const bonus = CLASS_MASTER_BONUSES[classId];
    if (!bonus) return;

    const equippable = player.getComponent('minecraft:equippable');
    if (!equippable) return;

    // Check if player is wearing full Class Master set
    const classPrefix = classId;
    const slots = {
        head: equippable.getEquipment('Head'),
        chest: equippable.getEquipment('Chest'),
        legs: equippable.getEquipment('Legs'),
        feet: equippable.getEquipment('Feet')
    };

    const isFullSet = (
        slots.head && slots.head.typeId === `realms:${classPrefix}_master_helmet` &&
        slots.chest && slots.chest.typeId === `realms:${classPrefix}_master_chestplate` &&
        slots.legs && slots.legs.typeId === `realms:${classPrefix}_master_leggings` &&
        slots.feet && slots.feet.typeId === `realms:${classPrefix}_master_boots`
    );

    if (!isFullSet) {
        // Clear any previous bonuses
        player.setDynamicProperty('rom:class_master_bonus', undefined);
        player.setDynamicProperty('rom:master_bonus_announced', undefined);
        return;
    }

    // Apply the bonus
    player.setDynamicProperty('rom:class_master_bonus', classId);

    // Only send the announcement once per (class, equip) state — re-equipping
    // or dying and respawning will not spam chat.
    const announced = player.getDynamicProperty('rom:master_bonus_announced');
    if (announced === classId) {
        return;
    }
    player.setDynamicProperty('rom:master_bonus_announced', classId);

    switch (classId) {
        case 'mage':
            // +30% ability damage — tracked in abilities.js via dynamic property
            player.sendMessage('§d✦ Arcane Amplification: +30% ability damage!');
            break;
        case 'ranger':
            // +15% speed, no fall damage
            player.runCommand('effect @s speed 999999 1 true');
            player.runCommand('effect @s slow_falling 999999 1 true');
            player.sendMessage('§a✦ Shadow\'s Grace: +15% speed, no fall damage!');
            break;
        case 'berserker':
            // +25% damage at <50% HP — tracked in abilities.js via dynamic property
            player.sendMessage('§c✦ Blood Fury: +25% damage when below 50% HP!');
            break;
        case 'paladin':
            // 10% damage reflect — tracked in abilities.js via dynamic property
            player.sendMessage('§e✦ Radiant Aegis: 10% damage reflected!');
            break;
        case 'druid':
            // Permanent regeneration
            player.runCommand('effect @s regeneration 999999 0 true');
            player.sendMessage('§2✦ Wildheart Vitality: permanent regeneration!');
            break;
    }

    console.log(`[Realms of Myth] Applied ${bonus.name} to ${player.name}`);
}
