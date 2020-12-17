import click

from .reporter import Reporter
from .typofinder import TypoFinder


@click.command()
@click.argument("path")
@click.option("-m", "--min", default=6, help="Minimum length of word", type=int)
@click.option("-r", "--report", default=False, help="Generate report", type=bool)
def main(path, min, report):
    tf = TypoFinder(path=path, min_len=min)
    typos = tf.get()

    if report:
        rpt = Reporter(repo_name=tf.repo_name, typos=typos)
        rpt.generate_report()


if __name__ == "__main__":
    main()
