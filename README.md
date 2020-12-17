# TypoFinder

Find possible typos from GitHub repository or local directory.

![](https://github.com/minho42/typofinder/blob/master/screenshot.png)

## Requirement

Python 3.6

## Usage

Copy the source code

```
git clone https://github.com/minho42/typofinder.git
cd typofinder/
```

Optional: Use virtual environment

```
python -m venv venv
source venv/bin/activate
```

Install required packages

```
pip install -r requirements.txt
```

Run the Python interpreter and download "wordnet". For more information, see [Installing NLTK Data](https://www.nltk.org/data.html)

```
python
>>> import nltk
>>> nltk.download("wordnet")
```

Finally, run the script

```
python __main__.py [GitHub repository]
python typofinder.py https://github.com/minho42/healthroster --min=11 --report=False
```

[GitHub repository] can be :

1. Full repository URL e.g. `https://github.com/django/django`
2. Shortened repository name e.g. `gh:django/django`
3. or local directory e.g. `/Users/minho/projects/django`

## Output

Highly likely typos are marked with '\*'
