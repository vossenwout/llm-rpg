# Combat and Damage

## Relevant Files
- `src/llm_rpg/systems/battle/damage_calculator.py`
- `config/game_config.yaml`

## Total Damage
Formula for calculating damage an attacker inflicts on a defender:

$$
\mathrm{TotalDamage} = \mathrm{LLMScaledBaseDamage} + \mathrm{CreativityBonusDamage} + \mathrm{BonusDamage}
$$

- **TotalDamage**: The total damage inflicted.
- **BaseDamage**: Pure stat based damage.
- **LLMDamageScaling**: LLM judgements.
- **LLMScaledBaseDamage**: Base damage scaled by LLM judgement.
- **CreativityBonusDamage**: Bonus or penalty from creativity of the action.
- **BonusDamage**: Bonus damage from special items.

## Base Damage
Classic RPG stat-based component:

$$
\mathrm{BaseDamage} =
\max\left(
1,
\left(
\mathrm{ADParityDamage}
+
\mathrm{ADDiffScaling} \cdot
(\mathrm{Attack} - \mathrm{Defense})
\right) \cdot \mathrm{RandomFactor}
\right)
$$

- **ADParityDamage**: Damage regardless of AD difference. [default: 1.25]
- **ADDiffScaling**: Impact of AD difference. [default: 0.5]
- **RandomFactor**: Random factor. [range: 0.95-1.05]
- **Attack**: Attack of attacker.
- **Defense**: Defense of defender.

## LLM Damage
LLM judgement component:

$$
\mathrm{LLMDamage} =
\mathrm{LLMDamageImpact} \cdot
\mathrm{Feasibility} \cdot
\mathrm{PotentialDamage}
$$

- **LLMDamageImpact**: How much the LLM judgements impact the damage. [default: 2]
- **Feasibility**: Feasibility of the action. [range: 0.0-1.0]
- **PotentialDamage**: Potential damage of the action. [range: 0.0-1.0]

$$ \mathrm{LLMScaledBaseDamage} = \lceil \mathrm{BaseDamage} \times \mathrm{LLMDamageScaling} \rceil $$

## Creativity Bonus Damage
Creativity bonus/penalty is applied to the LLM-scaled base damage.

$$
\mathrm{CreativityMultiplier} =
\begin{cases}
((\mathrm{NewWords} - \mathrm{MinNewWordsForBonus}) \cdot B) - (\mathrm{OverusedWords} \cdot P) & \text{if } \mathrm{NewWords} \ge \mathrm{MinNewWordsForBonus} \\
-(\mathrm{OverusedWords} \cdot P) & \text{if } \mathrm{NewWords} < \mathrm{MinNewWordsForBonus}
\end{cases}
$$

$$
\mathrm{CreativityBonusDamage} =
\begin{cases}
\lfloor \mathrm{LLMScaledBaseDamage} \cdot \mathrm{CreativityMultiplier} \rfloor & \text{if } \mathrm{CreativityMultiplier} < 0 \\
\lceil \mathrm{LLMScaledBaseDamage} \cdot \mathrm{CreativityMultiplier} \rceil & \text{if } \mathrm{CreativityMultiplier} \ge 0
\end{cases}
$$

- **NewWords**: Number of new words in the action (new to the current battle).
- **OverusedWords**: Number of overused words in the action (above threshold for the current battle).
- **B**: Bonus per new word. [default: 0.1]
- **P**: Penalty per overused word. [default: 0.1]
- **MinNewWordsForBonus**: Minimum new words required before any bonus applies (subtracted from the count). [default: 2]

## Bonus Damage
Bonus damage component from special items:

$$
\mathrm{BonusDamage} = \sum_{i=1}^{n}
\begin{cases}
\lfloor \mathrm{LLMScaledBaseDamage} \cdot M_i \rfloor & \text{if } M_i < 0 \\
\lceil \mathrm{LLMScaledBaseDamage} \cdot M_i \rceil & \text{if } M_i \geq 0
\end{cases}
$$

- **n**: Number of procced bonus multipliers from equipped items.
- **M_i**: The i-th bonus multiplier value. [range: -1.0-1.0]

Bonus multipliers proc based on item-specific conditions such as answer speed.
