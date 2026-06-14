/**
 * Realms of Myth - Shared Configuration
 * All mod constants exported for use by other modules.
 *
 * Note: `WEAPON_TIERS` and `ARMOR_TIERS` were removed in v0.2.0 as dead
 * exports (per-item JSON had its own damage/protection values). The
 * `CLASS_MASTER_BONUSES` is the only config currently in active use
 * (consumed by playerData.js#applyClassMasterBonuses).
 *
 * `ABILITY_ITEMS` is defined locally in abilities.js because it's coupled
 * to the ability dispatch order there.
 */

// Class Master Set Bonuses — keys match class IDs in classSystem.js
export const CLASS_MASTER_BONUSES = {
    mage:      { abilityDamageBonus: 0.30, name: 'Arcane Amplification' },
    ranger:    { speedBonus: 0.15, noFallDamage: true, name: "Shadow's Grace" },
    berserker: { lowHPDamageBonus: 0.25, name: 'Blood Fury' },
    paladin:   { damageReflect: 0.10, name: 'Radiant Aegis' },
    druid:     { permanentRegen: 0.5, name: 'Wildheart Vitality' }
};
