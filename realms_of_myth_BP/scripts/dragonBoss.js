/**
 * Realms of Myth - Dragon Boss AI
 * Multi-phase dragon behavior: ground, aerial, enraged.
 * Uses system.runInterval(40) for 2-second poll cadence (cheap, no tick math).
 */

import { world, system } from '@minecraft/server';
import { makeWhelpPet } from './dragonRiding.js';

const DRAGON_TYPES = ['realms:dragon_fire', 'realms:dragon_frost'];

// Phase thresholds (percent of max HP)
const PHASE_GROUND = 0.60;
const PHASE_AERIAL = 0.30;

const managedDragons = new Map();
const dragonWhelps = new Map();
/** playerId -> { fogId: 'realms:*', expireTick } — auto-clearing fog tracking */
const activePlayerFogs = new Map();

/** Apply a client fog to a player with automatic timed clear. */
function applyTimedFog(player, fogId, tagId, durationTicks) {
    const now = system.currentTick;
    try {
        player.runCommand(`fog @s push ${fogId} ${tagId}`);
        activePlayerFogs.set(player.id + ':' + tagId, {
            player, expireTick: now + durationTicks
        });
    } catch (e) { /* fog command unavailable */ }
}

/** Clear expired fogs every tick. */
export function registerFogMaintenance() {
    system.runInterval(() => {
        const now = system.currentTick;
        for (const [key, entry] of activePlayerFogs) {
            if (now >= entry.expireTick) {
                try {
                    const [pid, tag] = key.split(':');
                    entry.player.runCommand(`fog @s remove ${tag}`);
                } catch (e) { /* player gone */ }
                activePlayerFogs.delete(key);
            }
        }
    }, 20);
}

/**
 * Register dragon boss AI. Call once during mod init.
 */
export function registerDragonAI() {
    // Process dragons every 40 ticks (2 seconds)
    system.runInterval(() => {
        checkAllDragons();
    }, 40);

    // Clean up maps when a dragon dies — kill whelps, free the entry,
    // stop battle music + play victory sting for nearby players.
    world.afterEvents.entityDie.subscribe((event) => {
        const entity = event.deadEntity;
        if (!entity) return;
        const type = entity.typeId;
        if (type !== 'realms:dragon_fire' && type !== 'realms:dragon_frost') return;

        const did = entity.id;
        managedDragons.delete(did);
        if (dragonWhelps.has(did)) {
            const wids = dragonWhelps.get(did);
            const dim = entity.dimension;
            for (const wid of wids) {
                try {
                    const w = dim.getEntity(wid);
                    if (w && w.isValid()) w.remove();
                } catch (e) { /* chunk unload */ }
            }
            dragonWhelps.delete(did);
        }

        // Boss defeated — victory sting, stop battle music, clear domain fog
        try {
            const loc = entity.location;
            for (const player of world.getPlayers()) {
                const d = Math.hypot(player.location.x - loc.x, player.location.z - loc.z);
                if (d < 64) {
                    player.playSound('realms.music.battle_stop');
                    try { player.stopMusic(); } catch (e) { /* API variant */ }
                    player.sendMessage('§6§lThe dragon has fallen! The realm breathes easier...');
                    try { player.runCommand('fog @s remove rom_dragon_domain'); } catch (e) { /* */ }
                    activePlayerFogs.delete(player.id + ':rom_dragon_domain');
                }
            }
        } catch (e) { /* */ }
    });
}

