class Stats:
    def __init__(self, level: int, attack: int, defense: int, focus: int, hp: int):
        self.level = level
        # scales damage inflicted
        self.attack = attack
        # reduces damage taken
        self.defense = defense
        # determines amount of letters you can type
        self.max_focus = focus
        self.focus = focus
        # determines how much damage you can take
        self.max_hp = hp
        self.hp = hp


class Character:
    def __init__(self, name: str, description: str, stats: Stats):
        # name of the character
        self.name = name
        # description of th character, also includes the items they have equipped
        self.description = description
        # stats of the character
        self.stats = stats
