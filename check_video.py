#!/usr/bin/env python3

import argparse
import os
import re
import sqlite3
import syslog
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from subprocess import PIPE, Popen, TimeoutExpired
from types import NotImplementedType
from typing import List, Self


@dataclass
class _movie_info:
    """Store class for analized movie file."""

    # Media analyse command path
    __cmd: str = ""

    def __new__(cls: type[Self]) -> Self:
        if cls.__cmd == "":
            # Find mediainfo command
            if Path("/usr/bin/mediainfo").is_file():
                cls.__cmd = "/usr/bin/mediainfo"
            elif Path("/usr/local/bin/mediainfo").is_file():
                cls.__cmd = "/usr/local/bin/mediainfo"
            else:
                raise FileNotFoundError
        return super().__new__(cls)

    def __init__(self) -> None:
        self.name = ""
        self.duration = timedelta(seconds=0)
        self.height = 0
        self.format = ""
        self.codec = ""
        self.fps = 29.970

    def __str__(self) -> str:
        return self.name

    def analyze(self, movie: str) -> Self | None:
        """Get information about specified movie.

        Args:
            movie (str): File name to send to mediainfo command.

        Returns:
            [_movie_info]: Movie information.
        """
        # print("Target: {}".format(movie))
        # opt = (
        #     "--Output=General;%FileName%/%Duration%/%Format%/"
        #     + chr(13) + "Video;%Height%/%Format%/%FrameRate%"
        # )
        opt = "--Output=file:///var/lib/misc/chech_video.template.txt"
        proc = Popen(
            [self.__cmd, opt, movie], stdin=None, stdout=PIPE, stderr=PIPE, text=True
        )
        try:
            out, _ = proc.communicate(timeout=15.0)
        except TimeoutExpired as e:
            syslog.syslog(
                syslog.LOG_WARNING,
                "{} failed for {}".format(self.__cmd, movie),
            )
            syslog.syslog(syslog.LOG_INFO, ",".join(e.cmd))
            return None

        # Split output into proper variables.
        try:
            [
                self.name,
                self.duration,
                self.format,
                self.height,
                self.codec,
                self.fps,
            ] = out.split("/")
        except ValueError:
            syslog.syslog(
                syslog.LOG_WARNING,
                "{} failed for {}".format(self.__cmd, movie),
            )
            syslog.syslog(syslog.LOG_INFO, out)
            return None

        # Round down after the decimal point
        self.duration = self.duration.split(".")[0]

        try:
            self.duration = timedelta(
                seconds=int(self.duration[:-3]), microseconds=int(self.duration[-3:])
            ) / timedelta(hours=1)
            self.duration = f"{self.duration:.3f}"
        except ValueError:
            syslog.syslog(
                syslog.LOG_WARNING,
                f"{self.__cmd} returned invalid duration for {movie}",
            )
            syslog.syslog(syslog.LOG_INFO, out)
            return None

        return self

    def get_filename(self) -> str:
        return self.name


class _db:
    def __init__(self, home: str) -> None:
        # print("DBHome: {}".format(home))
        self.home = Path(home).resolve()
        self.dbname = ""
        if not Path.is_dir(self.home):
            raise NotADirectoryError
        self.dbname = str(self.home.joinpath("movies.sqlite"))

    def init_db(self, dbname: str):
        # Make file if not exist.
        if not Path(dbname).is_file():
            syslog.syslog(
                syslog.LOG_WARNING, f"DB is not exist. So we make it to {dbname}"
            )

            # Initialize table for store datas.
            con = sqlite3.connect(self.dbname)
            cur = con.cursor()
            cur.executescript(
                """
                CREATE TABLE IF NOT EXISTS movie(
                    id INTEGER PRIMARY KEY ASC,
                    name TEXT,
                    duration REAL,
                    height INTEGER,
                    format TEXT,
                    codec TEXT,
                    fps REAL
                );
                """
            )
            cur.close
            con.close

    def search_entry(self, filename: str) -> "list[_movie_info]":
        con = sqlite3.connect(self.dbname)
        con.row_factory = sqlite3.Row
        ret: list[_movie_info] = []
        cur = con.cursor()
        cur.execute("SELECT * FROM movie WHERE name LIKE ?;", (filename + "%",))
        for row in cur.fetchall():
            r = _movie_info()
            r.name = row["name"]
            r.duration = row["duration"]
            r.height = row["height"]
            r.format = row["format"]
            r.codec = row["codec"]
            r.fps = row["fps"]
            ret.append(r)
        cur.close
        con.close

        return ret

    def add_entry(self, mi: _movie_info) -> None:
        con = sqlite3.connect(self.dbname)
        with con:
            con.execute(
                """
                insert into movie
                    (name, duration, height, format, codec, fps)
                    values (?, ?, ?, ?, ?, ?);
                """,
                (
                    mi.name,
                    mi.duration,
                    mi.height,
                    mi.format,
                    mi.codec,
                    mi.fps,
                ),
            )
        con.close

    def update_entry(self, mi: _movie_info) -> None:
        pass

    def del_entry(self, name: str) -> int:
        con = sqlite3.connect(self.dbname)
        try:
            with con:
                syslog.syslog(
                    syslog.LOG_NOTICE,
                    f"Deleting {name} from DB...",
                )
                return con.execute(f"DELETE FROM movie WHERE name='{name}';").rowcount
        except sqlite3.IntegrityError:
            syslog.syslog(syslog.LOG_ERR, f"Entry {name} cannot delete")
            return -1
        finally:
            con.close

    def vacuum_table(self) -> None:
        con = sqlite3.connect(self.dbname)
        try:
            with con:
                syslog.syslog(syslog.LOG_NOTICE, "Execute vacuum command on DB...")
                con.execute("VACUUM;")
        except sqlite3.IntegrityError:
            syslog.syslog(syslog.LOG_ERR, "Cannot vacuum DB!")
        finally:
            con.close

    def get_all_entry(self) -> "list[str]":
        con = sqlite3.connect(self.dbname)
        ret: list[str] = []
        with con:
            ret = con.execute("SELECT name from movie;").fetchall()
        con.close
        return ret


