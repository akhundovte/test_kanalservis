
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from sources.services import load_orders
from shared.settings import config
from shared.utils.timezone import now_local_with_tz


def start_schedule() -> None:
    scheduler = BlockingScheduler(timezone=config.TIME_ZONE)
    start_date = now_local_with_tz() + config.JOB_PERIODIC_START_OFFSET
    scheduler.add_job(
        func=load_orders,
        trigger=IntervalTrigger(
            start_date=start_date,
            **config.PARAMS_PERIODIC_JOB_TRIG
        ),
        id='periodic_job',
        replace_existing=True,
        )
    scheduler.start()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    start_schedule()
