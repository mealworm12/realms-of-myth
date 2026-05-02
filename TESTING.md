# 🧪 Realms of Myth — Testing Guide

> **Target:** Minecraft Education Edition v1.21.06+ (also works on Bedrock Edition)
> **Package:** `realms-of-myth.mcaddon` — double-click to install

---

## 1. Installation

### On Windows (Education Edition or Bedrock)
1. Download `realms-of-myth.mcaddon` from https://github.com/mealworm12/realms-of-myth
2. **Double-click** the file — Minecraft opens automatically and shows "Import Started" at the top
3. If Minecraft doesn't launch, right-click → **Open with** → Minecraft Education Edition
4. You should see "Successfully imported" after a few seconds

### On Mac / iPad / Chromebook / Android
1. Download the `.mcaddon` file
2. Tap/click it → "Open in Minecraft"
3. Import should begin automatically

---

## 2. Create a Test World

1. Open Minecraft → **Play** → **Create New**
2. Under **Game Settings**:
   - **Game Mode:** Creative (easier for testing)
   - **Difficulty:** Peaceful → Easy (for mob spawning tests)
   - Scroll down to **Cheats** → toggle **Activate Cheats** ON
3. Go to **Add-Ons** tab:
   - Under **Available Resource Packs:** click **Realms of Myth Resource Pack** → Activate
   - Under **Available Behavior Packs:** click **Realms of Myth Behavior Pack** → Activate
4. Scroll down to **Experiments**:
   - Toggle **Beta APIs** ON (required for scripting)
   - Toggle **Holiday Creator Features** ON (for custom blocks/items)
5. Click **Create**

---

## 3. Enable Content Log (Debug Output)

This shows errors from your add-on in real time:

1. **Settings** → **Creator** → toggle both:
   - ✅ **Enable Content Log GUI**
   - ✅ **Enable Content Log File**
2. In-game, press **Ctrl + H** to open the Content Log window
3. Watch for red lines — these are errors from your add-on

---

## 4. Test Plan — Step by Step

### 🟢 Test 1: Basic Load Check

| Action | Expected Result |
|--------|----------------|
| Enter the world | No red errors in Content Log |
| Look in Content Log (`Ctrl+H`) | Should see `[Realms of Myth] Initializing...` and `[Realms of Myth] Ready!` |
| Check chat | Should see the welcome message with orange borders |

**If error:** Check that Beta APIs experiment is ON. The add-on won't load without it.

---

### 🟢 Test 2: Class Selection UI

| Action | Expected Result |
|--------|----------------|
| Type `!class` in chat | A UI form opens: **"Choose Your Race"** |
| Form shows 4 options | Elf, Troll, Giant, Human — each with trait descriptions |
| Click a race (e.g., Elf) | Form advances to **"Choose Your Class"** showing 5 classes |
| Click a class (e.g., Ranger) | Confirm screen shows: "Race: Elf, Class: Ranger" |
| Click **✓ Confirm** | Chat shows: *"Your destiny is sealed"* — you receive a class token item |
| Type `!classinfo` | Chat shows your 3 abilities with cooldowns |

**If nothing happens:** The script might not be loaded. Check Content Log for errors.

---

### 🟢 Test 3: Give Items (Creative Mode)

Open chat and run these commands to get all custom items:

```
/give @s realms:mythril_ingot 64
/give @s realms:dragon_scale 64
/give @s realms:dragon_heart 10
/give @s realms:fire_essence 10
/give @s realms:frost_essence 10
```

**For weapons:**
```
/give @s realms:mythril_sword
/give @s realms:elven_dagger
/give @s realms:troll_warhammer
/give @s realms:mythril_bow
/give @s realms:dragon_bone_greatsword
/give @s realms:giant_club
/give @s realms:enchanted_bow
/give @s realms:dragonslayer_spear
/give @s realms:magic_staff
/give @s realms:shadowfang_dagger
```

**For armor:**
```
/give @s realms:mythril_helmet
/give @s realms:mythril_chestplate
/give @s realms:mythril_leggings
/give @s realms:mythril_boots
/give @s realms:dragonscale_helmet
/give @s realms:dragonscale_chestplate
/give @s realms:dragonscale_leggings
/give @s realms:dragonscale_boots
```

| Expected | Problem if... |
|----------|---------------|
| Items appear in inventory with custom names like "Mythril Sword" | Item says "Unknown" or has missing texture (purple/black checkerboard) = texture mapping issue |

---

### 🟢 Test 4: Ability Triggers

Choose a class first (`!class`), then:

| Action | Expected Result |
|--------|----------------|
| Hold **Nether Star** in hand → right-click/use | Triggers Ability 1 (e.g., Fireball for Mage) |
| Hold **Blaze Powder** → right-click | Triggers Ability 2 (e.g., Ice Shield for Mage) |
| Hold **Ghast Tear** → right-click | Triggers Ability 3 (e.g., Arcane Teleport for Mage) |
| Use same ability again immediately | Chat shows: **"Fireball is on cooldown: 8s"** |
| Wait for cooldown → use again | Ability fires successfully |

