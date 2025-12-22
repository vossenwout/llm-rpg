# Enemy Generation

## Relevant Files
- `src/llm_rpg/systems/generation/enemy_generator.py`
- `src/llm_rpg/sprite_generator/sprite_generator.py`
- `config/game_config.yaml`

## What It Does
An enemy is generated during `BattleStartState` using an LLM prompt. The model returns a name and description, and the game randomly assigns an archetype. 

## Prompt Source
**Enemy description prompt**: `prompts.enemy_generation` in `config/game_config.yaml`.
**Enemy sprite prompt**: `sprite_generator.prompt_template` in `config/game_config.yaml`.