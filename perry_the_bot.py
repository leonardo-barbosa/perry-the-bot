from Class import ZendeskConnection
from apscheduler.schedulers.blocking import BlockingScheduler

Perry = ZendeskConnection.ZendeskConnection()

# Go Perry, GO!!!
sched = BlockingScheduler()

sched.add_job(Perry.assign_tickets(), minutes=2)
sched.add_job(Perry.tag_yesterday_tickets, hour=22, day_of_week='0-6')
sched.add_job(Perry.notify_pending_interaction_tickets, minutes=120, day_of_week='mon-fri', hour='7-19')

sched.start()
