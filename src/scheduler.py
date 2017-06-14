import logging

from telegram.ext.jobqueue import Job, JobQueue

from src import data_fetcher, filter, publisher
from src.database import Database
from settings import IMGUR_CHECK_INTERVAL, POSTING_INTERVAL, CLEARING_DB_INTERVAL


logger = logging.getLogger(__name__)


def scheduling(job_queue: JobQueue, db: Database):
    logger.info('Setting up schedule...')
    job_queue.run_once(get_posts_job, when=0, context=db)
    job_queue.run_repeating(cleanup_db_job, first=0, interval=CLEARING_DB_INTERVAL, context=db)


def get_posts_job(_, job: Job):
    logging.info('▶︎ Running GET_POSTS job')
    db = job.context
    job_queue = job.job_queue
    response = data_fetcher.get_data_from_imgur()

    if response["success"]:
        posts = response['data']
        filtered_posts = filter.filter_posts(posts, db)
    else:
        job_queue.run_once(get_posts_job, when=IMGUR_CHECK_INTERVAL, context=db)
        return

    if filtered_posts:
        logging.info(f"Received {len(filtered_posts)} filtered post(s).")
        job_queue.run_once(posting_job, when=0, context=(filtered_posts, db))
    else:
        logging.info(f"No posts remain after filtering.")
        job_queue.run_once(get_posts_job, when=IMGUR_CHECK_INTERVAL, context=db)


def posting_job(bot, job: Job):
    logging.info('▶︎ Running POSTING job')
    posts, db = job.context
    job_queue = job.job_queue

    if posts:
        logger.info(f"Received {len(posts)} post(s) for publication.")
        post = posts.pop()
        publisher.publish_post(bot, post, db)
        job_queue.run_once(posting_job, when=POSTING_INTERVAL, context=(posts, db))
    else:
        logger.info(f"All posts were published. "
                    f"After {IMGUR_CHECK_INTERVAL // 60}m will check new posts.")
        job_queue.run_once(get_posts_job, when=IMGUR_CHECK_INTERVAL, context=db)


def cleanup_db_job(_, job: Job):
    db = job.context
    logger.info('▶︎ Running CLEANUP_DATABASE job')
    deleted, remaining = db.clear(CLEARING_DB_INTERVAL)
    logger.info(f'Deleted from db: {deleted} post(s). Left: {remaining} ')
