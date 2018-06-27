from telegram.ext import JobQueue


# todo: move to the core.pipe
class Scheduler(object):
    def __init__(self, job_queue: JobQueue):
        self.job_queue = job_queue

    def run_repeating(self, callback, interval, first=None, name=None, *args, **kwargs):
        self.job_queue.run_repeating(callback=lambda bot, _job: callback(*args, **kwargs),
                                     first=first, interval=interval, name=name)

    def run_once(self, callback, when=0, name=None, *args, **kwargs):
        self.job_queue.run_once(callback=lambda bot, _job: callback(*args, **kwargs),
                                when=when, name=name)
