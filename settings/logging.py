import logging


def set_up_logging(debug):
    if debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(format='%(asctime)s ~ %(levelname)-10s %(name)-25s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        level=logging_level)

    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('JobQueue').setLevel(logging.WARNING)

    logging.addLevelName(logging.DEBUG, '🐛 DEBUG')
    logging.addLevelName(logging.INFO, '📑 INFO')
    logging.addLevelName(logging.WARNING, '🤔 WARNING')
    logging.addLevelName(logging.ERROR, '🚨 ERROR')
