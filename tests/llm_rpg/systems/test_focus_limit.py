from llm_rpg.objects.character import Stats
from llm_rpg.systems.hero.hero import Hero
from llm_rpg.scenes.battle.battle_states.battle_turn_state import BattleTurnState


class _BattleSceneStub:
    def __init__(self, hero):
        self.hero = hero


def test_build_proposed_action_respects_focus_limit():
    hero = Hero(
        name="Test",
        class_name="",
        description="",
        level=1,
        base_stats=Stats(attack=1, defense=1, focus=3, max_hp=5),
        max_items=3,
    )
    scene = _BattleSceneStub(hero)
    state = BattleTurnState(scene)
    state.input_text = "abcd"
    state.input_timer = 1.0

    action = state._build_proposed_action()

    assert not action.is_valid
    assert "focus" in (action.invalid_reason or "").lower()
