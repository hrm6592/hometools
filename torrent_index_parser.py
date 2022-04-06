from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Dict, List, Optional

import requests


class IndexParser(HTMLParser):
    def __init__(self, download_links: Dict[str, str]) -> None:
        super().__init__()
        self.flag_id_tag: bool = False
        self.flag_link_tag = False
        self.attr_base_t: str = "base-t"
        self.id: str = ""
        self.link: str | None = ""
        self.dl: dict[str, str] = download_links

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]):
        # print("Start tag:", tag)
        d: Dict[str, str | None] = dict(attrs)
        # print(type(d.get("class", "")))
        if tag == "span" and d.get("class", "") == self.attr_base_t:
            self.flag_id_tag = True
            return
        elif tag == "a" and d.get("class", "") in [
            "entry-dl",
            "entry-dl hd-1",
            "entry-dl hd-2",
        ]:
            self.flag_link_tag = True
            self.link = d.get("href", "")
            if self.link is not None:
                self.dl[self.id] = "".join(["http:", self.link])
            return
        else:
            return

    def handle_data(self, data: str):
        search = re.search(r"^\[([\w\-]+)\]", data)
        if search and self.flag_id_tag:
            self.dl[search[1]] = ""
            self.id = search[1]
            self.flag_id_tag = False
            return
        elif self.flag_link_tag and data == "HD":
            self.flag_link_tag = False
            return
        elif self.flag_link_tag and data == "DL":
            self.flag_link_tag = False
            return
        else:
            return


class RedirectorParser(HTMLParser):
    def __init__(self, dllink: str = "", convert_charrefs: bool = ...) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.flag_found_torrent: bool = False
        self.dllink: str = dllink

    def handle_starttag(
        self,
        tag: str,
        attrs: List[tuple[str, Optional[str]]],
    ):
        d: Dict[str, str | None] = dict(attrs)
        if tag == "div" and d.get("class", "") == "main":
            self.flag_found_torrent = True
            return
        elif (
            tag == "a"
            and self.flag_found_torrent is True
            and d.get("href", "") is not None
        ):
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;"
                + "q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja,en;q=0.5",
                "Connection": "keep-alive",
                "DNT": "1",
                "Host": "r.jtl.re",
                "Referer": "http://javtorrent.re/",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64;"
                + " rv:97.0) Gecko/20100101 Firefox/97.0",
            }
            href = d.get("href", "")
            if href is not None:
                href = "http://r.jtl.re" + href
                print("href: {}".format(href))
                r: requests.Response = requests.post(href, headers=headers)
                dlp = DLLinkParser(referer=str(href))
                dlp.feed(r.text)
                return


class DLLinkParser(HTMLParser):
    def __init__(
        self, referer: str = "http://r.jtl.re/", convert_charrefs: bool = ...
    ) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.flag_found_torrent: bool = False
        self.referer: str = referer

    def handle_starttag(
        self,
        tag: str,
        attrs: List[tuple[str, Optional[str]]],
    ):
        d: Dict[str, str | None] = dict(attrs)
        if tag == "div" and d.get("class", "") == "main":
            self.flag_found_torrent = True
            return
        elif (
            tag == "a"
            and self.flag_found_torrent is True
            and d.get("href", "") is not None
        ):
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;"
                + "q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ja,en;q=0.5",
                "Connection": "keep-alive",
                "DNT": "1",
                "Host": "jtl.re",
                "Referer": self.referer,
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64;"
                + " rv:97.0) Gecko/20100101 Firefox/97.0",
            }
            href = d.get("href", "")
            if href is not None:
                fname = re.search(r"\/([\w\-\.]+\.torrent)$", href)
                r: requests.Response = requests.post(
                    d.get("href", ""), headers=headers  # type: ignore
                )
                if fname and type(r.content) is bytes:
                    # print("Output: {}".format(fname[1]))
                    with open(fname[1], mode="wb") as t:
                        t.write(r.content)
