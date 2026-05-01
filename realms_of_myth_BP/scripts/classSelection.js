/**
 * Realms of Myth - Class Selection UI
 * Handles the multi-step form for race + class selection using @minecraft/server-ui
 */

import { ActionFormData, ModalFormData, MessageFormData } from '@minecraft/server-ui';
import { RACES, CLASSES, getRaceTraits, getClassAbilities } from './classSystem.js';
import { savePlayerData } from './playerData.js';
import { Player } from '@minecraft/server';

/**
 * Show the class selection form to a player.
 * Step 1: Choose race → Step 2: Choose class → Step 3: Confirm
 */
export function showClassSelectionForm(player) {
    showRaceSelection(player);
}

/**
 * Step 1: Race selection
 */
function showRaceSelection(player) {
    const form = new ActionFormData()
        .title('§lChoose Your Race')
        .body('Every hero begins somewhere. Choose your lineage:');

    for (const [id, race] of Object.entries(RACES)) {
        const traits = race.traits;
        let desc = [];
        if (traits.bowDamageBonus) desc.push(`+${Math.round(traits.bowDamageBonus*100)}% Bow Damage`);
        if (traits.nightVision) desc.push('Night Vision');
        if (traits.bonusHealth) desc.push(`+${traits.bonusHealth} HP`);
        if (traits.slowRegeneration) desc.push('Regeneration');
        if (traits.knockbackResistance) desc.push('Knockback Resist');
        if (traits.reachBonus) desc.push(`+${traits.reachBonus} Reach`);
        if (traits.xpBonus) desc.push(`+${Math.round(traits.xpBonus*100)}% XP`);

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

    for (const [id, cls] of Object.entries(CLASSES)) {
        let abilText = cls.abilities.map(a => a.name).join(', ');
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
        ].concat(cls.abilities.map((a, i) => `  §7${i+1}. §b${a.name}`)).join('\n'))
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

    // Clear pending
    player.setDynamicProperty('rom:race_pending', undefined);

    // Save permanent data
    savePlayerData(player, { race: raceId, class: classId, level: 1 });

    // Give class token
    player.runCommand(`give @s realms:class_token_${classId}`);

    // Welcome the player
    player.sendMessage({
        rawtext: [
            { text: '§6══════════════════════════════════\n' },
            { text: `§eYour destiny is sealed, §l${race.name} ${cls.name}§r§e!\n` },
            { text: `§7Use your abilities in combat — press §a!classinfo §7to see them.` },
        ]
    });

    // Play a sound
    player.playSound('random.levelup');

    console.log(`[Realms of Myth] ${player.name} chose ${race.name} ${cls.name}`);
}

/**
 * Handle class selection triggered by NPC interaction
 */
export function handleClassSelection(player) {
    const raceTag = player.getDynamicProperty('rom:race');
    if (raceTag) {
        player.sendMessage('§cYou have already chosen a path. Use §e!reset §cto begin anew.');
        return;
    }
    showClassSelectionForm(player);
}
