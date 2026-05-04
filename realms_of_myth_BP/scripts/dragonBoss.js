/**
 * Realms of Myth - Dragon Boss AI
 * Multi-phase dragon behavior: ground, aerial, enraged
 * Uses system.currentTick for reliable timing
 */

import { world, system, Entity, Player } from '@minecraft/server';

const DRAGON_TYPES = ['realms:dragon_fire', 'realms:dragon_frost'];

// Phase thresholds (percent of max HP)
const PHASE_GROUND = 0.60;
const PHASE_AERIAL = 0.30;

const managedDragons = new Map();
const dragonWhelps = new Map();

/**
 * Register dragon boss AI. Call once during mod init.
 */
export function registerDragonAI() {
    // Process dragons every 40 ticks (2 seconds)
    system.runInterval(() => {
        checkAllDragons();
    }, 40);

    // ── Clean up maps when a dragon dies ──────────────────
    world.afterEvents.entityDie.subscribe((event) => {
        const entity = event.deadEntity;
        if (!entity) return;
        const type = entity.typeId;
        if (type !== 'realms:dragon_fire' && type !== 'realms:dragon_frost') return;

        const did = entity.id;
        // Remove from managedDragons
        managedDragons.delete(did);
        // Kill all whelps associated with this dragon
        if (dragonWhelps.has(did)) {
            const wids = dragonWhelps.get(did);
            const dim = entity.dimension;
            for (const wid of wids) {
                try {
                    const w = dim.getEntity(wid);
                    if (w && w.isValid()) w.remove();
                } catch (e) {}
            }
            dragonWhelps.delete(did);
        }
    });
}

/**
 * Scan all loaded dimensions for dragon entities
 */
function checkAllDragons() {
    try {
        for (const dimName of ['overworld', 'nether']) {
            const dim = world.getDimension(dimName);
            for (const type of DRAGON_TYPES) {
                try {
                    const dragons = dim.getEntities({ type: type });
                    for (const dragon of dragons) {
                        if (dragon.isValid()) {
                            processDragon(dragon, dim);
                        }
                    }
                } catch (e) {
                    // Entity iteration can fail in unloaded chunks
                }
            }
        }
    } catch (e) {
        // Dimension may not be loaded
    }

    // Prune dead entries from managedDragons
    for (const [did, data] of managedDragons) {
        let alive = false;
        for (const dimName of ['overworld', 'nether']) {
            try {
                const dim = world.getDimension(dimName);
                const e = dim.getEntity(did);
                if (e && e.isValid() && (e.typeId === 'realms:dragon_fire' || e.typeId === 'realms:dragon_frost')) {
                    alive = true;
                    break;
                }
            } catch (e) {}
        }
        if (!alive) {
            // Dragon is dead/despawned — clean up whelps and managed entry
            if (dragonWhelps.has(did)) {
                dragonWhelps.delete(did);
            }
            managedDragons.delete(did);
        }
    }
}

/**
 * Process a single dragon: determine phase, execute behavior
 */
function processDragon(dragon, dim) {
    const health = dragon.getComponent('minecraft:health');
    if (!health || health.currentValue <= 0) return;

    const hpPercent = health.currentValue / health.effectiveMax;
    const dragonId = dragon.id;

    // Determine current phase
    let phase;
    if (hpPercent > PHASE_GROUND) {
        phase = 'ground';
    } else if (hpPercent > PHASE_AERIAL) {
        phase = 'aerial';
    } else {
        phase = 'enraged';
    }

    // Detect phase transition
    const lastPhase = managedDragons.get(dragonId)?.phase;
    if (phase !== lastPhase) {
        announcePhase(dragon, phase, dim);
    }

    // Execute phase behavior
    switch (phase) {
        case 'ground':  executeGroundPhase(dragon, dim); break;
        case 'aerial':  executeAerialPhase(dragon, dim); break;
        case 'enraged': executeEnragedPhase(dragon, dim, dragonId); break;
    }

    managedDragons.set(dragonId, { phase, hp: hpPercent });
}

// ═══════════════════════════════════════════════════════════
// PHASE TRANSITION
// ═══════════════════════════════════════════════════════════

function announcePhase(dragon, phase, dim) {
    const isFire = dragon.typeId === 'realms:dragon_fire';
    const name = isFire ? '§cFire Dragon' : '§bFrost Dragon';

    let msg;
    switch (phase) {
        case 'ground':
            msg = `${name} §7descends to the ground!`;
            dim.runCommand(`execute at @e[type=${dragon.typeId},c=1] run particle minecraft:large_explosion ~~~`);
            break;
        case 'aerial':
            msg = `${name} §7takes flight!`;
            try { dragon.runCommand('effect @s levitation 999999 5 true'); } catch (e) {}
            break;
        case 'enraged':
            msg = `${name} §4§lIS ENRAGED!`;
            dim.runCommand(`execute at @e[type=${dragon.typeId},c=1] run particle minecraft:angry_villager ~ ~ ~`);
            spawnWhelps(dragon, dim);
            break;
    }

    for (const player of world.getPlayers()) {
        player.sendMessage(msg);
    }
    dim.runCommand(`playsound mob.enderdragon.growl @a ~~~ 1 0.5`);
}

