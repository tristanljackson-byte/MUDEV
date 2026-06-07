"""Cyberware (chrome) item typeclass.

A :class:`Cyberware` is an installable augmentation. It carries the slot it
occupies, its Humanity cost, and the trait modifiers it grants while
installed. Per-piece behaviour is customised through the ``at_pre/at_post``
hooks so the handler never has to branch on piece type.
"""

from evennia.objects.objects import DefaultObject
from evennia.typeclasses.attributes import AttributeProperty

from .objects import ObjectParent


class Cyberware(ObjectParent, DefaultObject):
    """An installable piece of chrome.

    Attributes:
        slot (str): The body slot this piece occupies (e.g. ``eyes``).
        humanity_cost (int): Humanity spent on install / returned as
            Lingering on removal. Must be >= 0.
        mods (dict): Mapping of trait key to integer delta applied while
            installed (e.g. ``{"agility": 2}``).
        installed (bool): Whether the piece is currently installed.
    """

    slot = AttributeProperty(default="body")
    humanity_cost = AttributeProperty(default=0)
    mods = AttributeProperty(default={})
    installed = AttributeProperty(default=False)

    def at_pre_install(self, runner):
        """Hook called before this piece is installed.

        Override in subclasses or prototypes for special behaviour. Default
        is a no-op.

        Args:
            runner (Character): The Runner receiving the chrome.
        """

    def at_post_install(self, runner):
        """Hook called after this piece is installed.

        Args:
            runner (Character): The Runner that received the chrome.
        """

    def at_pre_remove(self, runner):
        """Hook called before this piece is removed.

        Args:
            runner (Character): The Runner losing the chrome.
        """

    def at_post_remove(self, runner):
        """Hook called after this piece is removed.

        Args:
            runner (Character): The Runner that lost the chrome.
        """
