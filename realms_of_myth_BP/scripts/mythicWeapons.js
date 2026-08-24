/**
 * Realms of Myth - Mythic Tier Weapons
 * Three weapons above Legendary:
 *   realms:dawnbreaker       — holy greatsword: AoE smite proc vs undead/dragons
 *   realms:void_reaver       — dagger: chance to teleport behind target on backstab
 *   realms:stormcaller_hammer— hammer: lightning strike on hit (cooldown)
 *
 * Procs are implemented here (script-side damage/proc engine); the item JSONs,
 * recipes, geometry, attachables and textures are separate assets.
 */

import { world, system, Player } from '@minecraft/server';
import { loadPlayerData } from './playerData.js';

// ── Tuning constants ───────────────────────────────────────────────
const DAWNBREAKER_PROC_CHANCE = 0.20;  // per hit vs undead/dragon family
const DAWNBREAKER_RADIUS = 6;
const VOID_REAVER_BACKSTAB_CHANCE = 0.35;
const STORMCALLER_COOLDOWN_TICKS = 100; // 5s between lightning strikes

// playerId -> tick when stormcaller may next fire
const stormCooldowns = new Map();

const UNDEAD_FAMILIES = ['undead', 'zombie', 'skeleton', 'phantom', 'wither'];

function isFamily(entity, fam) {
    try {
        const tf = entity.getComponent('minecraft:type_family');
        if (!tf) return false;
        if (tf.hasType(fam)) return true;
    } catch (e) { /* component missing */ }
    return false;
}

function isUndeadOrDragon(entity) {
    return isFamily(entity, 'dragon') ||
           UNDEAD_FAMILIES.some(f => isFamily(entity, f)) ||
           /zombie|skeleton|phantom|wither|husk|drowned|stray/.test(entity.typeId);
}

export function registerMythicWeapons() {
    // ── Proc engine: runs in the AFTER hurt event so we can add effects on top ──
    world.afterEvents.entityHurt.subscribe((event) => {
        const damager = event.damageSource?.damagingEntity;
        const victim = event.hurtEntity;
        if (!damager || !(damager instanceof Player) || !victim || !victim.isValid?.()) return;

        let weapon = null;
        try {
            const eq = damager.getComponent('minecraft:equippable');
            weapon = eq && eq.getEquipment('Mainhand');
        } catch (e) { return; }
        if (!weapon) return;
        if (event.damageSource.cause !== 'entityAttack' &&
            event.damageSource.cause !== 'entityAttackNoDamage') return;

        switch (weapon.typeId) {
            case 'realms:dawnbreaker':        procDawnbreaker(damager, victim); break;
            case 'realms:void_reaver':        procVoidReaver(damager, victim); break;
            case 'realms:stormcaller_hammer': procStormcaller(damager, victim); break;
        }
    });

    world.afterEvents.playerLeave.subscribe((e) => stormCooldowns.delete(e.playerId));
}

// ── Dawnbreaker — Holy Greatsword ──────────────────────────────────
function procDawnbreaker(player, victim) {
    if (!isUndeadOrDragon(victim)) return;
    if (Math.random() > DAWNBREAKER_PROC_CHANCE) return;

    const dim = player.dimension;
    const loc = victim.location;
    dim.runCommand(`execute at @e[type=${victim.typeId},c=1] run particle realms:holy_light_beam ~ ~1 ~`);
    try { dim.spawnParticle('realms:holy_light_beam', loc); } catch (e) { /* */ }
    dim.runCommand(`effect @e[r=${DAWNBREAKER_RADIUS},family=monster] instant_damage 2 3 true`);
    player.playSound('realms.ability.smite_cast');
    player.sendMessage('§e☀ Dawnbreaker unleashes holy radiance!');
}

// ── Void Reaver — Shadow Dagger ────────────────────────────────────
function procVoidReaver(player, victim) {
    if (Math.random() > VOID_REAVER_BACKSTAB_CHANCE) return;
    // Teleport the player behind the victim
    const vloc = victim.location;
    const dir = victim.getViewDirection ? victim.getViewDirection() : { x: 0, z: 0 };
    const behind = {
        x: vloc.x - dir.x * 2,
        y: vloc.y,
        z: vloc.z - dir.z * 2
    };
    try {
        player.dimension.spawnParticle('realms:arcane_step', player.location);
    } catch (e) { /* */ }
    player.teleport(behind);
    try {
        player.dimension.spawnParticle('realms:arcane_step', behind);
    } catch (e) { /* */ }
    player.runCommand(`effect @s speed 5 1 true`);
    player.playSound('mob.endermen.portal');
    player.sendMessage('§5⟳ Void Reaver: you slip through shadow!');
}

// ── Stormcaller Hammer — Lightning Hammer ──────────────────────────
function procStormcaller(player, victim) {
    const now = system.currentTick;
    const readyAt = stormCooldowns.get(player.id) || 0;
    if (now < readyAt) return;
    stormCooldowns.set(player.id, now + STORMCALLER_COOLDOWN_TICKS);

    const loc = victim.location;
    try { player.dimension.spawnParticle('realms:spear_lightning', loc); } catch (e) { /* */ }
    player.dimension.runCommand(
        `execute positioned ${loc.x.toFixed(1)} ${loc.y.toFixed(1)} ${loc.z.toFixed(1)} run summon lightning_bolt`
    );
    // Extra shockwave damage around the strike
    player.dimension.runCommand(
        `effect @e[r=4,family=monster] slowness 4 2 true`
    );
    player.playSound('ambient.weather.thunder');
    player.sendMessage('§b⚡ Stormcaller calls down the thunder!');
}
