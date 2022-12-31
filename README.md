<p align="center">
<img src="./docs/figures/pyri_logo_web.svg" height="200"/>
</p>

# PyRI Open Source Teach Pendant Command Line Interface

`pyri-cli` is a command line too to manage, develop, and interact with the PyRI Open Source Teach Pendant.

## Installation

Use pip with the PyRI package server:

```
python -m pip install  --extra-index-url=https://pyri-project.github.io/pyri-package-server/ pyri-cli
```

## Usage

```
PyRI Open Source Teach Pendant Command Line Interface

positional arguments:
  {webui-install,dev}
    webui-install      Install WebUI Browser Wheels to local storage
    dev                Development utility commands

options:
  -h, --help           show this help message and exit

```

### pyri-cli webui-install

The `pyri-cli webui-install` command is used to install WebUI packages. It takes the same arguments as pip, but
installs wheels to the WebUI storage directory to be used by Pyodide instead of the Python library directory. The 
installation process filters out packages that are already part of the Pyodide distribution and binary packages that
are not available for Pyodide.

Example usage:

```
pyri-cli webui-install --extra-index-url=https://pyri-project.github.io/pyri-package-server/ pyri-robotics-browser pyri-webui-browser pyri-vision-browser 
```
By default, the wheel directory is set to `%LOCALAPPDATA%\pyri-project\pyri-webui-server\wheels` on Windows
and `$HOME/.local/share/pyri-webui-server/wheels` on Linux. This location can be overridden using the
`PYRI_WEBUI_STATIC_DATA_DIR` environmental variable. The wheels directory will be created under the directory
specified in the environmental variable. The environmental variable must be set when PyRI is run so that the directory
is used at runtime.

### pyri-cli dev

The `dev` subcommand is used to help with development of a workspace folder containing multiple PyRI packages, one
per subfolder. Typically the workspace is initialized using `vcstool` to initialize the development environment.

Usage:

```
usage: pyri-cli dev [-h] [--dev-install-runtime] [--dev-install-webui]

options:
  -h, --help            show this help message and exit
  --dev-install-runtime
                        Editable install runtime packages
  --dev-install-webui   Install WebUI packages to wheels in browser local storage
```

The `dev` subcommand checks to `pypackage.toml` file for each package for keywords `pyri-runtime-package` and/or
`pyri-webui-package` to determine if the package is intended for the runtime or WebUI. Runtime packages are
editable installed on the local virtual environment, while WebUI packages are packed into wheels and copied to the
WebUI wheels directory, as described in the `webui-install` subcommand.

Example usage:

```
c:\python39\python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip

python -m pip install vcstool
vcs import --input https://raw.githubusercontent.com/pyri-project/pyri-core/master/pyri.repos

python -m pip install -e pyri-cli -e pyri-common

python -m pip install requests
python pyri-webui-resources\tools\install_npm_deps.py
python pyri-webui-resources\tools\install_pyodide.py

pyri-cli dev --dev-install-runtime --dev-install-webui

```

The `pyri-webui-resources` scripts only need to be run once, unless the contents of the resource package is updated.

Because an editable install is used, any changes to the runtime packages will be immediately applied. If changes
to `pypackage.toml` or `setup.py` are made, it is necessary to run `pyri-cli --dev-install-runtime` again. For the
WebUI packages, it is necessary to rerun `pyri-cli --dev-install-webui` to pack the wheels for the browser when
the packages are modified.

## Acknowledgment

This work was supported in part by Subaward No. ARM-TEC-21-01-F-19 from the Advanced Robotics for Manufacturing ("ARM") Institute under Agreement Number W911NF-17-3-0004 sponsored by the Office of the Secretary of Defense. ARM Project Management was provided by Christopher Adams. The views and conclusions contained in this document are those of the authors and should not be interpreted as representing the official policies, either expressed or implied, of either ARM or the Office of the Secretary of Defense of the U.S. Government. The U.S. Government is authorized to reproduce and distribute reprints for Government purposes, notwithstanding any copyright notation herein.

This work was supported in part by the New York State Empire State Development Division of Science, Technology and Innovation (NYSTAR) under contract C160142. 

![](docs/figures/arm_logo.jpg) ![](docs/figures/nys_logo.jpg)

PyRI is developed by Rensselaer Polytechnic Institute, Wason Technology, LLC, and contributors.


