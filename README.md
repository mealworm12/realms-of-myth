# 🏰 Realms of Myth

<p align="center">
  <img src="https://img.shields.io/badge/Minecraft-Education%20%26%20Bedrock-brightgreen?style=for-the-badge&logo=minecraft" alt="Minecraft Education & Bedrock">
  <img src="https://img.shields.io/badge/Status-Beta%20Ready-yellow?style=for-the-badge" alt="Beta Ready">
  <img src="https://img.shields.io/badge/Genre-Fantasy%20RPG-purple?style=for-the-badge" alt="Fantasy RPG">
</p>

> *"The Oracle awaits at the Ancient Altar. Choose wisely — your race and class will determine the fate of the realms."*

A fantasy Minecraft add-on featuring playable races, class-based abilities, dragon boss battles, and tiered fantasy weapons & armor.

**Compatible with:** Minecraft Education Edition v1.21.06+ & Bedrock Edition

---

## 🎮 Features

### 🧝 Races (choose one)
| Race | Passive Trait |
|------|---------------|
| **Elf** | +20% bow damage, permanent night vision |
| **Troll** | +4 HP (24 total), slow regeneration |
| **Giant** | 50% knockback resistance, +2 block reach |
| **Human** | +10% XP gain, +1 skill point |

### ⚔️ Classes (choose one — 3 abilities each)
| Class | Abilities |
|-------|-----------|
| **Mage** | Fireball, Ice Shield, Arcane Teleport |
| **Ranger** | Multi-Shot, Shadow Step, Eagle Eye |
| **Berserker** | Rage, Ground Slam, Bloodlust |
| **Paladin** | Holy Light, Divine Shield, Smite |
| **Druid** | Wolf Form, Entangling Roots, Nature's Blessing |

### 🐉 Dragon Bosses
| Boss | HP | Location | Special Drops |
|------|-----|----------|---------------|
| **Fire Dragon** | 300 | Volcano/Nether | Fire Essence, Dragon Heart |
| **Frost Dragon** | 350 | Ice Spikes/Tundra | Frost Essence, Dragon Heart |

Dragons have 3 phases: **Ground → Aerial → Enraged** with unique attack patterns per phase.

### 🗡️ Weapons (4 Tiers)
| Tier | Materials | Examples |
|------|-----------|----------|
| T1: Iron | Iron | Sword, Axe, Bow |
| T2: Mythril | Mythril Ingot | Mythril Sword, Elven Dagger, Troll Warhammer |
| T3: Dragon Bone | Dragon Scale | Dragon Bone Greatsword, Giant's Club |
| T4: Legendary | Dragon Heart + Essence | Dragonslayer Spear, Staff of Arcana, Shadowfang Dagger |

### 🛡️ Armor (4 Tiers)
| Tier | Set | Full Set Bonus |
|------|-----|----------------|
| T1 | Iron | — |
| T2 | Mythril | +10% magic resistance |
| T3 | Dragonscale | Fire & frost resistance |
| T4 | Class Master | Unique per-class bonus |

---

## 🚀 Getting Started

### Installation
1. Download the latest `.mcaddon` from [Releases](https://github.com/mealworm12/realms-of-myth/releases)
2. Double-click the file to import into Minecraft Education Edition or Bedrock Edition
3. Create a new world → activate both Behavior Pack and Resource Pack
4. Start the world!

### Quick Commands
| Command | Action |
|---------|--------|
| `!class` or `!choose` | Open race/class selection UI |
| `!classinfo` | View your current class abilities |
| `!reset` | Reset your race/class choice |

### Ability Usage
Hold one of these items and right-click to use your class abilities:
- `Nether Star` → Ability 1
- `Blaze Powder` → Ability 2
- `Ghast Tear` → Ability 3

---

## 📁 Project Structure

```
realms-of-myth/
├── realms_of_myth_BP/          ← Behavior Pack
│   ├── manifest.json
│   ├── scripts/                 ← JavaScript game logic
│   │   ├── main.js             ← Entry point & event hooks
│   │   ├── classSystem.js      ← Race + class data definitions
│   │   ├── classSelection.js   ← Multi-step selection UI
│   │   ├── abilities.js        ← All 15 ability implementations
│   │   ├── dragonBoss.js       ← Dragon AI & whelp system
│   │   ├── playerData.js       ← Persistence & trait application
│   │   └── config.js           ← Shared constants
│   ├── entities/                ← Custom mob definitions
│   ├── items/                   ← Custom item definitions
│   ├── armor/                   ← Custom armor definitions
│   ├── blocks/                  ← Custom block definitions
│   ├── recipes/                 ← Crafting recipes
│   ├── loot_tables/             ← Mob & block drop tables
│   ├── spawn_rules/             ← Natural spawning configs
│   └── functions/               ← Command functions
│
└── realms_of_myth_RP/          ← Resource Pack
    ├── manifest.json
    ├── textures/                ← Item/block/entity textures
    ├── models/                  ← 3D entity & armor models
    ├── animations/              ← Entity animations
    ├── sounds/                  ← Custom sound effects
    └── ui/                      ← Custom UI screens
```

---

## 🛠️ Development Status

```
Phase 1: Project Scaffolding     ████████████████████ 100%  ✅
Phase 2: Models & Textures       ░░░░░░░░░░░░░░░░░░░░   0%   ⬜ (needs Blockbench)
Phase 3: Items & Weapons         ████████████████████ 100%  ✅
Phase 4: Armor Sets              ████████████████████ 100%  ✅
Phase 5: Entities, Blocks, Rules ████████████████████ 100%  ✅
Phase 6: Class System & Scripts  ████████████████████ 100%  ✅
Phase 7: Functions & Dialogue    ████████████████████ 100%  ✅
Phase 8: Integration & Testing   ░░░░░░░░░░░░░░░░░░░░   0%   🔜 Next
Phase 9: Packaging & Release     ░░░░░░░░░░░░░░░░░░░░   0%   ⬜
```

**What's left:** 3D models/textures (Blockbench), playtesting & balance, `.mcaddon` packaging.

---

## 📄 License

MIT License — free for personal and educational use.
