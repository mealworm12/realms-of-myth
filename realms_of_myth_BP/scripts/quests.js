/**
 * Realms of Myth - Quest System
 * 8-quest progression chain per playthrough:
 *   1. Kill a Dragon Whelp          (kill)
 *   2. Collect 5 Mythril Ingots     (collect)
 *   3. Kill a Troll Brute           (kill)
 *   4. Craft any Tier-3 weapon      (craft milestone — detected by possession)
 *   5. Kill a Giant Colossus        (kill)
 *   6. Collect a Dragon Heart       (collect)
 *   7. Wear any full Master armor set (milestone)
 *   8. Slay a Fire OR Frost Dragon  (boss finale)
 *
 * Progress persists in the `rom:quest_stage` dynamic property (highest completed
 * quest index). Each completion grants loot + XP, shows a title, plays a sting.
 */

import { world, system } from '@minecraft/server';
import { loadPlayerData } from './playerData.js';

// ── Quest definitions ──────────────────────────────────────────────
export const QUESTS = [
    {
        id: 'whelp_bane', type: 'kill',
        targetTypes: ['realms:dragon_whelp'], count: 1,
        title: 'Whelp Bane', desc: 'Slay a Dragon Whelp',
        rewardItems: [{ id: 'realms:mythril_ingot', count: 2 }],
        rewardXpLevels: 2, sound: 'realms.ui.ability_ready'
    },
    {
        id: 'mythril_cache', type: 'collect',
        itemId: 'realms:mythril_ingot', count: 5,
        title: 'Mythril Cache', desc: 'Gather 5 Mythril Ingots',
        rewardItems: [{ id: 'realms:class_token_mage', count: 1 }],
        rewardXpLevels: 2, sound: 'realms.ui.ability_ready'
    },
    {
        id: 'troll_hunter', type: 'kill',
        targetTypes: ['realms:troll_brute'], count: 1,
        title: 'Troll Hunter', desc: 'Slay a Troll Brute',
        rewardItems: [{ id: 'realms:fire_essence', count: 2 }],
        rewardXpLevels: 3, sound: 'realms.ui.ability_ready'
    },
    {
        id: 'weaponsmith', type: 'possess',
        itemIds: ['realms:mythril_sword', 'realms:dragon_bone_greatsword', 'realms:dragonslayer_spear'],
        count: 1,
        title: 'Weaponsmith', desc: 'Forge a Tier-3 weapon (Mythril Sword, Dragon Bone Greatsword or Dragonslayer Spear)',
        rewardItems: [{ id: 'realms:frost_essence', count: 2 }],
        rewardXpLevels: 3, sound: 'realms.weapon.sword_swing'
    },
    {
        id: 'giant_feller', type: 'kill',
        targetTypes: ['realms:giant_colossus'], count: 1,
        title: 'Giant Feller', desc: 'Slay a Giant Colossus',
        rewardItems: [{ id: 'realms:dragon_scale', count: 4 }],
        rewardXpLevels: 4, sound: 'realms.ui.ability_ready'
    },
    {
        id: 'heart_seeker', type: 'collect',
        itemId: 'realms:dragon_heart', count: 1,
        title: 'Heart Seeker', desc: 'Claim a Dragon Heart',
        rewardItems: [{ id: 'realms:enchanted_bow', count: 1 }],
        rewardXpLevels: 5, sound: 'realms.ui.class_select_open'
    },
    {
        id: 'master_armorer', type: 'armorset',
        setTitle: true, // any full class master set (checked via rom:class_master_bonus)
        title: 'Master Armorer', desc: 'Wear a complete Class Master armor set',
        rewardItems: [{ id: 'realms:magic_staff', count: 1 }],
        rewardXpLevels: 5, sound: 'realms.ui.class_select_open'
    },
    {
        id: 'dragonslayers', type: 'kill',
        targetTypes: ['realms:dragon_fire', 'realms:dragon_frost'], count: 1,
        title: 'Dragonslayer', desc: 'Slay a Fire or Frost Dragon',
        rewardItems: [
            { id: 'realms:dragon_heart', count: 1 },
            { id: 'realms:mythril_ingot', count: 8 }
        ],
        rewardXpLevels: 10, sound: 'realms.music.battle_start'
    }
];

const STAGE_PROP = 'rom:quest_stage';
const PROGRESS_PROP = 'rom:quest_progress';

// ── Helpers ────────────────────────────────────────────────────────

function getStage(player) {
    return player.getDynamicProperty(STAGE_PROP) || 0;
}

