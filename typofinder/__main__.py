import sys

import click

from .typofinder import TypoFinder


@click.command()
@click.argument("path")
@click.option("-m", "--min", default=6, help="Minimum length of word")
def main(path, min):
    tf = TypoFinder(path=path, min_len=min)
    tf.find_typos()


if __name__ == "__main__":
    main()