def main():
    syslog.openlog(facility=syslog.LOG_LOCAL2)

    def get_height_suffix(mi: _movie_info) -> str:
        """Get height information to add suffix to filename.

        Args:
            mi (_movie_info): Target file information

        Returns:
            str: 1080p/720p/Null
        """
        height = int(mi.height)
        if height == 1080:
            return ".1080p"
        elif height == 720:
            return ".720p"
        else:
            return ""

    def get_format_suffix(mi: _movie_info) -> "str":
        """Check movie format and return proper suffix

        Args:
            mi (_movie_info): Target movie file object

        Returns:
            str: extension for suffix
        """
        format: str = mi.format
        sfx_list = {
            "MPEG-4": ".mp4",
            "AVI": ".avi",
            "Windows Media": ".wmv",
            "MPEG-TS": ".ts",
            "BDAV": ".m2ts",
            "Matroska": ".mkv",
        }
        return sfx_list[format]

    def regularization(filename: Path, mi: _movie_info) -> str:
        """Regularize file name of movie.

        Args:
            filename (Path): Target file for regularization
            mi (_movie_info): media information from mediainfo command

        Returns:
            str: Regularized file name.
        """
        ret: str = ""
        basename = filename.stem
        # print("Type: {}".format(type(basename)))
        re_list: dict[str, List[None] | List[str]] = {
            # Already renamed for re-encoding.
            r"(?:720|1080)p$": [None],
            # My encording test files.
            r"_TEST[0-9]$": [None],
            # Exception handling
            r"^\[Ohys\-Raws\]": [None],
            r"^(?:\d{2}ID|[A-Z]+?)-[0-9]+?$": ["all"],
            # only lower case file names
            r"^(?P<index>[a-z]+?-\d+?$)": ["index"],
            # FC2 and other Uncencored movies
            r"FC2-PPV-[0-9]{7}$": [None],
            r"(?:10mu|1pon|carib|paco)$": [None],
            # 420POW
            r"^(?P<index>420POW-[0-9]+?)$": ["index"],
            # unwanted index number from file name.
            # 420SWEET-041.mp4
            r"^(?P<headnum>[0-9]{3})(?P<index>[A-Z]+?-[0-9]+?)$": ["index"],
            # hhd000.com_免...内容_FSDSS-027.mp4
            r"^hhd000.*内容_(?P<index>[A-Z]+?-[0-9]+?)$": ["index"],
            # xxfhd.com_IPX-416.mp4
            # xxfhd.com_原版首发_JUNY-018.mp4
            # hhd800.com_原版首发_JUL-190.mp4
            r"""^(?:xxfhd|hhd800)\.com
                _(?:原版首发_)?
                (?P<index>[A-Z]+?-[0-9]+?)$
            """: [
                "index"
            ],
            # MIDE-765_hhd000.com_免翻_墙免费访问全球最大情_色网站P_ornhub_可看收费内容.mp4
            # SNIS-383_uncensored.mp4
            r"^(?P<index>[A-Z]+?-[0-9]+?)[_@].*?$": ["index"],
            # hhd800.com@ABP-948_UNCENSORED_LEAKED.mp4
            # HDD600.COM@STARS-199_UNCENSORED_LEAKED_NOWATERMARK.mp4
            r"""^(?:hhd800|hdd600|HDD600)\.(?:com|COM)@
                (?P<index>[A-Z]+?-[0-9]+?)
                _UNCENSORED_.*?$
            """: [
                "index"
            ],
        }

        # File name regularization
        for r, idx in re_list.items():
            m = re.search(r, basename, re.X)
            if m is None:
                continue
            elif idx[0] == "index":
                # TODO: Only "index" key is allowed.
                #       more flexible pattern should be allowed
                # print("Match pattern: {}".format(m.re))
                # print("Groups: {}".format(m.groups()))
                # print("GroupDict: {}".format(m.groupdict().items()))
                # print("Index: {}".format(m.groupdict().get("index")))
                ret: str = format(m.groupdict().get("index"))
                break
            elif idx[0] == "all":
                ret: str = basename
                break
            elif idx[0] is None:
                # Action is set to None in re_list
                return filename.name

        if ret == "":
            syslog.syslog(
                syslog.LOG_WARNING,
                "Unsupported file name: {}".format(basename),
            )
            ret = basename

        # Convert alphabet to upper case.
        ret = ret.upper()

        # Add movie size suffix
        ret = ret + get_height_suffix(mi)

        # Add movie format extension
        ext = get_format_suffix(mi)
        if ext == NotImplementedType:
            syslog.syslog(
                syslog.LOG_WARNING,
                "Unknown file format: {}".format(mi.format),
            )
            ret = ret + filename.suffix
        else:
            ret = ret + ext

        return ret

    def rescan_home(dir: Path) -> None:
        for e in db.get_all_entry():
            if dir.joinpath(e[0]).resolve().is_file() is False:
                # Try find similar file.
                for t in db.search_entry(Path(e[0]).stem):
                    if dir.joinpath(t.name).resolve().is_file() is False:
                        db.del_entry(t.name)

    parser = argparse.ArgumentParser(
        description="Store movie informations and rename it proper style."
    )
    arg_group1 = parser.add_argument_group(
        "directory settings", "Specify target and DB directry this tool use."
    )
    arg_group1.add_argument(
        "--home",
        action="store",
        type=Path,
        default="/mnt/torrent/",
        help="Directory for movie file stored.",
    )
    arg_group1.add_argument(
        "--dbhome",
        action="store",
        type=Path,
        default="/var/lib/misc/",
        help="Directory for put DB. Need wrightable permission.",
    )
    arg_group1.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="Force re-analyse all files in torrent directory",
    )
    arg_group2 = parser.add_argument_group(
        "actions",
        "Specify other action instead of scan and rename target directry",
    )
    arg_group2.add_argument(
        "-d",
        "--delete",
        action="extend",
        nargs="+",
        type=str,
        metavar=("SCOH-017.mp4", "MIDE-891.1080p.mp4"),
        help="Remove record(s) from DB specified by name.",
    )
    arg_group2.add_argument(
        "-r",
        "--rescan",
        action="store_true",
        default=False,
        help="""
            Scan home directory with DB entries, And update DB.
            This option is specified, this tool check each entry
            of name column listed in DB.
            When entry file doesn't exist, delete entry from DB.
            When found file but if movie information differ from DB,
            Display warning message and do nothing.
            """,
    )
    args = parser.parse_args()

    # Set HOME directory to work with.
    syslog.syslog(syslog.LOG_INFO, f"Check files in {args.home}")
    if not Path.is_dir(args.home):
        raise NotADirectoryError
    home_entries = Path(args.home)
    os.chdir(home_entries.resolve())

    # Preparing DB.
    if not Path.is_dir(args.dbhome):
        Path.mkdir(Path(args.dbhome))
    db = _db(args.dbhome)
    db.init_db(db.dbname)

    # Delete specified entry from DB
    if args.delete is not None:
        syslog.syslog(syslog.LOG_INFO, "Delete MODE")
        for d in args.delete:
            db.del_entry(d)
        return 3

    # Rescan mode.
    if args.rescan is True:
        syslog.syslog(syslog.LOG_INFO, "Rescan MODE")
        rescan_home(home_entries.resolve())
        db.vacuum_table()
        return 4

    # Check file entries.
    target_suffix = re.compile(r".(?:avi|mp4|wmv|mkv)$")
    regularized_suffix = re.compile(
        r"^\.(?:720p\.|1080p\.)?(?:mp4|avi|wmv|ts|m2ts|mkv)$"
    )
    for e in home_entries.iterdir():
        if e.is_dir():
            continue

        listed_file_search_result: list[_movie_info] = db.search_entry(e.name)
        # print(e.name, ":", listed_file_search_result)
        if len(listed_file_search_result) > 0 and args.force is False:
            continue
        elif e.is_file() and target_suffix.search(e.name):
            file = _movie_info()
            if file.analyze(e.name) is None:
                syslog.syslog(
                    syslog.LOG_WARNING,
                    "File analyse failed({})".format(e.name),
                )
                continue
            fname = regularization(e, file)
            file.name = Path(fname).name

            # NOTE: Following code try to rename file to regularized name.
            #       BE CAREFUL or lose your file and yourself ⚠
            sr: list[_movie_info] = db.search_entry(fname)
            if (
                len(sr) == 0
                and fname != e.name
                and Path(fname).is_file() is False
                and not regularized_suffix.match(fname)
            ):
                e.chmod(0o644)
                e.rename(Path(fname))

            if len(sr) == 0:
                db.add_entry(file)

    syslog.syslog(syslog.LOG_INFO, "Movie check done. exit.")
    syslog.closelog()
    return 0


if __name__ == "__main__":
    main()
