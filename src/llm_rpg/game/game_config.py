from functools import cached_property
import yaml

from llm_rpg.objects.character import Stats
from llm_rpg.objects.item import (
    AttackerStartingItem,
    DefenderStartingItem,
    FocusStartingItem,
)
from llm_rpg.systems.battle.damage_calculator import DamageCalculationConfig
from llm_rpg.systems.battle.action_judges import (
    ActionJudge,
    LLMActionJudge,
    TransformersActionJudge,
)
from llm_rpg.systems.battle.action_narrators import ActionNarrator, LLMActionNarrator
from llm_rpg.systems.battle.enemy_action_generators import (
    EnemyActionGenerator,
    LLMEnemyActionGenerator,
)
from llm_rpg.systems.battle.enemy_scaling import (
    EnemyArchetypesLevelingAttributeProbs,
    LevelScaling,
    LevelingAttributeProbs,
)
from llm_rpg.systems.hero.hero import HeroClass
from llm_rpg.llm.llm import LLM, OllamaLLM, GroqLLM
from llm_rpg.llm.llm_cost_tracker import LLMCostTracker


class GameConfig:
    def __init__(self, config_path: str):
        with open(config_path, "r") as file:
            self.game_config = yaml.safe_load(file)

    def _build_llm(self, llm_config: dict) -> LLM:
        if llm_config["type"] == "ollama":
            return OllamaLLM(
                llm_cost_tracker=LLMCostTracker(),
                model=llm_config["model"],
            )
        if llm_config["type"] == "groq":
            return GroqLLM(
                llm_cost_tracker=LLMCostTracker(),
                model=llm_config["model"],
            )
        raise ValueError(f"Unsupported LLM type: {llm_config['type']}")

    def _is_llm_block(self, block: dict) -> bool:
        return (
            "type" in block
            and "model" in block
            and block["type"]
            in [
                "ollama",
                "groq",
            ]
        )

    def _extract_llm_block(self, block: dict) -> dict:
        if "llm" in block:
            return block["llm"]
        return block

    def _get_llm_config(self, section_key: str) -> dict:
        if section_key not in self.game_config:
            raise ValueError(f"Missing required config section '{section_key}'")
        section = self.game_config[section_key]
        llm_block = self._extract_llm_block(section)
        if not self._is_llm_block(llm_block):
            raise ValueError(
                f"Invalid LLM config under '{section_key}'. Expected type/model."
            )
        return llm_block

    @cached_property
    def debug_mode(self) -> bool:
        return self.game_config["debug_mode"]

    @cached_property
    def action_judge(self) -> ActionJudge:
        section = self.game_config.get("action_judge")
        if section is None:
            raise ValueError("Missing required config section 'action_judge'")
        backend = section.get("backend")
        if backend is None:
            if self._is_llm_block(section) or "llm" in section:
                backend = "llm"
            else:
                backend = section.get("type")
        if backend == "llm":
            llm_config = self._extract_llm_block(section)
            if not self._is_llm_block(llm_config):
                raise ValueError("action_judge.llm must include type/model")
            llm = self._build_llm(llm_config)
            return LLMActionJudge(
                llm=llm, prompt=self.action_judge_prompt, debug=self.debug_mode
            )
        if backend == "transformers":
            model_name = section.get("model")
            if model_name is None:
                raise ValueError("action_judge.model is required for transformers")
            device = section.get("device", "cpu")
            return TransformersActionJudge(model_name=model_name, device=device)
        raise ValueError(f"Unsupported action_judge backend: {backend}")

    @cached_property
    def action_narrator(self) -> ActionNarrator:
        llm_config = self._get_llm_config("narrator")
        llm = self._build_llm(llm_config)
        return LLMActionNarrator(
            llm=llm, prompt=self.action_narration_prompt, debug=self.debug_mode
        )

    @cached_property
    def enemy_action_generator(self) -> EnemyActionGenerator:
        llm_config = self._get_llm_config("enemy_action")
        llm = self._build_llm(llm_config)
        return LLMEnemyActionGenerator(
            llm=llm, prompt=self.enemy_next_action_prompt, debug=self.debug_mode
        )

    @cached_property
    def hero_base_stats(self) -> Stats:
        return Stats(
            attack=self.game_config["hero"]["base_hero_stats"]["attack"],
            defense=self.game_config["hero"]["base_hero_stats"]["defense"],
            focus=self.game_config["hero"]["base_hero_stats"]["focus"],
            max_hp=self.game_config["hero"]["base_hero_stats"]["max_hp"],
        )

    def _parse_stats(self, stats: dict) -> Stats:
        return Stats(
            attack=stats["attack"],
            defense=stats["defense"],
            focus=stats["focus"],
            max_hp=stats["max_hp"],
        )

    @cached_property
    def attack_hero_class(self) -> HeroClass:
        return HeroClass(
            class_name=self.game_config["hero"]["classes"]["attack"]["class_name"],
            description=self.game_config["hero"]["classes"]["attack"]["description"],
            base_stats=self._parse_stats(
                self.game_config["hero"]["classes"]["attack"]["base_stats"]
            ),
            starting_item=AttackerStartingItem(),
            # starting_item=AdrenalinePump(),
        )

    @cached_property
    def focus_hero_class(self) -> HeroClass:
        return HeroClass(
            class_name=self.game_config["hero"]["classes"]["focus"]["class_name"],
            description=self.game_config["hero"]["classes"]["focus"]["description"],
            base_stats=self._parse_stats(
                self.game_config["hero"]["classes"]["focus"]["base_stats"]
            ),
            starting_item=FocusStartingItem(),
        )

    @cached_property
    def defense_hero_class(self) -> HeroClass:
        return HeroClass(
            class_name=self.game_config["hero"]["classes"]["defense"]["class_name"],
            description=self.game_config["hero"]["classes"]["defense"]["description"],
            base_stats=self._parse_stats(
                self.game_config["hero"]["classes"]["defense"]["base_stats"]
            ),
            starting_item=DefenderStartingItem(),
        )

    @cached_property
    def hero_stats_level_up_amount(self) -> int:
        return self.game_config["hero"]["stats_level_up_amount"]

    @cached_property
    def enemy_level_scaling(self) -> LevelScaling:
        return LevelScaling(
            exp_growth_rate=self.game_config["enemy"]["enemy_level_scaling"][
                "exp_growth_rate"
            ],
            linear_growth_rate=self.game_config["enemy"]["enemy_level_scaling"][
                "linear_growth_rate"
            ],
            linear_scaling_factor=self.game_config["enemy"]["enemy_level_scaling"][
                "linear_scaling_factor"
            ],
        )

    @cached_property
    def enemy_stats_level_up_amount(self) -> int:
        return self.game_config["enemy"]["stats_level_up_amount"]

    @cached_property
    def enemy_leveling_stats_probs(
        self,
    ) -> EnemyArchetypesLevelingAttributeProbs:
        return EnemyArchetypesLevelingAttributeProbs(
            attacker=LevelingAttributeProbs(
                attack=self.game_config["enemy"]["leveling_stats_probs"]["attacker"][
                    "attack"
                ],
                defense=self.game_config["enemy"]["leveling_stats_probs"]["attacker"][
                    "defense"
                ],
                max_hp=self.game_config["enemy"]["leveling_stats_probs"]["attacker"][
                    "max_hp"
                ],
            ),
            defender=LevelingAttributeProbs(
                attack=self.game_config["enemy"]["leveling_stats_probs"]["defender"][
                    "attack"
                ],
                defense=self.game_config["enemy"]["leveling_stats_probs"]["defender"][
                    "defense"
                ],
                max_hp=self.game_config["enemy"]["leveling_stats_probs"]["defender"][
                    "max_hp"
                ],
            ),
            tank=LevelingAttributeProbs(
                attack=self.game_config["enemy"]["leveling_stats_probs"]["tank"][
                    "attack"
                ],
                defense=self.game_config["enemy"]["leveling_stats_probs"]["tank"][
                    "defense"
                ],
                max_hp=self.game_config["enemy"]["leveling_stats_probs"]["tank"][
                    "max_hp"
                ],
            ),
        )

    @cached_property
    def damage_calculation(self) -> DamageCalculationConfig:
        return DamageCalculationConfig(
            ad_diff_scaling=self.game_config["damage_calculator"]["ad_diff_scaling"],
            ad_parity_dmg=self.game_config["damage_calculator"]["ad_parity_dmg"],
            random_factor_max=self.game_config["damage_calculator"][
                "random_factor_max"
            ],
            random_factor_min=self.game_config["damage_calculator"][
                "random_factor_min"
            ],
            llm_dmg_impact=self.game_config["damage_calculator"]["llm_dmg_impact"],
        )

    @cached_property
    def base_enemy_stats(self) -> Stats:
        return self._parse_stats(self.game_config["enemy"]["base_stats"])

    @cached_property
    def creativity_word_overuse_threshold(self) -> int:
        return self.game_config["creativity_tracker"]["word_overuse_threshold"]

    @cached_property
    def hero_max_items(self) -> int:
        return self.game_config["hero"]["max_items"]

    @cached_property
    def enemy_next_action_prompt(self) -> str:
        return self.game_config["prompts"]["enemy_next_action"]

    @cached_property
    def action_judge_prompt(self) -> str:
        prompts = self.game_config["prompts"]
        if "action_judge" in prompts:
            return prompts["action_judge"]
        return prompts["battle_ai_effect_determination"]

    @cached_property
    def action_narration_prompt(self) -> str:
        prompts = self.game_config["prompts"]
        if "action_narration" in prompts:
            return prompts["action_narration"]
        raise ValueError("prompts.action_narration is required in config")

    @cached_property
    def display_fullscreen(self) -> bool:
        return self.game_config["display"]["fullscreen"]

    @cached_property
    def display_windowed_scale(self) -> int:
        return self.game_config["display"]["windowed_scale"]
