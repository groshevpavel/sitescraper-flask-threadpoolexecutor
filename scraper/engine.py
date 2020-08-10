import requests
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse

from requests import Response

from scraper.parser import determine_link, get_link_filename, yield_links
from main.logging import get_logger
from tasks.files import save_task_file

logger = get_logger()


class ScrapeURL:
    url: str
    level: int
    is_file: bool = False

    response: Response = None

    scraped: bool = False

    def __init__(self, url, level, is_file: bool = False):
        self.url = url
        self.level = level

        self.is_file = is_file
        if is_file:
            self.path = get_link_filename(url)


class MultiThreadScraper:
    bytes_downloaded: int = 0
    files_processed: int = 0
    links_processed: int = 0

    def __init__(
            self,
            crawl_task=None,
            base_url: str = None,
            max_scrape_level: int = 1,
            max_workers: int = 5,
    ):

        self.crawl_task = crawl_task
        self.base_url = base_url if base_url else crawl_task.task_url
        self.max_scrape_level = max_scrape_level

        self.root_url = '{}://{}'.format(
            urlparse(self.base_url).scheme,
            urlparse(self.base_url).netloc,
        )

        self.scraped_pages = set()

        self.pool = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='crawl')
        self.to_crawl = Queue()

        self.timeout = (3, 30)  # requests: connect timeout, read timeout

        self.to_crawl.put(ScrapeURL(self.base_url, 0))

    def parse_links(self, scraped_url: ScrapeURL):
        for link in yield_links(scraped_url.response.text):
            url = link['link']

            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)

                if url not in self.scraped_pages:
                    next_level = scraped_url.level + 1

                    if next_level <= self.max_scrape_level:
                        self.to_crawl.put(ScrapeURL(url, next_level, is_file=determine_link(url)))
                        self.links_processed += 1

                        if self.crawl_task is not None:
                            self.crawl_task.task_links_processed = self.links_processed
                    # else:
                    #     print(f'skipped due level({next_level}) depth exceed\n{url}')

    def post_scrape_callback(self, task_result):
        result: ScrapeURL = task_result.result()

        if result and result.scraped and result.response.status_code == 200:
            if not result.is_file:
                self.parse_links(result)

    def scrape_page(self, scrape_url: ScrapeURL):
        try:
            scrape_url.response = requests.get(scrape_url.url, timeout=self.timeout)
            scrape_url.scraped = True

            if scrape_url.is_file:
                saved_file_size = save_task_file(
                    self.crawl_task.task_id,
                    scrape_url.path,
                    scrape_url.response.content,
                )

                self.bytes_downloaded += saved_file_size
                self.files_processed += 1

                if self.crawl_task is not None:
                    self.crawl_task.task_bytes_downloaded = self.bytes_downloaded
                    self.crawl_task.task_files_processed = self.files_processed

            return scrape_url
        except requests.RequestException as exc:
            logger.exception(exc)
            return

    def run_scraper(self):
        while True:
            try:
                target_url: ScrapeURL = self.to_crawl.get(timeout=60)

                if not target_url.scraped:
                    print(f'Scraping level {target_url.level} of URL: {target_url.url}')
                    # logger.info(f'Scraping level {target_url.level} of URL: {target_url.url}')
                    self.scraped_pages.add(target_url.url)

                    job = self.pool.submit(self.scrape_page, target_url)
                    job.add_done_callback(self.post_scrape_callback)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    s = MultiThreadScraper(base_url="https://yandex.ru")
    s.run_scraper()
