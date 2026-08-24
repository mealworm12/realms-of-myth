#!/usr/bin/env python3
"""One-shot generator for realms_of_myth_RP/particles/*.particle.json.
Writes tuned emitter/curve/motion configs for the 14 custom VFX particles."""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'realms_of_myth_RP', 'particles')
os.makedirs(OUT, exist_ok=True)


def particle(name, texture, *, max_particles, lifetime, emitter, space,
             size=None, color=None, speed=None, direction=None,
             gravity=None, drag=0, curves=None, rotation_rate=None,
             face_camera=True, lifetime_expr=None):
    """Build a standard Bedrock particle effect dict."""
    comps = {
        "minecraft:emitter_rate_steady": {"spawn_rate": emitter[0], "max_particles": max_particles},
        "minecraft:emitter_lifetime_looping": {"active_time": lifetime},
        "minecraft:emitter_shape_sphere": {
            "offset": [0, 0.2, 0],
            "radius": emitter[1],
            "direction": direction or "outwards",
        },
        "minecraft:particle_initial_speed": speed if speed is not None else 1.0,
        "minecraft:particle_lifetime_expression": (
            {"max_lifetime": lifetime_expr} if not isinstance(lifetime_expr, dict)
            else lifetime_expr),
        "minecraft:particle_motion_dynamic": {
            "linear_acceleration": gravity or [0, 0, 0],
            "linear_drag_coefficient": drag,
        },
        "minecraft:particle_appearance_billboard": {
            "size": size or [0.15, 0.15],
            "facing_camera_mode": "lookat_xyz" if face_camera else "rotate_xyz",
            "uv": {"texture_width": 1, "texture_height": 1, "uv": [0, 0], "uv_size": [1, 1]},
        },
        "minecraft:particle_appearance_tinting": {
            "color": color or [1.0, 1.0, 1.0, 1.0],
        },
        "minecraft:particle_appearance_lighting": {},
    }
    if rotation_rate is not None:
        comps["minecraft:particle_initial_spin"] = {
            "rotation": "math.random(0, 360)",
            "rotation_rate": rotation_rate,
        }
    if curves:
        comps["minecraft:particle_appearance_tinting"]["color"] = color
        for c in curves:
            comps[f"minecraft:curve_{c['id']}"] = c
    return {
        "format_version": "1.10.0",
        "particle_effect": {
            "description": {
                "identifier": f"realms:{name}",
                "basic_render_parameters": {
                    "material": "particles_alpha" if name in (
                        'ground_slam_dust', 'dragon_breath_fire',
                        'dragon_breath_frost', 'rage_blood_motes') else "particles_blend",
                    "texture": f"textures/particles/{texture}",
                },
            },
            "components": comps,
            "events": space or {},
        },
    }


def curve(id_, nodes_x, nodes_y, input_v, horizontal_range):
    return {
        "type": "bezier_chain",
        "input": input_v,
        "horizontal_range": horizontal_range,
        "nodes": {str(x): {"value": y, "left": 0.0, "right": 0.0}
                  for x, y in zip(nodes_x, nodes_y)},
        "_id": id_,
    }


P = []

# 1 fireball_trail — orange->crimson fading embers, upward drift
P.append(particle('fireball_trail', 'ember.png',
                  max_particles=64, lifetime=2.0, emitter=(24, 0.25),
                  space="entity_mother",
                  size=[0.14, 0.14], speed=0.4,
                  gravity=[0, 0.8, 0], drag=1.5,
                  lifetime_expr={"max_lifetime": "math.random(0.4,0.9)"},
                  rotation_rate=-40,
                  color=[
                      "(Variable.particle_age/Variable.particle_lifetime)*1.0",
                      "0.55-(Variable.particle_age/Variable.particle_lifetime)*0.45",
                      "0.20-(Variable.particle_age/Variable.particle_lifetime)*0.18",
                      "1.0-Variable.particle_age/Variable.particle_lifetime"],
                  ))

# 2 frost_nova_ring — expanding ring of ice shards
ring_shard = particle('frost_nova_ring', 'ice_shard.png',
                      max_particles=48, lifetime=1.0, emitter=(48, 0.3),
                      space="world",
                      size=[0.22, 0.22], speed=6.5, drag=4.0,
                      direction=[[0, "(variable.particle_random_1<0.85 ? 0 : math.random(-1,1))", 0]],
                      rotation_rate=180,
                      color=["0.75", "0.88", "1.0",
                             "1.0-Variable.particle_age/Variable.particle_lifetime"])
P.append(ring_shard)

# 3 arcane_step — violet motes swirling inward (teleport)
swirl = {
    "type": "linear",
    "input": "variable.particle_age",
    "horizontal_range": 0.8,
    "nodes": [1.0, 0.7, 0.35, 0.0],
}
p3 = particle('arcane_step', 'rune_mote.png',
              max_particles=32, lifetime=1.0, emitter=(28, 0.9),
              space="entity_mother",
              size=[0.12, 0.12], speed=-1.8, drag=0.5,
              direction=[[0, "math.random(-0.2,0.6)", 0]],
              lifetime_expr={"max_lifetime": "math.random(0.5,1.0)"},
              rotation_rate=90)
