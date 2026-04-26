import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from Functions.config import Config

logger = logging.getLogger(__name__)


def start_scheduler(func=None):
    """Initialize and start the scheduler for automatic EPG downloads"""
    Config().load_env_config()

    cron_schedule = os.getenv('CRON_SCHEDULE', '0 3 * * *')

    parts = cron_schedule.split()
    minute, hour = int(parts[0]), int(parts[1])
    day_of_month, month, day_of_week = parts[2], parts[3], parts[4]

    logger.info(
        f"CRON Schedule: {cron_schedule} -> Minute: {minute}, Hour: {hour}, Day of Month: {day_of_month}, Month: {month}, Day of Week: {day_of_week}")

    scheduler = BackgroundScheduler()
    # Run download_epg_files daily based on CRON_SCHEDULE
    scheduler.add_job(func, CronTrigger.from_crontab(cron_schedule))
    scheduler.start()
    logger.info(f"Scheduler started: EPG files will be downloaded daily at {hour:02d}:{minute:02d} (CRON: {cron_schedule})")
    return scheduler
