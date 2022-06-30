# pylint: disable=E0401
import sys
import random

from __init__ import run_ladder_game

from sc2 import maps
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer

# Load bot
from bot.bot import ascyBot
from bot.hydralisk_push import Hydralisk

# Load maps
from mapNames import mapNames

ascyZerg = Bot(Race.Zerg, ascyBot())
# ascyZerg = Bot(Race.Zerg, Hydralisk)

# Start game
if __name__ == "__main__":
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        result, opponentid = run_ladder_game(ascyZerg)
        print(result, " against opponent ", opponentid)
    else:
        # Local game
        print("Starting local game...")
        run_game(
            maps.get(random.choice(mapNames)),
            [ascyZerg, Computer(Race.Random, Difficulty.Medium)],
            realtime=False,
        )
