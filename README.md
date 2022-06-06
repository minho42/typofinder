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

Run below script to download nltk "wordnet", etc.

```
$ python download_wordnet.py
```

Finally, run the script

```
$ python __main__.py [GitHub repository]
```

[GitHub repository] can be :

1. Full repository URL e.g. `https://github.com/django/django`
2. Shortened repository name e.g. `gh:django/django`
3. or local directory e.g. `/Users/minho/projects/django`

## Options
```
$ python __main__.py --help
```

Run with options
```
$ python __main__.py [GitHub repository] --min=8 --report=True
```

## Output

Highly likely typos are marked with '\*'
