## Game Description
AI RPG is a roguelike where you battle increasingly difficult enemies until you get defeated.

Unlike classic RPGs with predefined actions, players type what they want to do. An LLM then determines the feasibility and potential damage of the action. These LLM judgements are combined with traditional RPG stats (attack, defense) to calculate the actual damage. Between battles, heroes level up and find items to become stronger. Both the enemies themselves and their actions are LLM-controlled, with the goal of having a unique experience each playthrough.


## Playthrough explanation

Each playthrough starts with the user naming his hero and choosing a class. After which the user gets send to the resting hub which serves as the menu in between battles where the user can inspect his hero and choose to start the next battle. In each battle the user goes up against a randomly generated enemy and fights by writing out his intended action. After a battle is won the user either levels up or obtains a new item. If the user's hp gets reduced to 0 the game is over. And the user has to start a new playthrough.


## Style / Visual guidelines

The UI and art style is heavily inspired by SNES RPGs such as Dragon Quest and especially Earthbound.

## Damage Calculation
### Relevant files
- `src/llm_rpg/systems/battle/damage_calculator.py`
- `config/game_config.yaml`

### Formulas
$$
\mathrm{TotalDamage} = \lceil \mathrm{BaseDamage} \cdot \mathrm{LLMDamageScaling} \rceil + \mathrm{BonusDamage}
$$
Formula used for calculating damage an attacker inflicts on a defender.
- **TotalDamage**: The total damage inflicted.
- **BaseDamage**: Pure stat based damage.
- **LLMDamageScaling**: LLM judgements.
- **BonusDamage**: Bonus damage from special items.

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
This is the classic RPG stat based component.
- **ADParityDamage**: Damage regardless of AD difference. [default: 1.25]
- **ADDiffScaling**: Impact of AD difference. [default: 0.5]
- **RandomFactor**: Random factor. [range: 0.95-1.05]
- **Attack**: Attack of attacker.
- **Defense**: Defense of defender.
$$
\mathrm{LLMDamage} =
\mathrm{LLMDamageImpact} \cdot
\mathrm{Feasibility} \cdot
\mathrm{PotentialDamage}
$$
This is the LLM judgement component.
- **LLMDamageImpact**: How much the LLM judgements impact the damage. [default: 2]
- **Feasibility**: Feasibility of the action. [range: 0.0-1.0] 
- **PotentialDamage**: Potential damage of the action. [range: 0.0-1.0]

$$
\mathrm{BonusDamage} = \sum_{i=1}^{n} 
\begin{cases}
\lfloor \mathrm{LLMScaledBaseDamage} \cdot M_i \rfloor & \text{if } M_i < 0 \\
\lceil \mathrm{LLMScaledBaseDamage} \cdot M_i \rceil & \text{if } M_i \geq 0
\end{cases}
$$
This is the bonus damage component from special items.
Bonus multipliers proc based on conditions such as number of new words used, number of overused words, or answer speed.

- **n**: Number of procced bonus multipliers from equipped items.
- **M_i**: The i-th bonus multiplier value. [range: -1.0-1.0]
- **LLMScaledBaseDamage**: `⌈BaseDamage × LLMDamageScaling⌉`

## Character stats

Relevant files:
- `src/llm_rpg/objects/character.py`
- `config/game_config.yaml`

Both hero and enemy have the usual classic RPG stats. However, focus is unique and doesn't effect damage calculation directly. Instead, it controls the number of characters the user can use to type his action.

### Hero stats
- **Attack**: Scales damage inflicted when attacking.
- **Defense**: Reduces damage taken when being attacked. 
- **Focus**: Maximum characters the user can use to type his action.
- **HP**: Gets reduced when taking damage. You die when HP reaches 0.
- **Max HP**: HP the hero starts with.

### Enemy stats
- **Attack**: Scales damage inflicted when attacking.
- **Defense**: Reduces damage taken when being attacked. 
- **HP**: Gets reduced when taking damage. Enemy dies when HP reaches 0.
- **Max HP**: HP the enemy starts with.

## Character classes

Relevant files:
- `config/game_config.yaml`

At the beginning of each playthrough, the player chooses a class for their hero. Each class has a unique starting item and a description which determines the playing style.

Currently, there are 3 classes:
- **Gym Bro**
- **Awkward Poet**
- **Doomsday Prepper**

## Leveling

### Hero leveling

Relevant files:
- `src/llm_rpg/systems/hero/hero.py`
- `config/game_config.yaml`
- `src/llm_rpg/scenes/resting_hub/resting_hub_states/resting_hub_level_up_state.py`

Every two battles the hero character levels up. So after the first, third, fifth, etc. battles, the hero levels up.

The hero can choose to level up one of their stats by a fixed amount (default: 5).

Stats that can be leveled up are:
- Attack
- Defense
- Focus
- Max HP

### Enemy scaling
Relevant files:
- `src/llm_rpg/systems/battle/enemy_scaling.py`
- `config/game_config.yaml`

Enemies start from a **base statline** (default: ATK 2, DEF 2, HP 5 see `config/game_config.yaml`) and then get “leveled up” a number of times based on how many battles the player has already won. 

#### 1) Compute how many level-ups to apply

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
- **LinearScalingFactor**: 0.8 (so exponential factor is \(1-0.8=0.2\))

#### 2) Apply the level-ups (random, archetype-weighted)
Each level-up increases **exactly one** of (Attack, Defense, Max HP) by a fixed amount (default: **+5** see `config/game_config.yaml`), The stat is chosen randomly using archetype-specific weights (see `config/game_config.yaml`):
- **Attacker**: Attack 0.7, Defense 0.2, Max HP 0.1
- **Defender**: Attack 0.1, Defense 0.7, Max HP 0.2
- **Tank**: Attack 0.1, Defense 0.2, Max HP 0.7

An enemy cannot level focus as it controls the number of characters the user can use to type his action and is thus irrelevant for enemy scaling.