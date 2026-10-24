/**
 * Realms of Myth - player-facing command surface.
 *
 * Bedrock's script API no longer exposes chatSend (absent in every module
 * version on 1.26.x), so the old `!class`-style chat commands cannot work.
 * The Oracle now opens this menu instead; admins can still run
 * `/scriptevent realms:cmd <command>`.
 */

import { system } from '@minecraft/server';
import { ActionFormData } from '@minecraft/server-ui';
import { CLASSES, RACES } from './classSystem.js';
import { loadPlayerData, resetPlayerData } from './playerData.js';
import { questStatus } from './quests.js';
import { showClassSelectionForm } from './classSelection.js';

export function sendClassInfo(player) {
    const data = loadPlayerData(player);
    if (!data) {
        player.sendMessage("§cYou haven't chosen a class yet! Talk to the Oracle.");
        return;
    }
    const cls = CLASSES[data.class];
    if (!cls) return;
    const race = RACES[data.race];
    player.sendMessage({ rawtext: [{ text: `§6═══ §e${cls.name} §7(${race ? race.name : data.race}) §6═══\n` }] });
    cls.abilities.forEach((a, i) => {
        player.sendMessage({
            rawtext: [{ text: `§b${i + 1}. ${a.name} §8- §7${a.description} §8(${Math.round(a.cooldown / 20)}s cooldown)` }]
        });
    });
    if (race) {
        player.sendMessage({ rawtext: [{ text: '§6— Race passives —' }] });
        for (const [k, v] of Object.entries(race.traits)) {
            if (k === 'baseHealth') continue;
            player.sendMessage({ rawtext: [{ text: `  §7• §e${k}§7: ${v}` }] });
        }
    }
}

export function sendHelp(player) {
    player.sendMessage({
        rawtext: [
            { text: '§6═══ §eRealms of Myth §6═══\n' },
            { text: '§aOracle§7 — class info, quest status, reset, help\n' },
            { text: '§aAncient Altar§7 — summoning ritual and class prestige\n' },
            { text: '§aClass Tokens§7 — pre-select a class when you use one\n' },
            { text: '§7Abilities: hold Nether Star (☆), Blaze Powder (🔥), Ghast Tear (💧) + right-click\n' },
            { text: '§8Admins: /scriptevent realms:cmd help' }
        ]
    });
}

export function resetDestiny(player) {
    resetPlayerData(player);
    system.runTimeout(() => showClassSelectionForm(player), 20);
}

/** Oracle menu: the replacement for the removed chat commands. */
export function showCommandMenu(player) {
    const form = new ActionFormData()
        .title('§lChronicle of the Realm')
        .body('The Oracle regards you. What do you seek?')
        .button('§bClass & Abilities')
        .button('§eCurrent Quest')
        .button('§cReset Destiny')
        .button('§7Help');

    form.show(player).then((response) => {
        if (response.canceled || response.selection === undefined) return;
        switch (response.selection) {
            case 0: sendClassInfo(player); break;
            case 1: questStatus(player); break;
            case 2: resetDestiny(player); break;
            case 3: sendHelp(player); break;
        }
    }).catch(() => { /* UI closed */ });
}
