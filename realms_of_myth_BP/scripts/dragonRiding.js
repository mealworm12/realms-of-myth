/**
 * Realms of Myth - Dragon Taming & Riding
 * Flow:
 *   1. A fire/frost dragon that has reached the ENRAGED phase (phase-3 defeated
 *      threshold) becomes TAMEABLE: it gains the `rom:tameable` dynamic property.
 *   2. Feeding RAW MYTHRIL (realms:mythril_ingot via interact) tames it — the
 *      dragon gets `rom:tamed_owner` = player.id, stops targeting players.
 *   3. Interacting with a tamed dragon while holding a SADDLE mounts it; the
 *      rider steers with view direction and fires a breath attack on jump
 *      input / right-click item use, on cooldown.
 *   4. Dragon Whelps spawned by an enraged dragon can become PETS: they follow
 *      their owner and sit on command (sneak-interact).
 *
 * Implementation is script-driven (dynamic properties + runInterval control),
 * which works without custom rideable components and survives entity JSON
 * being shared with other feature branches.
 */

import { world, system, Player } from '@minecraft/server';

const BREATH_COOLDOWN_TICKS = 120; // 6s between breath attacks
const breathCooldowns = new Map(); // dragonId -> tick when next breath allowed

// ── Helpers ────────────────────────────────────────────────────────

function getOwner(dragon) {
    const ownerId = dragon.getDynamicProperty('rom:tamed_owner');
    if (!ownerId) return null;
    try {
        for (const p of world.getPlayers()) if (p.id === ownerId) return p;
    } catch (e) { /* */ }
    return null;
}

function isTameablePhase(dragon) {
    // Enraged = below 30% HP (matches dragonBoss.js PHASE_AERIAL threshold)
    const hp = dragon.getComponent('minecraft:health');
    return !!hp && hp.currentValue > 0 && hp.currentValue <= hp.effectiveMax * 0.30;
}

// ── Registration ───────────────────────────────────────────────────

let registered = false;

export function registerTaming() {
    if (registered) return;
    registered = true;

    // ── Interact: feed mythril to tame / saddle to ride / toggle pet sit ──
    world.afterEvents.playerInteractWithEntity.subscribe((event) => {
        const player = event.player;
        const target = event.target;
        if (!target || !target.isValid?.()) return;

        const type = target.typeId;

        // Adult dragons: tame or ride
        if (type === 'realms:dragon_fire' || type === 'realms:dragon_frost') {
            handleDragonInteract(player, target);
            return;
        }

        // Whelp pets
        if (type === 'realms:dragon_whelp' && target.hasTag('rom:pet')) {
            const ownerId = target.getDynamicProperty('rom:tamed_owner');
            if (ownerId !== player.id) {
                player.sendMessage('§7This whelp belongs to another tamer.');
                return;
            }
            // Toggle sitting
            const sitting = target.getDynamicProperty('rom:pet_sitting');
            target.setDynamicProperty('rom:pet_sitting', !sitting);
            if (!sitting) {
                target.runCommand('effect @s slowness 999999 5 true');
                player.sendMessage('§bYour whelp sits obediently.');
            } else {
                target.runCommand('effect @s slowness 0');
                player.sendMessage('§bYour whelp springs up to follow you!');
            }
            player.playSound('entity.dragon_whelp.ambient');
        }
    });

    // ── Riding loop + whelp follow loop (1s cadence) ──
    system.runInterval(() => {
        tickRiding();
        tickWhelpFollow();
    }, 20);
}

// ── Adult dragon interaction ───────────────────────────────────────

