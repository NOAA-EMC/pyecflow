import os
from pwd import getpwuid

import pyflow as pf


scratchdir = os.path.join(os.path.abspath(''), 'scratch')
filesdir = os.path.join(scratchdir, 'files')
outdir = os.path.join(scratchdir, 'out')

if not os.path.exists(filesdir):
    os.makedirs(filesdir, exist_ok=True)

if not os.path.exists(outdir):
    os.makedirs(outdir, exist_ok=True)

passwd = getpwuid(os.getuid())

server_host = 'localhost'
server_port = 1500+passwd.pw_uid


with pf.Suite('test') as n:
    with pf.Family('f2'):
        pf.Variable('SLEEP', 20)
        t1 = pf.Task('t1')
        t2 = pf.Task('t2')
        t3 = pf.Task('t3')
        t4 = pf.Task('t4')
        t5 = pf.Task('t5')

    t1.time = '00:30 23:30 00:30'  # start(hh:mm) end(hh:mm) increment(hh:mm)
    t2.day = 'thursday'            # thursday at 1 pm
    t2.time = '13:00'
    t3.time = '0 12 * * *'         # time is not considered until date is free
    t3.date = '1.*.*'              # `day.month.year` - * means every day, month, year
    t4.time = '+00:02'             # + means realative to suite begin/requeue time
    t5.time = '00:02'              # 2 minutes past midnight

with pf.Suite('test') as m:
    with pf.Family('f3'):
        with pf.Task('t1') as t1:
            t1.time = '23:00'               # at next 23:00
        with pf.Task('t2') as t2:
            t2.time = '0 10-20 * * *'       # every hour between 10 am and 8 pm
        with pf.Task('t3') as t3:
            t3.time = '+00:01'              # one minute after the suite has begun
        with pf.Task('t4') as t4:
            t4.time = '+00:10 01:00 00:05'  # 10 to 60 minutes after begin every 5 minutes

with pf.Suite('test') as p:
    with pf.Family('f4'):
        with pf.Task('t1') as t1:
            t1.cron = '0 23 * * *'                                           # every day at 11 pm
        with pf.Task('t2') as t2:
            t2.cron = '0 8-12 * * *'                                         # every hour between 8 and 12 am
        with pf.Task('t3') as t3:
            t3.cron = '0 11 * * SUN,TUE'                                     # every Sunday and Tuesday at 11 am
        with pf.Task('t4') as t4:
            t4.cron = '0 2 1,15 * *'                                         # every 1st and 15th of each month at 2 am
        with pf.Task('t5') as t5:
            t5.cron = '0 14 1 1 *'                                           # every first of January at 2 pm
        with pf.Task('t6'):
            pf.Cron('23:00', last_week_days_of_the_month=[5])                # every *last* Friday of month at 11 pm
        with pf.Task('t7'):
            pf.Cron('23:00', days_of_month=[1], last_day_of_the_month=True)  # every first and last of month at 11 pm

with pf.Suite('test', host=pf.LocalHost(), files='/test') as s:
    with pf.Family('house_keeping'):
        with pf.Task('clear_log', script=[
            '# copy the log file to the ECF_HOME/log directory',
            'cp %ECF_LOG% %ECF_HOME%/log/.',
            '',
            '# clear the log file',
            'ecflow_client --log=clear',
        ]):
            pf.Cron('30 22 * * SUN') # run every Sunday at 10:30 pm

with pf.Suite('test') as r:
    with pf.Family('f5'):
        with pf.Task('t1') as t1:
            t1.date = '31.12.2012' # the 31st of December 2012
        with pf.Task('t2') as t2:
            t2.date = '01.*.*'     # every first of the month
        with pf.Task('t3') as t3:
            t3.date = '*.10.*'     # every day in October
        with pf.Task('t4') as t4:
            t4.date = '1.*.2008'   # every first of the month, but only in 2008
        with pf.Task('t5') as t5:
            t5.day = 'monday'      # every monday

with pf.Suite('test') as t:
    with pf.Family('f6'):
        with pf.Task('t1') as t1:
            t1.time = '10:00'                # here day acts like a guard over the time. i.e. time is not considered until Monday
            t1.day = 'monday'                # run on Monday at 10 am
        with pf.Task('t2') as t2:
            t2.time = '0 1,16 * * *'         # on the same node, day/date acts like a guard over the time attributes
            t2.date = ['01.*.*', '10.*.*']   # the first and tenth of every month and year
            t2.day = ['sunday', 'wednesday'] # the time is only set free *if* we are on one of the day/dates

with pf.Suite('test') as u:
    with pf.Family('f1') as f1:
        f1.day = 'monday'     # the day *still* guards the time attribute
        with pf.Task('t1') as t1:
            t1.time = '10:00' # will run on Monday at 10 am
    with pf.Family('f2') as f2:
        f2.time = '10:00'
        with pf.Task('t2') as t2:
            t2.day = 'monday' # this will run on Monday morning at 00:00 and Monday at 10 am

with pf.Suite('test') as v:
    with pf.Family('f1') as f1:
        with pf.Task('t1') as t1:
            t1.time = '23:00' # t1.triggers = ':TIME == 2300'
        with pf.Task('t2') as t2:
            t2.date = '1.*.*' # t2.triggers = ':DD == 1'
        with pf.Task('t3') as t3:
            t3.day = 'monday' # t3.triggers = ':DOW == 1'

with pf.Suite('test') as w:
    with pf.Family('f1') as f1:
        with pf.Task('t1') as t1:
            t1.time = '23:00'                           # time attributes
            t1.day = 'monday'
        with pf.Task('t2') as t2:
            t2.triggers = ':DOW == 1 and :TIME >= 1300' # time based trigger
        with pf.Task('t3') as t3:
            t3.triggers = ':TIME >= 1300'               # combination
            t3.day = 'monday'

with pf.Suite('test') as x:
    with pf.Family('f1') as f1:
        with pf.Task('t1') as t1:
            t1.triggers = ':ECF_DATE == 20200720 and :TIME >= 1000'
        with pf.Task('t2') as t2:
            t2.triggers = ':DOW == 4 and :TIME >= 1300'
        with pf.Task('t3') as t3:
            t3.triggers = ':DD == 1 and :TIME >= 1200'
        with pf.Task('t4') as t4:
            t4.triggers = '(:DOW == 1 and :TIME >= 1300) or (:DOW == 5 and :TIME >= 1000)'
        with pf.Task('t5') as t5:
            t5.triggers = ':TIME == 0002' # 2 minutes past midnight


#s.check_definition()
print('time:')
print(n)
print('time set:')
print(m)
print("\n cron:")
print(p)
print("\nMake log:")
print(s)
print("\nDate time:")
print(r)
print("Mixing dependencies on a node:")
print(t)
print("mixing time dependencies:")
print(u)
print("time triggers:")
print(v)
print("time triggers with and/or logic:")
print(w)
print("time triggers with and/or logic 2:")
print(x)
#s.deploy_suite()
#s.replace_on_server(server_host, server_port)
