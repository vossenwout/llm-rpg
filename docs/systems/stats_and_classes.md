# Character Stats and Classes

## Relevant Files
- `src/llm_rpg/objects/character.py`
- `config/game_config.yaml`

## Character Stats
Both hero and enemy have classic RPG stats. Focus is unique and does not affect damage directly; it controls how many characters the user can type for an action.

### Hero Stats
- **Attack**: Scales damage inflicted when attacking.
- **Defense**: Reduces damage taken when being attacked.
- **Focus**: Maximum characters the user can use to type an action.
- **HP**: Reduced when taking damage. You die when HP reaches 0.
- **Max HP**: HP the hero starts with.

### Enemy Stats
- **Attack**: Scales damage inflicted when attacking.
- **Defense**: Reduces damage taken when being attacked.
- **HP**: Reduced when taking damage. Enemy dies when HP reaches 0.
- **Max HP**: HP the enemy starts with.

## Character Classes
At the beginning of each playthrough, the player chooses a class for their hero. Each class has a unique starting item and a description that determines the playing style.

Current classes:
- **Gym Bro**
- **Awkward Poet**
- **Doomsday Prepper**
