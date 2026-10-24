/**
 * Realms of Myth - Main Entry Point
 * Fantasy Minecraft Add-On for Education & Bedrock Edition
 *
 * Module-scope event subscriptions are registered at import time; nothing
 * needs to be called after import.
 */

import { world, system } from '@minecraft/server';
import { CLASSES } from './classSystem.js';
import { restorePlayerState, applyClassMasterBonuses } from './playerData.js';
import { showClassSelectionForm } from './classSelection.js';
import { registerAbilities } from './abilities.js';
import { registerDragonAI, registerFogMaintenance, registerLairAmbience } from './dragonBoss.js';
import { registerQuests, questStatus } from './quests.js';
import { registerMythicWeapons } from './mythicWeapons.js';
import { registerTaming, tryBreathAttack } from './dragonRiding.js';
import { handleAltarRitual } from './altar.js';
import { tickPrestigeAuras } from './altar.js';
import { registerScaling } from './difficultyScaling.js';
import { showCommandMenu, sendClassInfo, sendHelp, resetDestiny } from './commands.js';

console.log('[Realms of Myth] Initializing...');

// ── World Initialization ────────────────────────────────────────────
// @minecraft/server 2.x renamed WorldInitializeAfterEvent to
// WorldLoadAfterEvent (the old name is gone, so subscribing to it throws at
// module-eval time and disables every script in the pack). Prefer the 2.x
// event and keep a 1.x fallback so Education builds still boot.
const worldReadyEvent = world.afterEvents.worldLoad ?? world.afterEvents.worldInitialize;

if (!worldReadyEvent) {
    console.warn('[Realms of Myth] No world-load event on this API version; scripts are inactive.');
} else {
    worldReadyEvent.subscribe(() => {
        console.log('[Realms of Myth] World loaded');
        registerDragonAI();
        registerFogMaintenance();
        registerLairAmbience();
        registerQuests();
        registerMythicWeapons();
        registerTaming();
        registerScaling();

        // Prestige aura renderer (every second)
        system.runInterval(() => {
            try { tickPrestigeAuras(); } catch (e) { /* */ }
        }, 20);
    });
}

// ── Player Spawn (first join + respawn) ─────────────────────────────
// playerJoin only exposes playerId/playerName in every 2.x API — it has no
// Player object. playerSpawn is the supported hook and also carries
// initialSpawn, which is exactly what the first-join welcome needs.
world.afterEvents.playerSpawn.subscribe((event) => {
    const player = event.player;
    restorePlayerState(player);

    if (!event.initialSpawn) return;

    const hasChosen = player.getDynamicProperty('rom:has_chosen');
    const raceTag = player.getDynamicProperty('rom:race');

    if (!hasChosen && !raceTag) {
        system.runTimeout(() => {
            try {
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
            } catch (e) { /* player left during the delay */ }
        }, 40);
    }
});

// ── Player Leave cleanup ────────────────────────────────────────────
world.afterEvents.playerLeave.subscribe((event) => {
    // Cooldown + bloodlust cleanup happens in abilities.js — kept here as
    // an extension point in case future per-player state needs cleanup.
});

// ── Class Master set bonus: live re-evaluation ──────────────────────
// entityEquip is not part of @minecraft/server 2.4.0 (verified against the
// 2.4.0 API reference), so the old try/catch subscription silently never ran
// and the bonus only appeared after a respawn. A 5-second poll is cheap
// (one equippable lookup per player) and works on every API version.
system.runInterval(() => {
    for (const player of world.getPlayers()) {
        try { applyClassMasterBonuses(player); } catch (e) { /* transient */ }
    }
}, 100);

// ── Item Use: Class Token pre-selection ───────────────────────────────
// When a player right-clicks a class token, the class selection form opens
// with that class pre-selected. This is the primary way class tokens are
// "used" in-game.
const CLASS_TOKENS = new Set([
    'realms:class_token_mage', 'realms:class_token_ranger', 'realms:class_token_berserker',
    'realms:class_token_paladin', 'realms:class_token_druid',
]);

