"""Tests for the idempotent world build (AC6)."""

from typeclasses.rooms import DistrictRoom
from world import eclipse_build

from evennia.utils.test_resources import EvenniaTest

DISTRICT_KEYS = ("ash", "neon_sprawl", "heights", "old_quarter", "undermarket")


class WorldBuildTest(EvenniaTest):
    """AC6: build creates five Districts + a Hideout, idempotently."""

    room_typeclass = "typeclasses.rooms.Room"

    def test_build_creates_districts_and_hideout(self):
        """A single build produces five DistrictRooms and one Hideout."""
        rooms = eclipse_build.build_world()
        districts = [r for r in rooms.values() if isinstance(r, DistrictRoom)]
        self.assertEqual(len(districts), 5)
        keys = {r.db.district for r in districts}
        self.assertEqual(keys, set(DISTRICT_KEYS))
        self.assertIn("hideout", rooms)

    def test_build_is_idempotent(self):
        """Running build twice does not create duplicate rooms."""
        eclipse_build.build_world()
        first = DistrictRoom.objects.all().count()
        eclipse_build.build_world()
        second = DistrictRoom.objects.all().count()
        self.assertEqual(first, second)
        self.assertEqual(second, 5)

    def test_districts_are_linked(self):
        """Districts are walkable: each has at least one exit out."""
        rooms = eclipse_build.build_world()
        for key in DISTRICT_KEYS:
            room = rooms[key]
            exits = [obj for obj in room.contents if obj.destination]
            self.assertGreater(len(exits), 0, msg=f"district '{key}' has no exits")

    def test_traverse_and_back(self):
        """An exit and its reverse connect two rooms (edge/regression)."""
        rooms = eclipse_build.build_world()
        ash = rooms["ash"]
        exits = [obj for obj in ash.contents if obj.destination]
        dest = exits[0].destination
        back = [obj for obj in dest.contents if obj.destination == ash]
        self.assertGreater(len(back), 0, msg="no return exit found")
