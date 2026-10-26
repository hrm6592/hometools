#!/usr/bin/env python3
"""RSSフィードとMixcloudの新着ミックスを監視してSlackに通知します。"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_STATE_PATH = Path(".mix_feed_state.json")
REQUEST_TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class RssSource:
    """監視対象のRSSフィード。"""

    key: str
    name: str
    url: str


@dataclass(frozen=True)
class MixcloudSource:
    """監視対象のMixcloudユーザー。"""

    key: str
    name: str
    username: str


Source = RssSource | MixcloudSource


@dataclass(frozen=True)
class Track:
    """取得元にある1件のミックス情報。"""

    id: str
    title: str
    link: str
    published_at: str | None


SOURCES: list[Source] = [
    RssSource(
        key="kushsessions",
        name="KushSessions",
        url="https://feed.podbean.com/kushsessions/feed.xml",
    ),
    MixcloudSource(
        key="mixcloud_mdrt9",
        name="MDRT",
        username="mdrt9",
    ),
]


def main() -> int:
    """引数と環境変数を読み取り、監視処理を実行します。"""

    args = parse_args()
    sources = get_sources(args.feed_url)
    webhook_url = args.slack_webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    state_path = Path(args.state_path or os.getenv("STATE_PATH") or DEFAULT_STATE_PATH)

    if not webhook_url and not args.dry_run:
        print(
            "SLACK_WEBHOOK_URL が未設定です。"
            "通知するにはSlack Incoming Webhook URLを設定してください。",
            file=sys.stderr,
        )
        return 2

    previous_track_ids = load_previous_track_ids(state_path)
    latest_track_ids = previous_track_ids.copy()
    new_tracks: list[tuple[Source, Track]] = []

    for source in sources:
        latest_track = fetch_latest_track(source)
        latest_track_ids[source.key] = latest_track.id
        previous_track_id = previous_track_ids.get(source.key)

        if previous_track_id is None:
            if args.notify_on_first_run:
                new_tracks.append((source, latest_track))
            else:
                print(
                    f"初回実行のため現在の最新トラックを記録しました: "
                    f"{source.name}: {latest_track.title}"
                )
            continue

        if latest_track.id != previous_track_id:
            new_tracks.append((source, latest_track))
        else:
            print(f"新しいミックスはありません: {source.name}: {latest_track.title}")

    for source, track in new_tracks:
        notify(webhook_url, source, track, args.dry_run)
        print(f"新しいミックスを通知しました: {source.name}: {track.title}")

    if args.dry_run:
        print("dry-runのため状態ファイルは更新しません。")
    else:
        save_latest_track_ids(state_path, latest_track_ids)
    return 0


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析します。"""

    parser = argparse.ArgumentParser(
        description="RSSとMixcloudの新着ミックスを監視してSlackに通知します。"
    )
    parser.add_argument(
        "--feed-url",
        help=(
            "一時的に監視するRSSフィードURL。"
            "未指定時はスクリプト内のSOURCESを使います。"
        ),
    )
    parser.add_argument(
        "--slack-webhook-url",
        help=("Slack Incoming Webhook URL。未指定時はSLACK_WEBHOOK_URLを使います。"),
    )
    parser.add_argument(
        "--state-path",
        help=(
            "最新トラックIDを保存するJSONファイル。"
            f"既定値は {DEFAULT_STATE_PATH} です。"
        ),
    )
    parser.add_argument(
        "--notify-on-first-run",
        action="store_true",
        help="初回実行時にも現在の最新トラックをSlackへ通知します。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Slackへ投稿せず、投稿内容だけを標準出力に表示します。",
    )
    return parser.parse_args()


def get_sources(feed_url: str | None) -> list[Source]:
    """監視対象の取得元一覧を返します。"""

    if feed_url:
        return [RssSource(key="custom", name="Custom Feed", url=feed_url)]
    return SOURCES


def fetch_latest_track(source: Source) -> Track:
    """取得元に応じて最新のミックス情報を返します。"""

    if isinstance(source, RssSource):
        return fetch_latest_rss_track(source)
    return fetch_latest_mixcloud_track(source)


def fetch_latest_rss_track(source: RssSource) -> Track:
    """RSSフィードを取得し、先頭のミックス情報を返します。"""

    feed_xml = fetch_bytes(source.url, "RSSフィード")

    try:
        root = ET.fromstring(feed_xml)
    except ET.ParseError as exc:
        raise RuntimeError("RSSフィードのXMLを解析できませんでした。") from exc

    item = root.find("./channel/item")
    if item is None:
        raise RuntimeError("RSSフィードにトラック情報がありません。")

    title = get_required_text(item, "title")
    link = get_required_text(item, "link")
    guid = item.findtext("guid")
    published_at = item.findtext("pubDate")

    return Track(
        id=(guid or link).strip(),
        title=title.strip(),
        link=link.strip(),
        published_at=published_at.strip() if published_at else None,
    )


