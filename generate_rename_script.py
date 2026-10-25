#!/bin/env python
import argparse
import os
import re
import sys
from scrapers import DMMScraper, AVWikiScraper, AVWikiDBScraper, MissAVScraper


# --------------------------------------------------------------------
### ★★★ 要変更箇所 (ここから) ★★★
# ファイルの移動先ディレクトリ
DEST_DIR = "/mnt/share/Movies/R18/Featured/"
### ★★★ 要変更箇所 (ここまで) ★★★
# --------------------------------------------------------------------


def sanitize_filename(name: str) -> str:
    """ファイル名として使えない文字を削除し、前後の空白を取り除く"""
    sanitized = re.sub(r"[\/*?:\"<>|]", "", name)
    return sanitized.strip(" .")


def fetch_movie_info(model_number: str) -> dict | None:
    """
    利用可能なScraperを順番に試し、映画情報を取得する
    """
    print(f"  型番: {model_number}")
    scrapers = [
        DMMScraper(model_number),
        AVWikiScraper(model_number),
        AVWikiDBScraper(model_number),
        MissAVScraper(model_number),
    ]

    for scraper in scrapers:
        try:
            # 情報を取得し、タイトルがあれば成功とみなす
            info = scraper.fetch_info()
            if info and info.get("title"):
                # タイトルから取得済みの出演者名を除去
                final_title = info["title"]
                for p_name in info["performers"]:
                    final_title = final_title.replace(p_name, "")
                info["title"] = final_title.strip()
                
                print(f"  [成功] {scraper.source_name} から情報を取得しました。")
                return info
        except Exception as e:
            print(f"  [エラー] {scraper.source_name} の処理中に予期せぬエラーが発生しました: {e}")
            
    print("  [情報] Webから情報を取得できませんでした。")
    return None


def process_file(filepath: str) -> dict | None:
    """単一のファイルを処理し、成功すればコマンドと出演者情報を含む辞書を返す"""
    print("----------------------------------------")
    print(f"処理中: {filepath}")

    if not os.path.isfile(filepath):
        print("  [警告] ファイルが存在しません。スキップします。")
        return None

    filename = os.path.basename(filepath)
    match = re.search(r"([a-zA-Z0-9]+-[0-9]+)", filename)
    if not match:
        print("  [警告] 型番を抽出できませんでした。")
        return None

    model_number = match.group(1)
    
    try:
        info = fetch_movie_info(model_number)
        if not info:
            return None

        title = sanitize_filename(info["title"])
        if not title:
            print("  [情報] サニタイズ後のタイトル名が空です。")
            return None

        if info["performers"]:
            performers = sanitize_filename(" ".join(info["performers"]))
        else:
            performers = "（出演者情報なし）"

        print(f"  最終タイトル: {title}")
        print(f"  最終出演者: {performers}")

        extension = filename.split(".")[-1]
        new_filename_part = f"{performers} {title} ({model_number.upper()}).{extension}"
        new_filepath = os.path.join(DEST_DIR, new_filename_part)

        # シェルスクリプト用にパスをクォートする
        quoted_old_path = f'"{filepath}"'
        quoted_new_path = f'"{new_filepath}"'

        command = f"mv -f {quoted_old_path} {quoted_new_path}"
        print(f"  生成コマンド: {command}")

        return {"command": command, "performers": performers}

    except Exception as e:
        print(f"  [エラー] 処理中に予期せぬエラーが発生しました: {e}")
        return None


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description="動画ファイル一覧からリネーム用シェルスクリプトを生成します。"
    )
    parser.add_argument(
        "input_file",
        help="処理する動画ファイルのパスを1行ずつ記載したテキストファイル",
    )
    args = parser.parse_args()

    input_file = args.input_file
    if not os.path.isfile(input_file):
        print(f"エラー: ファイルリスト '{input_file}' が見つかりません。")
        sys.exit(1)

    # 出力するシェルスクリプトのファイル名を決定
    output_sh_file = os.path.splitext(input_file)[0] + ".sh"

    file_info_list = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            filepath = line.strip()
            if filepath:
                info = process_file(filepath)
                if info:
                    file_info_list.append(info)

    if not file_info_list:
        print("----------------------------------------")
        print("生成するリネームコマンドはありませんでした。")
        return

    # 出演者名で並べ替え
    sorted_list = sorted(file_info_list, key=lambda x: x["performers"])

    # シェルスクリプトを書き出す
    with open(output_sh_file, "w", encoding="utf-8") as f_out:
        f_out.write("#!/bin/bash\n")
        f_out.write(
            "# このスクリプトを実行する前に、内容が正しいか確認してください。\n\n"
        )
        for info in sorted_list:
            f_out.write(info["command"] + "\n")

    print("----------------------------------------")
    print(f"リネーム用シェルスクリプト '{output_sh_file}' を生成しました。")
    print("内容を確認後、ターミナルで以下のコマンドを実行してください:")
    print(f"bash '{output_sh_file}'")


if __name__ == "__main__":
    main()
