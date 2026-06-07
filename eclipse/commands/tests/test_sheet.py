"""Command tests for sheet and setclass (AC5, AC2)."""

from commands.setclass import CmdSetClass
from commands.sheet import CmdSheet

from evennia.utils.test_resources import EvenniaCommandTest


class SheetCommandTest(EvenniaCommandTest):
    """AC5: the sheet command renders class, attributes, skills, Humanity."""

    character_typeclass = "typeclasses.characters.Character"

    def test_sheet_shows_attributes_and_humanity(self):
        """sheet output lists attribute labels and a Humanity X/Y string."""
        self.char1.apply_class("samurai")
        output = self.call(CmdSheet(), "")
        self.assertIn("Body", output)
        self.assertIn("Charisma", output)
        self.assertIn("Humanity", output)
        self.assertIn("10/10", output)

    def test_sheet_shows_class_display(self):
        """sheet output lists the chosen Class display name."""
        self.char1.apply_class("face")
        output = self.call(CmdSheet(), "")
        self.assertIn("Face", output)

    def test_sheet_renders_without_class(self):
        """sheet renders even when no Class has been chosen yet."""
        output = self.call(CmdSheet(), "")
        self.assertIn("Humanity", output)

    def test_score_alias(self):
        """The score alias invokes the same command."""
        output = self.call(CmdSheet(), "", cmdstring="score")
        self.assertIn("Humanity", output)

    def test_sheet_renders_at_zero_humanity(self):
        """sheet renders without error when Humanity is 0 (edge case)."""
        self.char1.lose_humanity(10)
        output = self.call(CmdSheet(), "")
        self.assertIn("0/10", output)


class SetClassCommandTest(EvenniaCommandTest):
    """AC2: setclass assigns a Class and rejects invalid input."""

    character_typeclass = "typeclasses.characters.Character"

    def test_setclass_valid(self):
        """setclass with a valid key assigns the Class."""
        self.call(CmdSetClass(), "samurai", "You are now a Samurai.")
        self.assertEqual(self.char1.db.runner_class, "samurai")

    def test_setclass_invalid(self):
        """setclass with an invalid key reports an error, no change."""
        self.call(CmdSetClass(), "netrunner", "Unknown Runner Class")
        self.assertIsNone(self.char1.db.runner_class)

    def test_setclass_no_arg(self):
        """setclass with no argument lists the valid Classes."""
        output = self.call(CmdSetClass(), "")
        self.assertIn("samurai", output.lower())

    def test_setclass_locks_after_first(self):
        """setclass can only succeed once (class_locked guard)."""
        self.call(CmdSetClass(), "samurai", "You are now a Samurai.")
        self.call(CmdSetClass(), "face", "Your Class is already set")
        self.assertEqual(self.char1.db.runner_class, "samurai")
