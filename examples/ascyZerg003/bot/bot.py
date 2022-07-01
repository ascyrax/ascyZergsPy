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
        # self.minerals = Common.minerals
        # self.vespene = Common.vespene

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
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_DRONE.value):
                self.eggDronesCnt = self.eggDronesCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_OVERLORD.value):
                self.eggOverlordsCnt = self.eggOverlordsCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_ZERGLING.value):
                self.eggZerglingsCnt = self.eggZerglingsCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_ROACH.value):
                self.eggRoachesCnt = self.eggRoachesCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_HYDRALISK.value):
                self.eggHydralisksCnt = self.eggHydralisksCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_MUTALISK.value):
                self.eggMutalisksCnt = self.eggMutalisksCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.TRAIN_SWARMHOST.value):
                self.eggSwarmhostsCnt = self.eggSwarmhostsCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_INFESTOR.value):
                self.eggInfestorsCnt = self.eggInfestorsCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_CORRUPTOR.value):
                self.eggCorruptorsCnt = self.eggCorruptorsCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_ULTRALISK.value):
                self.eggUltralisksCnt = self.eggUltralisksCnt + 1
        for egg in self.eggs:
            if egg.orders[0].ability.id_exists(AbilityId.LARVATRAIN_VIPER.value):
                self.eggVipersCnt = self.eggVipersCnt + 1

    async def on_step(self, iteration):
        self.getValues()
        self.iteration = iteration

        if self.hatcheries.amount < 2:
            self.early_a()

        time.sleep(1 / 60)

    def early_a(self):

        if self.drones.amount + self.eggDronesCnt == 12:
            if self.minerals >= 50:
                self.larvas.random.train(UnitTypeId.DRONE)
        elif self.overlords.amount + self.eggOverlordsCnt == 1:
            if self.minerals >= 100:
                print("overlord started")
                self.larvas.random.train(UnitTypeId.OVERLORD)
        elif (
            self.drones.amount + self.eggDronesCnt == 13
            and self.overlords.amount + self.eggOverlordsCnt == 2
        ):
            if self.minerals >= 50:
                self.larvas.random.train(UnitTypeId.DRONE)
        elif self.drones.amount + self.eggDronesCnt <= 16:
            if self.overlords.amount + self.eggOverlordsCnt == 2:
                print(
                    "overlordsCnt: ",
                    self.overlords.amount,
                    " ::: eggOverlordsCnt: ",
                    self.eggOverlordsCnt,
                )
                if self.minerals >= 50:
                    self.larvas.random.train(UnitTypeId.DRONE)

    def printSth(self):
        4

    async def on_start(self):
        await super().on_start()
        print("Game started")
        # Do things here before the game starts
        self.client.game_step = 1
        self.getValues()

    async def on_end(self, game_result: Result):
        print("Game ended.")
        # Do things here after the game ends
