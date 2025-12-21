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

## Sprite Generation
Sprite generation is configured in `config/game_config.yaml` under `sprite_generator`. The generator is created in `GameConfig` and passed into `EnemyGenerator`. Paths in this section are resolved relative to the game root (the parent directory of `config`).

### Config
Minimal dummy setup:
```yaml
sprite_generator:
  type: "dummy"
  latency_seconds: 1.0
```

Stable Diffusion setup:
```yaml
sprite_generator:
  type: "sd"
  base_model: "models/sprite/westernBeautiful_v10.safetensors"
  lora_path: "models/sprite/earthbound_lora.safetensors"
  trigger_prompt: "sprite, pixel art"
  lcm_lora_path: "models/sprite/LCM_LoRA_Weights_SD15.safetensors"
  guidance_scale: 7
  num_inference_steps: 20
  inference_height: 512
  inference_width: 512
  vae_path: null
  use_lcm: false
  negative_prompt: "blurry, low quality"
```

## Output Schema
- `name`: short enemy name (2–40 chars)
- `description`: 1–2 sentence description (10–200 chars)

## Flow
1. `BattleStartState` calls `EnemyGenerator.generate_enemy`.
2. The enemy generator uses the configured `enemy_generation` LLM to produce name/description.
3. An `Enemy` instance is created with a random archetype and base stats.
4. The enemy generator produces a sprite in the same loading pass using its internal sprite generator.
