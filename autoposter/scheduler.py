import logging

from telegram import Bot
from telegram.ext.jobqueue import Job, JobQueue

from autoposter import AbstractFetcher, AbstractFilter, AbstractPublisher
from autoposter.database import AbstractDB


class Scheduler(object):
    def __init__(self,
                 name: str,
                 job_queue: JobQueue,
                 db: AbstractDB,
                 fetcher: AbstractFetcher,
                 filtr: AbstractFilter or None,
                 publisher: AbstractPublisher,
                 data_collection_interval=5*60,  # 5 minutes
                 data_posting_interval=2,  # 2 seconds
                 cleanup_interval=2*24*60*60,  # 2 days
                 ):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.name = name

        self.job_queue = job_queue
        self.db = db

        self.fetcher = fetcher
        self.filter = filtr
        self.publisher = publisher

        self.data_collection_interval = data_collection_interval
        self.data_posting_interval = data_posting_interval
        self.cleanup_interval = cleanup_interval

        self.data_chunks = []

    def __str__(self):
        return f"Scheduler(name='{self.name}')"

    def run(self):
        """
        Scheduling for one run `getting posts job` 
        and for repetitive running `db cleanup job`.
        """
        self.logger.debug('Setting up scheduler...')
        self.job_queue.run_once(self.get_data_job, when=0)
        self.job_queue.run_repeating(self.cleanup_job, first=0,
                                     interval=self.cleanup_interval)

    def get_data_job(self, bot: Bot, job: Job):
        """
        Trying to obtain data. 
        If successfully then filter data and schedule `posting job`.
        Otherwise schedule `this` job to run after ``self.data_acquisition_interval`` seconds.
        If after filtration remains 0 data chunks then also schedule `this` job.

        Args:
            bot (Bot): Unused ``bot`` instance needed as part of callback signature.
            job (Job): Unused ``job`` instance needed as part of callback signature.
        """
        self.logger.info(f'▶︎ {self.name}: Running 🌚 GET_DATA job...')
        response = self.fetcher.fetch()
        dai_minutes = self.data_collection_interval // 60

        if response.success:
            if self.filter:
                self.data_chunks = self.filter.filter(response.data)
            else:
                self.data_chunks = response.data
        else:
            self.logger.info(f"Failed to receive data."
                              f"After {dai_minutes} minutes will try again.")
            self.job_queue.run_once(self.get_data_job,
                                    when=self.data_collection_interval)
            return

        if self.data_chunks:
            chunks_count = len(self.data_chunks)
            self.logger.info(f"Received {chunks_count} filtered chunks.")
            self.job_queue.run_once(self.post_job, when=0)
        else:
            self.logger.info(f"No chunks remain after filtration." 
                             f"After {dai_minutes} minutes will try again.")
            self.job_queue.run_once(self.get_data_job,
                                    when=self.data_collection_interval)

    def post_job(self, bot: Bot, job: Job):
        """
        If obtained not empty list of data chunks
        then publish first post, remove it from posts list and schedule next `posting job`.
        Otherwise schedule `get posts job`.

        Args:
            bot (Bot): Bot instance needed for publishing post.
            job (Job): Job object that holds ``job_queue`` and context parameter 
                with database and list of posts.
        """
        self.logger.info(f'▶︎ {self.name}: Running 📨 POSTING job...')
        dai_minutes = self.data_collection_interval // 60

        if self.data_chunks:
            chunks_count = len(self.data_chunks)
            self.logger.info(f"Received {chunks_count} chunk(s) for publication.")
            chunk = self.data_chunks.pop(0)
            self.publisher.publish(chunk)
            self.job_queue.run_once(self.post_job, when=self.data_posting_interval)
        else:
            self.logger.info(f"All posts were published. "
                             f"After {dai_minutes} minutes will try again.")
            self.job_queue.run_once(self.get_data_job, when=self.data_collection_interval)

    def cleanup_job(self, bot: Bot, job: Job):
        """
        Removing posts from the database that are older than ``CLEARING_DB_INTERVAL``.

        Args:
            bot (Bot): Unused ``bot`` instance needed as part of callback signature.
            job (Job): Unused ``job`` instance needed as part of callback signature.
        """
        self.logger.info(f'▶︎ {self.name}: Running 🔥 CLEANUP_DATABASE job...')
        deleted, remaining = self.db.clear(self.cleanup_interval)
        self.logger.info(f'Deleted from db: {deleted} post(s). Left: {remaining} ')
