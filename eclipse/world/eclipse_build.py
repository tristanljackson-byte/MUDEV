"""Idempotent starting-world build for Eclipse City.

Builds the five District hub rooms and a Crew Hideout, linked with named
exits. Every built object is tagged so the build can run repeatedly without
creating duplicates.
"""

from typeclasses.rooms import DistrictRoom, Room

from evennia import create_object, search_tag
from evennia.objects.objects import DefaultExit

# Tag marking every room/exit created by this build.
BUILD_TAG = "eclipse_build"
BUILD_CATEGORY = "system"

# District key -> display name. Single source of truth for the hubs.
DISTRICTS = {
    "ash": "The Ash",
    "neon_sprawl": "Neon Sprawl",
    "heights": "The Heights",
    "old_quarter": "Old Quarter",
    "undermarket": "The Undermarket",
}

# Directed links (from_key, to_key, exit_name, return_name). The Hideout
# is reached from neon_sprawl; the five Districts form a connected ring.
LINKS = (
    ("ash", "neon_sprawl", "neon", "ash"),
    ("neon_sprawl", "heights", "heights", "sprawl"),
    ("heights", "old_quarter", "oldquarter", "heights"),
    ("old_quarter", "undermarket", "undermarket", "oldquarter"),
    ("undermarket", "ash", "ash", "undermarket"),
    ("neon_sprawl", "hideout", "hideout", "out"),
)


def _find_built(key):
    """Return the already-built room with the given build key, if any.

    Args:
        key (str): The per-room build key (e.g. ``"ash"`` or ``"hideout"``).

    Returns:
        Object or None: The existing tagged room, or None.
    """
    matches = search_tag(key, category=BUILD_CATEGORY)
    return matches.first() if matches else None


def _get_or_create_room(key, name, typeclass, district=None):
    """Fetch the build-tagged room for ``key`` or create it.

    Args:
        key (str): The per-room build key, used as a unique build tag.
        name (str): The room's display name.
        typeclass (class): The room typeclass to create.
        district (str, optional): District key for DistrictRooms.

    Returns:
        Object: The existing or newly created room.
    """
    existing = _find_built(key)
    if existing:
        return existing
    room = create_object(typeclass, key=name)
    room.tags.add(BUILD_TAG, category=BUILD_CATEGORY)
    room.tags.add(key, category=BUILD_CATEGORY)
    if district is not None:
        room.db.district = district
    return room


def _ensure_exit(source, destination, name):
    """Create a named exit from ``source`` to ``destination`` if absent.

    Args:
        source (Object): The room the exit leaves from.
        destination (Object): The room the exit leads to.
        name (str): The exit's key.
    """
    for obj in source.contents:
        if obj.destination == destination and obj.key == name:
            return
    create_object(DefaultExit, key=name, location=source, destination=destination)


def build_world():
    """Build (idempotently) the Eclipse City starting world.

    Creates five District hub rooms and a Crew Hideout, then links them
    with named two-way exits. Safe to run multiple times: existing rooms
    and exits are reused rather than duplicated.

    Returns:
        dict: Mapping of build key (district key or ``"hideout"``) to the
        corresponding room object.
    """
    rooms = {}
    for key, name in DISTRICTS.items():
        rooms[key] = _get_or_create_room(key, name, DistrictRoom, district=key)
    rooms["hideout"] = _get_or_create_room("hideout", "Crew Hideout", Room)

    for from_key, to_key, exit_name, return_name in LINKS:
        source = rooms[from_key]
        destination = rooms[to_key]
        _ensure_exit(source, destination, exit_name)
        _ensure_exit(destination, source, return_name)

    return rooms
