import argparse
import sys

def main(argv = None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="PyRI Open Source Teach Pendant Command Line Interface")
    subparsers = parser.add_subparsers(dest="command_name", required=True)
    webui_install = subparsers.add_parser("webui-install", help="Install WebUI Browser Wheels to local storage")
    dev_parser = subparsers.add_parser('dev', help="Development utility commands")
    dev_parser.add_argument("--dev-install-runtime", action='store_true', default=False, help="Editable install runtime packages")
    dev_parser.add_argument("--dev-install-webui", action='store_true', default=False, help="Install WebUI packages to wheels in browser local storage")
    args, argv2 = parser.parse_known_args()

    if args.command_name == "webui-install":
        from . import pyri_webui_install
        pyri_webui_install.main(argv2)

    if args.command_name == "dev":
        from . import dev
        dev.main(args, argv2)