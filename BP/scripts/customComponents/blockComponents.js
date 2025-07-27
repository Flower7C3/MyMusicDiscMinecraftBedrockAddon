import { world } from '@minecraft/server';
import { jukeboxManager } from '../jukebox/jukeboxManager';
const blockComponents = [
    {
        id: "my_music_disc:jukebox",
        data: {
            onPlayerInteract: (data) => {
                if (!data.player)
                    return;
                jukeboxManager.interactWithJukebox(data.block, data.player);
            },
            onPlayerDestroy: (data) => {
                jukeboxManager.breakJukebox(data);
            },
            onTick: (data) => {
                const { block, dimension } = data;
                jukeboxManager.tick(block, dimension);
            }
        }
    }
];
world.beforeEvents.worldInitialize.subscribe((data) => {
    console.warn("[DEBUG] Registering custom components...");
    for (const comp of blockComponents) {
        console.warn(`[DEBUG] Registering component: ${comp.id}`);
        data.blockComponentRegistry.registerCustomComponent(comp.id, comp.data);
    }
    console.warn("[DEBUG] Custom components registered successfully");
});
