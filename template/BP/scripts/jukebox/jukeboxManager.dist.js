import { EquipmentSlot, EntityEquippableComponent, GameMode, system, ItemStack, BlockInventoryComponent } from '@minecraft/server';
import { musicDiscs } from '../musicDisc/musicDiscs';
import { randomNum, randomWholeNum } from '../math/randomNumbers';

var JukeboxStates;
(function (JukeboxStates) {
    JukeboxStates["Playing_Disc"] = "personal_music_compilation:playing_disc";
    JukeboxStates["Vanilla_Disc_1"] = "personal_music_compilation:vanilla_disc_1";
    JukeboxStates["Vanilla_Disc_2"] = "personal_music_compilation:vanilla_disc_2";
{{CUSTOM_DISC_STATES}}
})(JukeboxStates || (JukeboxStates = {}));

const states = [
    JukeboxStates.Vanilla_Disc_1,
    JukeboxStates.Vanilla_Disc_2{{CUSTOM_DISC_STATES_ARRAY}}
];

var HopperLocations;
(function (HopperLocations) {
    HopperLocations["Up"] = "up";
    HopperLocations["North"] = "north";
    HopperLocations["South"] = "south";
    HopperLocations["East"] = "east";
    HopperLocations["West"] = "west";
})(HopperLocations || (HopperLocations = {}));

function debug(message){
	console.log(`[DEBUG] ${message}`);
}

const playingJukeboxes = {};

export class jukeboxManager {
    static jukeboxID = 'personal_music_compilation:jukebox';
    
    static tick(block, dimension) {
        const center = block.center();
        const players = this.getPlayersInRadius(center, dimension, 40);
        if (!players[0])
            return;
        const isPlayingDisc = block.permutation.getState(JukeboxStates.Playing_Disc);
        if (isPlayingDisc) {
            if (!playingJukeboxes[`${block.dimension.id}.${JSON.stringify(block.location)}`]) {
                block.setPermutation(block.permutation.withState(JukeboxStates.Playing_Disc, false));
                const discData = this.getPlayingDisc(block.permutation);
                if (discData && discData.data && discData.data.sound) {
                    this.stopSoundInRadius(discData.data.sound.id, block.location, block.dimension, 100);
                }
            }
            return;
        }
        const discData = this.getPlayingDisc(block.permutation);
        if (discData) {
            const hopper = this.getOutputHopper(block);
            if (!hopper)
                return;
            const inv = this.getInventory(hopper);
            if (!inv)
                return;
            if (!inv.container)
                return;
            if (inv.container.emptySlotsCount <= 0)
                return;
            if (discData.id && typeof discData.id === 'string') {
                const item = new ItemStack(discData.id, 1);
                inv.container.addItem(item);
            }
            this.clearDisc(block);
        }
        else {
            const hoppers = this.getConnectedHoppers(block, dimension);
            if (!hoppers[0])
                return;
            let found = false;
            for (const hopper of hoppers) {
                if (found)
                    return;
                const inv = this.getInventory(hopper);
                if (!inv)
                    continue;
                if (!inv.container)
                    continue;
                for (let i = 0; i < inv.container.size; i++) {
                    if (found)
                        return;
                    const item = inv.container.getItem(i);
                    if (!item)
                        continue;
                    const disc = musicDiscs[item.typeId];
                    if (!disc)
                        continue;
                    this.playDisc(block, dimension, disc, item.typeId);
                    inv.container.setItem(i, undefined);
                    found = true;
                }
            }
        }
    }
    
    static getInventory(block) {
        const inv = block.getComponent(BlockInventoryComponent.componentId);
        return inv;
    }
    
