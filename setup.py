from setuptools import setup, find_packages

with open("README.md") as file:
    long_description = file.read()

with open("requirements.txt") as file:
    install_requires = [req.strip() for req in file.readlines()]

setup(
    name="typofinder",
    version="0.0.8",
    description="Find typos from GitHub repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/minho42/typofinder",
    author="Min ho Kim",
    author_email="minho42@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="misspelling, grammar",
    package_dir={"": "typofinder"},
    packages=find_packages(where="typofinder"),
    install_requires=install_requires,
    package_data={"data": ["data/*"]},
    scripts=["download_wordnet.py"],
    entry_points={"console_scripts": ["typofinder=typofinder:main"]},
)
