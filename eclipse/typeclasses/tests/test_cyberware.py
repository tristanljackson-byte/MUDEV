"""Tests for the Cyberware typeclass and prototypes (AC1, AC7)."""

from world import prototypes

from evennia import spawn
from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest

CYBERWARE_PROTOTYPES = (
    "WIRED_REFLEXES",
    "CYBEREYES",
    "DERMAL_PLATING",
    "SMARTLINK",
)


class CyberwareTypeclassTest(EvenniaTest):
    """The Cyberware typeclass exposes its configured fields and hooks."""

    character_typeclass = "typeclasses.characters.Character"

    def test_fields_default(self):
        """A bare Cyberware has sensible defaults."""
        piece = create.create_object("typeclasses.cyberware.Cyberware", key="Chrome")
        self.assertFalse(piece.installed)
        self.assertEqual(piece.mods, {})
        self.assertEqual(piece.humanity_cost, 0)

    def test_hooks_are_callable(self):
        """The install/remove hooks exist and are no-ops by default."""
        piece = create.create_object("typeclasses.cyberware.Cyberware", key="Chrome")
        # Should not raise.
        self.assertIsNone(piece.at_pre_install(self.char1))
        self.assertIsNone(piece.at_post_install(self.char1))
        self.assertIsNone(piece.at_pre_remove(self.char1))
        self.assertIsNone(piece.at_post_remove(self.char1))


class PrototypeSpawnTest(EvenniaTest):
    """AC7: each example prototype spawns and installs end-to-end."""

    character_typeclass = "typeclasses.characters.Character"

    def test_prototypes_defined(self):
        """At least four cyberware prototypes are defined in the module."""
        defined = [
            name
            for name in dir(prototypes)
            if name.isupper() and isinstance(getattr(prototypes, name), dict)
        ]
        for proto in CYBERWARE_PROTOTYPES:
            self.assertIn(proto, defined)

    def test_each_prototype_spawns_and_installs(self):
        """Every prototype spawns and installs without error."""
        for proto_key in CYBERWARE_PROTOTYPES:
            obj = spawn(getattr(prototypes, proto_key))[0]
            runner = create.create_object(
                self.character_typeclass,
                key=f"R_{proto_key}",
                location=self.room1,
                home=self.room1,
            )
            runner.cyberware.install(obj)
            self.assertTrue(obj.installed)
            self.assertIn(obj, runner.cyberware.installed_pieces)
