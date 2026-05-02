# 🏰 Realms of Myth

<p align="center">
  <img src="https://img.shields.io/badge/Minecraft-Education%20%26%20Bedrock-brightgreen?style=for-the-badge&logo=minecraft" alt="Minecraft Education & Bedrock">
  <img src="https://img.shields.io/badge/Status-Ready%20for%20Testing-brightgreen?style=for-the-badge" alt="Ready for Testing">
  <img src="https://img.shields.io/badge/Genre-Fantasy%20RPG-purple?style=for-the-badge" alt="Fantasy RPG">
  <img src="https://img.shields.io/badge/Files-256-blue?style=for-the-badge" alt="256 Files">
</p>

> *"The Oracle awaits at the Ancient Altar. Choose wisely — your race and class will shape your destiny in the realms."*

A fantasy Minecraft add-on featuring playable races, class-based abilities with cooldowns, multi-phase dragon boss battles, and four tiers of fantasy weapons & armor — all in a single double-click `.mcaddon` package.

**Compatible with:** Minecraft Education Edition v1.21.06+ & Bedrock Edition v1.21.60+

---

## 🎮 Features

### 🧝 4 Playable Races
| Race | Passive Trait |
|------|---------------|
| **Elf** | +20% bow damage, permanent night vision |
| **Troll** | +4 HP (24 total), slow regeneration |
| **Giant** | 50% knockback resistance, +2 block reach |
| **Human** | +10% XP gain, +1 skill point |

### ⚔️ 5 Classes — 15 Unique Abilities
| Class | Ability 1 (☆) | Ability 2 (🔥) | Ability 3 (💧) |
|-------|:---:|:---:|:---:|
| **Mage** | Fireball *(8s)* | Ice Shield *(30s)* | Arcane Teleport *(25s)* |
| **Ranger** | Multi-Shot *(5s)* | Shadow Step *(25s)* | Eagle Eye *(35s)* |
| **Berserker** | Rage *(30s)* | Ground Slam *(12s)* | Bloodlust *(40s)* |
| **Paladin** | Holy Light *(15s)* | Divine Shield *(60s)* | Smite *(10s)* |
| **Druid** | Wolf Form *(30s)* | Entangling Roots *(18s)* | Nature's Blessing *(45s)* |

*Trigger abilities by holding the item and right-clicking: Nether Star (☆), Blaze Powder (🔥), or Ghast Tear (💧).*

### 🐉 Dragon Bosses — 3-Phase AI
| Boss | HP | Location | Special Drops |
|------|-----|----------|---------------|
| **Fire Dragon** | 300 | Volcano/Nether | Fire Essence, Dragon Heart (25%) |
| **Frost Dragon** | 350 | Ice Spikes/Tundra | Frost Essence, Dragon Heart (30%) |

**Phase behavior:**
- **Ground** (>60% HP) — melee, breath attacks
- **Aerial** (30-60% HP) — flight, dive bombs, strafing
- **Enraged** (<30% HP) — cataclysm AoE, summons 3 dragon whelps

### 🗡️ 4 Weapon Tiers
| Tier | Damage Bonus | Materials | Examples |
|------|:---:|------|----------|
| **T1: Iron** | +0 | Iron | Sword, Axe, Bow |
| **T2: Mythril** | +3 | Mythril Ingot | Mythril Sword, Elven Dagger, Troll Warhammer |
| **T3: Dragon Bone** | +6 | Dragon Scale | Dragon Bone Greatsword, Giant's Club, Enchanted Bow |
| **T4: Legendary** | +9 | Dragon Heart + Essence | Dragonslayer Spear, Staff of Arcana, Shadowfang Dagger |

**Legendary weapon specials:**
- **Dragonslayer Spear** — double damage vs dragons
- **Staff of Arcana** — reduces ability cooldowns by 20%
- **Shadowfang Dagger** — invisibility on kill (3s)

### 🛡️ 4 Armor Tiers
| Tier | Protection | Full Set Bonus |
|------|:---:|------|
| T1: Iron | 60% | — |
| T2: Mythril | 68% | +10% magic resistance |
| T3: Dragonscale | 76% | Fire & frost resistance |
| T4: Class Master | 72% | Unique per-class bonus (see below) |

**Class Master bonuses:** Mage (+30% ability damage), Ranger (+15% speed, no fall damage), Berserker (+25% damage <50% HP), Paladin (10% damage reflect), Druid (permanent regeneration)

---

## 🚀 Getting Started

