"""Characters.

The :class:`Character` typeclass is the Eclipse City *Runner*: a custom
character with a Trait-based attribute/skill system, the signature Humanity
gauge, and a Class identity drawn from :mod:`world.classes`.

"""

from world import classes

from evennia.contrib.rpg.traits import TraitHandler
from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import lazy_property

from .objects import ObjectParent

# Baseline trait definitions, applied to every new Runner before any Class
# modifiers. (key, display, base) tuples keep this a single source of truth.
ATTRIBUTES = (
    ("body", "Body", 3),
    ("agility", "Agility", 3),
    ("reaction", "Reaction", 3),
    ("strength", "Strength", 3),
    ("willpower", "Willpower", 3),
    ("logic", "Logic", 3),
    ("intuition", "Intuition", 3),
    ("charisma", "Charisma", 3),
)
SKILLS = (
    ("firearms", "Firearms", 1),
    ("stealth", "Stealth", 1),
    ("hacking", "Hacking", 1),
    ("conjuring", "Conjuring", 1),
)
HUMANITY_MAX = 10


class Character(ObjectParent, DefaultCharacter):
    """A playable Runner in Eclipse City.

    A Runner carries eight core attributes and a handful of starting skills
    (as Traits), a Humanity gauge with a Lingering buffer, and a Class
    identity stored as both a Tag and an Attribute for fast display.
    """

    @lazy_property
    def traits(self):
        """TraitHandler holding this Runner's attributes, skills and gauges.

        Returns:
            TraitHandler: The handler bound to this Character.
        """
        return TraitHandler(self)

    def at_object_creation(self):
        """Initialise a new Runner's traits and Humanity gauge.

        Adds the eight core attributes (static), the starting skills
        (counter), a Humanity gauge (``base=10, min=0``) and a Lingering
        static buffer used by :meth:`gain_lingering`.
        """
        super().at_object_creation()
        for key, name, base in ATTRIBUTES:
            self.traits.add(key, name, trait_type="static", base=base)
        for key, name, base in SKILLS:
            self.traits.add(key, name, trait_type="counter", base=base, min=0)
        self.traits.add("humanity", "Humanity", trait_type="gauge", base=HUMANITY_MAX, min=0)
        self.traits.add("lingering", "Lingering", trait_type="static", base=0)

    # -- Humanity ---------------------------------------------------------

    @property
    def humanity(self):
        """Current (true) Humanity value.

        Returns:
            int: The current value of the Humanity gauge (0-10).
        """
        return self.traits.humanity.current

    def lose_humanity(self, amount):
        """Spend Humanity, drawing from Lingering first.

        Lingering Humanity acts as a buffer: it is consumed before true
        Humanity is reduced. True Humanity floors at 0.

        Args:
            amount (int): The amount of Humanity to spend. Must be >= 0.

        Raises:
            ValueError: If ``amount`` is negative (fail fast).
        """
        if amount < 0:
            raise ValueError("lose_humanity amount must be non-negative.")
        lingering = self.traits.lingering
        absorbed = min(lingering.value, amount)
        lingering.base -= absorbed
        remainder = amount - absorbed
        humanity = self.traits.humanity
        humanity.current = max(0, humanity.current - remainder)

    def gain_lingering(self, amount):
        """Grant Lingering Humanity without exceeding the gauge maximum.

        Lingering is capped so that current Humanity plus Lingering can
        never represent more than the gauge's max (10).

        Args:
            amount (int): The amount of Lingering to grant. Must be >= 0.

        Raises:
            ValueError: If ``amount`` is negative (fail fast).
        """
        if amount < 0:
            raise ValueError("gain_lingering amount must be non-negative.")
        humanity = self.traits.humanity
        lingering = self.traits.lingering
        headroom = humanity.max - humanity.current - lingering.value
        lingering.base += max(0, min(amount, headroom))

    # -- Class ------------------------------------------------------------

    def apply_class(self, key):
        """Assign a Runner Class and apply its starting trait modifiers.

        Validation happens before any write, so an invalid key leaves the
        Runner's state untouched (fail fast, no partial application).

        Args:
            key (str): One of :data:`world.classes.CLASS_KEYS`.

        Raises:
            ValueError: If ``key`` is not a registered Class.
        """
        definition = classes.get_class(key)
        mods = definition["mods"]

        self.tags.clear(category="class")
        self.tags.add(key, category="class")
        self.db.runner_class = key

        for trait_key, delta in mods.items():
            trait = self.traits.get(trait_key)
            if trait is None:
                # Class-special trait not present at baseline (e.g. magic).
                self.traits.add(
                    trait_key,
                    trait_key.title(),
                    trait_type="static",
                    base=delta,
                )
            else:
                trait.mod += delta

    # -- Cyberware (stub) -------------------------------------------------

    @property
    def augmentations(self):
        """Installed augmentations (cyberware).

        Returns an empty list for now; the Cyberware issue will populate
        this. Present so the sheet command can call it safely.

        Returns:
            list: The installed augmentations (currently always empty).
        """
        return []
