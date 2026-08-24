/**
 * Realms of Myth - Class Selection UI
 * Handles the multi-step form for race + class selection using @minecraft/server-ui.
 *
 * Supports pre-selection via class token: when a player uses a class token item,
 * the form opens with that class pre-selected on the second step.
 */

import { world } from '@minecraft/server';
import { ActionFormData } from '@minecraft/server-ui';
import { RACES, CLASSES } from './classSystem.js';
import { savePlayerData } from './playerData.js';
import { startQuestChain } from './quests.js';

/** Per-class signature sound played on class confirmation. */
const CLASS_CONFIRM_SOUNDS = {
    mage:      'realms.weapon.staff_cast',
    ranger:    'realms.weapon.bow_release',
    berserker: 'realms.ability.rage_cast',
    paladin:   'realms.ability.holy_light_cast',
    druid:     'realms.ability.natures_blessing_cast'
};

/**
 * Show the class selection form to a player.
 * Step 1: Choose race → Step 2: Choose class → Step 3: Confirm
 *
 * @param {Player} player
 * @param {string|null} preselectedClassId - if set, skip class selection step
 *        and go straight to confirm with this class (used by class tokens)
 */
export function showClassSelectionForm(player, preselectedClassId = null) {
    // Custom UI sound when the selection flow opens
    try { player.playSound('realms.ui.class_select_open'); } catch (e) { /* */ }
    // If race already chosen + class pre-selected (from a class token),
    // go directly to the confirm step.
    const racePending = player.getDynamicProperty('rom:race_pending');
    if (preselectedClassId && racePending) {
        const race = RACES[racePending];
        const cls = CLASSES[preselectedClassId];
        if (race && cls) {
            showConfirmScreen(player, race, cls);
            return;
        }
    }
    showRaceSelection(player);
}

/**
 * Step 1: Race selection
 */
function showRaceSelection(player) {
    const form = new ActionFormData()
        .title('§lChoose Your Race')
        .body('Every hero begins somewhere. Choose your lineage:');

    for (const [, race] of Object.entries(RACES)) {
        const traits = race.traits;
        const desc = [];
        if (traits.bowDamageBonus) desc.push(`+${Math.round(traits.bowDamageBonus * 100)}% Bow Damage`);
        if (traits.nightVision) desc.push('Night Vision');
        if (traits.bonusHealth) desc.push(`+${traits.bonusHealth} HP`);
        if (traits.slowRegeneration) desc.push('Regeneration');
        if (traits.knockbackResistance) desc.push('Knockback Resist');
        if (traits.reachBonus) desc.push(`+${traits.reachBonus} Reach`);
        if (traits.xpBonus) desc.push(`+${Math.round(traits.xpBonus * 100)}% XP`);

        form.button(`§e${race.name}\n§7${desc.join(' • ')}`);
    }

    form.show(player).then((response) => {
        if (response.canceled) return;

        const raceIds = Object.keys(RACES);
        const selectedRaceId = raceIds[response.selection];
        const selectedRace = RACES[selectedRaceId];

        // Store race choice temporarily
        player.setDynamicProperty('rom:race_pending', selectedRaceId);

        // Continue to class selection
        showClassSelection(player, selectedRace);
    });
}

/**
 * Step 2: Class selection
 */
function showClassSelection(player, selectedRace) {
    const form = new ActionFormData()
        .title(`§lChoose Your Class §7(${selectedRace.name})`)
        .body('The path you walk defines who you become:');

    for (const [, cls] of Object.entries(CLASSES)) {
        const abilText = cls.abilities.map(a => a.name).join(', ');
        form.button(`§b${cls.name}\n§7${cls.description}\n§8Abilities: ${abilText}`);
    }

    form.show(player).then((response) => {
        if (response.canceled) {
            player.setDynamicProperty('rom:race_pending', undefined);
            return;
        }

        const classIds = Object.keys(CLASSES);
        const selectedClassId = classIds[response.selection];
        const selectedClass = CLASSES[selectedClassId];

        // Show confirmation
        showConfirmScreen(player, selectedRace, selectedClass);
    });
}

/**
 * Step 3: Confirmation
 */
function showConfirmScreen(player, race, cls) {
    const form = new ActionFormData()
        .title('§lConfirm Your Choice')
        .body([
            `§6Race: §e${race.name}`,
            `§6Class: §b${cls.name}`,
            ``,
            `§7${cls.description}`,
            ``,
            `§aAbilities:`
        ].concat(cls.abilities.map((a, i) => `  §7${i + 1}. §b${a.name}`)).join('\n'))
        .button('§a✓ Confirm')
        .button('§c↩ Go Back');

    form.show(player).then((response) => {
        if (response.canceled) {
            player.setDynamicProperty('rom:race_pending', undefined);
            return;
        }

        if (response.selection === 0) {
            // Confirm! Save the choices
            finalizeClassSelection(player, race.id, cls.id);
        } else {
            // Go back to race selection
            player.setDynamicProperty('rom:race_pending', undefined);
            showRaceSelection(player);
        }
    });
}

/**
 * Finalize the player's class and race choices
 */
export function finalizeClassSelection(player, raceId, classId) {
    const race = RACES[raceId];
    const cls = CLASSES[classId];
    if (!race || !cls) {
        player.sendMessage('§cInvalid race or class selection.');
        return;
    }

    // Clear pending
    player.setDynamicProperty('rom:race_pending', undefined);

    // Save permanent data
    savePlayerData(player, { race: raceId, class: classId, level: 1 });
    startQuestChain(player);

    // Welcome the player (no token is given here — tokens are only given
    // via the loot/treasure flow, not as a result of selection)
    player.sendMessage({
        rawtext: [
            { text: '§6══════════════════════════════════\n' },
            { text: `§eYour destiny is sealed, §l${race.name} ${cls.name}§r§e!\n` },
            { text: `§7Use your abilities in combat — press §a!classinfo §7to see them.` },
        ]
    });

    // Play a sound (custom class-select burst SFX; themed signature follows below)
    player.playSound('realms.ui.class_select_open');

    // Custom FX: class-select burst + class-themed signature sound.
    // Prestige ritual aura: re-choosing a class after having one counts as
    // the prestige moment — divine shield aura + holy light beam.
    try {
        player.dimension.spawnParticle('realms:class_select_burst', {
            x: player.location.x, y: player.location.y + 1, z: player.location.z
        });
        const themedSound = CLASS_CONFIRM_SOUNDS[classId] || 'realms.ui.ability_ready';
        player.playSound(themedSound);
        // Prestige ritual aura (player had a previous destiny sealed)
        player.dimension.spawnParticle('realms:divine_shield_aura', {
            x: player.location.x, y: player.location.y + 1, z: player.location.z
        });
    } catch (e) { /* particle may not resolve */ }

    console.log(`[Realms of Myth] ${player.name} chose ${race.name} ${cls.name}`);
}
