"""Cyberware slot capacity configuration.

Single source of truth for how many pieces of chrome each body slot can
hold. Both the handler (enforcement) and any UI read from here.
"""

# Body slot -> number of pieces it can hold.
SLOT_CAPACITY = {
    "eyes": 1,
    "arms": 2,
    "skull": 1,
    "body": 1,
    "nervous": 1,
    "skin": 1,
}


def capacity(slot):
    """Return the capacity of a body slot.

    Args:
        slot (str): One of the keys in :data:`SLOT_CAPACITY`.

    Returns:
        int: The number of pieces the slot can hold.

    Raises:
        ValueError: If ``slot`` is not a known body slot (fail fast).
    """
    try:
        return SLOT_CAPACITY[slot]
    except KeyError:
        valid = ", ".join(SLOT_CAPACITY)
        raise ValueError(f"Unknown cyberware slot '{slot}'. Valid slots: {valid}.")
