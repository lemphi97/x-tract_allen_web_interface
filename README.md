# X-Tract Allen web interface
A web interface to query experiment data from the [Allen SDK](https://allensdk.readthedocs.io/en/latest/) mouse connectivity project 
and helps identifying region of interest (ROI) for fiber crossing in the brain. 

![interface](/web/static/img/interface_pic.PNG "Interface home page")

> This application was developed with the help of my supervisor 
> [Joël Lefebvre](https://github.com/joe-from-mtl) for my internship during summer 2020.

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
```
conda env create -f environment.yml
```
* Activate your virtual environment with: 
```
conda activate xtract
```
* Install the missing dependecies with 
```
pip install -r requirements.txt
```

## Update
* On Linux or Mac, Open a terminal. On Windows, open the application `Anaconda Prompt`
* Go to the repository directory
* Update the environment with:
```
conda env update -f environment.yml
```

## Usage
* To run the web application locally, you need to execute the file `__init__.py` with your `python` executable.
    * Launch a terminal
    * Execute the file (from project root):
        * On Unix:
        ```
        python web/__init__.py
        ```
        * On Windows:
        ```
        :: Depending or your python version
        python web\__init__.py
        :: or
        python3 web\__init__.py
        ```
    * In the folder `web` is the file `config.py`. From it, easily configure the application and daemon cleaner.
    * Access the application by opening your browser of choice at the address and port in `config.py` (ex: [127.0.0.1:5000](127.0.0.1:5000) or [localhost:5000](localhost:5000))

## Contributors

| <a href="https://github.com/lemphi97" target="_blank">**Developer**</a> | <a href="https://github.com/joe-from-mtl" target="_blank">**Supervisor / Developer**</a> |
| :---: |:---:|
| [<img src="https://avatars3.githubusercontent.com/u/39384460?s=460&u=7ea26ea74a737890a77bc8357da770493081098f&v=4" width="250">](https://github.com/lemphi97) | [<img src="https://avatars1.githubusercontent.com/u/4246744?s=400&v=4" width="250">)](https://github.com/joe-from-mtl) |
| <a href="https://github.com/lemphi97" target="_blank">`github.com/lemphi97`</a> | <a href="https://github.com/joe-from-mtl" target="_blank">`github.com/joe-from-mtl`</a> |

## License

- **[Allen Institute Software License](https://github.com/AllenInstitute/AllenSDK/blob/master/LICENSE.txt)**