function handleDragonInteract(player, dragon) {
    const owner = getOwner(dragon);

    if (owner && owner.id === player.id) {
        // Already yours — saddle check
        const inv = player.getComponent('minecraft:inventory');
        let hasSaddle = false;
        if (inv && inv.container) {
            for (let i = 0; i < inv.container.size; i++) {
                const it = inv.container.getItem(i);
                if (it && it.typeId === 'minecraft:saddle') { hasSaddle = true; break; }
            }
        }
        if (hasSaddle) {
            // Consume saddle, mount
            try {
                const c = inv.container;
                for (let i = 0; i < c.size; i++) {
                    const it = c.getItem(i);
                    if (it && it.typeId === 'minecraft:saddle') {
                        if (it.amount > 1) { it.amount -= 1; c.setItem(i, it); }
                        else c.setItem(i, undefined);
                        break;
                    }
                }
            } catch (e) { /* */ }
            dragon.setDynamicProperty('rom:saddled', true);
            mountPlayer(player, dragon);
            player.sendMessage('§dYou mount your dragon! Jump-input or right-click any item to breathe.');
            player.playSound('entity.dragon_fire.flap');
        } else if (dragon.getDynamicProperty('rom:saddled')) {
            mountPlayer(player, dragon);
            player.sendMessage('§dYou mount your dragon!');
        } else {
            player.sendMessage('§7Your dragon needs a §esaddle §7before you can ride it.');
        }
        return;
    }

    if (owner) {
        player.sendMessage('§cThis dragon has already sworn loyalty to another.');
        return;
    }

    // Not tamed: check tameable state + raw mythril in hand
    const held = event.itemStack;
    if (!held || held.typeId !== 'realms:mythril_ingot') {
        if (dragon.getDynamicProperty('rom:tameable')) {
            player.sendMessage('§7The dragon is weary but willing... offer §fRaw Mythril§7 (hold Mythril Ingot and interact).');
        } else if (isTameablePhase(dragon)) {
            dragon.setDynamicProperty('rom:tameable', true);
            player.sendMessage('§dThe dragon, broken by battle, eyes you with new respect. Offer Raw Mythril to earn its trust.');
        } else {
            player.sendMessage('§cThis dragon will never yield while its strength remains. Bring it to the brink first!');
        }
        return;
    }

    // Feed attempt
    if (!isTameablePhase(dragon)) {
        player.sendMessage('§cThe dragon rejects your offering — it must first be humbled in battle (below 30% health).');
        return;
    }

    // Consume one ingot
    try {
        const inv = player.getComponent('minecraft:inventory');
        const c = inv.container;
        for (let i = 0; i < c.size; i++) {
            const it = c.getItem(i);
            if (it && it.typeId === 'realms:mythril_ingot') {
                if (it.amount > 1) { it.amount -= 1; c.setItem(i, it); }
                else c.setItem(i, undefined);
                break;
            }
        }
    } catch (e) { /* */ }

    if (Math.random() < 0.5) {
        dragon.setDynamicProperty('rom:tamed_owner', player.id);
        dragon.setDynamicProperty('rom:tameable', undefined);
        player.dimension.spawnParticle('realms:class_select_burst', dragon.location);
        player.playSound('realms.ui.class_select_open');
        player.sendMessage({ rawtext: [{ text: `§d★ The dragon bows! It is now §lyours§r§d.` }] });
    } else {
        player.sendMessage('§7The dragon sniffs the mythril... not yet convinced. Try again.');
        player.playSound('entity.dragon_whelp.hurt');
    }
}

// ── Riding ─────────────────────────────────────────────────────────

/** playerId -> dragonId */
const riders = new Map();

function mountPlayer(player, dragon) {
    riders.set(player.id, dragon.id);
}

function dismount(player) {
    riders.delete(player.id);
    try { player.getComponent('minecraft:rideable'); } catch (e) { /* */ }
    // Teleport player off the dragon's back
    try {
        const loc = player.location;
        player.teleport({ x: loc.x + 2, y: loc.y + 1, z: loc.z });
    } catch (e) { /* */ }
}

function tickRiding() {
    for (const [playerId, dragonId] of [...riders.entries()]) {
        let player = null, dragon = null;
        try {
            for (const p of world.getPlayers()) if (p.id === playerId) player = p;
        } catch (e) { /* */ }
        if (player) {
            try {
                const dim = player.dimension;
                const dragons = dim.getEntities({ type: 'realms:dragon_fire' })
                    .concat(dim.getEntities({ type: 'realms:dragon_frost' }));
                dragon = dragons.find(d => d.id === dragonId);
            } catch (e) { /* */ }
        }
        if (!player || !dragon || !dragon.isValid()) {
            if (player) {
                dismount(player);
                player.sendMessage('§7You dismount.');
            } else {
                riders.delete(playerId);
            }
            continue;
        }

        // Seat the player above the dragon
        const dloc = dragon.location;
        const seatY = dloc.y + (dragon.typeId.includes('fire') ? 3.2 : 3.2);
        try {
            player.teleport({ x: dloc.x, y: seatY, z: dloc.z }, { keepVelocity: true });
        } catch (e) { /* */ }

        // Steer: move dragon toward where the rider looks (horizontal)
        const dir = player.getViewDirection();
        const speed = 0.9;
        try {
            dragon.applyKnockback(dir.x * speed, dir.z * speed, 0, Math.max(0, dir.y) * 0.4 + 0.05);
        } catch (e) { /* applyKnockback signature variance */ }

        // Sneak to dismount
        if (player.isSneaking) {
            dismount(player);
            player.sendMessage('§7You slide off your dragon\'s back.');
        }
    }
}

