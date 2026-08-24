/**
 * Realms of Myth - Ancient Altar Rituals
 * Two rituals, both triggered from the altar interact hook in main.js:
 *
 * 1. SUMMONING RITUAL — right-click altar with 1x dragon_heart + 4x mythril
 *    ingot in inventory → consumes them → spawns a wave of 3 elite mobs
 *    (buffed HP via effects, custom names, glowing) around the altar.
 *    Defeat all three → Mythic weapon picker UI (server-ui ActionFormData).
 *
 * 2. CLASS PRESTIGE — at class level 30+ (rom:xp_level), the altar offers to
 *    prestige: resets XP level to 1, grants permanent +2 max HP and a class-
 *    colored particle aura (divine_shield_aura variant per class).
 */

import { world, system } from '@minecraft/server';
import { ActionFormData } from '@minecraft/server-ui';

const MYTHIC_WEAPONS = [
    { id: 'realms:dawnbreaker', name: 'Dawnbreaker', desc: 'Holy greatsword — radiant smite vs undead & dragons' },
    { id: 'realms:void_reaver', name: 'Void Reaver', desc: 'Shadow dagger — slip behind your prey' },
    { id: 'realms:stormcaller_hammer', name: 'Stormcaller Hammer', desc: 'Calls lightning upon every strike' }
];

const ELITE_WAVE = [
    { type: 'realms:troll_brute', name: '§5Elite Bloodtroll' },
    { type: 'realms:giant_colossus', name: '§5Elite Colossus' },
    { type: 'realms:elf_warrior', name: '§5Darkblade Champion' }
];

/** altarKey ("x,y,z,dim") -> ritual state */
const activeRituals = new Map();

// ── Helpers ────────────────────────────────────────────────────────

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

function consumeItem(player, typeId, amount) {
    const inv = player.getComponent('minecraft:inventory');
    if (!inv || !inv.container) return false;
    let remaining = amount;
    const c = inv.container;
    for (let i = 0; i < c.size && remaining > 0; i++) {
        const it = c.getItem(i);
        if (it && it.typeId === typeId) {
            const take = Math.min(it.amount, remaining);
            if (it.amount - take > 0) { it.amount -= take; c.setItem(i, it); }
            else c.setItem(i, undefined);
            remaining -= take;
        }
    }
    return remaining === 0;
}

function keyOf(block) {
    const l = block.location;
    return `${l.x},${l.y},${l.z},${block.dimension.id}`;
}

// ── Ritual entry point (called from main.js on altar right-click) ──

export function handleAltarRitual(player, block) {
    // Prestige first if eligible
    const xpLevel = player.getDynamicProperty('rom:xp_level') || 0;
    const prestiged = player.getDynamicProperty('rom:prestige_count') || 0;

    if ((xpLevel >= 30 || player.getDynamicProperty('rom:xp_level') >= 30)) {
        showPrestigeForm(player);
        return true;
    }

    const k = keyOf(block);
    if (activeRituals.has(k)) {
        player.sendMessage('§7A ritual is already underway at this altar...');
        return true;
    }

    if (countItem(player, 'realms:dragon_heart') >= 1 && countItem(player, 'realms:mythril_ingot') >= 4) {
        startSummoningRitual(player, block, k);
        return true;
    }

    // Nothing eligible — informational message
    player.sendMessage({
        rawtext: [{
            text: '§6═══ The Ancient Altar ═══\n' +
                  '§7• Summoning Ritual: §e1 Dragon Heart + 4 Mythril Ingots\n' +
                  '§7• Class Prestige: reach §elevel 30§7, then touch the altar\n' +
                  `§8Your level: ${xpLevel}${prestiged ? ` • Prestiges: ${prestiged}` : ''}`
        }]
    });
    return false;
}

// ── Summoning ritual ───────────────────────────────────────────────

function startSummoningRitual(player, block, k) {
    consumeItem(player, 'realms:dragon_heart', 1);
    consumeItem(player, 'realms:mythril_ingot', 4);

    const dim = block.dimension;
    const loc = block.location;

    player.playSound('realms.music.battle_start');
    for (const p of world.getPlayers()) {
        p.sendMessage('§4⚠ The altar blazes! Guardians of the old blood rise!');
    }
    try { dim.spawnParticle('realms:phase_enrage', { x: loc.x + 0.5, y: loc.y + 1, z: loc.z + 0.5 }); } catch (e) { /* */ }

    const spawned = [];
    ELITE_WAVE.forEach((spec, i) => {
        const angle = (i / ELITE_WAVE.length) * Math.PI * 2;
        const spawnLoc = {
            x: loc.x + Math.cos(angle) * 4,
            y: loc.y + 1,
            z: loc.z + Math.sin(angle) * 4
        };
        system.runTimeout(() => {
            try {
                const mob = dim.spawnEntity(spec.type, spawnLoc);
                // Elite buffs: extra HP via absorption + glowing outline + custom name
                try { mob.nameTag = spec.name; } catch (e) { /* */ }
                try { mob.runCommand('effect @s health_boost 999999 3 true'); } catch (e) { /* */ }
                try { mob.runCommand('effect @s resistance 999999 1 true'); } catch (e) { /* */ }
                try { mob.runCommand('effect @s strength 999999 1 true'); } catch (e) { /* */ }
                try { mob.addTag('rom:elite'); } catch (e) { /* */ }
                spawned.push(mob.id);
            } catch (e) { /* spawn failure */ }
        }, 20 + i * 15);
    });

    activeRituals.set(k, { playerIds: [player.id], spawned, startedTick: system.currentTick });

    // Watch for completion
    system.runTimeout(() => checkRitualCompletion(block, k), 60); // poll every 3s
}

