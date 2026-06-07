"""Minimal chargen command for choosing a Runner Class."""

from world import classes

from evennia.commands.command import Command


class CmdSetClass(Command):
    """Choose your Runner Class.

    Usage:
      setclass <class>

    Valid classes: demolitionist, face, ghost, hacker, magus, samurai.

    Your Class sets your starting attribute and skill modifiers. It can
    only be chosen once.
    """

    key = "setclass"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Validate and apply the chosen Class, guarding against re-setting."""
        caller = self.caller
        arg = self.args.strip().lower()

        if not arg:
            valid = ", ".join(classes.CLASS_KEYS)
            caller.msg(f"Usage: setclass <class>. Valid classes: {valid}.")
            return

        if caller.db.class_locked:
            caller.msg(
                f"Your Class is already set to " f"{caller.db.runner_class}. It cannot be changed."
            )
            return

        try:
            caller.apply_class(arg)
        except ValueError as err:
            caller.msg(str(err))
            return

        caller.db.class_locked = True
        display = classes.get_class(arg)["display"]
        caller.msg(f"You are now a {display}.")
