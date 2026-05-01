/**
 * Realms of Myth - Player Data Persistence
 * Stores/retrieves player class, race, level via dynamic properties
 */

import { world, Player } from '@minecraft/server';
import { RACES } from './classSystem.js';

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
                   'rom:bloodlust_active', 'rom:bloodlust_end'];
    for (const key of props) {
        player.setDynamicProperty(key, undefined);
    }

    // Clear any class tokens from inventory
    const classes = ['mage', 'ranger', 'berserker', 'paladin', 'druid'];
    for (const c of classes) {
        player.runCommand(`clear @s realms:class_token_${c} 0 0`);
    }

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

    // Troll: bonus max HP
    if (traits.bonusHealth) {
        const health = player.getComponent('minecraft:health');
        if (health) {
            // Use max attribute if available, otherwise fallback to 20 + bonus
            const effectiveMax = health.effectiveMax || 20;
            health.setCurrentValue(effectiveMax + traits.bonusHealth);
        }
    }

    // Elf: permanent night vision (999999 seconds = ~11.5 days = effectively permanent)
    if (traits.nightVision) {
        player.runCommand('effect @s night_vision 999999 0 true');
    }

    // Giant: knockback resistance
    if (traits.knockbackResistance) {
        const level = Math.round(traits.knockbackResistance * 5); // 0.5 * 5 = 2.5 → 2
        player.runCommand(`effect @s resistance 999999 ${level} true`);
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

    // Regive class token if missing
    if (data.class) {
        const inventory = player.getComponent('minecraft:inventory');
        if (inventory) {
            player.runCommand(`give @s realms:class_token_${data.class} 1`);
        }
    }
}
