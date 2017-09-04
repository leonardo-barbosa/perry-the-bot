from Class import ZendeskConnection
from apscheduler.schedulers.blocking import BlockingScheduler
Perry = ZendeskConnection.ZendeskConnection()

# Go Perry, GO!!!
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    Perry.assign_tickets()

sched.start()