/**
 * Scan all loaded dimensions for dragon entities.
 * Limited to overworld + nether per the README spawn rules (volcano, ice spikes).
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

    // Prune dead entries from managedDragons (dragon may have died between polls)
    for (const [did] of managedDragons) {
        let alive = false;
        for (const dimName of ['overworld', 'nether']) {
            try {
                const dim = world.getDimension(dimName);
                const e = dim.getEntity(did);
                if (e && e.isValid() && (e.typeId === 'realms:dragon_fire' || e.typeId === 'realms:dragon_frost')) {
                    alive = true;
                    break;
                }
            } catch (e) { /* chunk unload */ }
        }
        if (!alive) {
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

    // Boss fight start: first time a player is within aggro range, kick off
    // the battle sting + looped battle music.
    const meta = managedDragons.get(dragonId) || {};
    if (!meta.musicStarted) {
        let engaged = false;
        for (const p of world.getPlayers()) {
            const d = Math.hypot(p.location.x - dragon.location.x,
                                 Math.abs(p.location.y - dragon.location.y),
                                 p.location.z - dragon.location.z);
            if (d < 24) {
                engaged = true;
                try {
                    p.playSound('realms.music.battle_start');
                    p.playMusic('music.realms_battle', { loop: true });
                } catch (e) { /* */ }
            }
        }
        if (engaged) meta.musicStarted = true;
    }

    // Execute phase behavior
    switch (phase) {
        case 'ground':  executeGroundPhase(dragon, dim); break;
        case 'aerial':  executeAerialPhase(dragon, dim); break;
        case 'enraged': executeEnragedPhase(dragon, dim, dragonId); break;
    }

    managedDragons.set(dragonId, { phase, hp: hpPercent });
}

// ═══════════════════════════════════════════════════════════════════
// PHASE TRANSITION
// ═══════════════════════════════════════════════════════════════════

