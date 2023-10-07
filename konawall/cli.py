# This is due a rewrite.

import os
import sys
import logging
import argparse
import screeninfo
from environment import set_environment_wallpapers, detect_environment
from module_loader import import_dir, environment_handlers, source_handlers
from imager import combine_to_viewport

def main():
    parser = argparse.ArgumentParser(
        prog="konawall",
        description="Set wallpapers from various sources on various platforms",
        epilog="If you need help with this, I'm @floofywitch on Discord and Telegram. ^^;"
    )

    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-e", "--environment", help="override the environment detection", type=str)
    parser.add_argument("-s", "--source", help="override the source provider", type=str, default="konachan")
    parser.add_argument("-c", "--count", help="override the number of wallpapers to fetch", type=int)
    parser.add_argument("-q", "--quiet", help="silence all output", action="store_true")
    parser.add_argument("tags", nargs="+")
    args = parser.parse_args()

    if args.quiet:
        sys.stdout = open(os.devnull, "w")

    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        filename="app.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.debug(f"Called with args={args}")

    import_dir(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "sources"))
    logging.debug(f"Loaded source handlers: {', '.join(source_handlers)}")
    import_dir(os.path.join(os.path.dirname(os.path.abspath( __file__ )), "environments"))
    logging.debug(f"Loaded environment handlers: {', '.join(environment_handlers)}")

    environment = detect_environment()
    environment_handlers[environment + "_init"]()

    displays = screeninfo.get_monitors()
    if not args.count:
        count = len(displays)
    else:
        count = args.count

    files = source_handlers[args.source](count, args.tags)

    if not args.environment:
        set_environment_wallpapers(environment, files, displays)
    else:
        environment_handlers[f"{args.environment}_setter"](files, displays)
        logging.debug("Wallpapers set!")


if __name__ == "__main__":
    main()