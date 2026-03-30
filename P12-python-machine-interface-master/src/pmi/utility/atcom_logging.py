from loguru import logger
import sys

class PMI_logger:

    def __init__(self, terminal_lvl='INFO', logfile_lvl='DEBUG', logfile_path='log.log') -> None:
        logger.remove()
        logger.add(sys.stderr, level=terminal_lvl)
        # Log to file with rotation
        logger.add(
            logfile_path,
            level=logfile_lvl,
            rotation="100 MB",         # Rotate after file exceeds 50 MB
            retention=5,      # Keep last 5 files, delete older
            compression="zip"         # Optional: compress old logs to save space
        )


if __name__ == '__main__':
    # init
    pmi_logger = PMI_logger('DEBUG', 'ERROR', 'test.log')

    # try
    logger.debug('test')
    logger.info('test')
    logger.warning('test')
    logger.error('test')
    logger.critical('test')
    logger.success('test')