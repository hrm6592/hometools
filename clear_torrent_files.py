#!/usr/bin/env python3

import argparse
import os
import re
import syslog
from pathlib import Path

from torrentool.api import Torrent


def main():
    syslog.openlog(logoption=syslog.LOG_NDELAY,  # type: ignore
                   facility=syslog.LOG_LOCAL2)  # type: ignore
    args = argparse.ArgumentParser(
        description="Clear operation finished torrent file.")
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
    if not os.path.exists(entries):
        raise NotADirectoryError
    syslog.syslog(syslog.LOG_INFO, "TorrentDir: {}".format(  # type: ignore
        args.homedir))
    os.chdir(args.homedir)

    resumes = Path(args.resumedir)
    if not resumes.is_dir():
        raise NotADirectoryError
    syslog.syslog(syslog.LOG_INFO, "ResumeDir: {}".format(  # type: ignore
        args.resumedir))
    resume_files = list(resumes.iterdir())

    target_suffix = re.compile(r".torrent$")
    for e in entries.iterdir():
        if not target_suffix.search(e.name):
            continue

        torrent = Torrent.from_file(e.name)
        # Some invalid torrent file does not have any information.
        if torrent.name is None:
            syslog.syslog(  # type: ignore
                syslog.LOG_WARNING, "Torrent {} does not have name!".format(  # type: ignore
                    e.name)
            )
            e.unlink()
            continue

        for f in resume_files:
            if re.search("^{}".format(re.escape(str(torrent.name))), f.name):
                break
        else:
            syslog.syslog(syslog.LOG_DEBUG, "Unlink {}".format(  # type: ignore
                e.name))
            e.unlink()
            continue

    syslog.syslog(syslog.LOG_INFO, "Torrent file check done. exit.")
    syslog.closelog()  # type: ignore
    return 0


if __name__ == "__main__":
    main()
