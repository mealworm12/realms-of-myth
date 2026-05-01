/**
 * Realms of Myth - Main Entry Point
 * Fantasy Minecraft Add-On for Education & Bedrock Edition
 */

import { world, system } from '@minecraft/server';

console.log('[Realms of Myth] Initializing...');

// Subscribe to world initialization
world.afterEvents.worldInitialize.subscribe((event) => {
    console.log('[Realms of Myth] World initialized');
});

// Subscribe to player spawn - apply race traits, restore classes
world.afterEvents.playerSpawn.subscribe((event) => {
    const player = event.player;
    console.log(`[Realms of Myth] Player spawned: ${player.name}`);
    // TODO: Apply race traits
    // TODO: Restore class abilities
});

// Tick loop for ability cooldowns and dragon AI
system.runInterval(() => {
    // TODO: Process ability cooldowns
    // TODO: Run dragon boss AI
}, 20); // Run every second (20 ticks)

console.log('[Realms of Myth] Ready!');
