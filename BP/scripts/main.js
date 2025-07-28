import { system, world, ItemStack } from '@minecraft/server';
import './customComponents/blockComponents';
if (world.getDynamicProperty("jukeboxes") == undefined)
    world.setDynamicProperty("jukeboxes", JSON.stringify({}));
system.runInterval(() => {
    for (const player of world.getAllPlayers()) {
        const inv = player.getComponent("inventory");
        if (!inv)
            continue;
        if (!inv.container)
            continue;
        for (let i = 0; i < inv.container.size; i++) {
            const item = inv.container.getItem(i);
            if (!item)
                continue;
            if (item.typeId != 'minecraft:jukebox')
                continue;
            const newItem = new ItemStack("personal_music_compilation:jukebox", item.amount);
            inv.container.setItem(i, newItem);
        }
    }
}, 5);
