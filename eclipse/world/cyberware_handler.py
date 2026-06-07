"""Cyberware handler living on each Runner.

Manages installed chrome, enforces slot capacity, applies and reverses trait
modifiers (the single stat path, same as ``apply_class``), spends and
refunds Humanity via the Runner's own helpers, and keeps Obsession states
and the Magus magic penalty in sync with current Humanity.
"""

from world import magic
from world.cyberware_slots import capacity
from world.obsession import obsession_for

OBSESSION_CATEGORY = "obsession"


class CyberwareHandler:
    """Per-Runner manager for installed cyberware.

    Stat changes flow exclusively through the Traits system: installing a
    piece does ``trait.mod += delta`` (creating the trait if absent, exactly
    as ``apply_class`` does for ``magic``), and removal reverses it. The
    handler records what it applied so reversal is exact.

    Args:
        runner (Character): The Runner this handler is bound to.
    """

    def __init__(self, runner):
        """Bind the handler to its Runner."""
        self.runner = runner

    # -- persistence helpers ---------------------------------------------

    @property
    def installed_pieces(self):
        """The currently installed cyberware pieces.

        Returns:
            list: The installed :class:`~typeclasses.cyberware.Cyberware`.
        """
        stored = self.runner.attributes.get("cyberware_pieces", category="system", default=None)
        return list(stored) if stored else []

    def _set_installed_pieces(self, pieces):
        """Persist the installed-pieces list.

        Args:
            pieces (list): The pieces to store.
        """
        self.runner.attributes.add("cyberware_pieces", list(pieces), category="system")

    # -- slot accounting --------------------------------------------------

    def capacity(self, slot):
        """Return the capacity of a body slot.

        Args:
            slot (str): The body slot.

        Returns:
            int: The slot's capacity.
        """
        return capacity(slot)

    def slots_used(self, slot):
        """Return how many pieces currently occupy a slot.

        Args:
            slot (str): The body slot.

        Returns:
            int: The number of installed pieces in that slot.
        """
        return sum(1 for piece in self.installed_pieces if piece.slot == slot)

    # -- trait helpers ----------------------------------------------------

    def _apply_mods(self, mods):
        """Apply trait deltas, creating missing traits.

        Args:
            mods (dict): Mapping of trait key to integer delta.
        """
        for trait_key, delta in mods.items():
            trait = self.runner.traits.get(trait_key)
            if trait is None:
                self.runner.traits.add(trait_key, trait_key.title(), trait_type="static", base=0)
                trait = self.runner.traits.get(trait_key)
            trait.mod += delta

    def _reverse_mods(self, mods):
        """Reverse previously applied trait deltas.

        Args:
            mods (dict): Mapping of trait key to integer delta to undo.
        """
        for trait_key, delta in mods.items():
            trait = self.runner.traits.get(trait_key)
            if trait is not None:
                trait.mod -= delta

    # -- install / remove -------------------------------------------------

    def install(self, piece):
        """Install a piece of cyberware (fail fast, no partial state).

        Validation happens before any write: an already-installed piece, a
        full slot, or a negative Humanity cost each raise with no change.

        Args:
            piece (Cyberware): The piece to install.

        Raises:
            ValueError: On any invalid install.
        """
        if piece.installed:
            raise ValueError(f"{piece.key} is already installed.")
        if piece.humanity_cost < 0:
            raise ValueError(f"{piece.key} has an invalid (negative) Humanity cost.")
        if self.slots_used(piece.slot) >= self.capacity(piece.slot):
            raise ValueError(
                f"Your {piece.slot} slot is full; remove a piece before installing " f"{piece.key}."
            )

        piece.at_pre_install(self.runner)
        self._apply_mods(piece.mods)
        self.runner.lose_humanity(piece.humanity_cost)
        piece.installed = True
        pieces = self.installed_pieces
        pieces.append(piece)
        self._set_installed_pieces(pieces)

        self.evaluate_obsession()
        self.apply_magic_penalty()
        piece.at_post_install(self.runner)

    def remove(self, piece):
        """Remove an installed piece, reversing its effects.

        Args:
            piece (Cyberware): The piece to remove.

        Raises:
            ValueError: If the piece is not currently installed.
        """
        pieces = self.installed_pieces
        if not piece.installed or piece not in pieces:
            raise ValueError(f"{piece.key} is not installed.")

        piece.at_pre_remove(self.runner)
        self._reverse_mods(piece.mods)
        self.runner.gain_lingering(piece.humanity_cost)
        piece.installed = False
        pieces.remove(piece)
        self._set_installed_pieces(pieces)

        self.evaluate_obsession()
        self.apply_magic_penalty()
        piece.at_post_remove(self.runner)

    # -- obsession --------------------------------------------------------

    def evaluate_obsession(self):
        """Recompute Obsession tags and penalties from current Humanity.

        Idempotent: clears any previously applied obsession penalties and
        tags, then reapplies exactly those active at the current Humanity.
        Running it repeatedly never duplicates effects.
        """
        # Reverse whatever obsession penalties we last applied.
        previous = self.runner.attributes.get(
            "obsession_penalties", category="system", default=None
        )
        if previous:
            self._reverse_mods(dict(previous))
        self.runner.tags.clear(category=OBSESSION_CATEGORY)

        active = obsession_for(self.runner.humanity)
        combined = {}
        for tag, penalties in active:
            self.runner.tags.add(tag, category=OBSESSION_CATEGORY)
            for trait_key, delta in penalties.items():
                combined[trait_key] = combined.get(trait_key, 0) + delta

        self._apply_mods(combined)
        self.runner.attributes.add("obsession_penalties", combined, category="system")

    # -- magus magic ------------------------------------------------------

    def apply_magic_penalty(self):
        """Recompute the Magus magic penalty from effective Humanity.

        Only Runners of Class ``magus`` are affected. Effective Humanity
        includes Lingering, so removing chrome restores magic. Idempotent:
        reverses the last applied penalty before applying the current one.
        Magic is floored at 0.
        """
        magic_trait = self.runner.traits.get("magic")
        if magic_trait is None:
            return
        if self.runner.db.runner_class != "magus":
            return

        previous = self.runner.attributes.get("magic_penalty", category="system", default=0)
        # Reverse the previously applied penalty first.
        magic_trait.mod += previous

        effective = min(10, self.runner.humanity + self.runner.traits.lingering.value)
        penalty = magic.magus_magic_penalty(effective)
        # Never drive magic below 0.
        penalty = min(penalty, magic_trait.value)
        magic_trait.mod -= penalty
        self.runner.attributes.add("magic_penalty", penalty, category="system")
