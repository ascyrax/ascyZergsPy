import random
import sc2, sys

# Load bot
# from lucid_bot import LucidBot
# bot = Bot(Race.Protoss, LucidBot())

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Race, Difficulty
from sc2.main import run_game
from __init__ import run_ladder_game
from sc2.player import Bot, Computer


class WorkerRushBot(BotAI):

    async def on_step(self, iteration:int ):
        if iteration == 0:
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])


# Start game
if __name__ == '__main__':
	if "--LadderServer" in sys.argv:
		# Ladder game started by LadderManager
		print("Starting ladder game...")
		run_ladder_game(Bot(Race.Zerg,WorkerRushBot()))
	else:
		# Local game
		print("Starting local game...")
		# sc2.run_game(sc2.maps.get("Abyssal Reef LE"), [
		map_name = random.choice(["AbyssalReefLE", "BelShirVestigeLE", "CactusValleyLE", "HonorgroundsLE", "NewkirkPrecinctTE", "PaladinoTerminalLE", "ProximaStationLE"])
		run_game(sc2.maps.get(map_name), [
			Bot(Race.Zerg,WorkerRushBot()),
			Computer(Race.Protoss, Difficulty.Medium)
			# Computer(Race.Random, Difficulty.Hard)
			# Computer(Race.Random, Difficulty.VeryHard)
			# Computer(Race.Random, Difficulty.CheatVision)
], realtime=False)


# sc2.run_game(sc2.maps.get(map_name), [
# 			bot,
# 			# bot
# 			# Computer(Race.Protoss, Difficulty.Medium)
# 			# Computer(Race.Random, Difficulty.Hard)
# 			# Computer(Race.Random, Difficulty.VeryHard)
# 			Computer(Race.Random, Difficulty.CheatVision)
# ], realtime=False)