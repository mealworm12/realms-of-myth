/**
 * Realms of Myth - Ability Execution System
 */
import { CLASSES, getClassAbilities } from './classSystem.js';
import { world } from '@minecraft/server';

const cooldowns = new Map();

export function useAbility(player, classId, abilityIndex) {
    const abilities = getClassAbilities(classId);
    if (!abilities || abilityIndex >= abilities.length) return false;
    // TODO: Implement cooldown tracking and ability execution
    return true;
}

export function getCooldown(player, classId, abilityIndex) {
    return 0;
}
