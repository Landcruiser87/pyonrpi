<h1 align="center">
  <b>Py on Pi</b><br>
</h1>

<p align="center">
      <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/Python->3.11-blue" /></a>    
</p>

## Purpose
The purpose of this repo is to show how to run python scripts on a raspberry pi.  Additionally, the scripts will be controlled via bash scripts and versioned to git automatically.

## Requirements
- Python >= 3.11
- numpy
- psutil
- rich 

# Project setup with Poetry

## How to check Poetry installation

In your terminal, navigate to your root folder.

To check if poetry is installed on your system. Type the following into your terminal

```terminal
poetry -V
```

If poetry is not installed, do so in order to continue
This will install version 1.7.0.  Adjust to your preference

```terminal
curl -sSL https://install.python-poetry.org | python3 - --version 1.7.0
```

if you see a `version` returned, you have Poetry installed.  Follow this [link](https://python-poetry.org/docs/) and follow installation commands for your systems requirements. If on windows, we recommend the `powershell` option for easiest installation. Using pip to install poetry will lead to problems down the road and we do not recommend that option.  It needs to be installed separately from your standard python installation to manage your many python installations.  `Note: Python 2.7 is not supported`

## Environment storage

Some prefer Poetry's default storage method of storing environments in one location on your system.  The default storage are nested under the `{cache_dir}/virtualenvs`.  See the below image for general system location of the cache.

![Cache Directory](data/images/p_cach_dir.png)

If you want to store you virtual environment locally.  Set this global configuration flag below once poetry is installed.  This will now search for whatever environments you have in the root folder before trying any global versions of the environment in the cache.

```terminal
poetry config virtualenvs.in-project true
```

For general instruction as to poetry's functionality and commands, please see read through poetry's [cli documentation](https://python-poetry.org/docs/cli/)

To spawn a new and/or current poetry .venv

```terminal
poetry env use python #or python3
```

To install libraries

```terminal
poetry install --no-root
```

This will read from the poetry lock file that is included in this repo and install all necessary package versions.  Should other versions be needed, the project TOML file will be utilized and packages updated according to your system requirements.  

To view the all current libraries installed

```terminal
poetry show
```

To view only top level library requirements

```terminal
poetry show -T
```

## Runtime Notes

To run the extraction script, run the command

```terminal
poetry run python scripts/main.py
```

# Project setup *without* Poetry

First you would make your virtual environment and then activate it.

```terminal
python -m venv .venv

#activate the environment in your terminal 
#On Windows
.venv\Scripts\activate.bat

#On Mac
source .venv/bin/activate
```

Before next step, ensure you see the environment name to the left of your command prompt.  If you see it and the path file to your current directory, then the environment is activated.  If you don't activate it, and start installing things.  You'll install all the `requirements.txt` libraries into your base python environment. Which will lead to dependency problems down the road.  I promise.

Once activated, install the required libraries and run the script.

```terminal
pip install -r requirements.txt
python -m scripts/main.py
```
