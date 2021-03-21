import logging
from utils.cron import cron_task
from config.common import LOGGING
from dao.mysql import nms_session_scope
from dao.nms_mysql import get_inspect_recycle, get_inspect_tasks, get_inspect_task, set_inspect_task_executed

logger = logging.getLogger(LOGGING['loggername'])


def init_inspect():
    logger.info('init_inspect')
    with nms_session_scope() as session:
        tasks = get_inspect_tasks(session)
    for info in tasks:
        add_inspect(info[0])


def add_inspect(taskid):
    cron_args = {}
    week = ('sunday', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday')
    with nms_session_scope() as session:
        task = get_inspect_task(session, taskid)
        recycle = get_inspect_recycle(session, taskid)
        set_inspect_task_executed(session, taskid, 0)
        cron_args['start_date'] = task.start_time
        cron_args['end_date'] = recycle.end_time
        cron_args['hour'] = task.start_time.hour
        cron_args['minute'] = task.start_time.minute
        cron_args['second'] = task.start_time.second
        day_of_week = []
        for index, name in enumerate(week):
            if getattr(recycle, name):
                day_of_week.append(str(index))
        if day_of_week:
            cron_args['day_of_week'] = ','.join(day_of_week)

    logger.info('add_inspect: %s' % cron_args)
    cron_task.add_job(inspect_task, (taskid, ),
                      'inspect_{}'.format(taskid), cron_args)


def del_inspect(taskid):
    cron_task.remove_job('inspect_{}'.format(taskid))


def update_inspect(taskid):
    del_inspect(taskid)
    add_inspect(taskid)


def inspect_task(taskid):
    import requests
    import time
    from config.common import NMS_SERVER_IP, NMS_SERVER_PORT
    url = 'http://{ip}:{port}/api/inner/nms/inspect/{taskid}/'.format(
        ip=NMS_SERVER_IP, port=NMS_SERVER_PORT, taskid=taskid)
    try:
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        r = requests.post(url, data={'start_time': start_time})
        logger.info('inspect_task: %s' % r.json())
    except Exception as e:
        logger.error(e)
