import subprocess

import click
import i3ipc

i3 = i3ipc.Connection()


def run():
    """Set up and run the daemon which will listen for workspace focus changes and
    refresh the desktops on all outputs when they occur"""
    click.echo("Starting daemon...")
    i3.on("workspace::focus", on_workspace_focus)
    i3.main()


def on_workspace_focus(self, e):
    refresh_wallpaper(get_visible_workspaces())


def get_visible_workspaces():
    """Return a list of output names, ordered by x position"""

    return list(
        map(
            lambda w: w.num,
            sorted(
                filter(lambda w: w.visible, i3.get_workspaces()),
                key=lambda w: w.rect.x),
        ))


def refresh_wallpaper(workspaces):
    command = ["feh", "--bg-fill"]

    for workspace in workspaces:
        command.append(f"/home/david/wallpaper/workspaces/{workspace}")

    subprocess.run(command)
