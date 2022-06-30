import random
from contextlib import suppress
from typing import Set

from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.unit import Unit
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2


class ascyBot(BotAI):
    droneCnt = 0

    async def getValues(self):
        self.droneCnt++;

    async def on_step(self, iteration):
        # Populate this function with whatever your bot should do!
        self.getValues(self)
        # if (extractorCnt < 1)
        # {
        # 	earlyA();
        # }
        # else if (hatcheryCnt <= 2 && extractorCnt <= 4 && roachWarrenCnt == 0)
        # {
        # 	earlyB();
        # }
        # else if (roachWarrenCnt == 1 && hydraDenCnt == 0)
        # {
        # 	earlyC();
        # }
        # else if (hydraDenCnt == 1 && !roachHydraTimingAttack1Sent)
        # {
        # 	earlyD();
        # }
        # else if (!roachHydraTimingAttack2Sent)
        # {
        # 	earlyE();
        # }
        # else if (!roachHydraTimingAttack3Sent)
        # {
        # 	earlyF();
        # }
        if self.droneCnt < 20:
            self.earlyA()
        # else if roachWarrenCnt<1:
        #     earlyB()

    async def on_start(self):
        print("Game started")
        # Do things here before the game starts
        self.client.game_step = 1
        # await self.client.debug_show_map()

    async def on_end(self, game_result: Result):
        print("Game ended.")
        # Do things here after the game ends