# inward spiral via dynamic motion parametric swirl
p3['particle_effect']['components']['minecraft:particle_motion_dynamic'] = {
    "linear_acceleration": [0, 0.4, 0],
    "linear_drag_coefficient": 0.5,
    "rotation_acceleration": 0,
}
p3['particle_effect']['components']['minecraft:emitter_shape_sphere']['radius'] = 1.1
p3['particle_effect']['components']['minecraft:particle_appearance_tinting']['color'] = \
    ["0.73", "0.43", "1.0", "1.0-Variable.particle_age/Variable.particle_lifetime"]
P.append(p3)

gold_fade = ["1.0", "0.85", "0.38", "1.0-Variable.particle_age/Variable.particle_lifetime"]

# 4 holy_light_beam — rising gold sparkles column
P.append(particle('holy_light_beam', 'sparkle_gold.png',
                  max_particles=80, lifetime=2.5, emitter=(36, 0.4),
                  space="world",
                  size=[0.16, 0.16], speed=2.2,
                  direction=[[0, 1, 0]], drag=0.8,
                  lifetime_expr={"max_lifetime": "math.random(0.8,1.6)"},
                  color=gold_fade))

# 5 divine_shield_aura — long-lived slow orbiting gold halo (aura style)
aura = particle('divine_shield_aura', 'halo_glow.png',
                max_particles=24, lifetime=10.0, emitter=(10, 0.7),
                space="entity_mother",
                size=[0.2, 0.2], speed=0.0, drag=0.0,
                direction=[[0, 0.05, 0]],
                lifetime_expr={"max_lifetime": "math.random(2.5,4.0)"},
                color=gold_fade)
# orbiting halo: torus-ish shape + slow tangential velocity
aura['particle_effect']['components']['minecraft:emitter_shape_disc'] = \
    aura['particle_effect']['components'].pop('minecraft:emitter_shape_sphere')
aura['particle_effect']['components']['minecraft:emitter_shape_disc'] = {
    "offset": [0, 1.0, 0], "radius": 0.9,
    "plane_normal": [0, 1, 0], "direction": [[
        "-variable.particle_random_2*2+1", 0.05, "-variable.particle_random_1*2+1"]],
}
aura['particle_effect']['components']['minecraft:particle_initial_speed'] = 1.1
P.append(aura)

# 6 rage_blood_motes — crimson drips falling + heat shimmer
blood = particle('rage_blood_motes', 'blood_drip.png',
                 max_particles=40, lifetime=3.0, emitter=(12, 0.5),
                 space="entity_mother",
                 size=[0.13, 0.13], speed=0.2,
                 direction=[[0, -0.4, 0]],
                 gravity=[0, -6.0, 0], drag=0.2,
                 lifetime_expr={"max_lifetime": "math.random(0.5,1.2)"},
                 color=["0.67", "0.06", "0.09", "1.0-Variable.particle_age/Variable.particle_lifetime"])
P.append(blood)

# 7 ground_slam_dust — radial low shockwave dust puffs
dust = particle('ground_slam_dust', 'dust_puff.png',
                max_particles=60, lifetime=1.2, emitter=(30, 0.4),
                space="world",
                size=[0.5, 0.5], speed=4.0, drag=3.0,
                direction=[[0, 0.08, 0]],
                rotation_rate=25,
                lifetime_expr={"max_lifetime": "math.random(0.5,1.1)"},
                color=["0.58", "0.51", "0.42", "0.9-Variable.particle_age/Variable.particle_lifetime*0.9"])
dust['particle_effect']['components']['minecraft:emitter_shape_sphere']['offset'] = [0, 0.05, 0]
dust['particle_effect']['components']['minecraft:particle_appearance_billboard']['size'] = [
    "0.3+variable.particle_age*0.5", "0.3+variable.particle_age*0.5"]
P.append(dust)

# 8 nature_blessing_leaves — drifting leaves + pollen
leaf = particle('nature_blessing_leaves', 'leaf.png',
                max_particles=48, lifetime=4.0, emitter=(8, 1.2),
                space="world",
                size=[0.16, 0.16], speed=0.3,
                direction=[["math.random(-0.5,0.5)", -0.3, "math.random(-0.5,0.5)"]],
                gravity=[0, -0.6, 0], drag=1.2,
                lifetime_expr={"max_lifetime": "math.random(2.0,3.5)"},
                rotation_rate=60,
                color=["0.34", "0.69", "0.28", "1.0-Variable.particle_age/Variable.particle_lifetime"])
P.append(leaf)

# 9 entangle_roots — brown/green spiral wisps low to ground
roots = particle('entangle_roots', 'root_wisp.png',
                 max_particles=40, lifetime=2.5, emitter=(16, 0.6),
                 space="world",
                 size=[0.2, 0.2], speed=-1.2,
                 direction=[[0, 0.15, 0]], drag=0.8,
                 lifetime_expr={"max_lifetime": "math.random(0.8,1.6)"},
                 rotation_rate=-70,
                 color=[
                     "0.48-Variable.particle_age*0.1",
                     "(Variable.particle_age>0.5?0.62:0.34)",
                     "0.19", "0.95-Variable.particle_age/Variable.particle_lifetime*0.9"])
