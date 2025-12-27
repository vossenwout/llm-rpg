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

## Theme Word Steering
Enemy generation can be nudged with random words on three axes.

- **Word lists**: `enemy_generation.character_words_path`, `enemy_generation.adjective_words_path`, `enemy_generation.place_words_path` in `config/game_config.yaml`.
- **Prompt variables**: use `{enemy_character}`, `{enemy_adjective}`, `{enemy_place}` inside `prompts.enemy_generation`.

The game picks a random word per enemy for each axis and injects them into the prompt before the JSON schema is appended.

All three word lists are required; the game raises an error if any list is missing or empty.
