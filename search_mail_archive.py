"""Search Sylpheed messages in a selected folder of a 7-Zip backup.

Pass a search string, with --regex for a regular expression. Use --copy DIR
to save matches, or --list-files to inspect archive contents without searching.
Numeric MH message files and .eml files are searched, including subfolders.
"""

import argparse
from email import policy
from email.parser import BytesParser
from html import unescape
from pathlib import Path, PureWindowsPath
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import warnings


DEFAULT_ARCHIVE = Path(
    r"Z:\Backups\Delphinus\Mail&Settings\MailAndSettings_20241113.7z"
)
DEFAULT_SEVEN_ZIP = Path(r"D:\Program Files\7-Zip\7z.exe")
DEFAULT_FOLDER = "MailAndSettings/Sylpheed/Mailboxes/Mail/inbox"


def compile_query(query: str, regex: bool = False) -> re.Pattern[str]:
    """Match literal queries against the same normalized text as mail bodies."""
    expression = query if regex else re.escape(unicodedata.normalize("NFKC", query))
    return re.compile(expression, re.IGNORECASE)


def decode_body(payload: bytes, charset: str | None) -> str:
    """Honor declared charsets, then recognize common Japanese plain text."""
    # ISO-2022-JP escape sequences are valid ASCII, and thus also valid UTF-8.
    fallback = ("utf-8-sig", "iso-2022-jp", "cp932", "euc-jp")
    if b"\x1b$" in payload:
        fallback = ("iso-2022-jp", "utf-8-sig", "cp932", "euc-jp")
    encodings = list(
        dict.fromkeys(encoding for encoding in (charset, *fallback) if encoding)
    )
    for encoding in encodings:
        try:
            text = payload.decode(encoding)
        except UnicodeError, LookupError:
            continue
        if charset and encoding != charset:
            warnings.warn(
                f"Cannot decode declared charset {charset}; used {encoding}.",
                UnicodeWarning,
            )
        return text
    raise UnicodeError(f"Cannot decode mail body using {', '.join(encodings)}")


def search_messages(
    root: Path,
    pattern: re.Pattern[str],
    copy_to: Path | None,
    archive_root: Path | None = None,
) -> int:
    """Print archive-relative paths and optionally copy matching messages."""
    scanned = matched = failed = 0
    destination = None
    for path in root.rglob("*"):
        if not path.is_file() or not (
            path.suffix.lower() == ".eml" or re.fullmatch(r"[0-9]+", path.name)
        ):
            continue
        scanned += 1
        relative = path.relative_to(archive_root if archive_root is not None else root)
        try:
            with path.open("rb") as stream:
                message = BytesParser(policy=policy.default).parse(stream)
            texts = [str(message.get("Subject", ""))]
            for part in message.walk():
                if part.get_content_type() in ("text/plain", "text/html"):
                    payload = part.get_payload(decode=True)
                    if not isinstance(payload, bytes):
                        raise ValueError("Text part does not contain a byte payload")
                    texts.append(decode_body(payload, part.get_content_charset()))
            searchable = unicodedata.normalize("NFKC", unescape("\n".join(texts)))
        except (OSError, UnicodeError, LookupError, ValueError) as error:
            failed += 1
            print(f"ERROR reading {relative}: {error}", file=sys.stderr)
            continue

        if scanned % 500 == 0:
            print(f"Scanned {scanned} messages...", file=sys.stderr, flush=True)
        if not pattern.search(searchable):
            continue

        matched += 1
        print(f"\nFile: {relative}")
        for header in ("Date", "From", "Subject"):
            value = " ".join(str(message.get(header, "")).splitlines())
            print(f"{header}: {value}")
        if copy_to is not None:
            if destination is None:
                copy_to.mkdir(parents=True, exist_ok=True)
                destination = Path(tempfile.mkdtemp(prefix="mail-search-", dir=copy_to))
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

    print(f"\nScanned: {scanned}; Matched: {matched}; Failed: {failed}")
    if destination is not None:
        print(f"Copied to: {destination}")
    if not scanned:
        print(
            "No numeric MH messages or .eml files found in the selected folder. "
            "Use --list-files to check the folder and mail format.",
            file=sys.stderr,
        )
        return 2
    if not matched:
        print("No matching messages in the selected folder.")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "query",
        nargs="?",
        help="Text to find in subjects and bodies (case-insensitive).",
    )
    parser.add_argument(
        "--regex", action="store_true", help="Interpret the search string as a regex."
    )
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--seven-zip", type=Path, default=DEFAULT_SEVEN_ZIP)
    parser.add_argument(
        "--folder",
        default=DEFAULT_FOLDER,
        help="Folder inside the archive; includes its subfolders.",
    )
    parser.add_argument(
        "--copy",
        type=Path,
        metavar="DIR",
        help="Save matches in a new mail-search-* subfolder of DIR.",
    )
    parser.add_argument(
        "--list-files",
        action="store_true",
        help="List archive entries without extraction.",
    )
    parser.add_argument(
        "--pattern",
        help="Regular expression (alternative to QUERY --regex).",
    )
    parser.add_argument(
        "--temp-dir", type=Path, help="Parent directory for temporary extraction."
    )
    args = parser.parse_args(argv)
    if args.pattern is not None and (args.query is not None or args.regex):
        parser.error("Use QUERY [--regex] or --pattern REGEX, not both")
    query = args.pattern if args.pattern is not None else args.query
    if args.list_files:
        if args.copy is not None or query is not None or args.regex:
            parser.error("--list-files cannot be combined with search or copy options")
    elif query is None or not query.strip():
        parser.error("Provide a non-empty search string or use --list-files")
    try:
        pattern = (
            compile_query(query, args.regex or args.pattern is not None)
            if query is not None
            else None
        )
    except re.error as error:
        parser.error(f"Invalid regular expression: {error}")
    folder = PureWindowsPath(args.folder)
    if (
        folder.anchor
        or not folder.parts
        or ".." in folder.parts
        or any(character in args.folder for character in "*?:\r\n")
    ):
        parser.error(
            "--folder must be a relative archive folder without wildcards or '..'"
        )
    archive_filter = folder.as_posix() + "/*"
    for path in (args.seven_zip, args.archive):
        if not path.is_file():
            parser.error(f"File does not exist: {path}")
    if args.list_files:
        return subprocess.run(
            [str(args.seven_zip), "l", "-slt", str(args.archive), archive_filter],
            check=False,
        ).returncode

    assert pattern is not None
    # Extract once: repeated per-message extraction is expensive in solid archives.
    with tempfile.TemporaryDirectory(
        prefix="MailArchiveSearch-", dir=args.temp_dir
    ) as temporary:
        root = Path(temporary)
        print(f"Archive folder: {folder}", flush=True)
        print(f"Extracting selected folder to: {root}", flush=True)
        print("Temporary files will be removed after the search.", flush=True)
        subprocess.run(
            [
                str(args.seven_zip),
                "x",
                str(args.archive),
                f"-o{root}",
                "-y",
                archive_filter,
            ],
            check=True,
        )
        selected = root.joinpath(*folder.parts)
        return search_messages(selected, pattern, args.copy, archive_root=root)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
