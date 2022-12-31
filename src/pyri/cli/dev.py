import argparse
import subprocess
from pathlib import Path
import sys
import toml

def _find_packages_with_keyword(kwd):
    runtime_packages = dict()

    cwd = Path('.').absolute()
    for d in cwd.iterdir():
        toml_path = d / "pyproject.toml"
        if (toml_path).is_file():
            with open(toml_path, "r") as f:
                py_toml = toml.load(f)

            py_name = py_toml["project"]["name"]
            py_kwds = py_toml["project"]["keywords"]

            if kwd in py_kwds:
                runtime_packages[py_name] = d
    print(f"Discovered packages {list(runtime_packages.keys())} for keyword {kwd}")
    return runtime_packages

def dev_install_runtime(args, argv2):

    runtime_packages = _find_packages_with_keyword("pyri-runtime-package")

    subprocess.check_call([sys.executable, "-mpip", "uninstall", "-y"] + list(runtime_packages.keys()))
    subprocess.check_call([sys.executable, "-mpip", "install"] + [f"-e{p}" for p in runtime_packages.values()])

def dev_install_webui(args, argv2):

    webui_packages = _find_packages_with_keyword("pyri-webui-browser-package")
    assert len(webui_packages) > 0, "No webui packages found!"

    from . import pyri_webui_install

    pyri_webui_install.main(list(webui_packages.values()) + argv2)

def main(args, argv2):

    if args.dev_install_runtime:
        dev_install_runtime(args, argv2)

    if args.dev_install_webui:
        dev_install_webui(args, argv2)
    

    