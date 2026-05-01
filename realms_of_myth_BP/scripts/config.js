/**
 * Realms of Myth - Shared Configuration
 * All mod constants exported for use by other modules
 */

export const MOD_ID = 'rom';
export const MOD_PREFIX = 'realms';

// Weapon Tiers
export const WEAPON_TIERS = {
    IRON: { tier: 1, damageBonus: 0, material: 'iron' },
    MYTHRIL: { tier: 2, damageBonus: 3, material: 'mythril' },
    DRAGON_BONE: { tier: 3, damageBonus: 6, material: 'dragon_bone' },
    LEGENDARY: { tier: 4, damageBonus: 9, material: 'legendary' }
};

// Armor Tiers
export const ARMOR_TIERS = {
    IRON: { tier: 1, defense: 15, protection: 0.60 },
    MYTHRIL: { tier: 2, defense: 18, protection: 0.68, bonus: 'magic_resist' },
    DRAGONSCALE: { tier: 3, defense: 21, protection: 0.76, bonus: 'elemental_resist' },
    CLASS_MASTER: { tier: 4, defense: 20, protection: 0.72, bonus: 'class_unique' }
};

// Class Master Set Bonuses
export const CLASS_MASTER_BONUSES = {
    mage: { abilityDamageBonus: 0.30, name: 'Arcane Amplification' },
    ranger: { speedBonus: 0.15, noFallDamage: true, name: 'Shadow\'s Grace' },
    berserker: { lowHPDamageBonus: 0.25, name: 'Blood Fury' },
    paladin: { damageReflect: 0.10, name: 'Radiant Aegis' },
    druid: { permanentRegen: 0.5, name: 'Wildheart Vitality' }
};

// Ability trigger items
export const ABILITY_ITEMS = [
    'minecraft:nether_star',    // Ability 1
    'minecraft:blaze_powder',   // Ability 2
    'minecraft:ghast_tear'      // Ability 3
];
