# crawler/crawler.py
import os
import time
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from urllib import robotparser
import hashlib
import re
from utils.logger import get_logger

class WebCrawler:
    def __init__(self, start_url, max_depth=2, max_pages=200, delay=0.5, output_dir="data/raw_html"):
        self.start_url = start_url.rstrip("/")
        parsed = urlparse(self.start_url)
        self.scheme = parsed.scheme or "http"
        self.domain = parsed.netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.delay = delay
        self.output_dir = output_dir
        self.visited = set()
        self.pages = {}  # {url: html}

        os.makedirs(self.output_dir, exist_ok=True)

        self.logger=get_logger("crawler")
        self.logger.info(f"Initializing crawler for {self.start_url}")

        # robots.txt
        self.rp = robotparser.RobotFileParser()
        robots_url = urljoin(self.start_url, "/robots.txt")
        self.rp.set_url(robots_url)
        try:
            self.rp.read()
            self.logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            self.logger.warning(f"Could not read robots.txt: {e}")
            self.rp = None 
            # silent: continue if cannot read robots


    def is_allowed(self, url):
        """Check if URL is allowed by robots.txt"""
        if self.rp is None:
            # Safer default: disallow if robots.txt not readable
            self.logger.warning(f"robots.txt unreadable — skipping {url}")
            return False
        try:
            allowed = self.rp.can_fetch("*", url)
            if not allowed:
                self.logger.warning(f"Blocked by robots.txt: {url}")
            return allowed
        except Exception as e:
            self.logger.error(f"Error checking robots.txt for {url}: {e}")
            return False

    def is_same_domain(self, url):
        p = urlparse(url)
        return p.netloc == self.domain or (p.netloc == "" and p.path)

    def save_html(self, url, html):
        name = re.sub(r'[\\/*?:"<>|]', "_", url)
        name = name.replace("://", "_").replace("/", "_")
        name = name[:200]  # optional: limit length
        path = os.path.join(self.output_dir, f"{name}.html")
    
    # Save the file
        with open(path, "w", encoding="utf-8") as f:
         f.write(html)
    
    # Log saved path
        self.logger.info(f"Saved {url} → {path}")
   # print("Before")

    def get_links(self, html, base_url):
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if href is None or href.strip() == "":
                continue
            full = urljoin(base_url, href.split("#")[0])
            parsed = urlparse(full)
            if parsed.scheme not in ("http", "https"):
                continue
            if self.is_same_domain(full) and self.is_allowed(full):
                links.add(full.rstrip("/"))
        return links
    
    #print("After")

    def crawl_page(self, url, depth):
        """Recursively crawl pages within allowed depth and domain."""
        if len(self.pages) >= self.max_pages or depth > self.max_depth or url in self.visited:
            return

        if not self.is_allowed(url):
            self.visited.add(url)
            return

        self.visited.add(url)
        self.logger.info(f"[Depth {depth}] Crawling: {url}")

        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "RAG-WebCrawler/1.0"})
            if resp.status_code != 200:
                self.logger.warning(f"Non-200 status for {url}: {resp.status_code}")
                return

            html = resp.text
            self.pages[url] = html
            self.save_html(url, html)
            time.sleep(self.delay)

            links = self.get_links(html, url)
            for link in links:
                if len(self.pages) >= self.max_pages:
                    break
                self.crawl_page(link, depth + 1)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")

    def start(self):
        self.logger.info("Starting crawl...")
        self.crawl_page(self.start_url, 0)
        self.logger.info(f"Crawl finished. Pages: {len(self.pages)}, Skipped: {len(self.visited) - len(self.pages)}")

        return {
            "page_count": len(self.pages),
            "skipped_count": len(self.visited) - len(self.pages),
            "urls": list(self.pages.keys())
        }