function announceQuest(player, quest, done) {
    const display = player.getComponent('minecraft:onScreenDisplay') ||
                    player.getComponent('on_screen_display');
    try {
        if (display && display.setTitle) {
            display.setTitle(`§6§l${done ? 'Quest Complete!' : 'New Quest'}§r\n§e${quest.title}`);
        }
    } catch (e) { /* title API may vary */ }
    if (done) {
        player.sendMessage({ rawtext: [{ text: `§6✔ §e§l${quest.title}§r §7— complete!` }] });
        try { player.playSound(quest.sound); } catch (e) { /* sound optional */ }
        // Loot + XP rewards
        for (const r of quest.rewardItems) {
            try { player.runCommand(`give @s ${r.id} ${r.count}`); }
            catch (e2) { /* commands disabled */ }
        }
        if (quest.rewardXpLevels > 0) {
            try { player.runCommand(`xp ${quest.rewardXpLevels}L @s`); } catch (e) { /* */ }
            bumpScriptedLevel(player, quest.rewardXpLevels);
        }
    } else {
        player.sendMessage({ rawtext: [{ text: `§6◆ New Quest: §e${quest.title} §8- §7${quest.desc}` }] });
    }
}

/** Mirror vanilla XP into our scripted level counter (used by class prestige). */
function bumpScriptedLevel(player, amount) {
    const cur = player.getDynamicProperty('rom:xp_level') || 0;
    player.setDynamicProperty('rom:xp_level', cur + amount);
}

// ── Progress evaluation ────────────────────────────────────────────

function countItem(player, typeId) {
    let total = 0;
    const inv = player.getComponent('minecraft:inventory');
    if (!inv || !inv.container) return 0;
    for (let i = 0; i < inv.container.size; i++) {
        const it = inv.container.getItem(i);
        if (it && it.typeId === typeId) total += it.amount;
    }
    return total;
}

function evaluateActiveQuest(player) {
    const stage = getStage(player);
    if (stage >= QUESTS.length) return;
    const quest = QUESTS[stage];
    let met = false;

    switch (quest.type) {
        case 'collect':
        case 'possess':
            {
                const ids = quest.type === 'collect' ? [quest.itemId] : quest.itemIds;
                met = ids.some(id => countItem(player, id) >= quest.count);
            }
            break;
        case 'armorset':
            met = !!player.getDynamicProperty('rom:class_master_bonus');
            break;
        // 'kill' quests advance through the entityDie hook, not here.
    }

    if (met) completeQuest(player);
}

function completeQuest(player) {
    const stage = getStage(player);
    if (stage >= QUESTS.length) return;
    const quest = QUESTS[stage];
    player.setDynamicProperty(STAGE_PROP, stage + 1);
    player.setDynamicProperty(PROGRESS_PROP, undefined);
    announceQuest(player, quest, true);

    // Offer the next quest shortly after
    if (stage + 1 < QUESTS.length) {
        system.runTimeout(() => {
            try {
                if (player.isValid()) announceQuest(player, QUESTS[stage + 1], false);
            } catch (e) { /* player left */ }
        }, 60);
    } else {
        player.sendMessage('§d★ You have completed the Chronicles of the Realm!');
        try { player.playSound('realms.music.battle_start'); } catch (e) { /* */ }
    }
}

// ── Registration ───────────────────────────────────────────────────

let registered = false;

export function registerQuests() {
    if (registered) return;
    registered = true;

    // Kill tracking
    world.afterEvents.entityDie.subscribe((event) => {
        const killer = event.damageSource?.damagingEntity;
        if (!killer || !killer.typeId || killer.typeId !== 'minecraft:player') return;
        const stage = getStage(killer);
        if (stage >= QUESTS.length) return;
        const quest = QUESTS[stage];
        if (quest.type !== 'kill') return;
        if (quest.targetTypes.includes(event.deadEntity?.typeId)) {
            completeQuest(killer);
        }
    });

    // Poll collect / possess / armor-set quests every 2 seconds
    system.runInterval(() => {
        for (const player of world.getPlayers()) {
            try {
                const data = loadPlayerData(player);
                if (!data) continue; // class chosen gates quest chain
                evaluateActiveQuest(player);
            } catch (e) { /* transient */ }
        }
    }, 40);
}

/** Called on first class choice (from main.js) to kick off the chain. */
export function startQuestChain(player) {
    if ((player.getDynamicProperty(STAGE_PROP) || 0) === 0 &&
        !player.getDynamicProperty('rom:quest_started')) {
        player.setDynamicProperty('rom:quest_started', true);
        announceQuest(player, QUESTS[0], false);
    }
}

/** Chat helper: !quest status */
export function questStatus(player) {
    const stage = getStage(player);
    if (stage >= QUESTS.length) {
        player.sendMessage('§6All 8 Chronicle quests are complete! ★');
        return;
    }
    const q = QUESTS[stage];
    player.sendMessage({
        rawtext: [{
            text: `§6═══ Chronicles of the Realm (${stage}/8 done) ═══\n` +
                  `§eCurrent: §l${q.title}§r §8- §7${q.desc}`
        }]
    });
}
