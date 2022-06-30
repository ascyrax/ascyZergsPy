import random
import sc2
import sys

# Load bot
# from lucid_bot import LucidBot
# bot = Bot(Race.Protoss, LucidBot())

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Race, Difficulty
from sc2.main import run_game
from __init__ import run_ladder_game
from sc2.player import Bot, Computer

from ascyZerg003 import ascyZerg003

maps = [
    "AbyssalReefLE",
    "BelShirVestigeLE",
    "CactusValleyLE",
    "HonorgroundsLE",
    "NewkirkPrecinctTE",
    "PaladinoTerminalLE",
    "ProximaStationLE",
]

# Start game
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        run_ladder_game(Bot(Race.Zerg, ascyZerg003()))
    else:
        # Local game
        print("Starting local game...")
        map_name = random.choice(maps)
        run_game(
            sc2.maps.get(map_name),
            [Bot(Race.Zerg, ascyZerg003()), Computer(Race.Random, Difficulty.Medium)],
            realtime=False,
        )
