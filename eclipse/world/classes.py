"""Runner Class registry for Eclipse City.

This module is the single source of truth for the six playable Runner
Classes. Each entry maps a stable Class key to its display name, a short
flavour blurb, and a dict of starting trait modifiers applied at chargen.

Class differences live here as data (a registry), never as ``if class ==
...`` branches elsewhere in the codebase. Modifiers are deltas applied on
top of a Runner's baseline trait values.
"""

# All trait keys a Class is allowed to modify. Used both to validate the
# registry (tests) and to document the modifiable surface in one place.
MODIFIABLE_TRAIT_KEYS = (
    # core attributes
    "body",
    "agility",
    "reaction",
    "strength",
    "willpower",
    "logic",
    "intuition",
    "charisma",
    # starting skills
    "firearms",
    "stealth",
    "hacking",
    "conjuring",
    # class-special
    "magic",
)


# The registry. Numbers are simple, Shadowrun-inspired deltas.
CLASSES = {
    "demolitionist": {
        "display": "Demolitionist",
        "blurb": "Breachers and bombers who open doors the loud way.",
        "mods": {
            "body": 1,
            "strength": 1,
            "firearms": 1,
        },
    },
    "face": {
        "display": "Face",
        "blurb": "Smooth talkers who run the social angle of every job.",
        "mods": {
            "charisma": 2,
            "intuition": 1,
        },
    },
    "ghost": {
        "display": "Ghost",
        "blurb": "Infiltrators who get in and out unseen.",
        "mods": {
            "agility": 1,
            "reaction": 1,
            "stealth": 2,
        },
    },
    "hacker": {
        "display": "Hacker",
        "blurb": "Deckers who own the Matrix and the locks it controls.",
        "mods": {
            "logic": 2,
            "intuition": 1,
            "hacking": 2,
        },
    },
    "magus": {
        "display": "Magus",
        "blurb": "Awakened spellslingers channeling the city's residue.",
        "mods": {
            "willpower": 1,
            "magic": 2,
            "conjuring": 2,
        },
    },
    "samurai": {
        "display": "Samurai",
        "blurb": "Street samurai built for speed, steel, and gunfire.",
        "mods": {
            "body": 2,
            "agility": 2,
            "reaction": 1,
            "firearms": 1,
        },
    },
}


# Stable ordered tuple of valid Class keys.
CLASS_KEYS = tuple(CLASSES.keys())


def get_class(key):
    """Return the registry definition for a Class key.

    Args:
        key (str): One of the keys in :data:`CLASS_KEYS`.

    Returns:
        dict: The Class definition with ``display``, ``blurb`` and ``mods``.

    Raises:
        ValueError: If ``key`` is not a registered Class (fail fast).
    """
    try:
        return CLASSES[key]
    except KeyError:
        valid = ", ".join(CLASS_KEYS)
        raise ValueError(f"Unknown Runner Class '{key}'. Valid classes: {valid}.")
