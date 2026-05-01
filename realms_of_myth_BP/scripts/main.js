/**
 * Realms of Myth - Main Entry Point
 * Fantasy Minecraft Add-On for Education & Bedrock Edition
 */

import { world, system, Player } from '@minecraft/server';
import { CLASSES } from './classSystem.js';
import { restorePlayerState, resetPlayerData } from './playerData.js';
import { showClassSelectionForm } from './classSelection.js';
import { registerAbilities } from './abilities.js';
import { registerDragonAI } from './dragonBoss.js';

console.log('[Realms of Myth] Initializing...');

// ── World Initialization ─────────────────────────────────
world.afterEvents.worldInitialize.subscribe(() => {
    console.log('[Realms of Myth] World initialized');
    registerDragonAI();
});

// ── Player Spawn (respawn) ───────────────────────────────
world.afterEvents.playerSpawn.subscribe((event) => {
    console.log(`[Realms of Myth] Player spawned: ${event.player.name}`);
    restorePlayerState(event.player);
});

// ── Player Join (first time) ──────────────────────────────
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
                    { text: '§7Find the Ancient Altar to choose your destiny.\n' },
                    { text: '§7Type §a!class §7to open the class selection screen.\n' },
                    { text: '§6══════════════════════════════════' }
                ]
            });
        }, 40);
    }
});

// ── Chat Commands ─────────────────────────────────────────
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
        const classId = player.getDynamicProperty('rom:class');
        const race = player.getDynamicProperty('rom:race');
        if (!classId || !race) {
            player.sendMessage("§cYou haven't chosen a class yet! Use §e!class");
            return;
        }
        const cls = CLASSES[classId];
        if (!cls) return;
        player.sendMessage({
            rawtext: [{ text: `§6═══ §e${cls.name} §7(${race}) §6═══\n` }]
        });
        cls.abilities.forEach((a, i) => {
            player.sendMessage({
                rawtext: [{ text: `§b${i + 1}. ${a.name} §8- §7${a.description} §8(${Math.round(a.cooldown / 20)}s cooldown)` }]
            });
        });
    }
});

// ── Register ability system ───────────────────────────────
registerAbilities();

console.log('[Realms of Myth] Ready!');
