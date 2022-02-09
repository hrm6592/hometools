#!/usr/bin/env python3

import argparse
import re
from os import chdir
from pathlib import Path

from torrentool.api import Torrent


def main():
    args = argparse.ArgumentParser(description="Clear operation finished torrent file.")
    args.add_argument(
        "-d",
        "--homedir",
        type=Path,
        help="Scan directly for torrent files.",
        default="/srv/storage/download/.config/transmission-daemon/torrents/",
    )
    args.add_argument(
        "-r",
        "--resumedir",
        type=Path,
        help="Directory which transmission resume file stored.",
        default="/srv/storage/download/.config/transmission-daemon/resume/",
    )
    args = args.parse_args()

    entries = Path(args.homedir)
    if not entries.is_dir:
        raise NotADirectoryError
    chdir(args.homedir)

    resumes = Path(args.resumedir)
    if not resumes.is_dir:
        raise NotADirectoryError
    resume_files = list(resumes.iterdir())

    target_suffix = re.compile(r".torrent$")
    for e in entries.iterdir():
        if not target_suffix.search(e.name):
            continue

        torrent = Torrent.from_file(e.name)
        if torrent.name is None:
            print("Torrent {} does not have name!".format(e.name))
            e.unlink()
            continue

        for f in resume_files:
            if re.search("^{}".format(re.escape(str(torrent.name))), f.name):
                break
        else:
            e.unlink()
            continue


if __name__ == "__main__":
    main()
