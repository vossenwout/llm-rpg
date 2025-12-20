# Enemy Generation

## Relevant Files
- `src/llm_rpg/systems/generation/enemy_generator.py`
- `src/llm_rpg/scenes/factory.py`
- `src/llm_rpg/scenes/battle/battle_states/battle_start_state.py`
- `config/game_config.yaml`

## What It Does
An enemy is generated during `BattleStartState` using an LLM prompt. The model returns a name and description, and the game randomly assigns an archetype. Sprite generation happens in the same loading step so the enemy is fully ready before the battle begins.

## Prompt Source
**Prompt**: `prompts.enemy_generation` in `config/game_config.yaml`.

**Prompt inputs**: none (static prompt).

## Output Schema
- `name`: short enemy name (2–40 chars)
- `description`: 1–2 sentence description (10–200 chars)

## Flow
1. `BattleStartState` calls `EnemyGenerator.generate_enemy`.
2. The enemy generator uses the configured `enemy_generation` LLM to produce name/description.
3. An `Enemy` instance is created with a random archetype and base stats.
4. The enemy generator produces a sprite in the same loading pass using its internal sprite generator.
