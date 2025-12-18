# Combat and Damage

## Relevant Files
- `src/llm_rpg/systems/battle/damage_calculator.py`
- `config/game_config.yaml`

## Total Damage
Formula for calculating damage an attacker inflicts on a defender:

$$
\mathrm{TotalDamage} = \lceil \mathrm{BaseDamage} \cdot \mathrm{LLMDamageScaling} \rceil + \mathrm{BonusDamage}
$$

- **TotalDamage**: The total damage inflicted.
- **BaseDamage**: Pure stat based damage.
- **LLMDamageScaling**: LLM judgements.
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

## Bonus Damage
Bonus damage component from special items:

$$
\mathrm{BonusDamage} = \sum_{i=1}^{n}
\begin{cases}
\lfloor \mathrm{LLMScaledBaseDamage} \cdot M_i \rfloor & \text{if } M_i < 0 \\
\lceil \mathrm{LLMScaledBaseDamage} \cdot M_i \rceil & \text{if } M_i \geq 0
\end{cases}
$$

$$ \mathrm{LLMScaledBaseDamage} = \lceil \mathrm{BaseDamage} \times \mathrm{LLMDamageScaling} \rceil $$
- **n**: Number of procced bonus multipliers from equipped items.
- **M_i**: The i-th bonus multiplier value. [range: -1.0-1.0]

Bonus multipliers proc based on conditions such as number of new words used, number of overused words, or answer speed.