roots['particle_effect']['components']['minecraft:emitter_shape_cylinder'] = \
    roots['particle_effect']['components'].pop('minecraft:emitter_shape_sphere')
roots['particle_effect']['components']['minecraft:emitter_shape_cylinder'] = {
    "offset": [0, 0.1, 0], "radius": 1.2, "height": 0.3,
    "direction": "outwards",
}
P.append(roots)

# 10 spear_lightning — electric arc crackle
bolt = particle('spear_lightning', 'lightning_arc.png',
                max_particles=24, lifetime=0.6, emitter=(40, 0.3),
                space="entity_mother",
                size=[0.3, 0.3], speed=0.5, drag=2.0,
                lifetime_expr={"max_lifetime": "math.random(0.08,0.25)"},
                color=["0.59", "0.78", "1.0",
                       "1.0-Variable.particle_age/Variable.particle_lifetime"])
P.append(bolt)

breath_common = dict(
    space="entity_mother",
    lifetime_expr={"max_lifetime": "math.random(0.4,0.9)"},
)
# 11 dragon_breath_fire — sustained cone stream, embers + smoke
fbreath = particle('dragon_breath_fire', 'fire_smoke.png',
                   max_particles=160, lifetime=5.0, emitter=(60, 0.35),
                   size=[0.35, 0.35], speed=7.0, drag=1.8,
                   direction=[[-0.15, "math.random(-0.1,0.15)", "math.random(-0.1,0.15)"]],
                   rotation_rate=40,
                   **breath_common,
                   color=["1.0-Variable.particle_age*0.6",
                          "(Variable.particle_age<0.3?0.65:0.35)",
                          "(Variable.particle_age<0.3?0.25:0.18)",
                          "0.9-Variable.particle_age/Variable.particle_lifetime*0.8"])
fbreath['particle_effect']['components']['minecraft:emitter_shape_sphere']['radius'] = 0.3
fbreath['particle_effect']['components']['minecraft:particle_appearance_billboard']['size'] = [
    "0.2+variable.particle_age*0.6", "0.2+variable.particle_age*0.6"]
P.append(fbreath)

# 12 dragon_breath_frost — crystalline mist cone
rbreath = particle('dragon_breath_frost', 'frost_mist.png',
                   max_particles=140, lifetime=5.0, emitter=(50, 0.35),
                   size=[0.3, 0.3], speed=6.0, drag=2.2,
                   direction=[[-0.15, "math.random(-0.08,0.12)", "math.random(-0.08,0.12)"]],
                   rotation_rate=30,
                   **breath_common,
                   color=["0.78", "0.91", "1.0", "0.7-Variable.particle_age/Variable.particle_lifetime*0.6"])
rbreath['particle_effect']['components']['minecraft:emitter_shape_sphere']['radius'] = 0.3
rbreath['particle_effect']['components']['minecraft:particle_appearance_billboard']['size'] = [
    "0.18+variable.particle_age*0.55", "0.18+variable.particle_age*0.55"]
P.append(rbreath)

# 13 phase_enrage — dramatic red shockwave burst
enrage = particle('phase_enrage', 'shockwave_ring.png',
                  max_particles=64, lifetime=1.5, emitter=(64, 0.2),
                  space="world",
                  size=[1.2, 1.2], speed=9.0, drag=4.5,
                  direction=[[0, 0.05, 0]],
                  rotation_rate=0,
                  lifetime_expr={"max_lifetime": "math.random(0.6,1.2)"},
                  color=["1.0", "0.16", "0.16",
                         "1.0-Variable.particle_age/Variable.particle_lifetime"])
enrage['particle_effect']['components']['minecraft:particle_appearance_billboard']['size'] = [
    "0.8+variable.particle_age*2.5", "0.8+variable.particle_age*2.5"]
P.append(enrage)

# 14 class_select_burst — celebratory gold star burst
burst = particle('class_select_burst', 'sparkle_gold.png',
                 max_particles=72, lifetime=1.2, emitter=(72, 0.15),
                 space="world",
                 size=[0.18, 0.18], speed=5.5, drag=3.5,
                 gravity=[0, -2.0, 0],
                 lifetime_expr={"max_lifetime": "math.random(0.5,1.1)"},
                 rotation_rate=120,
                 color=gold_fade)
P.append(burst)

for p in P:
    # strip helper keys
    eff = p['particle_effect']
    eff['components'] = {k: v for k, v in eff['components'].items()
                         if k != '_id' and v is not None}
    for comp in list(eff.get('curves', {})):
        pass
    name = eff['description']['identifier'].split(':')[1]
    path = os.path.join(OUT, f'{name}.particle.json')
    with open(path, 'w') as f:
        json.dump(p, f, indent=2)
    print('wrote', path)
print('total:', len(P))
