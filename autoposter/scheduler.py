import logging

from telegram import Bot
from telegram.ext.jobqueue import Job, JobQueue

from autoposter.collector import Collector
from autoposter.database import AbstractDB


class Scheduler(object):
    def __init__(self,
                 name: str,
                 job_queue: JobQueue,
                 db: AbstractDB,
                 collector: Collector,
                 data_collection_interval=5*60,     # 5 minutes
                 data_posting_interval=2,           # 2 seconds
                 cleanup_interval=2*24*60*60,       # 2 days
                 ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name

        self.job_queue = job_queue
        self.db = db

        self.collector = collector

        self.data_collection_interval = data_collection_interval
        self.data_posting_interval = data_posting_interval
        self.cleanup_interval = cleanup_interval

        self.data_chunks = []

    def __str__(self):
        return f"Scheduler(name='{self.name}')"

    def run(self):
        """
        Scheduling for one run `getting data job` 
        and for repetitive running `database cleanup job`.
        """
        self.logger.debug('Setting up scheduler...')
        self.job_queue.run_once(self.get_data_job, when=0)
        self.job_queue.run_repeating(self.cleanup_job, first=0,
                                     interval=self.cleanup_interval)

    def get_data_job(self, bot: Bot, job: Job):
        """
        Trying to obtain data. 
        If ``self.collector`` receive 0 data chunks then schedule `this` job again.
        Otherwise schedule `post data job` to run after ``self.data_posting_interval`` seconds.

        Args:
            bot (Bot): Unused ``Bot`` instance needed as part of callback signature.
            job (Job): Unused ``Job`` instance needed as part of callback signature.
        """
        del bot, job
        self.logger.info(f'▶︎ {self.name}: Running 🌚 GET_DATA job...')
        dai_minutes = self.data_collection_interval // 60

        self.collector.collect()

        if not self.collector.is_empty:
            chunks_count = self.collector.size
            self.logger.info(f"Received {chunks_count} filtered data.")
            self.job_queue.run_once(self.post_job, when=0)
        else:
            self.logger.info(f"No data remain after filtration or it weren't fetched.")
            self.logger.info(f"After {dai_minutes} minutes will try again.")
            self.job_queue.run_once(self.get_data_job,
                                    when=self.data_collection_interval)

    def post_job(self, bot: Bot, job: Job):
        """
        If obtained not empty list of data
        then publish data and schedule next `posting job`.
        Otherwise schedule `get data job`.

        Args:
            bot (Bot): Unused ``Bot`` instance needed as part of callback signature.
            job (Job): Unused ``Job`` instance needed as part of callback signature.
        """
        del bot, job
        self.logger.info(f'▶︎ {self.name}: Running 📨 POSTING job...')
        dai_minutes = self.data_collection_interval // 60

        if self.collector.updated:
            self.logger.info(f"Collector was updated. In a moment will run GET_DATA job.")
            self.job_queue.run_once(self.get_data_job, when=0)
            return

        if not self.collector.is_empty:
            chunks_count = self.collector.size
            self.logger.info(f"Received {chunks_count} posts for publication.")
            self.collector.publish()
            self.job_queue.run_once(self.post_job, when=self.data_posting_interval)
        else:
            self.logger.info(f"All posts were published.")
            self.logger.info(f"After {dai_minutes} minutes will try to collect new.")
            self.job_queue.run_once(self.get_data_job, when=self.data_collection_interval)

    def cleanup_job(self, bot: Bot, job: Job):
        """
        Removing old data from database.

        Args:
            bot (Bot): Unused ``Bot`` instance needed as part of callback signature.
            job (Job): Unused ``Job`` instance needed as part of callback signature.
        """
        del bot, job
        self.logger.info(f'▶︎ {self.name}: Running 🔥 CLEANUP_DATABASE job...')
        deleted, remaining = self.db.clear(self.cleanup_interval)
        self.logger.info(f'Deleted from db: {deleted} post(s). Left: {remaining} ')
