import threading
from concurrent.futures.thread import ThreadPoolExecutor

from tasks import logger
from tasks.crawl_task import CrawlTask

task_id = 0
tasks = {}
thread_lock = threading.Lock()

tasks_pool = ThreadPoolExecutor(max_workers=20, thread_name_prefix='tasks')


def set_new_task(task_url: str, task_crawl_depth_level: int):
    global task_id, tasks, thread_lock, tasks_pool

    with thread_lock:
        task_id += 1

        while task_id in tasks:
            logger.warning(f'Task with ID {task_id} already exists')
            task_id += 1

        new_task = CrawlTask(
            task_id=task_id,
            task_url=task_url,
            task_crawl_depth_level=task_crawl_depth_level,
        )
        tasks[task_id] = new_task

    job = tasks_pool.submit(new_task.crawl_start)
    job.add_done_callback(new_task.crawl_finish)

    return new_task


def get_task(task_id: int) -> CrawlTask:
    global tasks

    if task_id not in tasks:
        return

    return tasks[task_id]
