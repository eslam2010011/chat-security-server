import base64
import pickle

import pytz
from apscheduler.job import Job
from apscheduler.jobstores.base import BaseJobStore
from pysondb import db


class JsonDBJobStore(BaseJobStore):
    def __init__(self, pickle_protocol=pickle.HIGHEST_PROTOCOL, path=""):
        super().__init__()
        self.path = path
        self.pickle_protocol = pickle_protocol
        self.db = db.getDb(path)

    def acquire(self, *args, **kwargs):
        pass

    def release(self, *args, **kwargs):
        pass

    def lookup_job(self, job_id):
        query_result = self.db.getByQuery({'_id': job_id})[0]
        if query_result:
            return self._reconstitute_job(query_result['job_state'])
        else:
            return None

    def _reconstitute_job(self, job_state):
        job_state = pickle.loads(job_state)
        job_state_str = base64.b64encode(job_state).decode('utf-8')
        job = Job.__new__(Job)
        job.__setstate__(job_state_str)
        job._scheduler = self._scheduler
        job._jobstore_alias = self._alias
        return job

    def _is_job_due(self, job, now):
        """Returns True if the job is due to run, False otherwise."""
        next_run_time = job.get('next_run_time')
        if next_run_time is None:
            return False
        return next_run_time <= now

    def add_job(self, job):
        job_state = pickle.dumps(job.__getstate__())

        job_state_str = base64.b64encode(job_state).decode('utf-8')
        value = {
            '_id': job.id,
            'next_run_time': self.datetime_to_utc_timestamp(job.next_run_time),
            'job_state': job_state_str
        }
        self.db.add(value)

    def datetime_to_utc_timestamp(self, dt):
        cairo_tz = pytz.timezone('Africa/Cairo')
        utc_tz = pytz.timezone('UTC')

        # Convert the datetime to Cairo timezone
        cairo_dt = dt.astimezone(cairo_tz)

        # Convert the Cairo datetime to UTC timezone
        utc_dt = cairo_dt.astimezone(utc_tz)

        # Get the UTC timestamp
        utc_timestamp = utc_dt.timestamp()

        return utc_timestamp

    def update_job(self, job):
        self.db.update(job.id, job.__getstate__())

    def remove_job(self, job):
        self.db.deleteById(job.id)

    def remove_all_jobs(self):
        self.db.deleteAll()

    def get_job(self, job_id):
        return self.db.getById(job_id)

    def get_all_jobs(self):
        return self.db.getAll()

    def get_due_jobs(self, now):
        timestamp = self.datetime_to_utc_timestamp(now)
        return [job for job in self.get_all_jobs() if self._is_job_due(job, timestamp)]

    def get_next_run_time(self):
        return None

    def close(self):
        pass

    def start(self, scheduler, alias):
        super().start(scheduler, alias)
        self.db = db.getDb(self.path)

    def shutdown(self):
        super().shutdown()

    def __str__(self):
        return f'JsonDBJobStore(path={self.path})'
