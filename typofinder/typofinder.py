import os
import re
import sys
from collections import defaultdict
from multiprocessing import Pool, Value
from typing import DefaultDict, List, Union
from urllib import parse

import click
import git
from halo import Halo
from nltk.corpus import wordnet as wn

from .utils import timeit, trim_trailing_slash

counter = 0
total = 0

GH_URL = "https://github.com"
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
EXCLUDE_LIST = [
    "data/exclude_django.txt",
    "data/exclude_list.txt",
    "data/exclude_lorem_ipsum.txt",
]

WORD_MAX_LEN = 16
COINED_WORD_MIN_LEN = 2
OCCURRENCE_COUNT_LIMIT = 3
# Need to use lowercase for file names and directories
CLONED_REPO_DIR = "cloned_repos"
INCLUDE_EXTENSIONS = [
    # "c",
    # "cxx",
    # "h",
    "htm",
    "html",
    # "js",
    # "py",
    "readme",
    "md",
    "rst",
    "rtf",
    # "sh",
    # "ts",
    "txt",
    # "xhtml",
    "yaml",
    "yml",
]
EXCLUDE_FILES = [
    "lorem_ipsum.py",  # django
    "svnmap",  # cpython
    "requirements",
    "license",
    "authors",
]  # File names without extensions
EXCLUDE_DIRS = [
    "test",
    "tests",
    "vendor",  # django
    "svntogit",  # djangoproject
    "data",
    "bin",
    "env",
    "venv",
    "__pycache__",
    ".git",
    "locale",
    "node_modules",
    "requirements",
    "static",
]

CONSECUTIVE_CHARS_RE = re.compile(r"(([A-Za-z])\2{3,})")  # e.g. 'aaaa', 'loooong',
URL_RE = re.compile(r"(?:http[s]?|HTTP[S]?)://([\w.\-/:=%&+?]+)")
EMAIL_RE = re.compile(r"[\w.-]+@.*\.[\w.-]+")
HTML_ATTRIBUTE_CLASS_RE = re.compile(r"<[\w.-]+.*class\s{0,}=\s{0,}([\'\"])(.+?)\1")
HTML_ATTRIBUTE_COLOR_RE = re.compile(r"<[\w.-]+.*color\s{0,}=\s{0,}([\'\"])(.+?)\1")
HTML_ATTRIBUTE_HREF_RE = re.compile(r"<[\w.-]+.*href\s{0,}=\s{0,}([\'\"])(.+?)\1")
HTML_ATTRIBUTE_SRC_RE = re.compile(r"<[\w.-]+.*src\s{0,}=\s{0,}([\'\"])(.+?)\1")


