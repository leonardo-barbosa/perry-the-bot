from Class import ZendeskConnection
from apscheduler.schedulers.blocking import BlockingScheduler
Perry = ZendeskConnection.ZendeskConnection()

sched = BlockingScheduler()

# Go Perry, GO!!!
Perry.assign_tickets()


@sched.scheduled_job('interval', minutes=1)
def timed_job():
    Perry.assign_tickets()

sched.start()