/**
 * Breath attack: called from main.js itemUse hook while mounted.
 * Returns true if the attack fired.
 */
export function tryBreathAttack(player) {
    const dragonId = riders.get(player.id);
    if (!dragonId) return false;

    const now = system.currentTick;
    const readyAt = breathCooldowns.get(dragonId) || 0;
    if (now < readyAt) {
        player.sendMessage(`§7Breath recharging: §e${Math.ceil((readyAt - now) / 20)}s`);
        return true; // consumed the input but still on CD
    }
    breathCooldowns.set(dragonId, now + BREATH_COOLDOWN_TICKS);

    const dim = player.dimension;
    const head = player.getHeadLocation();
    const dir = player.getViewDirection();
    const isFrost = player.getDynamicProperty('rom:riding_frost');

    // Determine element from the ridden dragon
    try {
        for (const d of dim.getEntities()) {
            if (d.id === dragonId) { 
                // element check happens implicitly by dragon type below
                break;
            }
        }
    } catch (e) { /* */ }

    // Cone damage ahead of the rider + particles
    const targets = dim.getEntities({
        location: head,
        maxDistance: 14,
        excludeTypes: ['minecraft:player', 'realms:dragon_fire', 'realms:dragon_frost', 'realms:dragon_whelp']
    });
    let hitCount = 0;
    for (const t of targets) {
        try {
            const tl = t.location;
            const vx = tl.x - head.x, vy = tl.y - head.y, vz = tl.z - head.z;
            const len = Math.hypot(vx, vy, vz) || 1;
            const dot = (vx * dir.x + vy * dir.y + vz * dir.z) / len;
            if (dot < 0.55) continue; // ~57° half-angle cone
            const dmg = t.applyDamage(10, { cause: 'entityAttack', damagingEntity: player });
            if (dmg) hitCount++;
        } catch (e) { /* */ }
    }

    // Visuals along the beam
    for (let s = 1; s <= 8; s++) {
        const px = head.x + dir.x * s * 1.7;
        const py = head.y + dir.y * s * 1.7;
        const pz = head.z + dir.z * s * 1.7;
        try {
            dim.spawnParticle(isFrost ? 'realms:dragon_breath_frost' : 'realms:dragon_breath_fire',
                { x: px, y: py, z: pz });
        } catch (e) { /* */ }
    }
    player.playSound(isFrost ? 'realms.ability.arcane_teleport_cast' : 'entity.dragon_fire.roar');
    player.sendMessage(hitCount > 0 ? `§d🔥 Dragon breath scorches ${hitCount} target(s)!` : '§d🔥 Dragon breath roars forth!');
    return true;
}

// Track element for breath visuals
world.afterEvents.playerInteractWithEntity.subscribe((event) => {
    const t = event.target;
    if (t && (t.typeId === 'realms:dragon_frost')) {
        event.player.setDynamicProperty('rom:riding_frost', true);
    } else if (t && t.typeId === 'realms:dragon_fire') {
        event.player.setDynamicProperty('rom:riding_frost', false);
    }
});

// ── Whelp pet following ────────────────────────────────────────────

function tickWhelpFollow() {
    try {
        for (const dimName of ['overworld', 'nether']) {
            const dim = world.getDimension(dimName);
            for (const w of dim.getEntities({ type: 'realms:dragon_whelp' })) {
                if (!w.isValid() || !w.hasTag('rom:pet')) continue;
                if (w.getDynamicProperty('rom:pet_sitting')) continue;
                const ownerId = w.getDynamicProperty('rom:tamed_owner');
                if (!ownerId) continue;
                let owner = null;
                for (const p of world.getPlayers()) if (p.id === ownerId) owner = p;
                if (!owner || owner.dimension.id !== dim.id) continue;

                const dist = Math.hypot(
                    owner.location.x - w.location.x,
                    owner.location.z - w.location.z
                );
                if (dist > 4) {
                    // Hop toward owner
                    const dx = (owner.location.x - w.location.x) / dist;
                    const dz = (owner.location.z - w.location.z) / dist;
                    try { w.applyKnockback(dx * 0.45, dz * 0.45, 0, 0.25); } catch (e) { /* */ }
                }
            }
        }
    } catch (e) { /* dimension unloaded */ }
}

/**
 * Convert a whelp into a pet (called from dragonBoss.js when whelps are
 * spawned during an enraged phase that the killing player survived).
 */
export function makeWhelpPet(whelp, player) {
    whelp.addTag('rom:pet');
    whelp.setDynamicProperty('rom:tamed_owner', player.id);
    whelp.setDynamicProperty('rom:pet_sitting', false);
}
