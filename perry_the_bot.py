from Class import ZendeskConnection
from apscheduler.schedulers.blocking import BlockingScheduler

Perry = ZendeskConnection.ZendeskConnection()

# Go Perry, GO!!!
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=2)
def timed_job():
    Perry.assign_tickets()

@sched.scheduled_job('cron', hour=22, day_of_week='0-6')
def timed_job():
    Perry.tag_yesterday_tickets()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour='7-19/2')
def timed_job():
    Perry.notify_pending_interaction_tickets()

sched.start()
