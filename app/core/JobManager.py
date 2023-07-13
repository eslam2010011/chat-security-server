import os

import pytz
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.SessionManager import SessionManager


class JobManager:

    def __init__(self):

        self.scheduler = AsyncIOScheduler()
        # self.scheduler.configure(
        #     jobstores={"default": SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')}
        # )
        self.sessionManager = SessionManager()

    def add_job(self, fun, hour, minute, jobName, param):

        if self.scheduler.running:
            self.scheduler.shutdown()

        # executors = {
        #     'default': {'type': 'threadpool', 'max_workers': 20},
        #     'processpool': ProcessPoolExecutor(max_workers=5)
        # }
        # jobstores = {
        #     'default': JsonDBJobStore(path=file_path_session)
        # }

        job = self.scheduler.add_job(fun, "cron", hour=hour, minute=minute, timezone=pytz.timezone('Africa/Cairo'),
                                     args=param)
        self.sessionManager.add_job(job.id, "Africa/Cairo", param[1], minute=minute, hour=hour, name=jobName)
        self.scheduler.start()

    def remove_job(self, job_id):
        try:
            job_id_ = self.sessionManager.jobs.getById(job_id)["job_id"]
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
            self.scheduler.remove_job(job_id_)
            self.scheduler.start()
            self.sessionManager.remove_job(job_id)
        except:
            self.sessionManager.remove_job(job_id)
