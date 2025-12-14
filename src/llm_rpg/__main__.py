from dotenv import load_dotenv

from llm_rpg.game.game import Game
from llm_rpg.game.game_config import GameConfig

env_files = [
    "config/.env.secret",
]

for env_file in env_files:
    load_dotenv(env_file)


if __name__ == "__main__":
    game = Game(config=GameConfig("config/game_config.yaml"))
    game.run()
