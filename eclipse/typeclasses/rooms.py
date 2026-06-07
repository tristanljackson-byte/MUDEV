"""Rooms.

Rooms are containers with no location of their own. Eclipse City adds the
:class:`DistrictRoom`, a hub room carrying a ``district`` key identifying
which of the five Districts it belongs to.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """Base room for Eclipse City.

    Behaves like a standard Evennia room; exists so all game rooms share a
    single project-owned base for future extension.
    """

    pass


class DistrictRoom(Room):
    """A District hub room.

    Carries a ``db.district`` key identifying which of the five Districts
    (``ash``, ``neon_sprawl``, ``heights``, ``old_quarter``,
    ``undermarket``) this room represents.
    """

    @property
    def district(self):
        """The District key this room belongs to.

        Returns:
            str or None: The District key, or None if unset.
        """
        return self.db.district
