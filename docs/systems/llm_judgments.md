# LLM Judgments

## Relevant Files
- `src/llm_rpg/systems/battle/battle_ai.py`
- `src/llm_rpg/systems/battle/enemy.py`
- `src/llm_rpg/systems/battle/battle_log.py`
- `config/game_config.yaml`

## What the LLM Does
- Judges a proposed action’s **feasibility**, **potential_damage**, and **effect_description**.
- Generates the enemy’s next action description.

## Action Effect Judgment (BattleAI)
**Prompt source**: `prompts.battle_ai_effect_determination` in `config/game_config.yaml`.

**Prompt inputs**:
- Attacker/defender names + descriptions
- Hero name + inventory list
- Battle history (last 5 events)
- Proposed action text

**Battle history format**: `{character_name} turn: {effect_description}` per line.

**Output schema** (Pydantic `ActionEffect`, schema appended to prompt as JSON):
- `feasibility`: 0–10
- `potential_damage`: 0–10
- `effect_description`: single sentence; if infeasible, explain why

**Scaling**: both numeric outputs are divided by 10 to become 0.0–1.0 before damage calc.

**Retries**: up to 3 attempts; raises `ValueError` if all fail. Debug prints full prompt.

## Enemy Next Action
**Prompt source**: `prompts.enemy_next_action` in `config/game_config.yaml`.

**Inputs**: enemy/hero names + descriptions + max HP + battle history (last 5 events).

**Output**: freeform, short third-person narrated action via `generate_completion`.

## Config Notes
LLM provider/model configured under `llm` in `config/game_config.yaml`.
