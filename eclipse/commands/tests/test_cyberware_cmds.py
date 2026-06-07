"""Command tests for install/remove and the augmented sheet (AC6)."""

from commands.cyberware_cmds import CmdInstall, CmdRemove
from commands.sheet import CmdSheet

from evennia.utils import create
from evennia.utils.test_resources import EvenniaCommandTest


def _make_piece(location, slot="nervous", humanity_cost=2, mods=None, key="wired reflexes"):
    """Create a Cyberware object in a location for command tests.

    Args:
        location (Object): Where to place the piece.
        slot (str): Body slot.
        humanity_cost (int): Humanity install cost.
        mods (dict): Trait deltas.
        key (str): Object key (used as the command argument).

    Returns:
        Cyberware: The created piece.
    """
    return create.create_object(
        "typeclasses.cyberware.Cyberware",
        key=key,
        location=location,
        attributes=[
            ("slot", slot),
            ("humanity_cost", humanity_cost),
            ("mods", mods if mods is not None else {"agility": 2}),
        ],
    )


class InstallCommandTest(EvenniaCommandTest):
    """install / remove commands drive the handler with clear messaging."""

    character_typeclass = "typeclasses.characters.Character"

    def test_install_command(self):
        """install <piece> installs and confirms."""
        _make_piece(self.char1)
        self.call(CmdInstall(), "wired reflexes", "You install wired reflexes.")
        self.assertEqual(len(self.char1.cyberware.installed_pieces), 1)

    def test_install_full_slot_message(self):
        """Installing into a full slot reports a clear error, no crash."""
        _make_piece(self.char1, slot="nervous", key="wired reflexes")
        second = _make_piece(self.char1, slot="nervous", key="reflex booster")
        self.call(CmdInstall(), "wired reflexes")
        self.call(CmdInstall(), "reflex booster", "Your nervous slot is full")
        self.assertNotIn(second, self.char1.cyberware.installed_pieces)

    def test_remove_command(self):
        """remove <piece> removes an installed piece."""
        _make_piece(self.char1)
        self.call(CmdInstall(), "wired reflexes")
        self.call(CmdRemove(), "wired reflexes", "You remove wired reflexes.")
        self.assertEqual(self.char1.cyberware.installed_pieces, [])


class SheetAugmentationTest(EvenniaCommandTest):
    """AC6: the sheet lists augmentations and total Humanity cost."""

    character_typeclass = "typeclasses.characters.Character"

    def test_sheet_lists_augmentations(self):
        """Installed chrome appears in the sheet with its slot."""
        piece = _make_piece(self.char1, key="wired reflexes", humanity_cost=2)
        self.char1.cyberware.install(piece)
        output = self.call(CmdSheet(), "")
        self.assertIn("wired reflexes", output.lower())
        self.assertIn("Augmentations", output)

    def test_sheet_shows_total_humanity_cost(self):
        """The sheet shows the total Humanity spent on chrome."""
        self.char1.cyberware.install(
            _make_piece(self.char1, slot="eyes", key="cybereyes", humanity_cost=1)
        )
        self.char1.cyberware.install(
            _make_piece(self.char1, slot="skin", key="dermal plating", humanity_cost=2)
        )
        output = self.call(CmdSheet(), "")
        self.assertIn("3", output)  # total cost 1 + 2

    def test_sheet_shows_obsession(self):
        """When obsessed, the sheet surfaces the active obsession state."""
        self.char1.cyberware.install(
            _make_piece(self.char1, slot="skull", mods={}, humanity_cost=8, key="big chrome")
        )
        output = self.call(CmdSheet(), "")
        self.assertIn("Obsession", output)
