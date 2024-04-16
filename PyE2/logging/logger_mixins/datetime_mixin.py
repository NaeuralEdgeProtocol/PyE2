from datetime import datetime as dt, timedelta
from dateutil.relativedelta import relativedelta
from ...const import WEEKDAYS_SHORT


class _DateTimeMixin(object):
  """
  Mixin for date and time functionalities that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_DateTimeMixin, self).__init__()
    return

  @staticmethod
  def get_delta_date(date, delta=None, period=None):
    daily_periods = ['d']
    weekly_periods = ['w', 'w-mon', 'w-tue', 'w-wed', 'w-thu', 'w-fri', 'w-sat', 'w-sun']
    monthly_periods = ['m']

    if delta is None:
      delta = 1

    if period is None:
      period = 'd'

    period = period.lower()
    assert period in daily_periods + weekly_periods + monthly_periods

    is_string_date = False
    fmt = '%Y-%m-%d'
    if type(date) is str:
      is_string_date = True
      date = dt.strptime(date, fmt)

    if period in daily_periods:
      delta_date = date + relativedelta(days=delta)
    elif period in monthly_periods:
      delta_date = date + relativedelta(months=delta)
    elif period in weekly_periods:
      delta_date = date + relativedelta(weeks=delta)

    if is_string_date:
      delta_date = dt.strftime(delta_date, fmt)

    return delta_date

  @staticmethod
  def split_time_intervals(start, stop, seconds_interval):
    """splits a predefined timeinterval [start, stop] into smaller intervals
    each of length seconds_interval.
    the method returns a list of dt tuples intervals"""
    lst = []
    _start = None
    _stop = start
    while _stop <= stop:
      _start = _stop
      _stop = _start + timedelta(seconds=seconds_interval)
      lst.append((_start, _stop))
    # endwhile
    return lst

  @staticmethod
  def timestamp_begin(ts, begin_of):
    """returns a new timestamp as if it were the start of minute/hour/day/week/month/year"""
    if ts is None:
      ts = dt.now()
    # endif
    if begin_of == 'minute':
      ts = dt(
        year=ts.year, month=ts.month, day=ts.day,
        hour=ts.hour, minute=ts.minute, second=0
      )
    elif begin_of == 'hour':
      ts = dt(
        year=ts.year, month=ts.month, day=ts.day,
        hour=ts.hour, minute=0, second=0
      )
    elif begin_of == 'day':
      ts = dt(
        year=ts.year, month=ts.month, day=ts.day,
        hour=0, minute=0, second=0
      )
    elif begin_of == 'month':
      ts = dt(
        year=ts.year, month=ts.month, day=1,
        hour=0, minute=0, second=0
      )
    elif begin_of == 'year':
      ts = dt(
        year=ts.year, month=1, day=1,
        hour=0, minute=0, second=0
      )
    # endif
    return ts

  @staticmethod
  def time_in_interval_hours(ts, start, end):
    """
    Parameters:
      ts: datetime timestamp
      start = 'hh:mm'
      end = 'hh:mm'
    Returns:
      True if given timestamp is in given interval
    """
    h_start, m_start = start.split(':')
    h_end, m_end = end.split(':')
    start_time = int(h_start) * 60 + int(m_start)
    end_time = int(h_end) * 60 + int(m_end)
    current_time = ts.hour * 60 + ts.minute
    is_inside_interval = start_time <= current_time < end_time
    if end_time < start_time:
      # e.g. for interval (22:30, 14:30) we will check that the current time is not in (14:30, 22:30)
      is_inside_interval = not (end_time <= current_time < start_time)
    return is_inside_interval

  @staticmethod
  def now_in_interval_hours(start, end):
    """
    Parameters:
      start = 'hh:mm'
      end = 'hh:mm'
    Returns:
      True if current time is in given interval
    """
    return _DateTimeMixin.time_in_interval_hours(
      ts=dt.now(),
      start=start,
      end=end
    )

  @staticmethod
  def extract_hour_interval_idx(ts, lst_schedule):
    """
    Method for extracting index of interval in which ts is situated.
    Parameters
    ----------
    ts - datetime timestamp - the searched timestamp
    schedule - list of format [
        ['hh:mm', 'hh:mm'],
        ...
      ] describing intervals of time

    Returns
    -------
    idx - int or None
    If found in an interval idx will be the index of that interval in schedule
    Otherwise it will be None
    """
    for idx, (start, end) in enumerate(lst_schedule):
      if _DateTimeMixin.time_in_interval_hours(ts=ts, start=start, end=end):
        return idx
    return None

  @staticmethod
  def extract_weekday_schedule(ts, schedule, weekdays=None, return_day_name=False):
    """
    Method for extracting the working hour intervals corresponding to the weekday
    indicated by ts in case the schedule is defined using weekdays.
    Parameters
    ----------
    ts - datetime timestamp - the timestamp for which we need the working hours
    schedule - dict or any
    - if dict it will be able to provide different working hours for each weekday
      - the keys from schedule need to be in weekdays of if weekdays not provided in ['MON', 'TUE', ..., 'SUN']
    - otherwise it will be returned as it is
    weekdays - list of aliases for the weekdays
    - if this is not provided it will default to ['MON', 'TUE', ..., 'SUN']
    - this has to be of length 7 if provided
    return_day_name - boolean that indicates if we will provide only
    the working hours or the name of the week day too

    Returns
    -------
    if return_day_name:
      res
        list of format [
          ['hh:mm', 'hh:mm'],
          ...
        ] describing intervals of time
      OR
        None
    otherwise:
      res, day_name - res described as above and day_name as a string or None in case schedule is not dict
    """
    if isinstance(schedule, dict):
      if weekdays is None:
        weekdays = WEEKDAYS_SHORT
      assert len(weekdays) == 7, \
        f"`weekdays` should be a list of length 7, but it is {weekdays} with length {len(weekdays)}"

      normalized_weekdays = [x.upper() for x in weekdays]
      normalized_schedule = {
        key.upper(): value
        for (key, value) in schedule.items()
      }
      for key in schedule.keys():
        if key.upper() not in normalized_weekdays:
          raise Exception(f'Key {key} should not be in the schedule dictionary!'
                          f'The keys in the schedule dictionary can only be from {normalized_weekdays}')
      # endfor key in schedule.keys()

      ts_weekday_str = normalized_weekdays[ts.weekday()]
      res = normalized_schedule.get(ts_weekday_str, None)
      return res if not return_day_name else (res, ts_weekday_str)
    return schedule if not return_day_name else (schedule, None)

  @staticmethod
  def extract_weekday_schedule_now(schedule, weekdays=None, return_day_name=False):
    """
    Shortcut extract_weekday_schedule with ts=datetime.now()
    """
    return _DateTimeMixin.extract_weekday_schedule(
      ts=dt.now(),
      schedule=schedule,
      weekdays=weekdays,
      return_day_name=return_day_name
    )

  @staticmethod
  def time_in_schedule(ts, schedule, weekdays=None):
    """
    Method for checking if the provided timestamp in ts is in some interval specified in schedule.
    Parameters
    ----------
    ts - datetime timestamp - the timestamp to be checked
    schedule - dict or any
    - if dict it will be able to provide different working hours for each weekday
      - the keys from schedule need to be in weekdays of if weekdays not provided in ['MON', 'TUE', ..., 'SUN']
    - otherwise it will be returned as it is
    weekdays - list of aliases for the weekdays
    - if this is not provided it will default to ['MON', 'TUE', ..., 'SUN']
    - this has to be of length 7 if provided
    return_day_name - boolean that indicates if we will provide only
    the working hours or the name of the week day too

    Returns
    -------
    False if:
      - schedule is None
      - schedule provides hour intervals but ts is not in any of them
    True otherwise
    """
    if schedule is None:
      return False
    if len(schedule) < 1:
      return True
    if isinstance(schedule, list):
      # ts in schedule ignoring the weekday
      if len(schedule) < 1:
        return True
      for (start, end) in schedule:
        if _DateTimeMixin.time_in_interval_hours(ts=ts, start=start, end=end):
          return True
      return False
    elif isinstance(schedule, dict):
      # ts in schedule considering the weekday
      return _DateTimeMixin.time_in_schedule(
        ts=ts,
        schedule=_DateTimeMixin.extract_weekday_schedule(
          ts=ts,
          schedule=schedule,
          weekdays=weekdays
        )
      )
    # endif isinstance(schedule, list)
    raise Exception(f'`schedule` should be either list, dict or None, but instead is {type(schedule)}')

  @staticmethod
  def now_in_schedule(schedule, weekdays=None):
    return _DateTimeMixin.time_in_schedule(
      ts=dt.now(),
      schedule=schedule,
      weekdays=weekdays
    )


if __name__ == '__main__':
  from PyE2 import Logger
  log = Logger(
    'gigi',
    base_folder='.',
    app_folder='_local_cache'
  )

  working_hours_tests = [
    [  # list of universal working hours interval for any day
      ['10:10', '21:10']
    ],
    [  # list of universal working hours intervals for any day
      ['21:10', '10:10'],
      ['11:10', '11:25']
    ],
    {  # dict of working hours intervals based on the week day with all the days described
      "mon": [["07:00", "18:00"]],
      "tue": [["07:00", "15:00"], ["16:30", "19:30"]],
      "wEd": [["07:00", "18:00"]],
      "thU": [["07:00", "18:00"]],
      "FRI": [],  # when [] given the entire day will be considered opened
      "sat": [["00:00", "24:00"]],
      "sun": [["10:00", "15:00"]]
    },
    {  # dict of working hours intervals based on the week day with some the days described
      # (the undescribed days will be considered fully closed)
      "mon": None,  # when None given the specified date will also be considered fully closed
      "tue": [["07:00", "15:00"], ["16:30", "19:30"]],
      "wed": [["07:00", "18:00"]],
    },
    {  # dict of working hours intervals based on the week day with some the days described,
      # but with unexpected fields => an exception should be raised
      "mon": [],
      "TuesdayWednesday": [["07:00", "15:11"]]
    }
  ]

  should_raise = [False, False, False, False, True]
  it = 0
  for cfg_test in working_hours_tests:
    log.P(f'Starting test {it + 1}/{len(working_hours_tests)}')
    log.P(f'Current schedule is: {cfg_test}')
    current_ts = dt.now()
    log.P(f'Now the time is: {current_ts}({WEEKDAYS_SHORT[current_ts.weekday()]})')
    try:
      if log.time_in_schedule(ts=current_ts, schedule=cfg_test):
        log.P('We are in working hours!')
      else:
        log.P('We are not in working hours!')
      log.P(f'Test {it + 1}/{len(working_hours_tests)} passed!')
    except Exception as e:
      log.P(f'Exception occured `{e}`')
      if should_raise[it]:
        log.P(f'Test {it + 1}/{len(working_hours_tests)} (expected exception) passed!')
      else:
        log.P(f'Test {it + 1}/{len(working_hours_tests)} failed!')

    it += 1
  # endfor cfg_test in working_hours_tests

