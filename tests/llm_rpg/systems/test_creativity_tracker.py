from llm_rpg.systems.battle.creativity_tracker import CreativityTracker


def test_preprocessing_removes_punctuation_and_stop_words():
    tracker = CreativityTracker(word_overuse_threshold=2)
    words = tracker._get_preprocessed_words_in_action("The Quick, brown fox!!!")
    assert words == ["quick", "brown", "fox"]


def test_new_words_counted_once_per_action():
    tracker = CreativityTracker(word_overuse_threshold=2)
    tracker.add_action("fire blast")
    # duplicate word inside same action should not double count
    assert tracker.count_new_words_in_action("fire fire bolt") == 1  # only "bolt"


def test_overused_words_respect_threshold():
    tracker = CreativityTracker(word_overuse_threshold=2)
    tracker.add_action("slash slash")
    tracker.add_action("slash")  # slash now at 3 uses
    assert tracker.count_overused_words_in_action("slash parry slash") == 2


def test_add_action_updates_usage_counts():
    tracker = CreativityTracker(word_overuse_threshold=3)
    tracker.add_action("lightning strike")
    assert tracker.count_new_words_in_action("lightning surge") == 1  # only surge new
    tracker.add_action("lightning surge")
    # lightning now used twice, still below threshold
    assert tracker.count_overused_words_in_action("lightning") == 0
    tracker.add_action("lightning")
    # now at 3 uses -> meets threshold
    assert tracker.count_overused_words_in_action("lightning") == 1
