# crawler/parser.py
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class HTMLParser:
    IGNORED = {"script", "style", "noscript", "iframe", "header", "footer", "nav"}

    def parse_html(self, html: str, url: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        for tag in self.IGNORED:
            for node in soup.find_all(tag):
                node.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        # remove navbars or common site chrome heuristically by ids/classes?
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return {
            "url": url,
            "domain": urlparse(url).netloc,
            "title": title,
            "content": text
        }

    def parse_multiple(self, pages: dict):
        return [ self.parse_html(html, url) for url, html in pages.items() ]
