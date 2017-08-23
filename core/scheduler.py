from telegram.ext import JobQueue, Job


class Scheduler(object):
    """
    Congregate jobs for one pipe in one place so when needed they can be easily stopped all at once.
    """

    def __init__(self, job_queue: JobQueue):
        self.job_queue = job_queue
        self.jobs = []

    def run_repeating(self, callback, interval, first=None, *args, **kwargs):
        job: Job = self.job_queue.run_repeating(callback=lambda bot, _job: callback(*args, **kwargs),
                                                first=first, interval=interval)
        self.jobs.append(job)

    def run_once(self, callback, when, *args, **kwargs):
        job: Job = self.job_queue.run_once(callback=lambda bot, _job: callback(*args, **kwargs),
                                           when=when)
        self.jobs.append(job)

    def stop(self):
        for job in self.jobs:
            job.schedule_removal()
        self.jobs = []
