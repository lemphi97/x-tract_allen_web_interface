# xtract
A collection of scripts, notebooks and other code for the xtract project.

## Dependencies
* [Anaconda 3](https://www.anaconda.com/distribution/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
* Python 3
* A git client to clone the repository, and pull the latest version.
  * Linux and Mac user can use the command line git client
  * Recommended clients for Windows are [Github Desktop](https://desktop.github.com/) or [Sourcetree](https://www.sourcetreeapp.com/)

## Installation
* Install [Anaconda](https://www.anaconda.com/distribution/)  (Python 3.7 version)
* Launch a terminal (or the `Anaconda Prompt` on Windows)
* Go to the source directory, and create a conda environment with:
```conda env create -f environment.yml```
* Activate your virtual environment with: `conda activate xtract`
* Install the missing dependecies with `pip install -r requirements.txt`

## Update
* On Linux or Mac, Open a terminal. On Windows, open the application `Anaconda Prompt`
* Go to the repository directory
* Update the environment with: `conda env update -f environment.yml`

## Usage
* To run the web application locally, you need to execute the file `__init__.py` with your `python` executable.
    * Launch a terminal
    * Execute the file (from project root):
        * On Unix: `python web/__init__.py`
        * On Windows: `python web\__init__.py`
    * In the folder `web` is the file `config.py`. From it, easily configure the application and daemon cleaner.
    * Access the application by opening your browser of choice at the address and port in `config.py` (ex: [127.0.0.1:5000](127.0.0.1:5000) or [localhost:5000](localhost:5000))