world.afterEvents.itemUse.subscribe((event) => {
    const player = event.source;
    const item = event.itemStack;

    // Dragon breath attack while mounted (any item right-click)
    try {
        if (tryBreathAttack(player)) return;
    } catch (e) { /* not mounted */ }

    if (!item || !CLASS_TOKENS.has(item.typeId)) return;

    // Extract classId from item id: 'realms:class_token_X' -> 'X'
    const classId = item.typeId.split('_').pop();

    // Allow the form to proceed even if the player has already chosen
    // (so they can re-pick a class by using a different token)
    if (!CLASSES[classId]) {
        player.sendMessage('§cUnknown class token.');
        return;
    }

    // If a race is already chosen, the form will skip to the confirm step.
    // Otherwise, the form will start at the race step and the player can
    // pick their race first.
    const hasChosen = player.getDynamicProperty('rom:has_chosen');
    const race = player.getDynamicProperty('rom:race');
    if (hasChosen && race) {
        player.sendMessage(`§7You are already a §e${race} ${CLASSES[player.getDynamicProperty('rom:class')].name}§7. Use §a!reset §7to re-pick.`);
        return;
    }

    event.cancel = true;
    player.sendMessage(`§6§lThe ${CLASSES[classId].name} Token resonates with your destiny...`);
    system.runTimeout(() => showClassSelectionForm(player, classId), 5);
});

// ── Entity Interact: Oracle opens class selection ───────────────────
world.afterEvents.playerInteractWithEntity.subscribe((event) => {
    const player = event.player;
    const target = event.target;
    if (!target) return;

    // Oracle / Elf Warrior: click to open class selection. Ritual elites use
    // the same entity type as the Oracle, so skip anything tagged rom:elite.
    if (target.typeId === 'realms:elf_warrior' && !target.hasTag('rom:elite')) {
        const raceTag = player.getDynamicProperty('rom:race');
        const hasChosen = player.getDynamicProperty('rom:has_chosen');
        if (raceTag && hasChosen) {
            // Chat commands are unavailable on current Bedrock; the Oracle is
            // the player-facing menu (class info, quest, reset, help).
            showCommandMenu(player);
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
        // Pending mythic reward from an interrupted ritual completion
        if (player.getDynamicProperty('rom:mythic_reward_pending')) {
            player.setDynamicProperty('rom:mythic_reward_pending', undefined);
            import('./altar.js').then(m => m.showMythicPicker(player));
            return;
        }
        if (!raceTag || !hasChosen) {
            player.sendMessage('§6§lThe Ancient Altar hums with ancient power...');
            system.runTimeout(() => showClassSelectionForm(player), 5);
        } else if (handleAltarRitual(player, block)) {
            // Ritual or prestige UI handled inside
        } else {
            const cls = player.getDynamicProperty('rom:class');
            const clsData = CLASSES[cls];
            player.sendMessage(`§7The Altar recognizes you: §e§l${raceTag} ${clsData ? clsData.name : cls}§r§7. Use §e!classinfo §7to review abilities.`);
        }
        return;
    }
});

// ── Chat Commands ──────────────────────────────────────────────────
// `chatSend` is a *before* event only on newer API versions; 2.4.0 exposes
// only world.afterEvents.chatSend. Support both (cancelling when possible),
// plus /scriptevent realms:cmd <command> which works on every version.
function handleChatCommand(player, rawMessage, cancellableEvent) {
    const msg = String(rawMessage || '').trim().toLowerCase();
    const consume = () => {
        if (cancellableEvent) cancellableEvent.cancel = true;
        return true;
    };

    if (msg === '!class' || msg === '!choose') {
        consume();
        const raceTag = player.getDynamicProperty('rom:race');
        if (raceTag && player.getDynamicProperty('rom:has_chosen')) {
            player.sendMessage('§cYou have already chosen a class! Use §e!reset §cto start over.');
        } else {
            showClassSelectionForm(player);
        }
    } else if (msg === '!reset') {
        consume();
        resetDestiny(player);
    } else if (msg === '!classinfo') {
        consume();
        sendClassInfo(player);
    } else if (msg === '!quest') {
        consume();
        questStatus(player);
    } else if (msg === '!help' || msg === '!commands') {
        consume();
        sendHelp(player);
    } else {
        return false;
    }
    return true;
}

const chatBefore = world.beforeEvents?.chatSend;
const chatAfter = world.afterEvents.chatSend;
if (chatBefore) {
    chatBefore.subscribe((event) => handleChatCommand(event.sender, event.message, event));
    console.log('[Realms of Myth] Chat commands: before-event (messages suppressed)');
} else if (chatAfter) {
    chatAfter.subscribe((event) => handleChatCommand(event.sender, event.message, null));
    console.log('[Realms of Myth] Chat commands: after-event fallback (message text remains visible)');
} else {
    console.warn('[Realms of Myth] No chat event available; use /scriptevent realms:cmd <command>');
}

// Version-independent command channel: /scriptevent realms:cmd !class
system.afterEvents.scriptEventReceive.subscribe((event) => {
    if (event.id !== 'realms:cmd') return;
    const player = event.sourceEntity;
    if (!player || player.typeId !== 'minecraft:player') return;
    handleChatCommand(player, event.message, null);
});

// ── Register ability system (event subscriptions + cooldowns) ──────
registerAbilities();

console.log('[Realms of Myth] Ready!');
