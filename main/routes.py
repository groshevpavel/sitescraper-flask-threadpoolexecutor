import flask

from main.logging import get_logger
from tasks.operate import get_task, set_new_task

main_blueprint = flask.Blueprint('main', __name__)

logger = get_logger()


@main_blueprint.route('/scrape', methods=['POST'])
def start_parse():
    url = flask.request.json['url']
    depth = flask.request.json.get('depth', 3)

    new_task = set_new_task(task_url=url, task_crawl_depth_level=depth)

    return flask.jsonify(task_id=new_task.task_id)


@main_blueprint.route('/task/<int:task_id>', methods=['GET'])
def task_result(task_id: int):
    task = get_task(task_id=task_id)

    if not task:
        return flask.abort(404, f'Task {task_id} does not exists!')

    if not task.completed:
        return flask.jsonify(
            task_id=task_id,
            status=task.task_status,
            files_processed=task.task_files_processed,
            bytes_downloaded=task.task_bytes_downloaded,
            links_processed=task.task_links_processed,
        )

    # return flask.jsonify(task_id=task_id, download_link=task.task_archive_path)
    try:
        return flask.send_file(task.task_archive_path, as_attachment=True)
    except Exception as e:
        logger.exception(e)
        flask.abort(404)