    static interactWithJukebox(block, player) {
        const dimension = block.dimension;
        const disc = this.getPlayingDisc(block.permutation);
        const center = block.center();
        
        if (!disc) {
            const mainHand = player.getComponent(EntityEquippableComponent.componentId).getEquipmentSlot(EquipmentSlot.Mainhand);
            if (!mainHand){
                debug('interactWithJukebox: !disc && !mainHand')
                return;
            }
            const item = mainHand.getItem();
            if (!item){
                debug('interactWithJukebox: !disc && !item')
                return;
            }
            const discData = musicDiscs[item.typeId];
            if (!discData){
                debug('interactWithJukebox: !disc && !discData')
                return;
            }
            if (player.getGameMode() != GameMode.creative)
                mainHand.setItem();
            this.playDisc(block, dimension, discData, item.typeId);
        } else {
            if (disc.data && disc.data.sound) {
                this.stopSoundInRadius(disc.data.sound.id, center, dimension, 100);
            }
            if (disc.id && typeof disc.id === 'string') {
                const item = new ItemStack(disc.id, 1);
                const itemEntity = this.spawnItemAnywhere(item, { x: center.x, y: center.y + 0.5, z: center.z }, block.dimension);
                itemEntity.applyImpulse({ x: randomNum(-0.2, 0.2), y: 0.2, z: randomNum(-0.2, 0.2) });
            }else{
                debug('interactWithJukebox: disc id not string')
                debug(disc.id)
            }
            this.clearDisc(block);
            delete playingJukeboxes[`${block.dimension.id}.${JSON.stringify(block.location)}`];
        }
    }
    
    static getConnectedHoppers(mainBlock, dimension) {
        const blockLoc = mainBlock.location;
        const hoppers = [];
        const directions = [HopperLocations.Up, HopperLocations.North, HopperLocations.South, HopperLocations.East, HopperLocations.West];
        
        for (const dir of directions) {
            let loc = undefined;
            switch (dir) {
                case HopperLocations.Up:
                    loc = { x: 0, y: 1, z: 0 };
                    break;
                case HopperLocations.North:
                    loc = { x: 0, y: 0, z: -1 };
                    break;
                case HopperLocations.South:
                    loc = { x: 0, y: 0, z: 1 };
                    break;
                case HopperLocations.East:
                    loc = { x: 1, y: 0, z: 0 };
                    break;
                case HopperLocations.West:
                    loc = { x: -1, y: 0, z: 0 };
                    break;
            }
            
            let block = undefined;
            if (loc == undefined)
                continue;
            try {
                block = dimension.getBlock({ x: blockLoc.x + loc.x, y: blockLoc.y + loc.y, z: blockLoc.z + loc.z });
            }
            catch { }
            if (!block)
                continue;
            if (block.typeId != "minecraft:hopper")
                continue;
            
            let connectedValue = undefined;
            const facing = block.permutation.getState("facing_direction");
            switch (facing) {
                case 0:
                    connectedValue = HopperLocations.Up;
                    break;
                case 3:
                    connectedValue = HopperLocations.North;
                    break;
                case 2:
                    connectedValue = HopperLocations.South;
                    break;
                case 4:
                    connectedValue = HopperLocations.East;
                    break;
                case 5:
                    connectedValue = HopperLocations.West;
                    break;
            }
            if (connectedValue == undefined)
                continue;
            if (connectedValue != dir)
                continue;
            hoppers.push(block);
        }
        return hoppers;
    }
    
    static getOutputHopper(block) {
        let hopper = undefined;
        try {
            hopper = block.below(1);
        }
        catch { }
        if (!hopper)
            return undefined;
        if (hopper.typeId != "minecraft:hopper")
            return undefined;
        return hopper;
    }
    
    static playDisc(block, dimension, discData, discName) {
        debug(`playDisc called for: ${discName}`);
        const center = block.center();
        const location = block.location;
        playingJukeboxes[`${block.dimension.id}.${JSON.stringify(block.location)}`] = true;
        
        dimension.playSound(discData.sound.id, center, { volume: discData.sound.volume });
        this.setDisc(block, discName);
        this.getPlayersInRadius(center, dimension, 20).forEach((player) => {
            player.onScreenDisplay.setActionBar(`§dNow Playing: ${discData.musicName} - ${discData.artist}`);
        });
        this.playNotes(block.location, dimension, discName);
        
        let canceled = false;
        let tick = 0;
        const interval = system.runInterval(() => {
            tick++;
            if ((tick * 10) > discData.sound.tickLength) {
                system.clearRun(interval);
                canceled = true;
                return;
            }
            if (canceled)
                return;
            const newBlock = dimension.getBlock(location);
            if (!newBlock)
                return;
            if (newBlock.typeId != this.jukeboxID)
                return;
            const newDiscData = this.getPlayingDisc(newBlock.permutation);
            if (!newDiscData){
                debug('playDisc runTimeout: !newDiscData');
                return;
            }
            if (newDiscData.id != discName){
                debug('playDisc runTimeout: newDiscData.id != discName');
                return;
            }
            newBlock.setPermutation(newBlock.permutation.withState(JukeboxStates.Playing_Disc, false));
            delete playingJukeboxes[`${block.dimension.id}.${JSON.stringify(block.location)}`];
            if (newDiscData.data && newDiscData.data.sound) {
                this.stopSoundInRadius(newDiscData.data.sound.id, center, dimension, 100);
            }
        }, discData.sound.tickLength);
    }
    
