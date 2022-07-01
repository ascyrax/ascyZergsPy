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
    # def getValues(self):
    # self.minerals = Common.minerals
    # self.vespene = Common.vespene

    async def on_step(self, iteration):
        # self.getValues()
        self.iteration = iteration
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
            if egg.is_using_ability([AbilityId.LARVATRAIN_DRONE]):
                self.eggDronesCnt = self.eggDronesCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_OVERLORD]):
                self.eggOverlordsCnt = self.eggOverlordsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_ZERGLING]):
                self.eggZerglingsCnt = self.eggZerglingsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_ROACH]):
                self.eggRoachesCnt = self.eggRoachesCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_HYDRALISK]):
                self.eggHydralisksCnt = self.eggHydralisksCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_MUTALISK]):
                self.eggMutalisksCnt = self.eggMutalisksCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.TRAIN_SWARMHOST]):
                self.eggSwarmhostsCnt = self.eggSwarmhostsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_INFESTOR]):
                self.eggInfestorsCnt = self.eggInfestorsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_CORRUPTOR]):
                self.eggCorruptorsCnt = self.eggCorruptorsCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_ULTRALISK]):
                self.eggUltralisksCnt = self.eggUltralisksCnt + 1
        for egg in self.eggs:
            if egg.is_using_ability([AbilityId.LARVATRAIN_VIPER]):
                self.eggVipersCnt = self.eggVipersCnt + 1

        # if self.hatcheries.amount < 2:
        #     self.early_a()

        # BUG
        # EGGOVERLORDSCNT  BECOMES 1 AFTER FIRST ITERATION.
        if self.drones.amount + self.eggDronesCnt == 12:
            if self.minerals >= 50:
                print("A: ", self.iteration)
                print(
                    "self.drones.amount: ",
                    self.drones.amount,
                    " , self.eggDronesCnt: ",
                    self.eggDronesCnt,
                    " , self.overlords.amount: ",
                    self.overlords.amount,
                    " , self.eggOverlordsCnt: ",
                    self.eggOverlordsCnt,
                )
                print("drone started")
                self.larvas.random.train(UnitTypeId.DRONE)
                for egg in self.eggs:
                    if egg.is_using_ability([AbilityId.LARVATRAIN_DRONE]):
                        self.eggDronesCnt = self.eggDronesCnt + 1
                for egg in self.eggs:
                    if egg.is_using_ability([AbilityId.LARVATRAIN_OVERLORD]):
                        self.eggOverlordsCnt = self.eggOverlordsCnt + 1
                print(
                    "self.drones.amount: ",
                    self.drones.amount,
                    " , self.eggDronesCnt: ",
                    self.eggDronesCnt,
                    " , self.overlords.amount: ",
                    self.overlords.amount,
                    " , self.eggOverlordsCnt: ",
                    self.eggOverlordsCnt,
                )
        elif self.overlords.amount + self.eggOverlordsCnt == 1:
            if self.minerals >= 100:
                print("B: ", self.iteration)
                print(
                    "self.drones.amount: ",
                    self.drones.amount,
                    " , self.eggDronesCnt: ",
                    self.eggDronesCnt,
                    " , self.overlords.amount: ",
                    self.overlords.amount,
                    " , self.eggOverlordsCnt: ",
                    self.eggOverlordsCnt,
                )
                print("overlord started")
                self.larvas.random.train(UnitTypeId.OVERLORD)
                for egg in self.eggs:
                    if egg.is_using_ability([AbilityId.LARVATRAIN_DRONE]):
                        self.eggDronesCnt = self.eggDronesCnt + 1
                for egg in self.eggs:
                    if egg.is_using_ability([AbilityId.LARVATRAIN_OVERLORD]):
                        self.eggOverlordsCnt = self.eggOverlordsCnt + 1
                print(
                    "self.drones.amount: ",
                    self.drones.amount,
                    " , self.eggDronesCnt: ",
                    self.eggDronesCnt,
                    " , self.overlords.amount: ",
                    self.overlords.amount,
                    " , self.eggOverlordsCnt: ",
                    self.eggOverlordsCnt,
                )
        elif (
            self.drones.amount + self.eggDronesCnt == 13
            and self.overlords.amount + self.eggOverlordsCnt == 2
        ):
            if self.minerals >= 50:
                print("C: ", self.iteration)
                print(
                    "self.drones.amount: ",
                    self.drones.amount,
                    " , self.eggDronesCnt: ",
                    self.eggDronesCnt,
                    " , self.overlords.amount: ",
                    self.overlords.amount,
                    " , self.eggOverlordsCnt: ",
                    self.eggOverlordsCnt,
                )
                print("drone started")
                self.larvas.random.train(UnitTypeId.DRONE)
                for egg in self.eggs:
                    if egg.is_using_ability([AbilityId.LARVATRAIN_DRONE]):
                        self.eggDronesCnt = self.eggDronesCnt + 1
                for egg in self.eggs:
                    if egg.is_using_ability([AbilityId.LARVATRAIN_OVERLORD]):
                        self.eggOverlordsCnt = self.eggOverlordsCnt + 1
                print(
                    "self.drones.amount: ",
                    self.drones.amount,
                    " , self.eggDronesCnt: ",
                    self.eggDronesCnt,
                    " , self.overlords.amount: ",
                    self.overlords.amount,
                    " , self.eggOverlordsCnt: ",
                    self.eggOverlordsCnt,
                )
        elif self.drones.amount + self.eggDronesCnt <= 16:
            if self.overlords.amount + self.eggOverlordsCnt == 2:
                if self.minerals >= 50:
                    print("D: ", self.iteration)
                    print(
                        "self.drones.amount: ",
                        self.drones.amount,
                        " , self.eggDronesCnt: ",
                        self.eggDronesCnt,
                        " , self.overlords.amount: ",
                        self.overlords.amount,
                        " , self.eggOverlordsCnt: ",
                        self.eggOverlordsCnt,
                    )
                    self.larvas.random.train(UnitTypeId.DRONE)
                for egg in self.eggs:
                    if egg.is_using_ability([AbilityId.LARVATRAIN_DRONE]):
                        self.eggDronesCnt = self.eggDronesCnt + 1
                for egg in self.eggs:
                    if egg.is_using_ability([AbilityId.LARVATRAIN_OVERLORD]):
                        self.eggOverlordsCnt = self.eggOverlordsCnt + 1
                    print(
                        "self.drones.amount: ",
                        self.drones.amount,
                        " , self.eggDronesCnt: ",
                        self.eggDronesCnt,
                        " , self.overlords.amount: ",
                        self.overlords.amount,
                        " , self.eggOverlordsCnt: ",
                        self.eggOverlordsCnt,
                    )

        time.sleep(1 / 60)

    # def early_a(self):

    def printSth(self):
        4

    async def on_start(self):
        await super().on_start()
        print("Game started")
        # Do things here before the game starts
        self.client.game_step = 1
        # self.getValues()

    async def on_end(self, game_result: Result):
        print("Game ended.")
        # Do things here after the game ends
