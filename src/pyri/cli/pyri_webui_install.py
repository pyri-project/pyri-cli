import subprocess
import tempfile
from pathlib import Path
import sys
import json
import os
import appdirs
import urllib.parse
import pathlib
import pkginfo

def pip_dry_run_get_report(pip_passthrough_args, no_deps):
    with tempfile.TemporaryDirectory() as tmpdir1:
        tmpdir = Path(tmpdir1)
        pip_report_fname = tmpdir / "pip_report.json"
        pip_args = ["install", "--dry-run", "--ignore-installed", f"--report={pip_report_fname}"]
        if no_deps:
            pip_args.append("--no-deps")
        subprocess_args = [sys.executable, "-mpip"] + pip_args + pip_passthrough_args
        subprocess.check_call(subprocess_args)

        with open(pip_report_fname, "rb") as f:
            #print(f.read())
            pip_report_json = json.load(f, strict=False)

        return pip_report_json

def get_pyodide_packages():
    pyodide_repodata_filename = Path(__file__).parent / "pyodide_repodata.json"
    with open(pyodide_repodata_filename, "r") as f:
        pyodide_repodata = json.load(f, strict=False)

    pyodide_packages = [p["name"].replace("_","-").lower() for p in pyodide_repodata["packages"].values()]
    return pyodide_packages

def get_pruned_install(pip_report):
    pyodide_packages = get_pyodide_packages()

    pip_packages = []
    for p in pip_report["install"]:
        p_name = p["metadata"]["name"].replace("_","-").lower()
        if p["requested"]:
            print(f"Installing requested package {p_name}")
            pip_packages.append(p)
            continue
        if p_name in pyodide_packages:
            print(f"Not installing package {p_name}, exists in Pyodide")
            continue
        if not p["download_info"]["url"].endswith("any.whl"):
            print(f"Not installing {p_name}, not an any wheel")
            continue
        print(f"Installing package {p_name}")
        pip_packages.append(p)

    return pip_packages

def install_indirect_packages(pruned_install, webui_wheels_dir, pip_passthrough_args):
    with tempfile.TemporaryDirectory() as tmpdir1:
        tmpdir = Path(tmpdir1)
        requirements_fname = tmpdir / "requirements.txt"

        with open(requirements_fname, "w") as f:
            for p in pruned_install:
                if not p["is_direct"]:
                    remove_existing_package(p["metadata"]["name"], webui_wheels_dir)
                    print(f'{p["metadata"]["name"]}=={p["metadata"]["version"]}',file=f)

        subprocess.check_call([sys.executable, "-mpip", "download", f"-r{requirements_fname}", f"--dest={webui_wheels_dir}", "--no-deps"] + pip_passthrough_args)

def file_uri_to_path(file_uri, path_class=pathlib.Path):
    # https://stackoverflow.com/questions/5977576/is-there-a-convenient-way-to-map-a-file-uri-to-os-path
    windows_path = isinstance(path_class(),pathlib.PureWindowsPath)
    file_uri_parsed = urllib.parse.urlparse(file_uri)
    file_uri_path_unquoted = urllib.parse.unquote(file_uri_parsed.path)
    if windows_path and file_uri_path_unquoted.startswith("/"):
        result = path_class(file_uri_path_unquoted[1:])
    else:
        result = path_class(file_uri_path_unquoted)
    if result.is_absolute() == False:
        raise ValueError("Invalid file uri {} : resulting path {} not absolute".format(
            file_uri, result))
    return result

def get_existing_packages(webui_wheels_dir: Path):
    packages = dict()
    for p in webui_wheels_dir.iterdir():
        if p.suffix == ".whl":
            pkg = pkginfo.Wheel(p)
            packages[pkg.name.lower()] = p
    return packages

def remove_existing_package(package_name, webui_wheels_dir):
    existing_packages = get_existing_packages(webui_wheels_dir)
    wheel_path = existing_packages.get(package_name.lower(), None)
    if wheel_path is not None:
        wheel_path.unlink()

def install_direct_packages(pruned_install, webui_wheels_dir, pip_passthrough_args):
    for p in pruned_install:
        if p["is_direct"]:
            remove_existing_package(p["metadata"]["name"], webui_wheels_dir)
            url = p["download_info"]["url"]
            if url.startswith('file://') and file_uri_to_path(url).is_dir():
                pkg_dir = file_uri_to_path(url)
                subprocess.check_call([sys.executable, "-mpip", "wheel", f"{pkg_dir}", 
                    f"--wheel-dir={webui_wheels_dir}", "--no-deps"] + pip_passthrough_args)
            else:
                subprocess.check_call([sys.executable, "-mpip", "download", f"{url}", f"--dest={webui_wheels_dir}", 
                    "--no-deps"] + pip_passthrough_args)

           
            

def get_webui_wheels_dir():
    static_data_dir = None
    if "PYRI_WEBUI_STATIC_DATA_DIR" in os.environ:
        static_data_dir = Path(os.environ["PYRI_WEBUI_STATIC_DATA_DIR"])
    else:
        static_data_dir = Path(appdirs.user_data_dir(appname="pyri-webui-server", appauthor="pyri-project", roaming=False))

    wheels_dir =  static_data_dir / "wheels"
    wheels_dir.mkdir(exist_ok=True,parents=True)
    return wheels_dir

def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]
    pip_passthrough_args = argv
    no_deps = False
    if "--no-deps" in pip_passthrough_args:
        pip_passthrough_args.remove("--no-deps")
        no_deps = True
    pip_report = pip_dry_run_get_report(pip_passthrough_args, no_deps)
    pruned_install = get_pruned_install(pip_report)
    wheels_dir = get_webui_wheels_dir()
    install_indirect_packages(pruned_install, wheels_dir, pip_passthrough_args)
    install_direct_packages(pruned_install, wheels_dir, pip_passthrough_args)



    # print(pruned_install)

if __name__ == "__main__":
    main()