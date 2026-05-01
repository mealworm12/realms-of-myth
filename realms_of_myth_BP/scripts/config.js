/**
 * Realms of Myth - Shared Configuration
 */
export const MOD_ID = 'rom';

export const WEAPON_TIERS = {
    IRON: { tier: 1, damageBonus: 0 },
    MYTHRIL: { tier: 2, damageBonus: 3 },
    DRAGON_BONE: { tier: 3, damageBonus: 6 },
    LEGENDARY: { tier: 4, damageBonus: 9 }
};

export const ARMOR_TIERS = {
    IRON: { tier: 1, defense: 15 },
    MYTHRIL: { tier: 2, defense: 18, bonus: 'magic_resist' },
    DRAGONSCALE: { tier: 3, defense: 21, bonus: 'elemental_resist' },
    CLASS_MASTER: { tier: 4, defense: 20, bonus: 'class_unique' }
};
