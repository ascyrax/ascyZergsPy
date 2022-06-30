import random
from contextlib import suppress
from typing import Set

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.unit import Unit
from sc2.units import Units
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2


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

        # self.swarmhosts = self.units.of_type(UnitTypeId.SWARMHOSTMP)
        # self.locusts = self.units.of_type(UnitTypeId.LOCUSTMP)

        self.ultralisks = self.units.of_type(UnitTypeId.ULTRALISK)

        self.nydusNets = self.units.of_type(UnitTypeId.NYDUSNETWORK)

        self.hatcheries = self.units.of_type(UnitTypeId.HATCHERY)
        self.lairs = self.units.of_type(UnitTypeId.LAIR)
        self.hives = self.units.of_type(UnitTypeId.HIVE)

        self.extractors = self.units.of_type(UnitTypeId.EXTRACTOR)

        self.spawnPools = self.units.of_type(UnitTypeId.SPAWNINGPOOL)
        self.baneNests = self.units.of_type(UnitTypeId.BANELINGNEST)

        self.roachWarrens = self.units.of_type(UnitTypeId.ROACHWARREN)

        self.spines = self.units.of_type(UnitTypeId.SPINECRAWLER)
        self.spores = self.units.of_type(UnitTypeId.SPORECRAWLER)
        self.creeps = self.units.of_type(UnitTypeId.CREEPTUMOR)

        self.evoChambers = self.units.of_type(UnitTypeId.EVOLUTIONCHAMBER)

        self.hydraDens = self.units.of_type(UnitTypeId.HYDRALISKDEN)
        self.lurkerDens = self.units.of_type(UnitTypeId.LURKERDEN)

        self.infestPits = self.units.of_type(UnitTypeId.INFESTATIONPIT)

        self.spires = self.units.of_type(UnitTypeId.SPIRE)
        self.greaterSpires = self.units.of_type(UnitTypeId.GREATERSPIRE)

        self.ultraCaverns = self.units.of_type(UnitTypeId.ULTRALISKCAVERN)

    async def on_step(self, iteration):
        self.getValues()

        if self.hatcheries.amount < 2:
            self.early_a()

    async def early_a(self):
        print(self.drones.amount)
        if self.drones.amount == 12:
            self.larvas.random.train(UnitTypeId.DRONE)

    async def on_start(self):
        await super().on_start()
        print("Game started")
        # Do things here before the game starts
        self.client.game_step = 1
        # await self.client.debug_show_map()
        self.getValues()
        print("droneCnt ON_START: ", self.drones.amount)

    async def on_end(self, game_result: Result):
        print("Game ended.")
        # Do things here after the game ends
