"""Magus chrome-vs-magic penalty mapping.

Pure function expressing the tension between chrome and magic: as a Magus
loses Humanity to cyberware, their magic capability degrades. Only applied
to Runners of Class ``magus``; the handler is responsible for that gate.
"""

# Magic capability lost per full point of Humanity below maximum.
MAGIC_PENALTY_PER_HUMANITY = 1
HUMANITY_MAX = 10


def magus_magic_penalty(humanity_current):
    """Return the magic penalty for a Magus at a given Humanity.

    The penalty grows as Humanity falls and is floored at 0 so it can never
    become a bonus. Callers must floor the resulting magic value at 0 too.

    Args:
        humanity_current (int): The Magus's current Humanity (0-10).

    Returns:
        int: A non-negative magic penalty (0 at full Humanity).
    """
    lost = max(0, HUMANITY_MAX - humanity_current)
    return lost * MAGIC_PENALTY_PER_HUMANITY