// ═══════════════════════════════════════════════════════════
// PHASE 1: GROUND (>60% HP)
// ═══════════════════════════════════════════════════════════

function executeGroundPhase(dragon, dim) {
    try { dragon.runCommand('effect @s levitation 0 0'); } catch (e) {}

    const roll = Math.random();
    if (roll < 0.04) {
        const dmg = dragon.typeId === 'realms:dragon_fire' ? 8 : 6;
        dim.runCommand(`effect @p[r=8] instant_damage 1 ${Math.round(dmg / 3)} true`);
        dim.runCommand(`execute at @e[type=${dragon.typeId},c=1] run particle minecraft:dragon_destroy_block ~ ~2 ~`);
    }
}

// ═══════════════════════════════════════════════════════════
// PHASE 2: AERIAL (30-60% HP)
// ═══════════════════════════════════════════════════════════

function executeAerialPhase(dragon, dim) {
    try { dragon.runCommand('effect @s levitation 40 8 true'); } catch (e) {}

    const roll = Math.random();
    if (roll < 0.03) {
        dim.runCommand(`effect @p[r=12] instant_damage 1 2 true`);
        dim.runCommand(`execute at @e[type=${dragon.typeId},c=1] run particle minecraft:dragon_destroy_block ~ ~1 ~`);
    } else if (roll < 0.06) {
        const players = world.getPlayers();
        if (players.length > 0) {
            const nearest = players.reduce((best, p) => {
                const d = Math.hypot(p.location.x - dragon.location.x, p.location.z - dragon.location.z);
                return d < best.dist ? { player: p, dist: d } : best;
            }, { player: players[0], dist: Infinity }).player;

            const tLoc = nearest.location;
            dragon.teleport({ x: tLoc.x, y: tLoc.y + 15, z: tLoc.z });
            dim.runCommand(`effect @p[r=6] instant_damage 1 4 true`);
            dim.runCommand(`execute at @e[type=${dragon.typeId},c=1] run particle minecraft:huge_explosion_emitter ~~~`);
            dim.runCommand(`playsound mob.enderdragon.hit @a ~~~ 1 0`);
        }
    }
}

// ═══════════════════════════════════════════════════════════
// PHASE 3: ENRAGED (<30% HP)
// ═══════════════════════════════════════════════════════════

function executeEnragedPhase(dragon, dim, dragonId) {
    const roll = Math.random();

    if (roll < 0.05) {
        dim.runCommand(`effect @p[r=20] instant_damage 1 3 true`);
        dim.runCommand(`execute at @e[type=${dragon.typeId},c=1] run particle minecraft:huge_explosion_emitter ~~~`);
        dim.runCommand(`playsound ambient.weather.thunder @a ~~~ 1 0`);
    }

    maintainWhelps(dragon, dim, dragonId);
}

// ═══════════════════════════════════════════════════════════
// WHELP SYSTEM
// ═══════════════════════════════════════════════════════════

function spawnWhelps(dragon, dim) {
    const loc = dragon.location;
    const dragonId = dragon.id;

    // Clear existing whelps
    if (dragonWhelps.has(dragonId)) {
        for (const wid of dragonWhelps.get(dragonId)) {
            try {
                const w = dim.getEntity(wid);
                if (w && w.isValid()) w.remove();
            } catch (e) {}
        }
    }
    dragonWhelps.set(dragonId, []);

    for (let i = 0; i < 3; i++) {
        const angle = (i / 3) * Math.PI * 2;
        const whelp = dim.spawnEntity('realms:dragon_whelp', {
            x: loc.x + Math.cos(angle) * 5,
            y: loc.y,
            z: loc.z + Math.sin(angle) * 5
        });
        dragonWhelps.get(dragonId).push(whelp.id);
    }
    dim.runCommand('playsound mob.enderdragon.growl @a ~~~ 1 0.8');
}

function maintainWhelps(dragon, dim, dragonId) {
    const whelps = dragonWhelps.get(dragonId) || [];
    const alive = [];

    for (const wid of whelps) {
        try {
            const w = dim.getEntity(wid);
            if (w && w.isValid() && w.getComponent('minecraft:health')?.currentValue > 0) {
                alive.push(wid);
            }
        } catch (e) {}
    }

    const missing = 3 - alive.length;
    if (missing > 0 && dragon && dragon.isValid()) {
        const loc = dragon.location;
        for (let i = 0; i < missing; i++) {
            const whelp = dim.spawnEntity('realms:dragon_whelp', {
                x: loc.x + (Math.random() - 0.5) * 8,
                y: loc.y + 2,
                z: loc.z + (Math.random() - 0.5) * 8
            });
            alive.push(whelp.id);
        }
    }
    dragonWhelps.set(dragonId, alive);
}

/**
 * Programmatically spawn a dragon
 */
export function spawnDragon(location, type = 'fire') {
    const dim = world.getDimension('overworld');
    const entityType = type === 'fire' ? 'realms:dragon_fire' : 'realms:dragon_frost';
    return dim.spawnEntity(entityType, location);
}
