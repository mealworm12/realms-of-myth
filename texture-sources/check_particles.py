import json, glob, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
ok = True
tex = set(os.listdir('realms_of_myth_RP/textures/particles'))
files = glob.glob('realms_of_myth_RP/particles/*.json') + glob.glob('realms_of_myth_RP/fogs/*.json') + [
 'realms_of_myth_RP/entity/dragon_fire.entity.json', 'realms_of_myth_RP/entity/dragon_frost.entity.json',
 'realms_of_myth_RP/animations/dragon_fire.animation.json']
for f in files:
    try:
        json.load(open(f)); print('OK ', f)
    except Exception as e:
        ok = False; print('BAD', f, e)
for f in glob.glob('realms_of_myth_RP/particles/*.json'):
    t = os.path.basename(json.load(open(f))['particle_effect']['description']['basic_render_parameters']['texture'])
    if t not in tex: ok = False; print('MISSING TEX', f, t)
efire = json.load(open('realms_of_myth_RP/entity/dragon_fire.entity.json'))['minecraft:client_entity']['description']
efrost = json.load(open('realms_of_myth_RP/entity/dragon_frost.entity.json'))['minecraft:client_entity']['description']
anim = json.load(open('realms_of_myth_RP/animations/dragon_fire.animation.json'))['animations']
tl = anim['animation.dragon_fire.breath'].get('particle_effects', {}).get('0.25', {}).get('effect')
assert tl in efire['particle_effects'], f'dangling fire timeline ref {tl}'
tl2 = anim['animation.dragon_frost.breath'].get('particle_effects', {}).get('0.25', {}).get('effect')
assert tl2 in efrost['particle_effects'], f'dangling frost timeline ref {tl2}'
print('ALL CHECKS PASS' if ok else 'FAILURES PRESENT')
