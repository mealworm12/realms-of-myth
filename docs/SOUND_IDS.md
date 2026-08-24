# Sound ID Reference

All custom sound-event IDs defined in `realms_of_myth_RP/sounds.json` and how to trigger them from script:

```js
player.playSound("realms.ability.fireball_cast");          // local player
world.playSound("realms.ability.fireball_cast", loc);      // world position
player.dimension.playSound("realms.music.battle_start");   // boss hooks
```

All WAVs are PCM 22050 Hz mono 16-bit, generated deterministically by
`audio-sources/gen_audio_suite.py` (numpy + stdlib `wave`). Re-run that
script from the repo root to regenerate every file byte-stably (seeded RNG).

## Mob voices (BP entity components)

| Entity | ambient_sound | hurt_sound | death_sound |
|---|---|---|---|
| realms:elf_warrior | `entity.elf_warrior.ambient` | `entity.elf_warrior.hurt` | `entity.elf_warrior.death` |
| realms:troll_brute | `entity.troll_brute.ambient` | `entity.troll_brute.hurt` | `entity.troll_brute.death` |
| realms:giant_colossus | `entity.giant_colossus.ambient` | `entity.giant_colossus.hurt` | `entity.giant_colossus.death` |
| realms:dragon_whelp | `entity.dragon_whelp.ambient` | `entity.dragon_whelp.hurt` | `entity.dragon_whelp.death` |
| realms:dragon_fire | `entity.dragon_fire.roar` | `entity.dragon_fire.hurt` | `entity.dragon_fire.death` |
| realms:dragon_frost | `entity.dragon_frost.roar` | `entity.dragon_frost.hurt` | `entity.dragon_frost.death` |

Also defined: `entity.dragon_fire.flap`, `entity.dragon_frost.flap`
(wing flaps), `entity.giant.stomp` (footsteps), `entity.troll.grunt`,
`block.ancient_altar.ambient` (mystic drone — play near the altar via a
script timer; Bedrock blocks have no native ambient loop component).

## Weapon / UI sounds

| ID | Trigger point (for wiring task) |
|---|---|
| `realms.weapon.sword_swing` | sword melee swing |
| `realms.weapon.staff_cast` | staff ability cast |
| `realms.weapon.bow_release` | bow shot |
| `realms.ui.class_select_open` | class selection UI opens |
| `realms.ui.ability_ready` | ability cooldown finishes |

## Ability SFX — mapping into abilities.js

Play `<id>` at cast time for each of the 15 abilities:

| Ability (abilities.js) | Sound ID |
|---|---|
| Fireball | `realms.ability.fireball_cast` |
| Ice Shield | `realms.ability.ice_shield_cast` |
| Arcane Teleport | `realms.ability.arcane_teleport_cast` |
| Multi-Shot | `realms.ability.multi_shot_cast` |
| Shadow Step | `realms.ability.shadow_step_cast` |
| Eagle Eye | `realms.ability.eagle_eye_cast` |
| Rage | `realms.ability.rage_cast` |
| Ground Slam | `realms.ability.ground_slam_cast` |
| Bloodlust | `realms.ability.bloodlust_cast` |
| Holy Light | `realms.ability.holy_light_cast` |
| Divine Shield | `realms.ability.divine_shield_cast` |
| Smite | `realms.ability.smite_cast` |
| Wolf Form | `realms.ability.wolf_form_cast` |
| Entangling Roots | `realms.ability.entangling_roots_cast` |
| Nature's Blessing | `realms.ability.natures_blessing_cast` |

## Boss fight music hooks

The music loops themselves (`sounds/music/realms_theme.wav`,
`sounds/music/realms_battle.wav`) are streamed by the client via
`player.playMusic()` / `player.stopMusic()` in script — they are NOT in
sounds.json (music category is handled separately by design). The stings
ARE sound events:

| ID | Use |
|---|---|
| `realms.music.battle_start` | play this sting, then `player.playMusic("music.realms_battle", {loop: true})` on boss aggro |
| `realms.music.battle_stop` | sting + `player.stopMusic()` when boss dies / player flees |

Suggested wiring in the dragon boss script (phase transitions):
- Phase 1 start → battle_start sting + looped `realms_battle`.
- Phase 3 (enraged) → keep loop, raise tension via pitch if desired.
- Boss death → battle_stop sting + stopMusic.

## File inventory (durations)

mob/: dragon_roar 4.4s, dragon_frost_hurt 3.8s, dragon_wing_flap 0.9s,
giant_stomp 2.6s, troll_grunt 0.8s, troll_bark 0.5s, troll_death 2.8s,
elf_hum 3.0s, elf_hurt 0.45s, elf_death 2.7s, colossus_voice 3.6s,
colossus_hurt 2.4s, colossus_death 4.0s, whelp_chirp 0.5s,
whelp_screech 0.6s, whelp_death 2.3s · block/: altar_drone 6.0s ·
weapons/: sword_swing 0.4s, staff_cast 2.1s, bow_release 0.5s ·
ui/: class_select_open 2.5s, ability_ready 1.2s · ability/: 15 one-shots
0.7–3.2s · music/: realms_theme 44.5s seamless loop, realms_battle 23.7s
seamless loop, battle_start/stop stings 2.7s.
