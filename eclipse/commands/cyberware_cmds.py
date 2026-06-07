"""Install / remove commands for cyberware (chrome)."""

from evennia.commands.command import Command


class CmdInstall(Command):
    """Install (jack in) a piece of cyberware.

    Usage:
      install <piece>
      jack-in <piece>

    Installs chrome you are carrying, applying its stat bonuses at the cost
    of Humanity. Fails clearly if the slot is full or the piece is already
    installed.
    """

    key = "install"
    aliases = ["jack-in"]
    locks = "cmd:all()"
    help_category = "Cyberware"

    def func(self):
        """Locate the named piece and install it through the handler."""
        caller = self.caller
        if not self.args.strip():
            caller.msg("Install what? Usage: install <piece>.")
            return
        piece = caller.search(self.args.strip(), location=caller)
        if not piece:
            return
        try:
            caller.cyberware.install(piece)
        except ValueError as err:
            caller.msg(str(err))
            return
        caller.msg(f"You install {piece.key}.")


class CmdRemove(Command):
    """Remove (jack out) an installed piece of cyberware.

    Usage:
      remove <piece>
      jack-out <piece>

    Removes installed chrome, reversing its bonuses and granting Lingering
    Humanity equal to its install cost.
    """

    key = "remove"
    aliases = ["jack-out"]
    locks = "cmd:all()"
    help_category = "Cyberware"

    def func(self):
        """Locate the named installed piece and remove it through the handler."""
        caller = self.caller
        if not self.args.strip():
            caller.msg("Remove what? Usage: remove <piece>.")
            return
        arg = self.args.strip().lower()
        match = None
        for piece in caller.cyberware.installed_pieces:
            if arg in piece.key.lower():
                match = piece
                break
        if match is None:
            caller.msg(f"You have no installed cyberware matching '{self.args.strip()}'.")
            return
        try:
            caller.cyberware.remove(match)
        except ValueError as err:
            caller.msg(str(err))
            return
        caller.msg(f"You remove {match.key}.")