function announcePhase(dragon, phase, dim) {
    const isFire = dragon.typeId === 'realms:dragon_fire';
    const name = isFire ? '§cFire Dragon' : '§bFrost Dragon';

    // Custom roar per dragon type (custom mob voice events)
    const roarEvent = isFire ? 'entity.dragon_fire.roar' : 'entity.dragon_frost.roar';

    let msg;
    let soundEvent = roarEvent;
    switch (phase) {
        case 'ground':
            msg = `${name} §7descends to the ground!`;
            try {
                dim.spawnParticle('realms:ground_slam_dust', {
                    x: dragon.location.x, y: dragon.location.y + 1, z: dragon.location.z
                });
            } catch (e) { /* */ }
            soundEvent = roarEvent;
            break;
        case 'aerial':
            msg = `${name} §7takes flight!`;
            try { dragon.runCommand('effect @s levitation 999999 5 true'); } catch (e) { /* skip */ }
            soundEvent = isFire ? 'entity.dragon_fire.flap' : 'entity.dragon_frost.flap';
            break;
        case 'enraged':
            msg = `${name} §4§lIS ENRAGED!`;
            // Phase enrage shockwave (custom VFX) at the dragon
            try {
                dim.spawnParticle('realms:phase_enrage', {
                    x: dragon.location.x, y: dragon.location.y + 2, z: dragon.location.z
                });
            } catch (e) { /* */ }
            spawnWhelps(dragon, dim);
            soundEvent = 'realms.music.battle_start';
            break;
    }

    for (const player of world.getPlayers()) {
        const d = Math.hypot(player.location.x - dragon.location.x,
                             player.location.z - dragon.location.z);
        if (d > 64) continue;
        player.sendMessage(msg);
        player.playSound(soundEvent);
        try { player.dimension.playSound(roarEvent, dragon.location); } catch (e) { /* */ }
        // Enraged phase: keep battle music running with tension sting
        if (phase === 'enraged') {
            try { player.playMusic('music.realms_battle', { loop: true }); } catch (e) { /* */ }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// PHASE 1: GROUND (>60% HP)
// ═══════════════════════════════════════════════════════════════════

function executeGroundPhase(dragon, dim) {
    // Cancel any leftover levitation from a previous aerial phase
    try { dragon.runCommand('effect @s levitation 0 0'); } catch (e) { /* skip */ }

    const roll = Math.random();
    if (roll < 0.04) {
        const isFire = dragon.typeId === 'realms:dragon_fire';
        const dmg = isFire ? 8 : 6;
        const breathId = isFire ? 'realms:dragon_breath_fire' : 'realms:dragon_breath_frost';
        const fogId = isFire ? 'realms:dragon_lair_fog' : 'realms:frost_domain_fog';

        // Breath attack: spawn breath particles along the path toward the nearest player
        try {
            const players = world.getPlayers();
            let target = null;
            for (const p of players) {
                const d = Math.hypot(p.location.x - dragon.location.x,
                                     Math.abs(p.location.y - dragon.location.y),
                                     p.location.z - dragon.location.z);
                if (d < 12) { target = p; break; }
            }
            const dest = target ? target.location : dragon.location;
            const steps = 8;
            for (let i = 1; i <= steps; i++) {
                const t = i / steps;
                dim.spawnParticle(breathId, {
                    x: dragon.location.x + (dest.x - dragon.location.x) * t,
                    y: dragon.location.y + 2 + (dest.y - dragon.location.y - 2) * t,
                    z: dragon.location.z + (dest.z - dragon.location.z) * t
                });
            }
        } catch (e) { /* particle may not resolve */ }

        // Domain fog on nearby players (auto-clears after ~10s)
        for (const p of world.getPlayers()) {
            const d = Math.hypot(p.location.x - dragon.location.x,
                                 Math.abs(p.location.y - dragon.location.y),
                                 p.location.z - dragon.location.z);
            if (d < 12) applyTimedFog(p, fogId, 'rom_dragon_domain', 200);
        }

        dim.runCommand(`effect @p[r=8] instant_damage 1 ${Math.round(dmg / 3)} true`);
    }
}

// ═══════════════════════════════════════════════════════════════════
// PHASE 2: AERIAL (30-60% HP)
// ═══════════════════════════════════════════════════════════════════

function executeAerialPhase(dragon, dim) {
    // Re-apply levitation each poll in case it expired
    try { dragon.runCommand('effect @s levitation 40 8 true'); } catch (e) { /* skip */ }

    const roll = Math.random();
    if (roll < 0.03) {
        // Strafe breath — frost dragons apply their domain fog briefly
        const isFire = dragon.typeId === 'realms:dragon_fire';
        const breathId = isFire ? 'realms:dragon_breath_fire' : 'realms:dragon_breath_frost';
        try {
            dim.spawnParticle(breathId, {
                x: dragon.location.x, y: dragon.location.y + 1, z: dragon.location.z
            });
        } catch (e) { /* */ }
        if (!isFire) {
            for (const p of world.getPlayers()) {
                const d = Math.hypot(p.location.x - dragon.location.x, p.location.z - dragon.location.z);
                if (d < 16) applyTimedFog(p, 'realms:frost_domain_fog', 'rom_dragon_domain', 160);
            }
        }
        dim.runCommand(`effect @p[r=12] instant_damage 1 2 true`);
    } else if (roll < 0.06) {
        // Dive bomb — teleport above nearest player, slam down with AoE
        const players = world.getPlayers();
        if (players.length > 0) {
            const nearest = players.reduce((best, p) => {
                const d = Math.hypot(p.location.x - dragon.location.x, p.location.z - dragon.location.z);
                return d < best.dist ? { player: p, dist: d } : best;
            }, { player: players[0], dist: Infinity }).player;

            const tLoc = nearest.location;
            dragon.teleport({ x: tLoc.x, y: tLoc.y + 15, z: tLoc.z });
            dim.runCommand(`effect @p[r=6] instant_damage 1 4 true`);
            try {
                dim.spawnParticle('realms:ground_slam_dust', { x: tLoc.x, y: tLoc.y + 1, z: tLoc.z });
                dim.playSound('entity.dragon_fire.roar', { x: tLoc.x, y: tLoc.y, z: tLoc.z });
            } catch (e) { /* */ }
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// PHASE 3: ENRAGED (<30% HP)
// ═══════════════════════════════════════════════════════════════════

function executeEnragedPhase(dragon, dim, dragonId) {
    const roll = Math.random();

    if (roll < 0.05) {
        // Cataclysm AoE — large radius damage
        dim.runCommand(`effect @p[r=20] instant_damage 1 3 true`);
        try {
            dim.spawnParticle('realms:phase_enrage', {
                x: dragon.location.x, y: dragon.location.y + 2, z: dragon.location.z
            });
            dim.playSound('ambient.weather.lightning', dragon.location, { volume: 0.8 });
        } catch (e) { /* */ }
    }

    maintainWhelps(dragon, dim, dragonId);
}

// ═══════════════════════════════════════════════════════════════════
// WHELP SYSTEM
// ═══════════════════════════════════════════════════════════════════

function spawnWhelps(dragon, dim) {
    const loc = dragon.location;
    const dragonId = dragon.id;

    // Clear existing whelps from a previous enraged cycle
    if (dragonWhelps.has(dragonId)) {
        for (const wid of dragonWhelps.get(dragonId)) {
            try {
                const w = dim.getEntity(wid);
                if (w && w.isValid()) w.remove();
            } catch (e) { /* chunk unload */ }
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
        // Whelps from an enraged dragon can be tamed as pets by nearby players
        try {
            let nearest = null, bestDist = 24;
            for (const p of world.getPlayers()) {
                if (p.dimension.id !== dim.id) continue;
                const d = Math.hypot(p.location.x - whelp.location.x, p.location.z - whelp.location.z);
                if (d < bestDist) { bestDist = d; nearest = p; }
            }
            if (nearest && Math.random() < 0.5) {
                makeWhelpPet(whelp, nearest);
                nearest.sendMessage('§bA dragon whelp imprints on you! Interact with it to make it sit or follow.');
            }
        } catch (e) { /* */ }
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
            if (w && w.isValid() && (w.getComponent('minecraft:health')?.currentValue || 0) > 0) {
                alive.push(wid);
            }
        } catch (e) { /* chunk unload */ }
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
 * Programmatically spawn a dragon (utility for testing / scripted events).
 */
export function spawnDragon(location, type = 'fire') {
    const dim = world.getDimension('overworld');
    const entityType = type === 'fire' ? 'realms:dragon_fire' : 'realms:dragon_frost';
    return dim.spawnEntity(entityType, location);
}

// ═══════════════════════════════════════════════════════════════════
// DRAGON LAIR AMBIENCE
// Proximity-based: any player standing within LAIR_RADIUS of a live
// dragon's roost (tracked while a dragon is loaded) gets the lair fog
// + occasional distant roar ambience. Approximates structure-bounds
// detection without needing structure spawn coordinates.
// ═══════════════════════════════════════════════════════════════════

const LAIR_RADIUS = 32;
const lairAmbienceTickRef = { lastRoar: 0 };

export function registerLairAmbience() {
    system.runInterval(() => {
        try {
            const now = system.currentTick;
            for (const dimName of ['overworld', 'nether']) {
                const dim = world.getDimension(dimName);
                for (const type of DRAGON_TYPES) {
                    let dragons = [];
                    try { dragons = dim.getEntities({ type }); } catch (e) { continue; }
                    for (const dragon of dragons) {
                        if (!dragon.isValid()) continue;
                        const isFire = dragon.typeId === 'realms:dragon_fire';
                        const fogId = isFire ? 'realms:dragon_lair_fog' : 'realms:frost_domain_fog';
                        for (const p of world.getPlayers()) {
                            if (p.dimension.id !== dim.id) continue;
                            const d = Math.hypot(p.location.x - dragon.location.x,
                                                 Math.abs(p.location.y - dragon.location.y),
                                                 p.location.z - dragon.location.z);
                            if (d < LAIR_RADIUS) applyTimedFog(p, fogId, 'rom_lair', 120);
                        }
                        // Distant roar every ~20s while a player is in the lair
                        if (now - lairAmbienceTickRef.lastRoar > 400) {
                            for (const p of world.getPlayers()) {
                                const d = Math.hypot(p.location.x - dragon.location.x,
                                                     p.location.z - dragon.location.z);
                                if (d < LAIR_RADIUS) {
                                    lairAmbienceTickRef.lastRoar = now;
                                    try {
                                        p.playSound(isFire ? 'entity.dragon_fire.roar'
                                                           : 'entity.dragon_frost.roar',
                                                    { volume: 0.4, pitch: 0.8 });
                                    } catch (e) { /* */ }
                                    break;
                                }
                            }
                        }
                    }
                }
            }
        } catch (e) { /* dims unloaded */ }
    }, 60);
}
