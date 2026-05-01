/**
 * Realms of Myth - Dragon Boss AI
 */
import { world, system } from '@minecraft/server';

export const PHASES = {
    GROUND: { threshold: 1.0, min: 0.6 },
    AERIAL: { threshold: 0.6, min: 0.3 },
    ENRAGED: { threshold: 0.3, min: 0.0 }
};

export function spawnDragon(location, type = 'fire') {
    // TODO: Spawn dragon at location
}

export function updateDragonAI(dragon) {
    // TODO: Phase-based behavior tree
}
