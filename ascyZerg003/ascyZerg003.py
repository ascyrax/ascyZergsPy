from sc2.bot_ai import BotAI


class ascyZerg003(BotAI):
    async def on_start(self):
        self.client.game_step: int = 1

    async def on_step(self, iteration: int):
        if iteration == 0:
            for worker in self.workers:
                worker.attack(self.enemy_start_locations[0])
