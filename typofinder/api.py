from .typofinder import TypoFinder


def get(repo, min_len, extensions, *args, **kwargs):
    tf = TypoFinder(repo, min_len, extensions, *args, **kwargs)
    return tf.get()