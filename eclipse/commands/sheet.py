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
        lines.append("|cAugmentations:|n")
        if augs:
            aug_table = EvTable("Piece", "Slot", "Mods", border="cells")
            total_cost = 0
            for aug in augs:
                mod_text = ", ".join(f"{key} {delta:+d}" for key, delta in aug.mods.items())
                aug_table.add_row(aug.key, aug.slot, mod_text or "-")
                total_cost += aug.humanity_cost
            lines.append(str(aug_table))
            lines.append(f"Total Humanity spent on chrome: {total_cost}")
        else:
            lines.append("None")

        obsessions = caller.tags.get(category="obsession", return_list=True)
        if obsessions:
            lines.append(f"|rObsession:|n {', '.join(sorted(obsessions))}")

        caller.msg("\n".join(lines))
