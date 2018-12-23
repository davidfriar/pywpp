import os
import subprocess
from pathlib import Path

import click

import i3ipc
import pyinotify

i3 = i3ipc.Connection()


def run():
    """Set up and run the daemon which will listen for workspace focus changes and
    refresh the desktops on all outputs when they occur"""
    click.echo("Starting daemon...")

    watch_files()

    i3.on("workspace::focus", on_workspace_focus)
    i3.main()


def on_workspace_focus(self, e):
    refresh()


def refresh():
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
        command.append(get_workspaces_dir() / str(workspace))

    subprocess.run(command)


def watch_files():
    class EventHandler(pyinotify.ProcessEvent):
        def process_IN_MODIFY(self, event):
            click.echo("change")
            refresh()

    path = str(get_workspaces_dir())

    click.echo(path)
    wm = pyinotify.WatchManager()
    notifier = pyinotify.ThreadedNotifier(wm, EventHandler())
    wm.add_watch(path, pyinotify.IN_MODIFY, rec=True)
    notifier.start()


def get_home_dir():
    """Get application home directory"""

    return Path(os.environ.get("PYWPP_HOME"))


def get_workspaces_dir():
    """Get directory for storing images. Create if necessary"""
    path = get_home_dir() / "workspaces"
    path.mkdir(parents=True, exist_ok=True)

    return path
