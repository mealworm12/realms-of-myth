/**
 * Realms of Myth - Class System
 * Race definitions, class definitions, and ability data
 */

/**
 * Race definitions with passive traits
 */
export const RACES = {
    elf: {
        id: 'elf',
        name: 'Elf',
        description: 'Graceful forest-dwellers with keen eyes',
        traits: {
            bowDamageBonus: 0.20,
            nightVision: true,
            baseHealth: 20
        },
        preferredClasses: ['ranger', 'druid']
    },
    troll: {
        id: 'troll',
        name: 'Troll',
        description: 'Massive cave-dwellers with regenerative flesh',
        traits: {
            bonusHealth: 4,
            slowRegeneration: true,
            baseHealth: 24
        },
        preferredClasses: ['berserker', 'paladin']
    },
    giant: {
        id: 'giant',
        name: 'Giant',
        description: 'Colossal mountain-born warriors',
        traits: {
            knockbackResistance: 0.50,
            reachBonus: 2,
            baseHealth: 20
        },
        preferredClasses: ['berserker', 'paladin']
    },
    human: {
        id: 'human',
        name: 'Human',
        description: 'Adaptable and determined',
        traits: {
            xpBonus: 0.10,
            bonusSkillPoint: 1,
            baseHealth: 20
        },
        preferredClasses: []
    }
};

/**
 * Class definitions with abilities
 * All cooldowns in ticks (20 ticks = 1 second)
 */
export const CLASSES = {
    mage: {
        id: 'mage',
        name: 'Mage',
        description: 'Wielder of arcane magic',
        abilities: [
            {
                id: 'fireball',
                name: 'Fireball',
                description: 'Launch an explosive fire projectile',
                cooldown: 160,
                damage: 8
            },
            {
                id: 'ice_shield',
                name: 'Ice Shield',
                description: 'Reduce damage by 50% for 5 seconds',
                cooldown: 600,
                duration: 100
            },
            {
                id: 'arcane_teleport',
                name: 'Arcane Teleport',
                description: 'Teleport 12 blocks forward',
                cooldown: 500,
                range: 12
            }
        ]
    },
    ranger: {
        id: 'ranger',
        name: 'Ranger',
        description: 'Master of bow and shadow',
        abilities: [
            {
                id: 'multi_shot',
                name: 'Multi-Shot',
                description: 'Fire 3 arrows in a spread',
                cooldown: 100,
                arrows: 3
            },
            {
                id: 'shadow_step',
                name: 'Shadow Step',
                description: 'Turn invisible for 8 seconds',
                cooldown: 500,
                duration: 160
            },
            {
                id: 'eagle_eye',
                name: 'Eagle Eye',
                description: 'Highlight all entities within 40 blocks',
                cooldown: 700,
                radius: 40,
                duration: 200
            }
        ]
    },
    berserker: {
        id: 'berserker',
        name: 'Berserker',
        description: 'Fury-driven melee warrior',
        abilities: [
            {
                id: 'rage',
                name: 'Rage',
                description: '+40% damage, +20% speed for 8s',
                cooldown: 600,
                duration: 160
            },
            {
                id: 'ground_slam',
                name: 'Ground Slam',
                description: 'AoE knockback + 6 damage',
                cooldown: 240,
                damage: 6,
                radius: 5
            },
            {
                id: 'bloodlust',
                name: 'Bloodlust',
                description: '30% lifesteal for 6s',
                cooldown: 800,
                duration: 120,
                lifestealPercent: 0.30
            }
        ]
    },
    paladin: {
        id: 'paladin',
        name: 'Paladin',
        description: 'Holy warrior of light',
        abilities: [
            {
                id: 'holy_light',
                name: 'Holy Light',
                description: 'Heal self + nearby allies for 6 HP',
                cooldown: 300,
                healAmount: 6,
                radius: 8
            },
            {
                id: 'divine_shield',
                name: 'Divine Shield',
                description: 'Full invulnerability for 4s',
                cooldown: 1200,
                duration: 80
            },
            {
                id: 'smite',
                name: 'Smite',
                description: '12 damage to undead/dragon types',
                cooldown: 200,
                damage: 12
            }
        ]
    },
    druid: {
        id: 'druid',
        name: 'Druid',
        description: 'Nature-bound shapeshifter',
        abilities: [
            {
                id: 'wolf_form',
                name: 'Wolf Form',
                description: 'Transform into wolf for 15s',
                cooldown: 600,
                duration: 300
            },
            {
                id: 'entangling_roots',
                name: 'Entangling Roots',
                description: 'Root target for 4s, 3 DPS',
                cooldown: 360,
                duration: 80,
                dps: 3
            },
            {
                id: 'natures_blessing',
                name: "Nature's Blessing",
                description: 'Heal 1 HP/s for 15s',
                cooldown: 900,
                duration: 300,
                healPerTick: 1
            }
        ]
    }
};

/**
 * Get abilities for a specific class
 */
export function getClassAbilities(classId) {
    const cls = CLASSES[classId];
    return cls ? cls.abilities : [];
}

/**
 * Get race traits by race ID
 */
export function getRaceTraits(raceId) {
    const race = RACES[raceId];
    return race ? race.traits : null;
}