    static breakJukebox(data) {
        debug(`breakJukebox`);
        const { block, dimension, player, destroyedBlockPermutation } = data;
        const playingDisc = this.getPlayingDisc(data.destroyedBlockPermutation);
        if (!playingDisc){
            debug('breakJukebox: !playingDisc');
            return;
        }
        const center = block.center();
        if (playingDisc.id && typeof playingDisc.id === 'string') {
            const item = new ItemStack(playingDisc.id, 1);
            const itemEntity = this.spawnItemAnywhere(item, { x: center.x, y: center.y, z: center.z }, block.dimension);
            itemEntity.applyImpulse({ x: randomNum(-0.2, 0.2), y: 0.2, z: randomNum(-0.2, 0.2) });
        }
        if (playingDisc.data && playingDisc.data.sound) {
            this.stopSoundInRadius(playingDisc.data.sound.id, center, block.dimension, 100);
        }
    }
    
    static stopSoundInRadius(soundID, location, dimension, radius) {
        debug(`stopSoundInRadius`);
        const players = this.getPlayersInRadius(location, dimension, 100);
        for (const player of players) {
            if (player.isValid())
                player.runCommand(`stopsound @s  ${soundID}`);
        }
    }
    

    
    static getPlayingDisc(permutation) {
        let disc = undefined;
        for (const state of states) {
            const data = permutation.getState(state);
            if (data != "none") {
                disc = { id: data, data: musicDiscs[data] };
                break;
            }
        }
        return disc;
    }
    
    static getPlayersInRadius(location, dimension, radius) {
        let players = [];
        players = dimension.getEntities({ location: location, maxDistance: radius, type: "minecraft:player" });
        return players;
    }
    
    static spawnItemAnywhere(item, location, dimension) {
        const itemEntity = dimension.spawnItem(item, { x: location.x, y: 100, z: location.z });
        itemEntity.teleport(location);
        return itemEntity;
    }
    
    static clearDisc(block) {
        debug(`clearDisc for ${block.typeId}[${block.dimension.id}.${JSON.stringify(block.location)}] block`);
        block.setPermutation(block.permutation.withState("personal_music_compilation:playing_disc", false));
        for (const state of states) {
            block.setPermutation(block.permutation.withState(state, "none"));
        }
    }
    
    static setDisc(block, id) {
        debug(`setDisc: ${id}`);
        for (const state of states) {
            block.setPermutation(block.permutation.withState("personal_music_compilation:playing_disc", true));
            try {
                block.setPermutation(block.permutation.withState(state, id));
            }
            catch { }
        }
    }
    
    static playNotes(location, dimension, playingID) {
        function tick() {
            const players = jukeboxManager.getPlayersInRadius(location, dimension, 30);
            if (players[0] != undefined) {
                let block = undefined;
                try {
                    block = dimension.getBlock(location);
                }
                catch { }
                if (block == undefined)
                    return;
                const isPlayingDisc = block.permutation.getState(JukeboxStates.Playing_Disc);
                if (!isPlayingDisc)
                    return;
                if (block.typeId != jukeboxManager.jukeboxID)
                    return;
                const playingDisc = jukeboxManager.getPlayingDisc(block.permutation);
                if (!playingDisc)
                    return;
                if (playingDisc.id != playingID)
                    return;
                const center = block.center();
                try {
                    dimension.spawnParticle("minecraft:note_particle", { x: center.x, y: center.y + 0.6, z: center.z });
                }
                catch { }
            }
            let randomTick = randomWholeNum(10, 20);
            system.runTimeout(() => {
                tick();
            }, randomTick);
        }
        tick();
    }
} 