"""Tests for the Runner Character typeclass (AC1-AC4)."""

from world import classes

from evennia.utils.test_resources import EvenniaTest

ATTRIBUTE_KEYS = (
    "body",
    "agility",
    "reaction",
    "strength",
    "willpower",
    "logic",
    "intuition",
    "charisma",
)
SKILL_KEYS = ("firearms", "stealth", "hacking", "conjuring")


class RunnerTraitTest(EvenniaTest):
    """AC1: a freshly created Runner has all traits and a 10/10 humanity gauge."""

    character_typeclass = "typeclasses.characters.Character"

    def test_all_attributes_present(self):
        """All eight attribute traits exist on a new Runner."""
        for key in ATTRIBUTE_KEYS:
            trait = self.char1.traits.get(key)
            self.assertIsNotNone(trait, msg=f"missing attribute trait '{key}'")

    def test_starting_skills_present(self):
        """The starting skill counter traits exist."""
        for key in SKILL_KEYS:
            trait = self.char1.traits.get(key)
            self.assertIsNotNone(trait, msg=f"missing skill trait '{key}'")

    def test_humanity_gauge_initialised(self):
        """Humanity starts at 10/10 (AC1)."""
        humanity = self.char1.traits.get("humanity")
        self.assertIsNotNone(humanity)
        self.assertEqual(humanity.value, 10)
        self.assertEqual(humanity.max, 10)

    def test_humanity_property(self):
        """The humanity convenience property reads the current value."""
        self.assertEqual(self.char1.humanity, 10)

    def test_lingering_trait_present(self):
        """A lingering static trait starts at 0."""
        lingering = self.char1.traits.get("lingering")
        self.assertIsNotNone(lingering)
        self.assertEqual(lingering.value, 0)

    def test_augmentations_stub_empty(self):
        """The augmentations accessor returns an empty list for now."""
        self.assertEqual(list(self.char1.augmentations), [])


class RunnerClassTest(EvenniaTest):
    """AC2 & AC3: Class assignment and starting modifiers."""

    character_typeclass = "typeclasses.characters.Character"

    def test_apply_valid_class_sets_tag_and_attribute(self):
        """A valid Class sets the class Tag and db.runner_class."""
        self.char1.apply_class("samurai")
        self.assertEqual(self.char1.db.runner_class, "samurai")
        self.assertEqual(self.char1.tags.get(category="class"), "samurai")

    def test_apply_invalid_class_fails_fast(self):
        """An invalid Class raises ValueError and does not partially apply."""
        before = {key: self.char1.traits.get(key).value for key in ATTRIBUTE_KEYS}
        with self.assertRaises(ValueError):
            self.char1.apply_class("netrunner")
        self.assertIsNone(self.char1.db.runner_class)
        self.assertIsNone(self.char1.tags.get(category="class"))
        after = {key: self.char1.traits.get(key).value for key in ATTRIBUTE_KEYS}
        self.assertEqual(before, after)

    def test_class_modifiers_reflected_in_traits(self):
        """Applying a Class shifts trait values by its registry mods (AC3)."""
        for key in classes.CLASS_KEYS:
            char = self.create_runner()
            mods = classes.get_class(key)["mods"]
            baseline = {}
            for trait_key in mods:
                trait = char.traits.get(trait_key)
                baseline[trait_key] = trait.value if trait is not None else 0
            char.apply_class(key)
            for trait_key, delta in mods.items():
                self.assertEqual(
                    char.traits.get(trait_key).value,
                    baseline[trait_key] + delta,
                    msg=f"class '{key}' trait '{trait_key}' not shifted by {delta}",
                )

    def test_magus_gains_magic_trait(self):
        """The Magus class makes its magic trait usable on the sheet."""
        self.char1.apply_class("magus")
        self.assertIsNotNone(self.char1.traits.get("magic"))
        self.assertGreater(self.char1.traits.get("magic").value, 0)

    def create_runner(self):
        """Helper: create a fresh Runner for parametrised tests."""
        from evennia.utils import create

        return create.create_object(
            self.character_typeclass, key="Runner", location=self.room1, home=self.room1
        )


class HumanityApiTest(EvenniaTest):
    """AC4: Humanity / Lingering math."""

    character_typeclass = "typeclasses.characters.Character"

    def test_lose_humanity_reduces_current(self):
        """lose_humanity reduces the gauge by the given amount."""
        self.char1.lose_humanity(2)
        self.assertEqual(self.char1.humanity, 8)

    def test_lose_humanity_floors_at_zero(self):
        """Humanity cannot drop below 0."""
        self.char1.lose_humanity(15)
        self.assertEqual(self.char1.humanity, 0)

    def test_runner_loads_at_zero_humanity(self):
        """A Runner at 0 Humanity still reports a valid value."""
        self.char1.lose_humanity(10)
        self.assertEqual(self.char1.humanity, 0)
        self.assertEqual(self.char1.traits.get("humanity").max, 10)

    def test_gain_lingering_does_not_exceed_max(self):
        """Lingering cannot accrue when Humanity is already full."""
        self.char1.gain_lingering(5)
        self.assertEqual(self.char1.humanity, 10)
        self.assertEqual(self.char1.traits.get("lingering").value, 0)

    def test_lingering_spent_first(self):
        """Lingering is spent before true Humanity (AC4 sequence test).

        Install cost 2 -> uninstall (grant 2 lingering) -> install cost 3.
        Net true-Humanity loss should be 1, with lingering exhausted.
        """
        self.char1.lose_humanity(2)
        self.assertEqual(self.char1.humanity, 8)

        self.char1.gain_lingering(2)
        self.assertEqual(self.char1.humanity, 8)
        self.assertEqual(self.char1.traits.get("lingering").value, 2)

        self.char1.lose_humanity(3)
        # 2 absorbed by lingering, 1 from true humanity -> 7, lingering 0
        self.assertEqual(self.char1.humanity, 7)
        self.assertEqual(self.char1.traits.get("lingering").value, 0)

    def test_gain_lingering_capped_by_headroom(self):
        """Lingering is capped so current + lingering never exceeds max."""
        self.char1.lose_humanity(2)
        self.char1.gain_lingering(5)
        # true Humanity unchanged; lingering buffer limited to the 2 headroom
        self.assertEqual(self.char1.humanity, 8)
        self.assertEqual(self.char1.traits.get("lingering").value, 2)
