#  Game Overview Entry Point

## Quick Summary
AI RPG is a roguelike where each battle is driven by player-written actions. An LLM evaluates the action (feasibility and potential damage), then classic RPG stats (Attack, Defense) combine with that LLM judgement to produce final damage. Between battles the hero levels or gains items. Enemies and their actions are also LLM-controlled, so each run can differ.

## Core Loop
1. Player names a hero and chooses a class.
2. Player enters the resting hub (menu between battles).
3. Player starts a battle against a randomly generated enemy.
4. Player writes an action; LLM judges it; damage is calculated.
5. After victory, player levels up or gains an item, and the hero fully heals to the current max HP (including item bonuses).
6. Repeat until hero HP reaches 0.

## Systems Index
| System | Purpose | Details |
| --- | --- | --- |
| Combat / Damage | Calculate total damage from stats + LLM judgement + bonuses | `docs/systems/combat.md` |
| Stats & Classes | Define hero/enemy stats and starting classes | `docs/systems/stats_and_classes.md` |
| Progression | Hero leveling and enemy scaling | `docs/systems/progression.md` |
| LLM Judgments | Define LLM action evaluations and prompt sources | `docs/systems/llm_judgments.md` |
| Enemy Generation | Generate enemy names/descriptions and sprite prompts | `docs/systems/enemy_generation.md` |

## Visual / UI Style
UI is inspired by SNES RPGs such as Dragon Quest and Earthbound, in pixel art style.
Battle backgrounds include classic Earthbound-style geometric patterns plus VCR-inspired glitch variants with scanlines, tracking bars, and horizontal jitter.
The main menu displays a pixel-art title logo from `src/llm_rpg/assets/sprites/logo.png`.
Panels use a 9-slice border sprite at `src/llm_rpg/assets/sprites/panel_border.png` (24x24 source with 8x8 tiles). Edges are tiled, corners are unscaled, and the panel interior is a solid fill using `Theme.colors["panel_inner"]`.
Battle scenes render a low-resolution procedurally generated background per enemy, seeded by enemy name, and then scale it to the display. Background base resolution and speed tuning live under `battle_background` in `config/game_config.yaml`.

## Source of Truth
Balance values and defaults are defined in `config/game_config.yaml`. Code files above should align with those values.
Sprite generation settings are also defined in `config/game_config.yaml` under `sprite_generator`. Large model files live under `models/`.
