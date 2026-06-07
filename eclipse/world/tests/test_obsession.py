"""No-DB tests for the Obsession threshold table and magic mapping (AC4, AC5)."""

from django.test import TestCase
from world import magic
from world.cyberware_slots import SLOT_CAPACITY, capacity
from world.obsession import OBSESSION_THRESHOLDS, obsession_for


class ObsessionTableTest(TestCase):
    """Pure tests for the single-source-of-truth Obsession table."""

    def test_full_humanity_has_no_obsession(self):
        """At full Humanity (10) no obsession states are active."""
        self.assertEqual(obsession_for(10), [])

    def test_thresholds_are_cumulative_at_lowest(self):
        """At Humanity 0 every threshold at/above 0 is active."""
        active = obsession_for(0)
        tags = {tag for tag, _ in active}
        expected = {entry[0] for entry in OBSESSION_THRESHOLDS.values()}
        self.assertEqual(tags, expected)

    def test_obsession_returns_tag_and_penalties(self):
        """Each active entry is a (tag, penalties-dict) pair."""
        active = obsession_for(0)
        for tag, penalties in active:
            self.assertIsInstance(tag, str)
            self.assertIsInstance(penalties, dict)

    def test_higher_humanity_fewer_obsessions(self):
        """Obsession count is monotonic: lower Humanity is never milder."""
        counts = [len(obsession_for(h)) for h in range(0, 11)]
        # counts must be non-increasing as humanity rises
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_threshold_boundary(self):
        """A threshold activates at-or-below its ceiling, not above."""
        for ceiling, (tag, _penalties) in OBSESSION_THRESHOLDS.items():
            at = {t for t, _ in obsession_for(ceiling)}
            above = {t for t, _ in obsession_for(ceiling + 1)}
            self.assertIn(tag, at, msg=f"'{tag}' should be active at {ceiling}")
            self.assertNotIn(tag, above, msg=f"'{tag}' should be inactive at {ceiling + 1}")


class MagicMappingTest(TestCase):
    """Pure tests for the Magus magic penalty mapping (AC5)."""

    def test_no_penalty_at_full_humanity(self):
        """No magic penalty when Humanity is full."""
        self.assertEqual(magic.magus_magic_penalty(10), 0)

    def test_penalty_grows_as_humanity_falls(self):
        """The penalty is non-decreasing as Humanity drops."""
        penalties = [magic.magus_magic_penalty(h) for h in range(10, -1, -1)]
        self.assertEqual(penalties, sorted(penalties))

    def test_penalty_non_negative(self):
        """The penalty is never negative at any Humanity value."""
        for h in range(0, 11):
            self.assertGreaterEqual(magic.magus_magic_penalty(h), 0)


class SlotCapacityTest(TestCase):
    """Pure tests for slot capacity config (AC2)."""

    def test_known_slots_present(self):
        """All six body slots are configured."""
        self.assertEqual(
            set(SLOT_CAPACITY),
            {"eyes", "arms", "skull", "body", "nervous", "skin"},
        )

    def test_capacity_helper(self):
        """capacity() returns the configured value for a known slot."""
        self.assertEqual(capacity("arms"), SLOT_CAPACITY["arms"])

    def test_capacity_unknown_slot_raises(self):
        """An unknown slot fails fast with ValueError."""
        with self.assertRaises(ValueError):
            capacity("tail")
