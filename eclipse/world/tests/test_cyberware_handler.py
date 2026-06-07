"""DB-backed tests for the CyberwareHandler (AC1-AC5, AC7)."""

from world import magic
from world.obsession import obsession_for

from evennia.utils import create
from evennia.utils.test_resources import EvenniaTest


def _make_piece(slot="nervous", humanity_cost=2, mods=None, key="Chrome"):
    """Create a Cyberware object for testing.

    Args:
        slot (str): The body slot the piece occupies.
        humanity_cost (int): Humanity spent to install.
        mods (dict): Trait deltas applied while installed.
        key (str): The object key.

    Returns:
        Cyberware: A freshly created, uninstalled piece.
    """
    return create.create_object(
        "typeclasses.cyberware.Cyberware",
        key=key,
        attributes=[
            ("slot", slot),
            ("humanity_cost", humanity_cost),
            ("mods", mods if mods is not None else {"agility": 2}),
        ],
    )


class InstallTest(EvenniaTest):
    """AC1: install applies mods + Humanity cost and occupies the slot."""

    character_typeclass = "typeclasses.characters.Character"

    def test_install_applies_mods_and_cost(self):
        """Installing raises the modified trait and lowers Humanity."""
        before_ag = self.char1.traits.agility.value
        before_hum = self.char1.humanity
        piece = _make_piece(mods={"agility": 2}, humanity_cost=2)
        self.char1.cyberware.install(piece)
        self.assertEqual(self.char1.traits.agility.value, before_ag + 2)
        self.assertEqual(self.char1.humanity, before_hum - 2)
        self.assertTrue(piece.installed)
        self.assertIn(piece, self.char1.cyberware.installed_pieces)

    def test_install_creates_missing_trait(self):
        """A mod for a trait not on the Runner creates it (like magic)."""
        piece = _make_piece(slot="skull", mods={"perception": 1}, humanity_cost=1)
        self.char1.cyberware.install(piece)
        self.assertIsNotNone(self.char1.traits.get("perception"))
        self.assertEqual(self.char1.traits.get("perception").value, 1)

    def test_augmentations_property_reflects_install(self):
        """The Runner.augmentations property lists installed pieces."""
        piece = _make_piece()
        self.char1.cyberware.install(piece)
        self.assertEqual(list(self.char1.augmentations), [piece])


class FailFastTest(EvenniaTest):
    """AC2: bad installs leave traits + Humanity unchanged (no partial state)."""

    character_typeclass = "typeclasses.characters.Character"

    def _snapshot(self):
        """Capture all attribute values plus Humanity for comparison."""
        keys = (
            "body",
            "agility",
            "reaction",
            "strength",
            "willpower",
            "logic",
            "intuition",
            "charisma",
        )
        snap = {k: self.char1.traits.get(k).value for k in keys}
        snap["__humanity__"] = self.char1.humanity
        return snap

    def test_full_slot_fails_fast(self):
        """Installing into a full slot raises and changes nothing."""
        first = _make_piece(slot="nervous", mods={"reaction": 1}, humanity_cost=1)
        self.char1.cyberware.install(first)
        snap = self._snapshot()
        second = _make_piece(slot="nervous", mods={"agility": 2}, humanity_cost=2)
        with self.assertRaises(ValueError):
            self.char1.cyberware.install(second)
        self.assertEqual(self._snapshot(), snap)
        self.assertFalse(second.installed)
        self.assertNotIn(second, self.char1.cyberware.installed_pieces)

    def test_double_install_fails_fast(self):
        """Installing an already-installed piece raises and changes nothing."""
        piece = _make_piece(slot="eyes", mods={"intuition": 1}, humanity_cost=1)
        self.char1.cyberware.install(piece)
        snap = self._snapshot()
        with self.assertRaises(ValueError):
            self.char1.cyberware.install(piece)
        self.assertEqual(self._snapshot(), snap)

    def test_negative_cost_fails_fast(self):
        """A negative humanity_cost raises and changes nothing."""
        snap = self._snapshot()
        piece = _make_piece(slot="skin", mods={"body": 1}, humanity_cost=-1)
        with self.assertRaises(ValueError):
            self.char1.cyberware.install(piece)
        self.assertEqual(self._snapshot(), snap)
        self.assertFalse(piece.installed)

    def test_remove_uninstalled_fails_fast(self):
        """Removing a piece that isn't installed raises and changes nothing."""
        snap = self._snapshot()
        piece = _make_piece(slot="skin", mods={"body": 1}, humanity_cost=1)
        with self.assertRaises(ValueError):
            self.char1.cyberware.remove(piece)
        self.assertEqual(self._snapshot(), snap)