def fetch_latest_mixcloud_track(source: MixcloudSource) -> Track:
    """Mixcloud APIからユーザーの最新ミックス情報を返します。"""

    username = urllib.parse.quote(source.username, safe="")
    api_url = f"https://api.mixcloud.com/{username}/cloudcasts/?limit=1&offset=0"
    response_body = fetch_bytes(api_url, "Mixcloud API")

    try:
        payload = json.loads(response_body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Mixcloud APIのJSONを解析できませんでした。") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("Mixcloud APIのレスポンス形式が不正です。")

    data = payload.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError(f"Mixcloudに公開ミックスがありません: {source.username}")

    item = data[0]
    if not isinstance(item, dict):
        raise RuntimeError("Mixcloud APIのミックス情報が不正です。")

    return Track(
        id=get_required_json_string(item, "key", "Mixcloud API"),
        title=get_required_json_string(item, "name", "Mixcloud API"),
        link=get_required_json_string(item, "url", "Mixcloud API"),
        published_at=get_optional_json_string(item, "created_time"),
    )


def fetch_bytes(url: str, source_name: str) -> bytes:
    """URLを取得してレスポンス本文を返します。"""

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "mix-feed-slack-notifier/0.1.0"},
    )
    try:
        with urllib.request.urlopen(
            request, timeout=REQUEST_TIMEOUT_SECONDS
        ) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"{source_name}を取得できませんでした: {url}") from exc


def get_required_text(element: ET.Element, tag_name: str) -> str:
    """必須テキスト要素を取得します。"""

    value = element.findtext(tag_name)
    if not value or not value.strip():
        raise RuntimeError(f"RSSフィードの item に {tag_name} がありません。")
    return value


def get_required_json_string(data: dict[str, Any], key: str, source_name: str) -> str:
    """JSONオブジェクトから必須文字列を取得します。"""

    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{source_name}の {key} が不正です。")
    return value.strip()


def get_optional_json_string(data: dict[str, Any], key: str) -> str | None:
    """JSONオブジェクトから任意文字列を取得します。"""

    value = data.get(key)
    return value.strip() if isinstance(value, str) and value.strip() else None


def load_previous_track_ids(state_path: Path) -> dict[str, str]:
    """状態ファイルから前回確認した最新トラックID一覧を読み込みます。"""

    if not state_path.exists():
        return {}

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"状態ファイルのJSONを解析できませんでした: {state_path}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError(f"状態ファイルの形式が不正です: {state_path}")

    feeds = data.get("feeds")
    if isinstance(feeds, dict):
        if not all(
            isinstance(feed_key, str)
            and feed_key.strip()
            and isinstance(track_id, str)
            and track_id.strip()
            for feed_key, track_id in feeds.items()
        ):
            raise RuntimeError(f"状態ファイルのfeedsが不正です: {state_path}")
        return {feed_key: track_id for feed_key, track_id in feeds.items()}

    if "feeds" in data:
        raise RuntimeError(f"状態ファイルのfeedsが不正です: {state_path}")

    # 旧形式の状態ファイルからの移行用。
    track_id = data.get("latest_track_id")
    if isinstance(track_id, str) and track_id.strip():
        return {SOURCES[0].key: track_id}

    if "latest_track_id" in data:
        raise RuntimeError(f"状態ファイルのlatest_track_idが不正です: {state_path}")

    return {}


def save_latest_track_ids(state_path: Path, track_ids: dict[str, str]) -> None:
    """最新トラックID一覧を状態ファイルに保存します。"""

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"feeds": track_ids}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def notify(
    webhook_url: str | None, source: Source, track: Track, dry_run: bool
) -> None:
    """Slackへ新しいトラック情報を投稿します。"""

    payload = build_slack_payload(source, track)
    if dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    if webhook_url is None:
        raise RuntimeError("Slack Webhook URLが未設定です。")

    request = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(
            request, timeout=REQUEST_TIMEOUT_SECONDS
        ) as response:
            if response.status >= 400:
                raise RuntimeError(f"Slack通知に失敗しました: HTTP {response.status}")
    except urllib.error.URLError as exc:
        raise RuntimeError("Slack通知リクエストに失敗しました。") from exc


def build_slack_payload(source: Source, track: Track) -> dict[str, Any]:
    """Slack Incoming Webhook用のペイロードを組み立てます。"""

    fields = [
        {"type": "mrkdwn", "text": f"*取得元:*\n{source.name}"},
        {"type": "mrkdwn", "text": f"*タイトル:*\n{track.title}"},
        {"type": "mrkdwn", "text": f"*取得元URL:*\n{get_source_url(source)}"},
    ]
    if track.published_at:
        fields.insert(
            2,
            {"type": "mrkdwn", "text": f"*公開日時:*\n{track.published_at}"},
        )

    message = (
        f":sound: *{source.name}に新しいミックスが登録されました*\n"
        f"<{track.link}|{track.title}>"
    )

    return {
        "text": f"{source.name}に新しいミックスが登録されました: {track.title}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                },
            },
            {"type": "section", "fields": fields},
        ],
    }


def get_source_url(source: Source) -> str:
    """通知に表示する取得元URLを返します。"""

    if isinstance(source, RssSource):
        return source.url
    return f"https://www.mixcloud.com/{source.username}/"


if __name__ == "__main__":
    raise SystemExit(main())
