from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from Functions.config import load_config
import os

def start_scheduler(func=None):
    """Initialize and start the scheduler for automatic EPG downloads"""
    load_config()

    cron_schedule = os.getenv('CRON_SCHEDULE', '0 3 * * *')

    parts = cron_schedule.split()
    minute, hour = int(parts[0]), int(parts[1])
    day_of_month, month, day_of_week = parts[2], parts[3], parts[4]

    print(f"CRON Schedule: {cron_schedule} -> Minute: {minute}, Hour: {hour}, Day of Month: {day_of_month}, Month: {month}, Day of Week: {day_of_week}")

    scheduler = BackgroundScheduler()
    # Run download_epg_files daily based on CRON_SCHEDULE
    scheduler.add_job(func, CronTrigger.from_crontab(cron_schedule))
    scheduler.start()
    print(f"Scheduler started: EPG files will be downloaded daily at {hour:02d}:{minute:02d} (CRON: {cron_schedule})")
    return scheduler