class RemoveAndReinstallTest(EvenniaTest):
    """AC3: remove reverses mods + grants Lingering; reinstall nets zero loss."""

    character_typeclass = "typeclasses.characters.Character"

    def test_remove_reverses_mods(self):
        """Removing restores the trait to its prior value."""
        before = self.char1.traits.agility.value
        piece = _make_piece(mods={"agility": 2}, humanity_cost=2)
        self.char1.cyberware.install(piece)
        self.char1.cyberware.remove(piece)
        self.assertEqual(self.char1.traits.agility.value, before)
        self.assertFalse(piece.installed)

    def test_reinstall_nets_zero_true_humanity_loss(self):
        """install -> remove -> reinstall spends Lingering first (AC3)."""
        piece = _make_piece(mods={"agility": 2}, humanity_cost=2)
        self.char1.cyberware.install(piece)
        self.assertEqual(self.char1.humanity, 8)
        self.char1.cyberware.remove(piece)
        # gain_lingering(2): true Humanity unchanged at 8, lingering buffer = 2
        self.assertEqual(self.char1.humanity, 8)
        self.assertEqual(self.char1.traits.get("lingering").value, 2)
        self.char1.cyberware.install(piece)
        # lingering absorbs the cost: true Humanity still 8, lingering exhausted
        self.assertEqual(self.char1.humanity, 8)
        self.assertEqual(self.char1.traits.get("lingering").value, 0)


class ObsessionEvaluationTest(EvenniaTest):
    """AC4: obsession tags/penalties apply and clear idempotently."""

    character_typeclass = "typeclasses.characters.Character"

    def test_obsession_applies_below_threshold(self):
        """Driving Humanity low applies the mapped obsession tags."""
        # Spend Humanity down to 2 via a costly install.
        piece = _make_piece(slot="skull", mods={}, humanity_cost=8)
        self.char1.cyberware.install(piece)
        self.assertEqual(self.char1.humanity, 2)
        active = {tag for tag, _ in obsession_for(2)}
        self.assertEqual(set(self.char1.tags.get(category="obsession", return_list=True)), active)

    def test_obsession_idempotent(self):
        """Re-evaluating obsession does not duplicate tags or penalties."""
        piece = _make_piece(slot="skull", mods={}, humanity_cost=8)
        self.char1.cyberware.install(piece)
        willpower_after_first = self.char1.traits.willpower.value
        self.char1.cyberware.evaluate_obsession()
        self.char1.cyberware.evaluate_obsession()
        self.assertEqual(self.char1.traits.willpower.value, willpower_after_first)
        tags = self.char1.tags.get(category="obsession", return_list=True)
        self.assertEqual(len(tags), len(set(tags)))

    def test_obsession_clears_on_recovery(self):
        """Recovering Humanity clears obsession tags and restores traits."""
        baseline_wp = self.char1.traits.willpower.value
        piece = _make_piece(slot="skull", mods={}, humanity_cost=8)
        self.char1.cyberware.install(piece)
        self.assertTrue(self.char1.tags.get(category="obsession", return_list=True))
        self.char1.cyberware.remove(piece)
        self.assertEqual(self.char1.humanity, 2)
        # recover fully and re-evaluate
        self.char1.lose_humanity(0)
        self.char1.traits.humanity.current = 10
        self.char1.cyberware.evaluate_obsession()
        self.assertEqual(self.char1.tags.get(category="obsession", return_list=True), [])
        self.assertEqual(self.char1.traits.willpower.value, baseline_wp)


class MagusPenaltyTest(EvenniaTest):
    """AC5: magic penalty applies only to magus and restores on recovery."""

    character_typeclass = "typeclasses.characters.Character"

    def test_magus_magic_penalised_on_install(self):
        """A Magus loses magic when installing chrome."""
        self.char1.apply_class("magus")
        base_magic = self.char1.traits.magic.value
        piece = _make_piece(slot="skull", mods={}, humanity_cost=4)
        self.char1.cyberware.install(piece)
        expected = max(0, base_magic - magic.magus_magic_penalty(self.char1.humanity))
        self.assertEqual(self.char1.traits.magic.value, expected)
        self.assertLess(self.char1.traits.magic.value, base_magic)

    def test_non_magus_unaffected(self):
        """A Samurai has no magic trait and no penalty applied."""
        self.char1.apply_class("samurai")
        piece = _make_piece(slot="skull", mods={}, humanity_cost=4)
        self.char1.cyberware.install(piece)
        self.assertIsNone(self.char1.traits.get("magic"))

    def test_magic_restored_on_removal(self):
        """Removing chrome and recovering Humanity restores magic."""
        self.char1.apply_class("magus")
        base_magic = self.char1.traits.magic.value
        piece = _make_piece(slot="skull", mods={}, humanity_cost=4)
        self.char1.cyberware.install(piece)
        self.char1.cyberware.remove(piece)
        self.assertEqual(self.char1.traits.magic.value, base_magic)

    def test_magic_floored_at_zero(self):
        """Heavy chrome never drives magic below 0."""
        self.char1.apply_class("magus")
        piece = _make_piece(slot="skull", mods={}, humanity_cost=10)
        self.char1.cyberware.install(piece)
        self.assertGreaterEqual(self.char1.traits.magic.value, 0)