**Test each class:**
1. Use `!reset` → re-choose a different class
2. Test all 3 abilities per class
3. Verify cooldowns are unique per ability (not shared)

| Class | Ability 1 (Nether Star) | Ability 2 (Blaze Powder) | Ability 3 (Ghast Tear) |
|-------|------------------------|-------------------------|------------------------|
| **Mage** | Fireball projectile appears | Resistance effect applied | You teleport forward |
| **Ranger** | 3 arrows spawn | Invisibility + speed | Nearby monsters glow |
| **Berserker** | Strength + speed effects | Nearby enemies damaged + knocked up | Small heal + lifesteal active |
| **Paladin** | Self + nearby players healed | Resistance effect | Thunder sound + nearby enemy damaged |
| **Druid** | Speed + strength effects | Nearest enemy frozen | Regeneration effect |

---

### 🟢 Test 5: Summon Entities

```
# Friendly NPCs
/summon realms:elf_warrior

# Hostile mobs (spawn in creative — they'll be passive)
/summon realms:troll_brute
/summon realms:giant_colossus

# Bosses
/summon realms:dragon_fire
/summon realms:dragon_frost
/summon realms:dragon_whelp

# Class selector NPC
/summon realms:class_selector_npc
```

| Expected | Problem if... |
|----------|---------------|
| Entity appears with correct size/model | Invisible entity or white cube = model/texture issue |
| Entity has correct name tag (e.g., "Fire Dragon") | Wrong name or blank = JSON definition issue |
| Dragon has boss bar at top of screen | No boss bar = `minecraft:boss` component issue |
| Giant is visibly 2× player size | Normal size = `minecraft:scale` not working |

---

### 🟢 Test 6: Dragon Boss AI

