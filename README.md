# TypoFinder

Find possible typos from GitHub repository or local directory.

![](https://github.com/minho42/typofinder/blob/master/screenshot.png)

## Requirement

Python 3.6

## Usage - command line

Copy the source code

```
$ git clone https://github.com/minho42/typofinder.git
$ cd typofinder/
```

Optional: Use virtual environment

```
$ python -m venv venv
$ source venv/bin/activate
```

Install required packages

```
$ pip install -r requirements.txt
```

Run the Python interpreter and download "wordnet".

```
$ python
```

```
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download("wordnet")
```

Finally, run the script

```
$ python __main__.py [GitHub repository] --min=8 --report=False
```

[GitHub repository] can be :

1. Full repository URL e.g. `https://github.com/django/django`
2. Shortened repository name e.g. `gh:django/django`
3. or local directory e.g. `/Users/minho/projects/django`

## Options
```
$ python __main__.py --help
```

## Output

Highly likely typos are marked with '\*'
