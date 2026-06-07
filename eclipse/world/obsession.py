"""Obsession threshold table for the Humanity gauge.

Single source of truth mapping Humanity ceilings to Obsession states. Each
state is a tag plus a set of trait penalties (negative deltas) applied while
the Runner's Humanity sits at or below that ceiling. The handler recomputes
active states idempotently from this table.
"""

# Humanity ceiling (inclusive) -> (tag_key, {trait_key: penalty_delta}).
# Lower Humanity activates more (and harsher) states cumulatively.
OBSESSION_THRESHOLDS = {
    6: ("twitchy", {"charisma": -1}),
    3: ("fracturing", {"willpower": -1, "logic": -1}),
    1: ("lost", {"willpower": -1, "intuition": -1}),
}


def obsession_for(humanity):
    """Return the Obsession states active at a given Humanity value.

    A state is active when ``humanity`` is at or below its ceiling. States
    are returned ordered from highest ceiling (mildest) to lowest.

    Args:
        humanity (int): The Runner's current Humanity (0-10).

    Returns:
        list: A list of ``(tag_key, penalties_dict)`` tuples for every
        active Obsession state. Empty when Humanity is high.
    """
    active = []
    for ceiling in sorted(OBSESSION_THRESHOLDS, reverse=True):
        if humanity <= ceiling:
            active.append(OBSESSION_THRESHOLDS[ceiling])
    return active