function checkRitualCompletion(block, k) {
    const ritual = activeRituals.get(k);
    if (!ritual) return;
    const dim = block.dimension;
    let alive = 0;
    for (const id of ritual.spawned) {
        try {
            const m = dim.getEntity(id);
            if (m && m.isValid() &&
                (m.getComponent('minecraft:health')?.currentValue || 0) > 0) alive++;
        } catch (e) { /* unloaded counts as alive */ alive++; }
    }
    if (alive > 0) {
        if (system.currentTick - ritual.startedTick < 20 * 600) { // 10 min timeout
            system.runTimeout(() => checkRitualCompletion(block, k), 60);
        } else {
            activeRituals.delete(k);
            for (const p of world.getPlayers()) p.sendMessage('§7The ritual\'s power fades... the guardians remain unslain.');
        }
        return;
    }

    // All elites dead → reward
    activeRituals.delete(k);
    for (const pid of ritual.playerIds) {
        for (const p of world.getPlayers()) {
            if (p.id !== pid) continue;
            p.sendMessage('§6★ The guardians fall! The altar offers its treasure...');
            p.playSound('realms.ui.class_select_open');
            system.runTimeout(() => showMythicPicker(p), 20);
        }
    }
}

// ── Mythic weapon picker ───────────────────────────────────────────

export function showMythicPicker(player) {
    const form = new ActionFormData()
        .title('Claim Your Mythic Weapon')
        .body('Choose one weapon of myth. This boon comes but once per ritual.');
    MYTHIC_WEAPONS.forEach(w => form.button(`§l${w.name}§r\n${w.desc}`));

    form.show(player).then((response) => {
        if (response.canceled || response.selection === undefined) {
            player.sendMessage('§7The vision waits... touch the altar again to choose.');
            // Re-offer next time they use the altar: set a pending flag
            player.setDynamicProperty('rom:mythic_reward_pending', true);
            return;
        }
        const w = MYTHIC_WEAPONS[response.selection];
        try { player.runCommand(`give @s ${w.id} 1`); }
        catch (e) { /* commands disabled */ }
        player.setDynamicProperty('rom:mythic_reward_pending', undefined);
        player.playSound('realms.weapon.sword_swing');
        player.dimension.spawnParticle('realms:class_select_burst', player.location);
        player.sendMessage(`§d★ You receive: §l${w.name}§r§d!`);
    }).catch(() => { /* UI closed */ });
}

// ── Class prestige ─────────────────────────────────────────────────

const CLASS_AURA_COLORS = {
    mage:      'realms:divine_shield_aura', // arcane violet base aura
    ranger:    'realms:nature_blessing_leaves',
    berserker: 'realms:rage_blood_motes',
    paladin:   'realms:holy_light_beam',
    druid:     'realms:nature_blessing_leaves'
};

function showPrestigeForm(player) {
    const xpLevel = player.getDynamicProperty('rom:xp_level') || 0;
    const cls = player.getDynamicProperty('rom:class') || 'paladin';
    const prestigeCount = player.getDynamicProperty('rom:prestige_count') || 0;

    const form = new ActionFormData()
        .title('Ancient Altar: Class Prestige')
        .body(`You stand at level §e${xpLevel}§r as a §l${cls}§r.\n` +
              'Prestige resets your level to 1 but grants:\n' +
              '§a+2 permanent maximum health\n' +
              '§aAn eternal class-colored aura\n' +
              `§8Current prestiges: ${prestigeCount}`)
        .button('§d§lASCEND')
        .button('§7Not yet');

    form.show(player).then((response) => {
        if (response.canceled || response.selection !== 0) return;
        doPrestige(player, cls);
    }).catch(() => { /* */ });
}

export function doPrestige(player, cls) {
    const xpLevel = player.getDynamicProperty('rom:xp_level') || 0;
    if (xpLevel < 30) {
        player.sendMessage('§cThe altar demands mastery: reach level 30 first.');
        return;
    }
    player.setDynamicProperty('rom:xp_level', 1);
    const prev = player.getDynamicProperty('rom:prestige_count') || 0;
    player.setDynamicProperty('rom:prestige_count', prev + 1);

    // Permanent +2 HP (stacking across prestiges)
    const hpBonus = 2 * (prev + 1);
    const boostLevel = Math.max(1, Math.floor(hpBonus / 2));
    player.runCommand(`effect @s health_boost 999999 ${boostLevel} true`);

    // Aura marker — main.js prestige loop renders particles periodically
    player.setDynamicProperty('rom:prestige_aura', cls);

    player.dimension.spawnParticle('realms:class_select_burst', player.location);
    player.dimension.spawnParticle('realms:holy_light_beam', player.location);
    player.playSound('realms.ui.class_select_open');
    player.sendMessage({ rawtext: [{ text: `§d✦ You have ASCENDED! Level reset to 1, +${hpBonus} permanent max HP, and an eternal ${cls} aura.` }] });
}

/** Called from main.js interval: render prestige auras. */
export function tickPrestigeAuras() {
    for (const player of world.getPlayers()) {
        const auraClass = player.getDynamicProperty('rom:prestige_aura');
        if (!auraClass) continue;
        try {
            player.dimension.spawnParticle(
                CLASS_AURA_COLORS[auraClass] || 'realms:divine_shield_aura',
                { x: player.location.x, y: player.location.y + 1.2, z: player.location.z }
            );
        } catch (e) { /* */ }
    }
}
