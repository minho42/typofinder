import click

from .reporter import Reporter
from .typofinder import TypoFinder


# TODO How to accept extensions in a list e.g. --extensions=txt,html
@click.command()
@click.argument("path")
@click.option("-m", "--min", default=6, help="Minimum length of word", type=int)
@click.option("-r", "--report", default=False, help="Generate report", type=bool)
@click.option(
    "-e",
    "--extensions",
    default=[],
    help="Extensions to check",
    multiple=True,
)
def main(path, min, report, extensions):
    tf = TypoFinder(repo=path, min_len=min, extensions=extensions)
    typos = tf.get()

    if report:
        rpt = Reporter(repo_name=tf.repo_name, typos=typos)
        rpt.generate_report()


if __name__ == "__main__":
    main()
