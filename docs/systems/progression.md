# Progression

## Hero Leveling

### Relevant Files
- `src/llm_rpg/systems/hero/hero.py`
- `config/game_config.yaml`
- `src/llm_rpg/scenes/resting_hub/resting_hub_states/resting_hub_level_up_state.py`

Every two battles the hero levels up. After the first, third, fifth, etc. battles, the hero levels up.

The hero chooses one stat to increase by a fixed amount (default: 5).

After each battle victory, the hero fully heals to the current max HP (including item bonuses).

Stats that can be leveled:
- Attack
- Defense
- Focus
- Max HP

## Enemy Scaling

### Relevant Files
- `src/llm_rpg/systems/battle/enemy_scaling.py`
- `config/game_config.yaml`

Enemies start from a base statline (default: ATK 2, DEF 2, HP 5 in `config/game_config.yaml`) and then get leveled up based on battles won.

### 1) Compute Level-Ups

$$
\mathrm{Progress} = \mathrm{BattlesWon} + 1
$$

$$
\mathrm{EnemyLevelUps} =
\max\left(
1,
\left\lfloor
(\mathrm{LinearGrowthRate}\cdot\mathrm{Progress})\cdot\mathrm{LinearScalingFactor}
+
(\mathrm{ExpGrowthRate}^{\mathrm{Progress}})\cdot(1-\mathrm{LinearScalingFactor})
\right\rfloor
\right)
$$

Default config values:
- **LinearGrowthRate**: 0.6
- **ExpGrowthRate**: 1.2
- **LinearScalingFactor**: 0.8 (so exponential factor is 0.2)

### 2) Apply Level-Ups
Each level-up increases exactly one of (Attack, Defense, Max HP) by a fixed amount (default: +5 in `config/game_config.yaml`).

The stat is chosen randomly using archetype-specific weights:
- **Attacker**: Attack 0.7, Defense 0.2, Max HP 0.1
- **Defender**: Attack 0.1, Defense 0.7, Max HP 0.2
- **Tank**: Attack 0.1, Defense 0.2, Max HP 0.7

Enemies do not level Focus because it controls the number of characters the user can type for an action.
