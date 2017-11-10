from Class import ZendeskConnection
from apscheduler.schedulers.blocking import BlockingScheduler

Perry = ZendeskConnection.ZendeskConnection()

# Go Perry, GO!!!
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=2)
def timed_job():
    Perry.assign_tickets()

@sched.scheduled_job('interval', days=1)
def timed_job():
    Perry.tag_yesterday_tickets()


sched.start()