1. Summon a dragon: `/summon realms:dragon_fire`
2. Set difficulty to **Easy** or higher (otherwise it won't attack)
3. Switch to **Survival Mode** (`/gamemode s`)
4. Attack the dragon

| Expected Behavior | Notes |
|-------------------|-------|
| Dragon attacks you (melee when close) | Must be in Survival, difficulty ≥ Easy |
| At ~60% HP: chat announces "takes flight!" and dragon flies up | Levitation effect applied |
| At ~30% HP: chat announces "IS ENRAGED!" — 3 dragon whelps spawn in a circle | Whelps are small hostile dragons |
| Dragon uses special attacks (breath, dive bomb) periodically | These are random — may need to wait |
| Whelps respawn if killed during enraged phase | Up to 3 constantly maintained |
| Kill the dragon → check drops | Should get Dragon Scales, possibly Dragon Heart |

---

### 🟢 Test 7: Crafting (Survival Mode)

Switch to Survival Mode. Place a crafting table:

| Recipe | Ingredients | Result |
|--------|------------|--------|
| Mythril Ingot (from ore) | 1× Mythril Ore in furnace | Mythril Ingot |
| Mythril Sword | 2× Mythril Ingot + 1× Stick (vertical line) | Mythril Sword |
| Elven Dagger | 1× Mythril Ingot + 1× Stick (diagonal) | Elven Dagger |
| Troll Warhammer | 3× Mythril Ingot (top) + 2× Stick (middle + bottom) | Troll Warhammer |
| Dragon Bone Greatsword | 2× Dragon Scale + 1× Stick | Dragon Bone Greatsword |
| Dragonslayer Spear | 1× Dragon Heart + 1× Mythril Sword | Dragonslayer Spear |
| Staff of Arcana | 1× Dragon Heart + 1× Fire Essence + 2× Stick | Staff of Arcana |
| Mythril Helmet | 5× Mythril Ingot (helmet shape) | Mythril Helmet |
| Dragonscale Chestplate | 8× Dragon Scale (chestplate shape) | Dragonscale Chestplate |

**Use recipe book** (green book icon in crafting table) — all custom recipes should appear.

---

### 🟢 Test 8: Dragonslayer Bonus

1. Give yourself a Dragonslayer Spear: `/give @s realms:dragonslayer_spear`
2. Summon a dragon: `/summon realms:dragon_fire`
3. Hit the dragon with the spear

| Expected | Problem if... |
|----------|---------------|
| Chat message: **"⚔ Dragonslayer! Double damage dealt."** after each hit | No message = the `entityHurt` event handler isn't firing |
| Dragon takes ~2× damage | Normal damage = weapon type check is failing |

---

### 🟢 Test 9: Death & Respawn Persistence

1. Choose a class (e.g., Elf Ranger)
2. Note your class token and effects (night vision for Elf)
3. Die (`/kill @s`)
4. Respawn

| Expected | Problem if... |
|----------|---------------|
| You still have night vision (Elf trait) | Race traits not reapplied |
| You receive a new class token | Class data lost |
| `!classinfo` still shows your class | Player data not persisted |

---

### 🟢 Test 10: Reset

1. Choose any class
2. Type `!reset`
3. Chat says "Your destiny has been reset"
4. Class selection form opens automatically
5. Choose a different class

| Expected | Problem if... |
|----------|---------------|
| Old class token removed from inventory | Old token still present |
| New class token given | Wrong token or none |
| Old abilities no longer work | Cooldowns not cleared |

---

### 🟢 Test 11: Block Textures

```
/give @s realms:mythril_ore
/give @s realms:dragon_egg
/give @s realms:ancient_altar
```

Place them in-world. All should have distinct colors:
- **Mythril Ore:** blue-gray
- **Dragon Egg:** purple with animated texture (shimmer effect)
- **Ancient Altar:** tan/gold

---

### 🟢 Test 12: Multiplayer (if possible)

1. Host a world with a friend (same O365 tenant for Education)
2. Both players choose classes
3. Test that abilities work for both simultaneously
4. Summon a dragon and fight it together
5. Test Paladin Holy Light — should heal nearby allies

---

## 5. Quick Test Commands Cheat Sheet

```
!class          → Open class selection UI
!classinfo      → Show your current class + abilities
!reset          → Reset and re-choose class

/give @s realms:mythril_sword       → Give a weapon
/give @s realms:dragonslayer_spear  → Give legendary weapon
/give @s realms:dragon_heart         → Give rare material

/summon realms:dragon_fire           → Spawn boss
/summon realms:troll_brute           → Spawn enemy
/summon realms:elf_warrior           → Spawn friendly NPC
/summon realms:class_selector_npc    → Spawn the Oracle

/gamemode c    → Creative mode
/gamemode s    → Survival mode
/difficulty e  → Easy difficulty
/difficulty n  → Normal difficulty
/kill @s       → Kill yourself (test respawn)
```

---

## 6. What to Do If Something Doesn't Work

### Check Content Log first (Ctrl+H)
Look for:
- `[Realms of Myth]` log messages — confirm scripts are loaded
- Red error lines — these tell you exactly what failed
- Warnings about missing textures/models — fix paths in texture files

### Common issues and fixes:

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `!class` does nothing | Scripts not loaded | Check Beta APIs experiment is ON |
| Purple/black items | Missing texture PNG | Verify `textures/items/*.png` files exist |
| Invisible mobs | Missing model or client entity file | Check `entity/*.entity.json` and `models/entity/*.geo.json` |
| Ability doesn't fire | Wrong item in hand | Must hold Nether Star, Blaze Powder, or Ghast Tear |
| Dragon doesn't attack | Peaceful difficulty | Set difficulty ≥ Easy |
| Boss bar not showing | Missing `minecraft:boss` component | Check entity JSON |
| Cooldown never expires | Tick system not running | Check for errors in `registerAbilities()` |

### If the add-on won't import:
1. Make sure Minecraft is updated to v1.21.06 or newer
2. Try importing BP and RP separately (unzip the .mcaddon, import each .mcpack)
3. Check that the `.mcaddon` file isn't corrupted (should be ~70 KB)

---

## 7. Test Checklist (Print or Copy)

```
[ ] World loads without Content Log errors
[ ] Welcome message appears on first join
[ ] !class opens race selection form
[ ] All 4 races visible with trait descriptions
[ ] Class selection form shows after race pick
[ ] Confirm screen shows correct choices
[ ] Class token given on confirm
[ ] !classinfo shows correct abilities
[ ] Ability 1 (Nether Star) works for each class
[ ] Ability 2 (Blaze Powder) works for each class
[ ] Ability 3 (Ghast Tear) works for each class
[ ] Cooldowns display correctly
[ ] !reset clears data and reopens form
[ ] All custom items can be /give'd
[ ] All custom entities can be /summon'd
[ ] Dragon has boss bar
[ ] Dragon phase transitions work (ground → aerial → enraged)
[ ] Whelps spawn during enraged phase
[ ] Dragon drops loot on death
[ ] Dragonslayer Spear does bonus damage
[ ] Race traits applied (Elf night vision, Troll HP, etc.)
[ ] Traits persist after death
[ ] All crafting recipes work
[ ] No purple/black placeholder textures
[ ] No invisible entities
```

---

## 8. Expected Total Test Time

| Phase | Time |
|-------|------|
| Installation & world setup | 3 min |
| Basic load check | 1 min |
| Class selection (all 4 races × 5 classes) | 5 min |
| Ability testing (15 abilities) | 10 min |
| Entity summoning | 2 min |
| Dragon boss fight | 5 min |
| Crafting verification | 3 min |
| Death/respawn persistence | 2 min |
| Multiplayer (optional) | 5 min |
| **Total** | **~30-35 min** |
