from .typofinder import TypoFinder


def get(repo, *args, **kwargs):
    tf = TypoFinder(repo, *args, **kwargs)
    return tf.get()