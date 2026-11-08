"""Regression tests for numeric Sylpheed mail and archive folder selection."""

from contextlib import redirect_stderr, redirect_stdout
from email.message import EmailMessage
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import search_mail_archive as search


class MailSearchTests(unittest.TestCase):
    def test_literal_and_regex_queries(self):
        literal = search.compile_query("Item[1].zip")
        self.assertIsNotNone(literal.search("ITEM[1].ZIP"))
        self.assertIsNone(literal.search("Item1Xzip"))
        self.assertIsNotNone(search.compile_query("\uff21\uff22\uff23").search("ABC"))
        regex = search.compile_query(r"repair|return\s+shipment", regex=True)
        self.assertIsNotNone(regex.search("RETURN SHIPMENT"))
        self.assertIsNone(regex.search("unrelated"))

    def test_invalid_arguments_fail_before_extraction(self):
        for arguments in (
            [],
            [""],
            ["   "],
            ["--regex", "["],
            ["--pattern", "["],
            ["query", "--copy"],
            ["query", "--pattern", "repair"],
            ["--list-files", "query"],
            ["--list-files", "--copy", "out"],
        ):
            with self.subTest(arguments=arguments), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    search.main(arguments)
                self.assertEqual(error.exception.code, 2)

    def test_plain_japanese_without_charset(self):
        text = "WF-1000XM4 \u4fee\u7406\u5f8c\u306b\u8fd4\u9001"
        for encoding in ("utf-8", "iso-2022-jp", "cp932"):
            with self.subTest(encoding=encoding):
                self.assertEqual(search.decode_body(text.encode(encoding), None), text)

    def test_declared_euc_jp_and_invalid_charset(self):
        text = "\u4fee\u7406\u767a\u9001"
        self.assertEqual(search.decode_body(text.encode("euc-jp"), "euc-jp"), text)
        with self.assertWarnsRegex(UnicodeWarning, "used utf-8-sig"):
            self.assertEqual(search.decode_body(text.encode(), "invalid-charset"), text)

    def test_numeric_mail_copy_and_metadata_exclusion(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            source.mkdir()
            plain = b"Subject: Repair\n\nWF-1000XM4 " + "\u4fee\u7406".encode()
            (source / "123").write_bytes(plain)
            (source / ".sylpheed_cache").write_bytes(plain)
            (source / "unrelated.txt").write_bytes(plain)
            nested = source / "nested"
            nested.mkdir()
            message = EmailMessage()
            message["Subject"] = "Delivery"
            message.set_content("<p>WF&#45;1000XM4</p>", subtype="html", cte="base64")
            (nested / "123.eml").write_bytes(message.as_bytes())
            output = io.StringIO()
            with redirect_stdout(output):
                status = search.search_messages(
                    source, search.compile_query("WF-1000XM4"), root / "downloads"
                )
            self.assertEqual(status, 0)
            self.assertIn("Scanned: 2; Matched: 2; Failed: 0", output.getvalue())
            destinations = list((root / "downloads").iterdir())
            self.assertEqual(len(destinations), 1)
            self.assertEqual((destinations[0] / "123").read_bytes(), plain)
            self.assertEqual(
                (destinations[0] / "nested" / "123.eml").read_bytes(),
                (nested / "123.eml").read_bytes(),
            )

    @unittest.skipUnless(search.DEFAULT_SEVEN_ZIP.is_file(), "7-Zip is required")
    def test_archive_scope_subfolders_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            folder = search.DEFAULT_FOLDER + "/\u304a\u8cb7\u3044\u7269\u95a2\u4fc2"
            for relative in (
                folder + "/1",
                folder + "/nested/2",
                search.DEFAULT_FOLDER + "/other/3",
                "outside/4",
            ):
                path = source / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"Subject: Test\n\nWF-1000XM4")
            archive = root / "test & mail.7z"
            subprocess.run(
                [str(search.DEFAULT_SEVEN_ZIP), "a", str(archive), "."],
                cwd=source,
                check=True,
                capture_output=True,
            )
            command = [
                sys.executable,
                str(Path(search.__file__).resolve()),
                "--archive",
                str(archive),
                "--temp-dir",
                str(root),
            ]
            result = subprocess.run(
                command + ["WF-1000XM4"], check=True, capture_output=True
            )
            self.assertIn(b"Scanned: 3; Matched: 3; Failed: 0", result.stdout)
            scoped = command + ["--folder", folder]
            result = subprocess.run(
                scoped + ["WF-1000XM4"], check=True, capture_output=True
            )
            self.assertIn(b"Scanned: 2; Matched: 2; Failed: 0", result.stdout)
            self.assertFalse((root / "downloads").exists())
            self.assertFalse(list(root.glob("MailArchiveSearch-*")))
            result = subprocess.run(
                scoped
                + [r"WF-1000XM[34]", "--regex", "--copy", str(root / "downloads")],
                check=True,
                capture_output=True,
            )
            copies = [
                path for path in (root / "downloads").rglob("*") if path.is_file()
            ]
            self.assertEqual({path.name for path in copies}, {"1", "2"})
            result = subprocess.run(
                command + ["WF-1000XM4", "--folder", "missing"], capture_output=True
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(b"No numeric MH messages", result.stderr)
            result = subprocess.run(
                command + ["--pattern", "WF-1000XM4"], check=True, capture_output=True
            )
            self.assertIn(b"Matched: 3", result.stdout)
            result = subprocess.run(
                command + ["--list-files"], check=True, capture_output=True
            )
            self.assertNotIn(b"Extracting selected folder", result.stdout)
            result = subprocess.run(
                command + ["no-such-message", "--copy", str(root / "no-matches")],
                check=True,
                capture_output=True,
            )
            self.assertIn(b"Matched: 0", result.stdout)
            self.assertFalse((root / "no-matches").exists())
            self.assertFalse(list(root.glob("MailArchiveSearch-*")))


if __name__ == "__main__":
    unittest.main()
