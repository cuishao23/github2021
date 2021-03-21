import logging
from apscheduler.schedulers.background import BackgroundScheduler
from config.common import LOGGING

logger = logging.getLogger(LOGGING['loggername'])

class CronTask:

    def __init__(self):
        self.scheduler=BackgroundScheduler()

    def add_job(self, func, args, job_id, cron_args):
        '''
        cron_args:
            :param int|str year: 4-digit year
            :param int|str month: month (1-12)
            :param int|str day: day of the (1-31)
            :param int|str week: ISO week (1-53)
            :param int|str day_of_week: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
            :param int|str hour: hour (0-23)
            :param int|str minute: minute (0-59)
            :param int|str second: second (0-59)
            :param datetime|str start_date: earliest possible date/time to trigger on (inclusive)
            :param datetime|str end_date: latest possible date/time to trigger on (inclusive)
        '''
        logging.info('[cron]: add job %s, cron_args=%s' % (job_id, cron_args))
        self.scheduler.add_job(func, 'cron', args, **cron_args, id=job_id)

    def remove_job(self, job_id):
        logging.info('[cron]: remove job %s' % job_id)
        self.scheduler.remove_job(job_id)

    def __repr__(self):
        return '%s %s' % (self.scheduler.state, self.scheduler.get_jobs())


cron_task=CronTask()
