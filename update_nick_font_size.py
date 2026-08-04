#!/usr/bin/env python3

import argparse
import re
import sys
from pathlib import Path

SIZE_ATTR = "size='{{xvm-stat?15|0}}'"
LINE_PATTERN = re.compile(r'^(\s*"nickFormat(?:Left|Right)"\s*:\s*")(.*?)(".*)$')
FONT_OPEN_PATTERN = re.compile(r"<font\b[^>]*>")


def add_size_to_name_fonts(value: str) -> tuple[str, int]:
    parts: list[str] = []
    replacements = 0
    cursor = 0
    stack: list[tuple[int, int]] = []
    i = 0

    while i < len(value):
        if value.startswith("<font", i):
            tag_match = FONT_OPEN_PATTERN.match(value, i)
            if not tag_match:
                i += 1
                continue
            stack.append((tag_match.start(), tag_match.end()))
            i = tag_match.end()
            continue

        if value.startswith("</font>", i):
            if stack:
                open_start, open_end = stack.pop()
                if not stack:
                    inner = value[open_end:i]
                    open_tag = value[open_start:open_end]
                    if (
                        "{{name%." in inner
                        and "color=" in open_tag
                        and SIZE_ATTR not in open_tag
                    ):
                        parts.append(value[cursor:open_start])
                        parts.append(open_tag[:-1] + f" {SIZE_ATTR}>")
                        parts.append(inner)
                        parts.append("</font>")
                        cursor = i + len("</font>")
                        replacements += 1
            i += len("</font>")
            continue

        i += 1

    if replacements == 0:
        return value, 0

    parts.append(value[cursor:])
    return "".join(parts), replacements


def update_line(line: str) -> tuple[str, int]:
    line_ending = ""
    if line.endswith("\r\n"):
        line_ending = "\r\n"
        line = line[:-2]
    elif line.endswith("\n"):
        line_ending = "\n"
        line = line[:-1]

    match = LINE_PATTERN.match(line)
    if not match:
        return f"{line}{line_ending}", 0

    prefix, value, suffix = match.groups()
    if "{{name%." not in value:
        return f"{line}{line_ending}", 0

    updated_value, replacements = add_size_to_name_fonts(value)
    if replacements == 0:
        return f"{line}{line_ending}", 0

    return f"{prefix}{updated_value}{suffix}{line_ending}", replacements


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "playersPanel.xc の nickFormatLeft/nickFormatRight にある "
            "{{name%.16s~..}} を表示する font タグへ size 属性を追加します。"
        )
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="playersPanel.xc",
        help="更新対象ファイル。デフォルトは playersPanel.xc",
    )
    args = parser.parse_args()

    path = Path(args.path)
    original_text = path.read_text(encoding="utf-8-sig")

    updated_lines = []
    replacement_count = 0

    for line in original_text.splitlines(keepends=True):
        updated_line, replacements = update_line(line)
        updated_lines.append(updated_line)
        replacement_count += replacements

    if replacement_count == 0:
        print("変更対象はありませんでした。")
        return 0

    updated_text = "".join(updated_lines)
    path.write_text(updated_text, encoding="utf-8-sig")
    print(f"{path}: {replacement_count} 箇所を更新しました。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
