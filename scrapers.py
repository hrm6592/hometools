#!/bin/env python
# -*- coding: utf-8 -*-

import re
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """
    情報取得処理の基底クラス（抽象クラス）
    """

    def __init__(self, model_number: str):
        self.model_number = model_number.upper()
        self.cid = model_number.lower().replace("-", "")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.source_name = "Unknown"

    def _get_soup(self, url: str, **kwargs) -> BeautifulSoup | None:
        """指定されたURLからBeautifulSoupオブジェクトを取得する"""
        print(f"  [{self.source_name}] 検索中... (URL: {url})")
        try:
            response = requests.get(url, timeout=10, headers=self.headers, **kwargs)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"  [{self.source_name}] アクセスに失敗しました: {e}")
            return None

    @abstractmethod
    def fetch_info(self) -> dict | None:
        """
        Webサイトからタイトルと出演者情報を取得する。
        成功した場合は {'title': str, 'performers': list[str], 'source': str} を返す。
        失敗した場合は None を返す。
        """
        raise NotImplementedError

    def _cleanup_title(self, title: str) -> str:
        """取得したタイトルから不要な文字列を削除する"""
        title = title.replace(self.model_number, "")
        return title.strip()

    def _get_meta_content(self, soup: BeautifulSoup, property_name: str) -> str | None:
        """meta要素のcontent属性を文字列として取得する"""
        meta_tag = soup.find("meta", property=property_name)
        if meta_tag is None:
            return None

        content = meta_tag.get("content")
        if isinstance(content, str):
            return content
        if content is not None:
            print(
                f"  [{self.source_name}] meta[property='{property_name}'] の"
                " content属性が文字列ではありません。"
            )
        return None

    def _extract_unique_performers(self, elements: list) -> list[str]:
        """
        BeautifulSoupの要素リストから、重複を除いた出演者名のリストを抽出する。
        """
        if not elements:
            return []

        unique_performers = set(p.get_text(strip=True) for p in elements)

        # 不要な文字列を除外
        final_performers = []
        for name in unique_performers:
            if "女優ランキング" in name or not name:
                continue
            final_performers.append(name)

        return sorted(list(final_performers))


class DMMScraper(BaseScraper):
    """DMMから情報を取得する"""

    def __init__(self, model_number: str):
        super().__init__(model_number)
        self.source_name = "DMM"
        self.url_template = "https://www.dmm.co.jp/mono/dvd/-/detail/=/cid={cid}/"
        self.title_selector = "#title"
        self.performers_selector = "#performer a"

    def fetch_info(self) -> dict | None:
        search_url = self.url_template.format(cid=self.cid)
        cookies = {"age_check_done": "1"}
        soup = self._get_soup(search_url, cookies=cookies)
        if not soup:
            return None

        title_element = soup.select_one(self.title_selector)
        if not title_element:
            return None  # タイトルがなければ失敗とみなす

        title = self._cleanup_title(title_element.get_text(strip=True))
        performer_elements = soup.select(self.performers_selector)
        performers = self._extract_unique_performers(performer_elements)

        if not performers:
            print(f"  [{self.source_name}] 出演者情報が見つかりませんでした。")
            return None

        print(f"  [{self.source_name}] タイトル取得成功")
        return {"title": title, "performers": performers, "source": self.source_name}


class AVWikiScraper(BaseScraper):
    """av-wiki.netから情報を取得する"""

    def __init__(self, model_number: str):
        super().__init__(model_number)
        self.source_name = "AV-Wiki"
        self.url_template = f"https://av-wiki.net/{self.model_number.lower()}/"

    def fetch_info(self) -> dict | None:
        soup = self._get_soup(self.url_template)
        if not soup:
            return None

        title = self._fetch_title(soup)
        performers = self._fetch_performers(soup)

        if not title:
            return None  # タイトルがなければ失敗

        title = self._cleanup_title(title)

        print(f"  [{self.source_name}] タイトル取得成功")
        return {"title": title, "performers": performers, "source": self.source_name}

    def _fetch_title(self, soup: BeautifulSoup) -> str | None:
        # 1. blockquote-like div から試す
        blockquote_div = soup.select_one("div.blockquote-like")
        if blockquote_div:
            blockquote_text = blockquote_div.get_text(strip=True)
            model_prefix = f"【{self.model_number}】"
            if blockquote_text.startswith(model_prefix):
                return blockquote_text.replace(model_prefix, "", 1).strip()

        # 2. h1.work-title-detail から試す
        title_element = soup.select_one("h1.work-title-detail")
        if title_element:
            return title_element.get_text(strip=True)

        return None

    def _fetch_performers(self, soup: BeautifulSoup) -> list[str]:
        # 1. 概要表から試す
        # AV-Wiki の概要表では、見出しに <th> ではなく <td> が使われている
        # ページがある。<dt> を使うレイアウトも含めて、値の兄弟要素を取得する。
        actress_header = soup.find(
            lambda tag: (
                tag.name in ["th", "td", "dt"]
                and tag.get_text(strip=True) == "AV女優名"
            )
        )
        if actress_header:
            value_cell = actress_header.find_next_sibling(["td", "dd"])
            if value_cell is None:
                value_cell = actress_header.find_next_sibling()

            if value_cell:
                found_performers = value_cell.find_all("a")
                if found_performers:
                    return self._extract_unique_performers(found_performers)

                # 女優名がリンク化されていないページ（例: 「＊＊＊」）にも対応する。
                performer_name = value_cell.get_text(" ", strip=True)
                if performer_name:
                    return [performer_name]

        # 2. itemprop から試す
        found_performers_prop = soup.select("span[itemprop='actors'] a")
        if found_performers_prop:
            return self._extract_unique_performers(found_performers_prop)

        return []


