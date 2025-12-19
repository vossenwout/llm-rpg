# LLM Judgments

## Relevant Files
- `src/llm_rpg/systems/battle/action_judges.py`
- `src/llm_rpg/systems/battle/action_narrators.py`
- `src/llm_rpg/systems/battle/enemy_action_generators.py`
- `src/llm_rpg/systems/battle/battle_ai.py`
- `src/llm_rpg/systems/battle/battle_log.py`
- `config/game_config.yaml`

## What the Models Do
- The **Action Judge** scores feasibility and potential damage.
- The **Narrator** writes the effect description.
- The **Enemy Action Generator** proposes the enemy's next action.

## Action Judgment
**Prompt source**: `prompts.action_judge` in `config/game_config.yaml`.

**Prompt inputs**:
- Attacker/defender names + descriptions
- Hero name + inventory list
- Battle history (last 5 events)
- Proposed action text

**Battle history format**: `{character_name} turn: {effect_description}` per line.

**Output schema** (Pydantic `LLMActionJudgmentOutput`, schema appended to prompt as JSON):
- `feasibility`: 0–10
- `potential_damage`: 0–10

**Scaling**: both numeric outputs are divided by 10 to become 0.0–1.0 before damage calc.

**Retries**: up to 3 attempts; raises `ValueError` if all fail. Debug prints full prompt.

## Action Narration
**Prompt source**: `prompts.action_narration` in `config/game_config.yaml`.

**Inputs**:
- Attacker/defender names + descriptions
- Hero name + inventory list
- Battle history (last 5 events)
- Proposed action text
- Feasibility + potential damage scores
- Total damage dealt

**Output**: single sentence effect description.

## Enemy Next Action
**Prompt source**: `prompts.enemy_next_action` in `config/game_config.yaml`.

**Inputs**: enemy/hero names + descriptions + max HP + battle history (last 5 events).

**Output**: freeform, short third-person narrated action via `generate_completion`.

## Config Notes
Models are configured separately under `action_judge`, `narrator`, and `enemy_action` in `config/game_config.yaml`. All three sections are required.
