"""No-DB tests for the Runner Class registry (AC2, AC3)."""

from django.test import TestCase
from world import classes


class ClassRegistryTest(TestCase):
    """Tests for the single-source-of-truth Class registry."""

    def test_six_class_keys(self):
        """Exactly the six expected Class keys are registered."""
        self.assertEqual(
            set(classes.CLASS_KEYS),
            {"demolitionist", "face", "ghost", "hacker", "magus", "samurai"},
        )

    def test_get_class_returns_definition(self):
        """get_class returns a definition with display, blurb and mods."""
        samurai = classes.get_class("samurai")
        self.assertEqual(samurai["display"], "Samurai")
        self.assertIn("blurb", samurai)
        self.assertIsInstance(samurai["mods"], dict)

    def test_get_class_invalid_raises(self):
        """An invalid Class key fails fast with ValueError."""
        with self.assertRaises(ValueError):
            classes.get_class("netrunner")

    def test_all_definitions_well_formed(self):
        """Every registered Class has display, blurb and a mods dict."""
        for key in classes.CLASS_KEYS:
            definition = classes.get_class(key)
            self.assertIn("display", definition)
            self.assertIn("blurb", definition)
            self.assertIsInstance(definition["mods"], dict)

    def test_mods_reference_known_trait_keys(self):
        """Class mods only reference known attribute/skill/special keys."""
        known = set(classes.MODIFIABLE_TRAIT_KEYS)
        for key in classes.CLASS_KEYS:
            for trait_key in classes.get_class(key)["mods"]:
                self.assertIn(
                    trait_key,
                    known,
                    msg=f"Class '{key}' references unknown trait '{trait_key}'",
                )

    def test_samurai_is_more_combat_capable_than_face(self):
        """Samurai has higher combat attributes than Face (AC3 intent)."""
        samurai = classes.get_class("samurai")["mods"]
        face = classes.get_class("face")["mods"]
        self.assertGreater(samurai.get("body", 0), face.get("body", 0))
        self.assertGreater(samurai.get("agility", 0), face.get("agility", 0))

    def test_face_is_more_charismatic_than_samurai(self):
        """Face has higher charisma than Samurai (AC3 intent)."""
        samurai = classes.get_class("samurai")["mods"]
        face = classes.get_class("face")["mods"]
        self.assertGreater(face.get("charisma", 0), samurai.get("charisma", 0))

    def test_hacker_has_logic_edge(self):
        """Hacker has a logic modifier."""
        self.assertGreater(classes.get_class("hacker")["mods"].get("logic", 0), 0)

    def test_magus_has_magic_trait(self):
        """Magus has a magic/essence modifier."""
        mods = classes.get_class("magus")["mods"]
        self.assertTrue(mods.get("magic", 0) > 0 or mods.get("essence", 0) > 0)
