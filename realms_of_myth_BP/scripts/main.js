/**
 * Realms of Myth - Main Entry Point
 * Fantasy Minecraft Add-On for Education & Bedrock Edition
 *
 * Module-scope event subscriptions are registered at import time; nothing
 * needs to be called after import.
 */

import { world, system } from '@minecraft/server';
import { CLASSES, RACES } from './classSystem.js';
import { restorePlayerState, resetPlayerData, loadPlayerData } from './playerData.js';
import { showClassSelectionForm } from './classSelection.js';
import { registerAbilities, clearCooldowns } from './abilities.js';
import { registerDragonAI } from './dragonBoss.js';

console.log('[Realms of Myth] Initializing...');

// ── World Initialization ────────────────────────────────────────────
world.afterEvents.worldInitialize.subscribe(() => {
    console.log('[Realms of Myth] World initialized');
    registerDragonAI();
});

// ── Player Spawn (respawn) ──────────────────────────────────────────
world.afterEvents.playerSpawn.subscribe((event) => {
    console.log(`[Realms of Myth] Player spawned: ${event.player.name}`);
    restorePlayerState(event.player);
});

// ── Player Join (first time) ────────────────────────────────────────
world.afterEvents.playerJoin.subscribe((event) => {
    const player = event.player;
    const hasChosen = player.getDynamicProperty('rom:has_chosen');
    const raceTag = player.getDynamicProperty('rom:race');

    if (!hasChosen && !raceTag) {
        system.runTimeout(() => {
            player.sendMessage({
                rawtext: [
                    { text: '§6══════════════════════════════════\n' },
                    { text: '§e§lWelcome to Realms of Myth!\n' },
                    { text: '§7Speak with the Oracle or find the Ancient Altar.\n' },
                    { text: '§7Type §a!class §7to open the class selection screen.\n' },
                    { text: '§7Type §a!help §7for the full command list.\n' },
                    { text: '§6══════════════════════════════════' }
                ]
            });
        }, 40);
    }
});

// ── Player Leave cleanup ────────────────────────────────────────────
world.afterEvents.playerLeave.subscribe((event) => {
    clearCooldowns(event.playerId);
});

// ── Entity Interact: Oracle opens class selection ───────────────────
world.afterEvents.playerInteractWithEntity.subscribe((event) => {
    const player = event.player;
    const target = event.target;
    if (!target) return;

    // Oracle / Elf Warrior: click to open class selection
    if (target.typeId === 'realms:elf_warrior') {
        const raceTag = player.getDynamicProperty('rom:race');
        const hasChosen = player.getDynamicProperty('rom:has_chosen');
        if (raceTag && hasChosen) {
            const cls = player.getDynamicProperty('rom:class');
            const clsData = CLASSES[cls];
            player.sendMessage(`§7The Oracle: §eYou walk the path of the §l${raceTag} ${clsData ? clsData.name : cls}§r§e. §7Use §e!reset §7to begin anew.`);
        } else {
            player.sendMessage('§6The Oracle opens the Scroll of Destiny...');
            system.runTimeout(() => showClassSelectionForm(player), 5);
        }
    }
});

// ── Block Interact: Ancient Altar opens class selection ────────────
world.afterEvents.playerInteractWithBlock.subscribe((event) => {
    const player = event.player;
    const block = event.block;
    if (!block) return;

    if (block.typeId === 'realms:ancient_altar') {
        const raceTag = player.getDynamicProperty('rom:race');
        const hasChosen = player.getDynamicProperty('rom:has_chosen');
        if (!raceTag || !hasChosen) {
            player.sendMessage('§6§lThe Ancient Altar hums with ancient power...');
            system.runTimeout(() => showClassSelectionForm(player), 5);
        } else {
            const cls = player.getDynamicProperty('rom:class');
            const clsData = CLASSES[cls];
            player.sendMessage(`§7The Altar recognizes you: §e§l${raceTag} ${clsData ? clsData.name : cls}§r§7. Use §e!classinfo §7to review abilities.`);
        }
    }
});

// ── Chat Commands ──────────────────────────────────────────────────
world.beforeEvents.chatSend.subscribe((event) => {
    const player = event.sender;
    const msg = event.message.trim().toLowerCase();

    if (msg === '!class' || msg === '!choose') {
        event.cancel = true;
        const raceTag = player.getDynamicProperty('rom:race');
        if (raceTag && player.getDynamicProperty('rom:has_chosen')) {
            player.sendMessage('§cYou have already chosen a class! Use §e!reset §cto start over.');
        } else {
            showClassSelectionForm(player);
        }
    } else if (msg === '!reset') {
        event.cancel = true;
        resetPlayerData(player);
        system.runTimeout(() => showClassSelectionForm(player), 20);
    } else if (msg === '!classinfo') {
        event.cancel = true;
        const data = loadPlayerData(player);
        if (!data) {
            player.sendMessage("§cYou haven't chosen a class yet! Use §e!class");
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
        // Active race passives
        if (race) {
            player.sendMessage({ rawtext: [{ text: '§6— Race passives —' }] });
            for (const [k, v] of Object.entries(race.traits)) {
                if (k === 'baseHealth') continue;
                player.sendMessage({ rawtext: [{ text: `  §7• §e${k}§7: ${typeof v === 'boolean' ? v : v}` }] });
            }
        }
    } else if (msg === '!help' || msg === '!commands') {
        event.cancel = true;
        player.sendMessage({
            rawtext: [
                { text: '§6═══ §eRealms of Myth §6═══\n' },
                { text: '§a!class §7/ §a!choose §7— open race & class selection\n' },
                { text: '§a!classinfo §7— show your class abilities + race passives\n' },
                { text: '§a!reset §7— reset your race & class (re-pick)\n' },
                { text: '§a!help §7— show this list\n' },
                { text: '§7Abilities: hold Nether Star (☆), Blaze Powder (🔥), Ghast Tear (💧) + right-click\n' },
                { text: '§7Find the Ancient Altar or speak to the Elf Warrior to start.' }
            ]
        });
    }
});

// ── Register ability system (event subscriptions + cooldowns) ──────
registerAbilities();

console.log('[Realms of Myth] Ready!');
