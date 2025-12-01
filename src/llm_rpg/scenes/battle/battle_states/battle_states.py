from enum import Enum


class BattleStates(Enum):
    START = "start"
    TURN = "turn"
    HERO_THINKING = "hero_thinking"
    ENEMY_THINKING = "enemy_thinking"
    HERO_RESULT = "hero_result"
    ENEMY_RESULT = "enemy_result"
    END = "end"
