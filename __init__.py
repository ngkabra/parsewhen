#!/usr/bin/python
import re
from datetime import datetime, date, time, timedelta

def ParseWhenError(Exception):
    pass


weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 
            'friday', 'saturday', 'sunday']
weekdays_dict = dict([(w, num) for (num, w) in enumerate(weekdays)] +
                     [(w[0:3], num) for (num, w) in enumerate(weekdays)])

time_re = re.compile('(?P<day>[a-zA-Z]*)\s*(?P<hours>\d{1,2})?(:(?P<mins>\d{2}))?\s*(?P<ampm>am|pm)?$', re.I)
relative_time_re = re.compile('\+\s*((?P<days>\d+)d)?\s*((?P<hours>\d+)h)?\s*((?P<mins>\d+)m)?$', re.I)

def usage(msg):
    if msg:
        msg = msg + '. '
    raise ParseWhenError(msg + 
                         '''Format for timestamp is "17:23"
or "tomorrow 9:32pm" or "Tue 19:15"
or "+1h30m" or "+3d 2h"
''')

def _aeq(d1, d2):
    return d1.replace(second=0, microsecond=0) == d2.replace(second=0, microsecond=0)

def weekday(str):
    '''convert weekday name 'str' to a weekday number mon=0, sun=6
    
    Return None if this is not a weekday
    '''
    return weekdays_dict.get (str.lower(), None)

def parse_day(str):
    '''parse the name of a day str and return a date object
    
    Returns a date object that is appropriately offest from today
    Thus tomorrow will return date.today() + timedelta(days=1) etc...

    If a day of the week is specified, then it will return the date
    of the next day (starting from tomorrow) which has that
    day-of-the-week. Thus, if today is Thursday, then Fri will return
    tomorrow's date, Mon will return the date that is 4 days from now
    and Thu will return the date that is 7 days from now.
    '''
    if not str or str == 'today':
        return datetime.today()
    elif str == 'tomorrow' or str == 'tom':
        return datetime.today() + timedelta(days=1)

    w = weekday(str)
    if w is None:
        usage('Incorrect day specified: ' + str
              + '. Use today/tomorrow/mon/tue/wed')
    else:
        diff = w - datetime.today().weekday()
        if diff <= 0:
            diff += 7
        return datetime.today() + timedelta(days=diff)

def parse_when(str):
    '''Parse a date+timestamp

    See how "parse_when" is used in the tests below to get
    an idea of how to use it.

    Note: _aeq checks whether to dates are approximately equal
          (This is needed because otherwise our tests will always fail
          due to differences in microseconds. Note: rarely, a test
          might still fail if the second changes over just after
          parse_when is called and before datetime.now() is called)

    >>> _aeq(parse_when('+1h'), datetime.now() + timedelta(hours=1))
    True
    >>> _aeq(parse_when('+1m'), datetime.now() + timedelta(minutes=1))
    True
    >>> _aeq(parse_when('+12h 1m'), datetime.now() + timedelta(hours=12, minutes=1))
    True
    >>> _aeq(parse_when('+3d2h'), datetime.now() + timedelta(hours=24*3+2))
    True
    >>> _aeq(parse_when('+3d 7m'), datetime.now() + timedelta(hours=24*3, minutes=7))
    True

    >>> d = parse_when('11:13')
    >>> d.date() == date.today() and d.hour == 11 and d.minute == 13
    True

    >>> d = parse_when('11:13pm')
    >>> d.date() == date.today() and d.hour == 23 and d.minute == 13
    True

    >>> d = parse_when('tomorrow 15:15')
    >>> d.date() == date.today() + timedelta(days=1) and d.hour == 15 and d.minute == 15
    True

    >>> d = parse_when('mon 12:00 pm')
    >>> d.strftime('%A') == 'Monday' and 0 < (d - datetime.now()).days <= 7
    True

    >>> d = parse_when('12pm')
    >>> d.hour == 12
    True
    
    >>> d = parse_when('12:05 am')
    >>> d.hour == 0 and d.date() == date.today()
    True

    >>> d = parse_when('1 am')
    >>> d.hour == 1 and d.date() == date.today()
    True
    '''
    str = str.strip().lower()
    if not str:
        return None

    if str.startswith('+'):
        m = relative_time_re.match(str)
        if m:
            #  convert all of them to integer (default=0)
            md = dict((k, int(v or '0')) for k,v in m.groupdict().items())
            return datetime.now() + timedelta(days=md['days'],
                                              hours=md['hours'],
                                              minutes=md['mins'])
        else:
            raise ParseWhenError('Bad format for relative date')

    else:
        m = time_re.match(str)
        if m:
            md = m.groupdict()
            the_minute = int(md['mins'] or '0')
            the_hour = int(md['hours'] or '0')
            if md['ampm'] == 'pm' and the_hour < 12:
                the_hour += 12
            if md['ampm'] == 'am' and the_hour == 12:
                the_hour = 0
            the_time = time(hour=the_hour,
                            minute=the_minute)
            the_date = parse_day(md['day'])
            return datetime.combine(the_date, the_time)
        else:
            usage('Bad format for day/date')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
