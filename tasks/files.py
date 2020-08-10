import random
import shutil
import string
import threading
import zipfile
from pathlib import Path

from tasks import logger

ROOT_FOLDER = 'files'
SYSTEM_ROOT = Path().cwd().joinpath(ROOT_FOLDER)

task_id_to_path = {}
lock = threading.Lock()


def get_task_path(task_id: int) -> str:
    if task_id not in task_id_to_path:
        logger.debug(f'Task ID {task_id} was not processed yet to store path')
        set_task_path(task_id)

    secure_filename_str = task_id_to_path[task_id]
    secure_filename_str += '.zip'
    return str(SYSTEM_ROOT.joinpath(secure_filename_str))


def randomword(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def set_task_path(task_id: int):
    global lock

    with lock:
        if task_id not in task_id_to_path:
            task_id_to_path[task_id] = randomword(random.choice(range(16, 32)))

    create_task_dir(task_id=task_id)


def get_task_dir(task_id: int) -> Path:
    return SYSTEM_ROOT.joinpath(str(task_id))


def create_task_dir(task_id: int):
    task_dir = get_task_dir(task_id=task_id)
    if not task_dir.exists():
        task_dir.mkdir()


def remove_task_dir(task_id: int):
    shutil.rmtree(SYSTEM_ROOT.joinpath(str(task_id)))


def zip_task_folder(task):
    task_dir = get_task_dir(task_id=task.task_id)

    if not task_dir.exists():
        msg = f'Attempt to zip non-existing folder {task_dir} for task {task.task_id}'
        logger.critical(msg)
        raise SystemError(msg)

    task_arch_name = get_task_path(task_id=task.task_id)
    to_zip = (file for file in task_dir.glob('**/*') if file.is_file())

    try:
        with zipfile.ZipFile(task_arch_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file in to_zip:
                zf.writestr(str(file.relative_to(task_dir)), file.read_bytes())
    except Exception as exc:
        logger.exception(exc)
        return
    else:
        remove_task_dir(task_id=task.task_id)


def save_task_file(task, filename: str, data):
    if not isinstance(task, int):
        task_id = task.task_id
    else:
        task_id = task
    task_dir = get_task_dir(task_id=task_id)

    filename = filename.lstrip('/')
    task_dir.joinpath(filename).parents[0].mkdir(parents=True, exist_ok=True)
    return task_dir.joinpath(filename).write_bytes(data)  # written filesize