class TypoFinder(object):
    def __init__(
        self, repo: str, min_len: int = 6, extensions: list = INCLUDE_EXTENSIONS
    ) -> None:
        if min_len < 6:
            min_len = 6

        assert WORD_MAX_LEN > min_len

        self.path = trim_trailing_slash(repo)
        self.original_path = self.path
        self.min_len = min_len
        self.extensions = extensions if extensions else INCLUDE_EXTENSIONS
        self.all_words = defaultdict(int)
        self.typo_list = set()
        self.en_dictionary_list = set()
        self.repo_name = os.path.basename(self.path)

        def _load_typo() -> None:
            name = "data/typo_list.txt"
            with open(os.path.join(BASE_DIR, name)) as file:
                self.typo_list = set(line.strip().lower() for line in file)
            assert len(self.typo_list) > 0

        def _load_en_dictionary() -> None:
            name = "data/en_dictionary.txt"
            with open(os.path.join(BASE_DIR, name)) as file:
                self.en_dictionary_list = set(line.strip().lower() for line in file)
            assert len(self.en_dictionary_list) > 0

        def _load_exclude_list() -> None:
            for name in EXCLUDE_LIST:
                with open(os.path.join(BASE_DIR, name)) as file:
                    self.en_dictionary_list.update(
                        line.strip().lower() for line in file
                    )

        def _load_all_data() -> None:
            _load_typo()
            _load_en_dictionary()
            _load_exclude_list()

        def _git_clone_repo() -> None:
            repo_dir = os.path.join(BASE_DIR, f"{CLONED_REPO_DIR}/{self.repo_name}")

            if os.path.exists(repo_dir):
                print(f"Repo already exists.")
                print(f"Trying: 'git pull [{repo_dir}]'")
                g = git.cmd.Git(repo_dir)
                pulled = g.pull()
                print(pulled)

            else:
                spinner = Halo(
                    text=f"Cloning repo to [{repo_dir}]",
                    text_color="green",
                    color="green",
                    spinner="dots",
                )
                try:
                    spinner.start()
                    try:
                        git.Repo.clone_from(self.path, repo_dir)
                        spinner.stop_and_persist(
                            symbol="", text=f"Repo cloned to [{repo_dir}]"
                        )
                    except git.GitCommandError:
                        print(f"git.GitCommandError: git.Repo.clone_from")
                        spinner.stop()
                except (KeyboardInterrupt, SystemExit):
                    spinner.stop()

            # This should come at the below if block
            self.path = repo_dir

        def _is_github_repo_full(path: str) -> bool:
            return path[: len(GH_URL)] == GH_URL

        def _is_github_repo_short(path: str) -> bool:
            # gh:[username]/[repository] e.g. 'gh:minho42/typofinder'
            gh_short = "gh:"
            return path[: len(gh_short)] == gh_short

        def _convert_to_full_gh_url(short):
            short = short.replace("gh:", "")
            return parse.urljoin(GH_URL, short)

        _load_all_data()

        # Allowed paths:
        # 1. GitHub repository e.g. 'https://github.com/minho42/typofinder'
        # 2. GitHub repository short 'gh:[username]/[repository]' e.g. 'gh:minho42/typofinder'
        # 3. Local directory e.g. '/Users/username/projects/myapp'

        if _is_github_repo_full(self.path):
            _git_clone_repo()
        elif _is_github_repo_short(self.path):
            self.path = _convert_to_full_gh_url(self.path)
            _git_clone_repo()

        if not os.path.exists(self.path):
            print(f"Path not exist: {self.path}")
            raise OSError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.path}>"

    def _is_to_collect(self, word: str, line: str) -> bool:
        line = line.lower()

        def _is_hex(word: str) -> bool:
            # e.g. 0xfffff
            pass

        def _is_out_of_length(word: str) -> bool:
            return len(word) < self.min_len or len(word) > WORD_MAX_LEN

        def _is_exist(word: str) -> bool:
            # Not being called due to visited_words checks
            return word in self.all_words

        def _is_plural_exist(word: str) -> bool:
            return f"{word}s" in self.all_words

        def _is_singular_exist(word: str) -> bool:
            return word[-1:] == "s" and word[:-1] in self.all_words

        def _is_consecutive_chars(word: str) -> bool:
            # e.g. aaaa, xxxx, xxxxxxxx
            return any(r[0] in word for r in CONSECUTIVE_CHARS_RE.findall(line))

        def _is_url(word: str) -> bool:
            return any(word in r for r in URL_RE.findall(line))

        def _is_email(word: str) -> bool:
            return any(word in s for r in EMAIL_RE.findall(line) for s in r)

        # TODO test regex with multiple class attributes
        def _is_html_attribute(word: str) -> bool:
            return (
                any(word in r[1] for r in HTML_ATTRIBUTE_CLASS_RE.findall(line))
                or any(word in r[1] for r in HTML_ATTRIBUTE_COLOR_RE.findall(line))
                or any(word in r[1] for r in HTML_ATTRIBUTE_HREF_RE.findall(line))
                or any(word in r[1] for r in HTML_ATTRIBUTE_SRC_RE.findall(line))
            )

        def _is_test(word: str) -> bool:
            return "test" in word

        ignore_conditions = [
            _is_out_of_length,
            _is_exist,
            _is_plural_exist,
            _is_singular_exist,
            _is_consecutive_chars,
            _is_url,
            _is_email,
            _is_html_attribute,
            _is_test,
        ]

        if any([func(word) for func in ignore_conditions]):
            return False

        return True

    # @timeit
    def _collect_all_words(self) -> DefaultDict[str, int]:
        def _remove_words_endwith_xy() -> bool:
            # e.g. positionx, positiony,
            # Should be called after all words are collected
            # TODO better add "z" or "ab" as well?
            endwith_xy = []
            for word, _ in self.all_words.items():
                # There is 1 empty string in self.all_words
                if not len(word):
                    continue
                if word[-1] in "xy":
                    endwith_xy.append(word[:-1])

            for word in endwith_xy:
                # Has words that ends both with "x" and "y"
                if endwith_xy.count(word) > 1:
                    if f"{word}x" in self.all_words:
                        self.all_words.pop(f"{word}x")
                    if f"{word}y" in self.all_words:
                        self.all_words.pop(f"{word}y")

        def _get_filename(file: str) -> str:
            return file.lower().rpartition(".")[0]

        def _get_filename_extension(file: str) -> str:
            return file.split(".")[-1].lower()

        visited_words = []
        skipped_extensions = []
        opened_file_count = 0

        spinner = Halo(text_color="green", color="green", spinner="dots")
        try:
            spinner.start()

            for root, dirs, files in os.walk(self.path):
                # TODO it is possible to falsely ignore if EXCLUDE_DIRS are named as regular directories, e.g. lib, include
                for dir in dirs:
                    if dir.startswith(".") or dir in EXCLUDE_DIRS:
                        dirs.remove(dir)
                for file in files:
                    if file.startswith(".") or file in EXCLUDE_FILES:
                        files.remove(file)

                for file in files:
                    file_ext = _get_filename_extension(file)
                    if file_ext not in self.extensions:
                        if file_ext not in skipped_extensions:
                            skipped_extensions.append(file_ext)
                        continue

                    try:
                        with open(os.path.join(root, file)) as file:
                            opened_file_count += 1
                            spinner.text = f"Files checked: {opened_file_count}"
                            for line in file:
                                new_words = re.findall(r"[a-zA-Z]+", line)
                                for new_word in new_words:
                                    # split by uppercase words
                                    split_words = re.split(r"(?=[A-Z][a-z])", new_word)
                                    for word in split_words:
                                        word = word.strip().lower()
                                        if word in self.all_words:
                                            self.all_words[word] += 1
                                        if word in visited_words:
                                            continue
                                        visited_words.append(word)
                                        if self._is_to_collect(word, line):
                                            self.all_words.update({word: 0})

                    except (FileNotFoundError, UnicodeDecodeError):
                        continue

            spinner.stop_and_persist(text=f"Files checked: {opened_file_count}")
        except (KeyboardInterrupt, SystemExit):
            spinner.stop()

        _remove_words_endwith_xy()

        # skipped_extensions = sorted(skipped_extensions, key=lambda k: k)
        # print(f"Skipped extensions/files: {skipped_extensions}")
        return self.all_words

    def _get_word_if_typo(self, word: str) -> Union[str, None]:
        # To use multiprocessing.Pool.map, need to return back the given word if typo.
        # Return None if not typo.

        with counter.get_lock():
            counter.value += 1

        sys.stdout.write(f"\r{counter.value}/{total}")
        sys.stdout.flush()

        word = word.lower()

        def _is_typo_by_typo_list(word: str) -> bool:
            return word in self.typo_list

        def _is_not_typo_by_dictionary(word: str) -> bool:
            # Exact word exist
            if word in self.en_dictionary_list:
                return True
            # Plural exist
            if f"{word}s" in self.en_dictionary_list:
                return True
            # Singular exist
            if word[-1:] == "s" and word[:-1] in self.en_dictionary_list:
                return True
            return False

        def _is_not_typo_by_wordnet(word: str) -> bool:
            return wn.morphy(word)

        def _is_not_typo_coined(word: str) -> bool:
            # e.g. 'blackbox', 'sourcecode', 'templatebuiltins', 'appletvsimulator'
            if word in self.en_dictionary_list:
                return True

            matches = [
                line
                for line in self.en_dictionary_list
                if len(line) >= COINED_WORD_MIN_LEN and word.startswith(line)
            ]
            # Try longer words first by reverse sorting
            # template.builtins instead of temp.late.built.in.s
            matches = sorted(matches, key=len, reverse=True)
            for match in matches:
                if _is_not_typo_coined(word[len(match) :]):
                    return True

            return False

        # if typo is also in exclude_list (=en_dictionary_list), it's not ignored as
        # '_is_typo_by_typo_list' find typo before '_is_not_typo_by_dictionary' igrnoe
        typo_conditions = [_is_typo_by_typo_list]
        not_typo_conditions = [
            _is_not_typo_by_wordnet,
            _is_not_typo_by_dictionary,
            _is_not_typo_coined,
        ]

        if any([func(word) for func in typo_conditions]):
            return f"*{word}"

        if any([func(word) for func in not_typo_conditions]):
            return None

        # It is a typo until proven otherwise for now
        return word

    def _init_global(self, c, t) -> None:
        global counter
        global total
        counter = c
        total = t

    # TODO apply decorator conditionally?
    # @timeit
    def get(self) -> List[str]:
        def _get_typos(collected_words: DefaultDict[str, int]) -> List[str]:
            typos = []
            counter = Value("i", 0)
            total = Value("i", 0)

            # TODO ?handle RuntimeError when running the typofinder.get() without __main__
            with Pool(
                initializer=self._init_global, initargs=(counter, len(collected_words))
            ) as pool:
                typos = pool.map(self._get_word_if_typo, collected_words)
                # Remove None values as _get_word_if_typo returns None if not typo
                typos = [typo for typo in typos if typo]

            print()
            return typos

        def _get_typos_to_print(
            typos: List[str], collected_words: DefaultDict[str, int]
        ) -> List[str]:
            typos_to_print = []
            for word, count in sorted(collected_words.items()):
                # Highly likely typo
                if f"*{word}" in typos:
                    typos_to_print.append(f"*{word}")
                # Potential typo if occurs less frequently
                elif word in typos and count <= OCCURRENCE_COUNT_LIMIT:
                    typos_to_print.append(f"{word}")

            typos_to_print = sorted(typos_to_print, key=lambda k: k)
            return typos_to_print

        print(f"Collecting all words")
        collected_words = self._collect_all_words()
        print(f"{len(collected_words)} words collected")

        typos = _get_typos(collected_words)
        typos_to_print = _get_typos_to_print(typos, collected_words)
        print(f"{len(typos_to_print)} possible typos found")
        return typos_to_print