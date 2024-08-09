import re
import uuid
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
        d: Dict[str, str | None] = dict(attrs)
        if "rel" in d and d["rel"] == "bookmark":
            self.flag_id_tag = True
            # print(d)
            id = str(uuid.uuid1())
            self.dl[id] = d.get("href", "")  # type: ignore
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
        # print(d)
        if (
            d.get("data-wpel-link") == "external"
            and d.get("target") == "_blank"
            and d.get("rel") == "follow"
            and re.search("mgate.xyz", d.get("href", ""))  # type: ignore
        ):
            href = d.get("href", "")
            # print("href: {}".format(href))
            r: requests.Response = requests.post(href, timeout=20)
            dlp = DLLinkParser_mgate_xyz(href)
            dlp.feed(r.text)
            return


class DLLinkParser_r_1img_tk(HTMLParser):
    def __init__(
        self, referer: str = "http://r.1img.tk/", convert_charrefs: bool = ...
    ) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.flag_found_torrent: bool = False
        self.referer: str = referer
        # print("Referer: {}".format(referer))

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
                "Host": "1img.tk",
                "Referer": self.referer,
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64;"
                + " rv:97.0) Gecko/20100101 Firefox/97.0",
            }
            href = d.get("href", "")
            if href is not None:
                fname = re.search(r"\/([\w\-\.]+\.torrent)$", href)
                print("href: {}".format(href))
                r: requests.Response = requests.post(href, headers=headers)
                if fname and type(r.content) is bytes:
                    # print("Output: {}".format(fname[1]))
                    with open(fname[1], mode="wb") as t:
                        t.write(r.content)


class DLLinkParser_mgate_xyz(HTMLParser):

    def __init__(self, target: str | None, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.flg_found_torrent_id: bool = False
        self.dlid: int = 0
        self.target: str | None = target

    def handle_starttag(
        self,
        tag: str,
        attrs: List[tuple[str, Optional[str]]],
    ):
        d: Dict[str, str | None] = dict(attrs)
        # print(d)
        if tag == "form":
            self.flg_found_torrent_id = True
            return
        elif self.flg_found_torrent_id and tag == "input":
            # POST /file/202404 HTTP/3
            header = {
                "Host": "mgate.xyz",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64;"
                + " rv:109.0) Gecko/20100101 Firefox/116.0",
                "Accept": "text/html,application/xhtml+xml,"
                + "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "ja,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Content-Length": "45",
                "Origin": "https://mgate.xyz",
                # "DNT": "1",
                "Alt-Used": "mgate.xyz",
                "Connection": "keep-alive",
                "Referer": self.target,
                "Cookie": "PHPSESSID=fa01d94ae2957d50b4711e2f8a0c19f4",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "TE": "trailers",
            }

            self.flg_found_torrent_id = False
            self.dlid = int(d.get("value", "0"))  # type: ignore
            print(f"{self.dlid} : {self.target}")
            fname = f"{self.dlid}.torrent"
            r: requests.Response = requests.post(
                self.target, headers=header, timeout=10
            )
            if fname and type(r.content) is bytes:
                print(f"Output: {fname}")
                with open(fname, mode="wb") as t:
                    t.write(r.content)
            return
