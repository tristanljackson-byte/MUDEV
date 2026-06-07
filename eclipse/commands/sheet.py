"""The character sheet command for Eclipse City Runners."""

from typeclasses.characters import ATTRIBUTES, SKILLS
from world import classes

from evennia.commands.command import Command
from evennia.utils.evtable import EvTable


class CmdSheet(Command):
    """Display your Runner's character sheet.

    Usage:
      sheet
      score

    Shows your Class, your eight core attributes and starting skills with
    their current values, your Humanity (current/max), and any installed
    augmentations.
    """

    key = "sheet"
    aliases = ["score"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Render the sheet as aligned EvTables."""
        caller = self.caller
        traits = caller.traits

        class_key = caller.db.runner_class
        class_display = classes.get_class(class_key)["display"] if class_key else "Unassigned"

        attr_table = EvTable("Attribute", "Value", border="cells")
        for key, name, _ in ATTRIBUTES:
            attr_table.add_row(name, traits.get(key).value)

        skill_table = EvTable("Skill", "Value", border="cells")
        for key, name, _ in SKILLS:
            skill_table.add_row(name, traits.get(key).value)
        magic = traits.get("magic")
        if magic is not None:
            skill_table.add_row("Magic", magic.value)

        humanity = traits.get("humanity")
        lines = [
            f"|cClass:|n {class_display}",
            str(attr_table),
            str(skill_table),
            f"|cHumanity|n {humanity.current}/{humanity.max}",
        ]

        augs = list(caller.augmentations)
        aug_text = ", ".join(str(aug) for aug in augs) if augs else "None"
        lines.append(f"|cAugmentations:|n {aug_text}")

        caller.msg("\n".join(lines))
