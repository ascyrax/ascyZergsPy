import random
from contextlib import suppress
from typing import Set
import time

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.unit import Unit
from sc2.units import Units
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2

from sc2.game_data import AbilityData
from sc2.game_state import Common


class ascyBot(BotAI):
    def getValues(self):
        self.larvas = self.units.of_type(UnitTypeId.LARVA)
        self.eggs = self.units.of_type(UnitTypeId.EGG)

        self.drones = self.units.of_type(UnitTypeId.DRONE)

        self.overlords = self.units.of_type(UnitTypeId.OVERLORD)
        self.overseers = self.units.of_type(UnitTypeId.OVERSEER)
        self.changelings = self.units.of_type(UnitTypeId.CHANGELING)

        self.queens = self.units.of_type(UnitTypeId.QUEEN)

        self.zergs = self.units.of_type(UnitTypeId.ZERGLING)
        self.banes = self.units.of_type(UnitTypeId.BANELING)

        self.roaches = self.units.of_type(UnitTypeId.ROACH)
        self.ravagers = self.units.of_type(UnitTypeId.RAVAGER)

        self.hydras = self.units.of_type(UnitTypeId.HYDRALISK)
        self.lurkers = self.units.of_type(UnitTypeId.LURKER)

        self.mutalisks = self.units.of_type(UnitTypeId.MUTALISK)

        self.corruptors = self.units.of_type(UnitTypeId.CORRUPTOR)
        self.broodlords = self.units.of_type(UnitTypeId.BROODLORD)
        self.broodlings = self.units.of_type(UnitTypeId.BROODLING)

        self.vipers = self.units.of_type(UnitTypeId.VIPER)

        self.infestors = self.units.of_type(UnitTypeId.INFESTOR)

        self.swarmhosts = self.units.of_type(UnitTypeId.SWARMHOSTMP)
        self.locusts = self.units.of_type(UnitTypeId.LOCUSTMP)

        self.ultralisks = self.units.of_type(UnitTypeId.ULTRALISK)

        self.nydusNets = self.units.of_type(UnitTypeId.NYDUSNETWORK)

        self.hatcheries = self.structures.of_type(UnitTypeId.HATCHERY)
        self.lairs = self.structures.of_type(UnitTypeId.LAIR)
        self.hives = self.structures.of_type(UnitTypeId.HIVE)

        self.extractors = self.structures.of_type(UnitTypeId.EXTRACTOR)

        self.spawningPools = self.structures.of_type(UnitTypeId.SPAWNINGPOOL)
        self.banelingNests = self.structures.of_type(UnitTypeId.BANELINGNEST)

        self.roachWarrens = self.structures.of_type(UnitTypeId.ROACHWARREN)

        self.spines = self.structures.of_type(UnitTypeId.SPINECRAWLER)
        self.spores = self.structures.of_type(UnitTypeId.SPORECRAWLER)
        self.creeps = self.structures.of_type(UnitTypeId.CREEPTUMOR)

        self.evolutionChambers = self.structures.of_type(UnitTypeId.EVOLUTIONCHAMBER)

        self.hydraliskDens = self.structures.of_type(UnitTypeId.HYDRALISKDEN)
        self.lurkerDens = self.structures.of_type(UnitTypeId.LURKERDEN)

        self.infestationPits = self.structures.of_type(UnitTypeId.INFESTATIONPIT)

        self.spires = self.structures.of_type(UnitTypeId.SPIRE)
        self.greaterSpires = self.structures.of_type(UnitTypeId.GREATERSPIRE)

        self.ultralisksCaverns = self.structures.of_type(UnitTypeId.ULTRALISKCAVERN)

        # eggs which are being morphed into some other unit
        self.eggDronesCnt = 0
        self.eggOverlordsCnt = 0
        self.eggZerglingsCnt = 0
        self.eggRoachesCnt = 0
        self.eggHydralisksCnt = 0
        self.eggMutalisksCnt = 0
        self.eggSwarmhostsCnt = 0
        self.eggInfestorsCnt = 0
        self.eggCorruptorsCnt = 0
        self.eggUltralisksCnt = 0
        self.eggVipersCnt = 0

        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_DRONE}):
                self.eggDronesCnt = self.eggDronesCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_OVERLORD}):
                self.eggOverlordsCnt = self.eggOverlordsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_ZERGLING}):
                self.eggZerglingsCnt = self.eggZerglingsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_ROACH}):
                self.eggRoachesCnt = self.eggRoachesCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_HYDRALISK}):
                self.eggHydralisksCnt = self.eggHydralisksCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_MUTALISK}):
                self.eggMutalisksCnt = self.eggMutalisksCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.TRAIN_SWARMHOST}):
                self.eggSwarmhostsCnt = self.eggSwarmhostsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_INFESTOR}):
                self.eggInfestorsCnt = self.eggInfestorsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_CORRUPTOR}):
                self.eggCorruptorsCnt = self.eggCorruptorsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_ULTRALISK}):
                self.eggUltralisksCnt = self.eggUltralisksCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability({AbilityId.LARVATRAIN_VIPER}):
                self.eggVipersCnt = self.eggVipersCnt + 1

        # self.minerals -> initialized by default
        # self.vespene -> initialized by default

    async def on_step(self, iteration):
        self.iteration = iteration
        self.getValues()

        if self.hatcheries.amount < 2:
            await self.early_a()
        elif self.roachWarrens.amount < 1:
            await self.early_b()
        # if self.hydraliskDens.amount < 1:
        #     await self.early_c()

        # await self.manageDrones()
        if self.supply_cap > 25:
            await self.manageOverlords()
        await self.chatJokes()

        # if self.iteration > 2400:
        #     time.sleep(1 / 200)

    async def early_b(self):
        # 18 -> spawning pool
        if self.drones.amount + self.eggDronesCnt < 18:
            await self.trainDrone()
        elif self.drones.amount == 18 and self.spawningPools.amount == 0:
            await self.buildSpawningPool()
        elif self.drones.amount + self.eggDronesCnt < 20:
            await self.trainDrone()
        # elif self.extractors.amount == 0:
        #     await self.buildExtractor(self.hatcheries[0].position)

        if self.spines.amount == 0:
            await self.buildSpine(self.hatcheries[0].position)
        # 20 -> extractor
        # spine crawler on natural
        # 15 zerg supply
        if self.supply_army < self.supply_cap:
            for larva in self.larvas:
                larva.train(UnitTypeId.ZERGLING)

        print(
            self.supply_army, self.supply_cap - self.supply_workers - self.supply_army
        )

        if (
            self.supply_army > 15
            and self.supply_cap - self.supply_workers - self.supply_army < 10
        ):
            for zerg in self.zergs:
                zerg.attack(self.enemy_start_locations[0])
        # firstZergPush
        # immediate roach warren

    async def manageOverlords(self):
        if self.supply_used >= self.supply_cap + self.eggOverlordsCnt * 8 - 8:
            await self.trainOverlord()

    async def buildSpawningPool(self):
        if (
            self.minerals >= 200
            and self.worker_en_route_to_build(UnitTypeId.SPAWNINGPOOL) == 0
        ):
            self.spawningPoolPos = await self.find_placement(
                UnitTypeId.SPAWNINGPOOL,
                near=self.hatcheries.ready.first.position,
                placement_step=8,
            )
            print(self.spawningPoolPos)
            self.temp = await self.can_place_single(
                building=UnitTypeId.SPAWNINGPOOL, position=self.spawningPoolPos
            )
            if self.temp:
                await self.build(UnitTypeId.SPAWNINGPOOL, near=self.spawningPoolPos)
                print(
                    self.iteration,
                    " : second hatchery built at position: ",
                    self.spawningPoolPos,
                )

    async def buildSpine(self, pos):
        if (
            self.spawningPools.ready.amount > 0
            and self.drones.amount > 0
            and self.can_afford(UnitTypeId.SPINECRAWLER)
            and self.worker_en_route_to_build(UnitTypeId.SPINECRAWLER) == 0
        ):
            self.buildPos = await self.find_placement(UnitTypeId.SPINECRAWLER, near=pos)
            self.builderDrone = self.select_build_worker(self.buildPos)
            if await self.can_place_single(UnitTypeId.SPINECRAWLER, self.buildPos):
                self.builderDrone.build(UnitTypeId.SPINECRAWLER, self.buildPos)
                print(
                    self.iteration,
                    ": defensive spine crawler built at location: ",
                    pos,
                )

    async def buildExtractor(self, pos):
        if (
            self.drones.amount > 0
            and self.can_afford(UnitTypeId.EXTRACTOR)
            and self.worker_en_route_to_build(UnitTypeId.EXTRACTOR) == 0
        ):
            self.buildPos = await self.find_placement(UnitTypeId.EXTRACTOR, near=pos)
            self.builderDrone = self.select_build_worker(self.buildPos)
            if await self.can_place_single(UnitTypeId.EXTRACTOR, self.buildPos):
                self.builderDrone.build(UnitTypeId.EXTRACTOR, self.buildPos)
                print(
                    self.iteration,
                    " : Building Extractor no - ",
                    self.extractors.amount + 1,
                    " ",
                )

    # async def early_c(self):
    # two base saturation
    # 50 roach supply
    # firstRoachPush
    # immediateHydraDen

    async def trainDrone(self):
        if (
            self.minerals >= 50
            and self.larvas.amount > 0
            and self.supply_used < self.supply_cap
        ):
            self.larvas.random.train(UnitTypeId.DRONE)
            print(
                self.iteration,
                " : Training Drone no - ",
                self.drones.amount + self.eggDronesCnt + 1,
                " ",
            )

    async def trainOverlord(self):
        if self.minerals >= 100 and self.larvas.amount > 0:
            self.larvas.random.train(UnitTypeId.OVERLORD)
            print(
                self.iteration,
                " : Training Overlord no - ",
                self.overlords.amount + self.eggOverlordsCnt + 1,
                " ",
            )

    async def expandToNatural(self):
        if self.minerals >= 180:
            # send a drone to natural for building the hatchery
            if not self.naturalDroneSent:
                self.naturalDroneSent = True
                print("sent a drone to natural for building the 2nd hatchery")
                self.expanderDrones = self.units.of_type(UnitTypeId.DRONE)
                self.expanderDrones[0].smart(await self.get_next_expansion())
            elif (
                self.naturalDroneSent
                and self.minerals >= 300
                and self.hatcheries.amount < 2
            ):
                print("built a natural.")
                await self.expand_now()

    async def early_a(self):
        if not self.overlordScout1Sent:
            self.overlordScout1 = self.units.of_type({UnitTypeId.OVERLORD})
            self.overlordScout1[0].smart(self.enemy_start_locations[0])
            self.overlordScout1Sent = True
            print("overlordScout1Sent to enemy base.")
        if self.drones.amount + self.eggDronesCnt == 12:
            await self.trainDrone()
        elif self.overlords.amount + self.eggOverlordsCnt == 1:
            await self.trainOverlord()
        elif (
            self.drones.amount + self.eggDronesCnt == 13
            and self.overlords.amount + self.eggOverlordsCnt == 2
        ):
            await self.trainDrone()
        elif self.drones.amount + self.eggDronesCnt < 16:
            if self.overlords.amount + self.eggOverlordsCnt == 2:
                await self.trainDrone()
        if self.drones.amount + self.eggDronesCnt >= 16:
            await self.expandToNatural()

    async def chatJokes(self):
        if self.iteration == 1000:
            await self.chat_send("Q. How did the programmer die in the shower?")
        elif self.iteration == 1300:
            await self.chat_send(
                "A. He read the shampoo bottle instructions: Lather. Rinse. Repeat."
            )
        elif self.iteration == 3000:
            await self.chat_send('Man: "Make me a sandwich"')
        elif self.iteration == 3200:
            await self.chat_send('Woman: "No"')
        elif self.iteration == 3400:
            await self.chat_send('Man: "sudo Make me a sandwich"')
        elif self.iteration == 3600:
            await self.chat_send('Woman: "Okay"')
        elif self.iteration == 10000:
            await self.chat_send(
                "There are 10 kinds of people in this world: those who know binary, those who don’t, and those who didn't expect this joke to be in ternary."
            )

    async def on_start(self):
        await super().on_start()
        print()
        print()
        print("GAME STARTED")
        print()
        print()
        # Do things here before the game starts
        self.client.game_step = 1
        self.getValues()
        await self.chat_send("gl hf", False)
        self.overlordScout1Sent = False
        self.naturalDroneSent = False
        # self.spawnPool

    async def on_end(self, game_result: Result):
        await self.chat_send("gg wp")
        await self.chat_send("byeeeeeee. cya again.")
        print()
        print()
        print("GAME ENDED.")
        print()
        print()
        # Do things here after the game ends
