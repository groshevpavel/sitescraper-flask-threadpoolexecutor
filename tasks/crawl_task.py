import time

from scraper.engine import MultiThreadScraper
from tasks import logger
from tasks.files import get_task_path, set_task_path, zip_task_folder
from tasks.statuses import TaskStatus


class CrawlTask:
    task_id: int
    task_url: str
    task_crawl_depth_level: int
    task_status: TaskStatus = TaskStatus.PENDING

    task_files_processed: int = 0
    task_links_processed: int = 0
    task_bytes_downloaded: int = 0

    _task_path: str = None

    def __init__(
            self,
            task_id: int,
            task_url: str,
            task_crawl_depth_level: int,
    ):
        self.task_id = task_id
        self.task_url = task_url
        self.task_crawl_depth_level = task_crawl_depth_level

    @property
    def task_archive_path(self):
        if self._task_path is None:
            self._task_path = get_task_path(self.task_id)

        return self._task_path

    @task_archive_path.setter
    def task_archive_path(self, value: str):
        if self.task_archive_path is not None:
            logger.error(f'Not set! self.task_archive_path already set as {self.task_archive_path}')
            return

        self.task_archive_path = value

    @property
    def completed(self):
        return self.task_status == TaskStatus.COMPLETE

    def crawl_start(self):
        set_task_path(self.task_id)

        self.task_status = TaskStatus.WORKING
        scraper = MultiThreadScraper(crawl_task=self, max_scrape_level=self.task_crawl_depth_level)
        scraper.run_scraper()

    def crawl_finish(self, task_result):
        self.task_status = TaskStatus.PACKING
        zip_task_folder(self)

        self.task_status = TaskStatus.COMPLETE