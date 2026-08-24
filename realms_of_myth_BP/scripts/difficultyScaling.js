/**
 * Realms of Myth - Difficulty Scaling
 * Mobs scale HP and damage by distance from world spawn:
 *   < 2,000 blocks  — ×1.00 (settled lands)
 *   2,000–8,000     — ×1.50 (wild frontier)
 *   > 8,000         — ×2.25 (the Deep Mythic)
 *
 * Applied on entitySpawn to realms:* hostile mobs via health component
 * attribute-style adjustment (setCurrentValue / heal) + a strength effect
 * proxy for the damage multiplier. Scaled mobs get a subtle name color so
 * players can read the danger tier.
 */

import { world, system } from '@minecraft/server';

const SCALABLE_TYPES = new Set([
    'realms:troll_brute',
    'realms:giant_colossus',
    'realms:elf_warrior',
    'realms:dragon_whelp'
]);
// Adult dragons are bosses — excluded by design.

const TIERS = [
    { maxDist: 2000, mult: 1.0,  label: '' },
    { maxDist: 8000, mult: 1.5,  label: '§e⚔' },
    { maxDist: Infinity, mult: 2.25, label: '§c☠' }
];

function tierFor(dist) {
    for (const t of TIERS) if (dist < t.maxDist || t.maxDist === Infinity && dist <= Infinity) {
        if (dist < t.maxDist) return t;
        if (t.maxDist === Infinity) return t;
    }
    return TIERS[0];
}

export function registerScaling() {
    world.afterEvents.entitySpawn.subscribe((event) => {
        const entity = event.entity;
        if (!entity || !entity.isValid?.()) return;
        if (!SCALABLE_TYPES.has(entity.typeId)) return;

        try {
            // Don't rescale pets or ritual elites
            if (entity.hasTag('rom:pet') || entity.hasTag('rom:elite')) return;

            let spawn = null;
            try { spawn = world.getDefaultSpawnLocation(); } catch (e) { /* */ }
            if (!spawn) return; // no default spawn set — skip

            const loc = entity.location;
            const dist = Math.hypot(loc.x - spawn.x, loc.z - spawn.z);
            const tier = tierFor(dist);
            if (tier.mult === 1.0) return;

            const hp = entity.getComponent('minecraft:health');
            if (hp) {
                const newMax = Math.round(hp.effectiveMax * tier.mult);
                hp.resetToMaxValue();
                // Boost current+max via health_boost effect proxy
                const boostLevel = Math.max(1, Math.round(newMax / 4));
                try { entity.runCommand(`effect @s health_boost 999999 ${Math.min(boostLevel - 1, 4)} true`); } catch (e) { /* */ }
                try { hp.setCurrentValue(Math.min(newMax, hp.effectiveMax)); } catch (e) { /* */ }
            }

            // Damage scaling proxy via strength effect
            const strLevel = tier.mult >= 2.25 ? 2 : 1;
            try { entity.runCommand(`effect @s strength 999999 ${strLevel} true`); } catch (e) { /* */ }
            try { entity.addTag(`rom:tier_${tier.maxDist === Infinity ? 'deep' : 'frontier'}`); } catch (e) { /* */ }

            // Subtle marker in nametag (only when it has one already)
            try {
                if (entity.nameTag) entity.nameTag = `${tier.label} ${entity.nameTag}`;
            } catch (e) { /* */ }
        } catch (e) { /* transient spawn-time errors */ }
    });
}
