import os
import subprocess
from pathlib import Path

import click
import requests
import validators.url
from dotenv import load_dotenv

from daemon import run
from mutex_option import MutuallyExclusiveOption

load_dotenv()


@click.group()
def cli():
    """CLI for managing wallpaper across multiple desktops in I3"""


@cli.command()
def daemon():
    """Run the daemon which refreshes desktop image when desktop changes"""
    click.echo("Yo dude, daemon is running")
    run()


class URL(click.ParamType):
    name = "url"

    def convert(self, value, param, ctx):
        if not validators.url(value):
            self.fail("This does not appear to be a valid url: " + value)

        return value


@cli.command()
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["url", "random"],
)
@click.option(
    "-u",
    "--url",
    type=URL(),
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["file", "random"],
)
@click.option(
    "-r",
    "--random",
    default="",
    cls=MutuallyExclusiveOption,
    mutually_exclusive=["file", "url"],
)
def set(file, url, random):
    """Set the wallpaper background image for the current desktop"""

    if file:
        display_wallpaper(Path(file))

    if url:
        r = requests.get(url, stream=True)
        name = url.split("/")[-1]
        path = get_image_dir() / name

        if r.status_code == 200:
            with open(path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        display_wallpaper(path)


def display_wallpaper(path):
    command = ["feh", "--bg-fill", path]
    subprocess.run(command)
    saveFile(path)


def saveFile(path):
    if not path.parent.samefile(get_image_dir()):
        link = get_image_dir() / path.name
        link.symlink_to(path)


@cli.command()
def select():
    """Open an image browser to select a background image for the
    current desktop """
    command = os.environ.get("PYWPP_IMAGE_VIEWER").split(" ")
    paths = list(
        map(
            lambda p: Path(p),
            os.environ.get("PYWPP_IMAGE_BROWSE_PATH").split(os.pathsep),
        ))

    for path in paths:
        command.append(str(path))

    proc = subprocess.run(command, capture_output=True, text=True)
    selected = Path(proc.stdout.splitlines()[-1])
    display_wallpaper(selected)


def get_home_dir():
    """Get application home directory"""

    return Path(os.environ.get("PYWPP_HOME"))


def get_image_dir():
    """Get directory for storing images. Create if necessary"""
    path = get_home_dir() / "images"
    path.mkdir(parents=True, exist_ok=True)

    return path