### Quick Install
1. Download `realms-of-myth.mcaddon` from the [repo root](https://github.com/mealworm12/realms-of-myth) or [Releases](https://github.com/mealworm12/realms-of-myth/releases)
2. **Double-click the file** — Minecraft imports both packs automatically
3. Create a new world → **Add-Ons** tab → activate both packs
4. **Important:** Enable **Beta APIs** under Experiments (required for scripting)
5. Start the world!

### Player Commands
| Command | Action |
|---------|--------|
| `!class` or `!choose` | Open race/class selection UI |
| `!classinfo` | View your current class + all abilities |
| `!reset` | Reset your class/race and choose again |

### How to Play
1. Type `!class` to open the selection screen
2. Pick your **race** (Elf, Troll, Giant, Human) → then your **class** (Mage, Ranger, Berserker, Paladin, Druid)
3. Confirm — you receive a class token and race passive traits
4. Use abilities in combat by holding Nether Star / Blaze Powder / Ghast Tear + right-click
5. Hunt dragons for Dragon Scales, Hearts & Essences to craft T3/T4 gear

---

## 📁 Project Structure

```
realms-of-myth/
├── realms_of_myth_BP/          ← Behavior Pack (game logic)
│   ├── manifest.json           ← @minecraft/server 2.7.0 + @minecraft/server-ui 1.3.0
│   ├── scripts/                 ← 7 JavaScript modules (~2,500 lines)
│   │   ├── main.js             ← Entry point, chat commands, event hooks
│   │   ├── classSystem.js      ← All race/class/ability data definitions
│   │   ├── classSelection.js   ← Multi-step UI (race → class → confirm)
│   │   ├── abilities.js        ← 15 ability implementations + cooldowns
│   │   ├── dragonBoss.js       ← 3-phase dragon AI + whelp system
│   │   ├── playerData.js       ← Persistence, traits, respawn handling
│   │   └── config.js           ← Weapon/armor tier constants
│   ├── entities/                ← 7 custom entity definitions
│   ├── items/                   ← 20 custom weapon/material items
│   ├── armor/                   ← 36 armor pieces (3 tiers × 4 pieces × 3 sets + class sets)
│   ├── blocks/                  ← 3 custom block definitions
│   ├── recipes/                 ← 16 crafting recipes
│   ├── loot_tables/             ← 6 entity/block drop tables
│   └── spawn_rules/             ← 4 natural spawning configurations
│
├── realms_of_myth_RP/          ← Resource Pack (visuals & audio)
│   ├── manifest.json
│   ├── textures/                ← 60 PNG textures (items, blocks, entities)
│   ├── models/                  ← 6 entity geometry models (Blockbench-compatible)
│   ├── animations/              ← Entity animation files
│   ├── sounds/                  ← 9 WAV audio files + sounds.json (11 events)
│   ├── render_controllers/      ← Entity rendering configuration
│   ├── entity/                  ← 7 client entity definitions
│   └── ui/                      ← Custom UI screens
│
├── .mcaddon                     ← Double-click install package (70 KB)
├── TESTING.md                   ← Comprehensive testing guide (12 test cases)
└── README.md                    ← You are here
```

---

## 🛠️ Development Status

```
Phase 1: Project Scaffolding      ████████████████████ 100%  ✅
Phase 2: Textures & Models        ████████████████████ 100%  ✅  (60 PNGs, 6 geo models, 9 WAVs)
Phase 3: Items & Weapons          ████████████████████ 100%  ✅  (20 items, 1 token × 5 classes)
Phase 4: Armor Sets               ████████████████████ 100%  ✅  (36 armor pieces, 3 tiers)
Phase 5: Entities, Blocks, Rules  ████████████████████ 100%  ✅  (7 entities, 3 blocks, 6 loot tables)
Phase 6: Class System & Scripts   ████████████████████ 100%  ✅  (7 JS modules, 15 abilities, AI)
Phase 7: Functions & Dialogue     ████████████████████ 100%  ✅  (start_game function, oracle NPC)
Phase 8: Audit & Bug Fixes        ████████████████████ 100%  ✅  (critical fixes applied)
Phase 9: Packaging & Release      ████████████████████ 100%  ✅  (.mcaddon shipped)
Phase 10: Testing Documentation   ████████████████████ 100%  ✅  (TESTING.md live)
```

**🔜 Next:** Playtesting on Education Edition and Bedrock. Real Blockbench models to replace placeholder textures.

---

## 🧪 Testing

See **[TESTING.md](TESTING.md)** for the complete step-by-step testing guide covering:
- 12 structured test cases (class selection, abilities, crafting, dragon boss AI, multiplayer)
- Quick-reference cheat sheet of all test commands
- Troubleshooting guide for common issues
- 35-item test checklist (printable)
- Expected total test time: ~30 minutes

---

## 📄 License

MIT License — free for personal, educational, and commercial use.

---

<p align="center">
  <strong>What destiny will you forge in the realms?</strong><br>
  <em>The Oracle is waiting.</em>
</p>