class AVWikiDBScraper(BaseScraper):
    """avwikidb.comから情報を取得する"""

    def __init__(self, model_number: str):
        super().__init__(model_number)
        self.source_name = "avwikidb"
        self.url_template = f"https://avwikidb.com/work/{self.model_number}/"

    def fetch_info(self) -> dict | None:
        soup = self._get_soup(self.url_template)
        if not soup:
            return None

        performers = self._fetch_performers(soup)
        title = self._fetch_title(soup, performers)

        if not title:
            return None

        title = self._cleanup_title(title)

        print(f"  [{self.source_name}] タイトル取得成功")
        return {"title": title, "performers": performers, "source": self.source_name}

    def _fetch_performers(self, soup: BeautifulSoup) -> list[str]:
        performers = set()

        # 1. <title> の "品番の女優は...｜作品タイトル" 形式から取得
        page_title_tag = soup.find("title")
        if page_title_tag:
            names_text = self._extract_performers_text_from_page_title(
                page_title_tag.get_text(strip=True)
            )
            if names_text:
                for name in names_text.split("、"):
                    name = name.strip()
                    if name:
                        performers.add(name)

        # 2. `a[href*="/actress/"]` から取得
        found_performers_tags = soup.select('a[href*="/actress/"]')
        for tag in found_performers_tags:
            performers.add(tag.get_text(strip=True))

        # 3. "出演しているAV女優は...です。" の形式から取得
        p_tags = soup.find_all("p")
        for p_tag in p_tags:
            p_text = p_tag.get_text(strip=True)
            match = re.search(r"出演しているAV女優は(.+?)です。", p_text)
            if match:
                names_text = match.group(1)
                for name in names_text.split("、"):
                    name = name.strip()
                    if name:
                        performers.add(name)

            match = re.search(r"の女優は(.+?)(?:です。|。)", p_text)
            if match:
                names_text = match.group(1)
                for name in names_text.split("、"):
                    name = name.strip()
                    if name:
                        performers.add(name)

        # クリーンアップ
        final_performers = []
        for name in performers:
            if "女優ランキング" in name or not name:
                continue
            final_performers.append(name)

        return sorted(list(final_performers))

    def _fetch_title(
        self, soup: BeautifulSoup, performers_list: list[str]
    ) -> str | None:
        # 1. <title> タグから試す
        page_title_tag = soup.find("title")
        if page_title_tag:
            page_title_text = page_title_tag.get_text(strip=True)
            parts = re.split(r"[|｜]", page_title_text, maxsplit=1)
            if len(parts) > 1:
                title_candidate = parts[1].strip()
                for p_name in performers_list:
                    title_candidate = title_candidate.replace(p_name, "")
                return title_candidate.strip()

        # 2. og:title メタタグから試す
        return self._get_meta_content(soup, "og:title")

    def _extract_performers_text_from_page_title(
        self, page_title_text: str
    ) -> str | None:
        title_prefix = re.split(r"[|｜]", page_title_text, maxsplit=1)[0].strip()
        match = re.search(r"の女優は(.+)$", title_prefix)
        if match:
            return match.group(1).strip()
        return None

    def _cleanup_title(self, title: str) -> str:
        title = super()._cleanup_title(title)
        return title.replace(" - AVWikiDB", "").strip()


class MissAVScraper(BaseScraper):
    """missav123.comから情報を取得する"""

    def __init__(self, model_number: str):
        super().__init__(model_number)
        self.source_name = "MissAV"
        self.url_template = f"https://missav123.com/dm13/ja/{self.model_number.lower()}"

    def fetch_info(self) -> dict | None:
        soup = self._get_soup(self.url_template)
        if not soup:
            return None

        title = self._fetch_title(soup)
        performers = self._fetch_performers(soup)

        if not title:
            return None

        title = self._cleanup_title(title)

        print(f"  [{self.source_name}] タイトル取得成功")
        return {"title": title, "performers": performers, "source": self.source_name}

    def _fetch_title(self, soup: BeautifulSoup) -> str | None:
        return self._get_meta_content(soup, "og:title")

    def _fetch_performers(self, soup: BeautifulSoup) -> list[str]:
        found_performers = soup.find_all("a", href=re.compile(r"/actress(es)?/"))
        if not found_performers:
            return []

        # '----' や '（出演者情報なし）' をフィルタリング
        performer_names = [p.get_text(strip=True) for p in found_performers]
        if "----" in performer_names or "（出演者情報なし）" in performer_names:
            return []

        return self._extract_unique_performers(found_performers)

    def _cleanup_title(self, title: str) -> str:
        title = super()._cleanup_title(title)
        return title.replace("- MissAV", "").strip()
