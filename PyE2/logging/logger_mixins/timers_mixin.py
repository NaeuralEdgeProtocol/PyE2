import traceback
import numpy as np

from collections import OrderedDict, deque
from time import perf_counter, sleep, time


DEFAULT_SECTION = 'main'
DEFAULT_THRESHOLD_NO_SHOW = 0
PERIODS = [60 * 60, 24 * 60 * 60, 30 * 24 * 60 * 60]
PERIODS_STR = ["hour", "day", "month"]
MAX_PERIOD_LAPS = 20
DEFAULT_PERIODIC_MULTIPLIER = 3

MAX_LAPS = 100
ZERO_THRESHOLD = 5e-4

_OBSOLETE_SECTION_TIME = 3600  # sections older than 1 hour are archived

class _TimersMixin(object):
  """
  Mixin for timers functionalities that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_TimersMixin, self).__init__()
    self.timers = None
    self.timer_level = None # no actual purpose following addition of graph
    self.sections_last_used = {}
    self.opened_timers = None
    self.timers_graph = None
    self._timer_error = None
    self.default_timers_section = DEFAULT_SECTION
    self.__timer_mutex = False

    self.start_show_timer = None

    self.reset_timers()
    return

  def _maybe_create_timers_section(self, section=None):
    section = section or self.default_timers_section

    if section in self.timers:
      return

    self.timers[section] = OrderedDict()
    self.timer_level[section] = 0
    self.opened_timers[section] = deque()
    self.timers_graph[section] = OrderedDict()
    self.timers_graph[section]["ROOT"] = {"SLOW" : OrderedDict(), "FAST" : OrderedDict()}
    self._timer_error[section] = False
    return

  def reset_timers(self):
    self.timers = {}
    self.timer_level = {}
    self.opened_timers = {}
    self.timers_graph = {}
    self._timer_error = {}

    self._maybe_create_timers_section()
    return

  @staticmethod
  def get_empty_timer():
    return {
      'MEAN': 0,
      'MAX': 0,
      'COUNT': 0,
      'START': 0,
      'END': 0,
      'PASS': True,
      'LEVEL': 0,

      'START_COUNT': 0,
      'STOP_COUNT': 0,
      
      'LAPS' : deque(maxlen=MAX_LAPS),
      'HISTORY': {
        'LAST': [None for _ in range(len(PERIODS))],
        'DEQUES': [deque(maxlen=MAX_PERIOD_LAPS) for _ in range(len(PERIODS))],
      }
    }

  def restart_timer(self, sname, section=None):
    section = section or self.default_timers_section
    self.timers[section][sname] = self.get_empty_timer()
    return

  def _add_in_timers_graph(self, sname, section=None):
    section = section or self.default_timers_section
    self.timers[section][sname]['LEVEL'] = self.timer_level[section]
    if sname not in self.timers_graph[section]:
      self.timers_graph[section][sname] = {"SLOW" : OrderedDict(), "FAST" : OrderedDict()}

    self.timers_graph[section][sname]["FAST"] = OrderedDict() ## there is no ordered set, so we use OrderedDict with no values
    return

  def start_timer(self, sname, section=None):
    section = section or self.default_timers_section
    if section == self.default_timers_section:
      assert self.is_main_thread, "Attempted to run threaded timer '{}' without section".format(sname)

    self._maybe_create_timers_section(section)

    if not self.DEBUG:
      return -1

    if sname not in self.timers[section]:
      self.restart_timer(sname, section)

    curr_time = perf_counter()
    self._add_in_timers_graph(sname, section=section)
    self.timers[section][sname]['START'] = curr_time
    self.timers[section][sname]['START_COUNT'] += 1
    if len(self.opened_timers[section]) >= 1:
      parent = self.opened_timers[section][-1]
    else:
      parent = "ROOT"
    #endif

    self.timers_graph[section][parent]["FAST"][sname] = None
    self.timers_graph[section][parent]["SLOW"][sname] = None

    self.timer_level[section] += 1
    self.opened_timers[section].append(sname)

    faulty_timers = self._get_section_faulty_timers(section)
    if len(faulty_timers) > 0 and not self._timer_error[section]:
      self.P("Something is wrong with the timers in section '{}':".format(section), color='r')
      for ft in faulty_timers:
        self.P("  {}: {}".format(ft, self.timers[section][ft]), color='r')
      self._timer_error[section] = True
    #endif

    return curr_time

  def get_time_until_now(self, sname, section=None):
    section = section or self.default_timers_section
    ctimer = self.timers[section][sname]
    return perf_counter() - ctimer['START']

  def get_faulty_timers(self):
    dct_faulty = {}
    for section in self.timers:
      dct_faulty[section] = self._get_section_faulty_timers(section)
    return dct_faulty

  def _get_section_faulty_timers(self, section=None):
    section = section or self.default_timers_section
    lst_faulty = []
    for tmr_name, tmr in self.timers[section].items():
      if (tmr['START_COUNT'] - tmr['STOP_COUNT']) > 1:
        lst_faulty.append(tmr_name)
    return lst_faulty

  def end_timer_no_skip(self, sname, section=None, periodic=False):
    return self.end_timer(sname, skip_first_timing=False, section=section, periodic=periodic)

  def get_opened_timer(self, section=None):
    section = section or self.default_timers_section
    timer = self.opened_timers[section][-1]
    return timer, perf_counter() - self.timers[section][timer]['START']

  def get_periodic_multiplier(self):
    if self.config_data is None:
      return DEFAULT_PERIODIC_MULTIPLIER
    return self.config_data.get('PERIODIC_MULTIPLIER', DEFAULT_PERIODIC_MULTIPLIER)

  def add_periodic_record(self, sname, record, section=None, idx=0, check=False):
    chistory = self.timers[section][sname]['HISTORY']
    dq_size = len(chistory['DEQUES'][idx])
    if check and dq_size > 2:
      cmean = np.array(chistory['DEQUES'][idx]).mean()
      cstd = np.std(chistory['DEQUES'][idx])
      cnt = self.timers[section][sname]['COUNT']
      q = self.get_periodic_multiplier()
      limit = cmean + cstd * q
      if limit < record:
        self.P(
          f"[WARNING]Timer {'' if section is None else section + '|'}{sname} "
          f"took longer than expected at iter {cnt} based on {dq_size} records ("
          f"{round(record, 3)} > {round(limit, 3)}[{round(cmean, 3)}+{round(q, 3)}*{round(cstd, 3)}]) [{PERIODS_STR[idx]}]",
          color='r'
        )
      # endif warning
    # endif anomaly check
    chistory['DEQUES'][idx].append(record)
    chistory['LAST'][idx] = self.timers[section][sname]['END']
    return

  def end_timer(self, sname, skip_first_timing=False, section=None, periodic=False):
    section = section or self.default_timers_section
    if sname not in self.timers[section]:
      return
    result = 0
    self.sections_last_used[section] = time()
    if self.DEBUG:
      self.opened_timers[section].pop()
      self.timer_level[section] -= 1

      ctimer = self.timers[section][sname]
      ctimer['STOP_COUNT'] += 1
      ctimer['END'] = perf_counter()
      result = ctimer['END'] - ctimer['START']
      ctimer['LAPS'].append(result)
      if periodic:
        chistory = ctimer['HISTORY']
        for i, period in enumerate(PERIODS):
          if chistory['LAST'][i] is None:
            self.add_periodic_record(sname, result, section=section, idx=i)
          elif ctimer['END'] - chistory['LAST'][i] > period:
            self.add_periodic_record(sname, result, section=section, idx=i, check=True)
          # endif periodic record
        # endfor i, period
      # endif periodic
      _count = ctimer['COUNT']
      _prev_avg = ctimer['MEAN']
      avg = _count * _prev_avg

      if ctimer['PASS'] and skip_first_timing:
        ctimer['PASS'] = False
        return result  # do not record first timing in average nor the max

      ctimer['MAX'] = max(ctimer['MAX'], result)

      ctimer['COUNT'] = _count + 1
      avg += result
      avg = avg / ctimer["COUNT"]
      ctimer['MEAN'] = avg
    return result

  def stop_timer(self, sname, skip_first_timing=False, section=None, periodic=False):
    return self.end_timer(sname=sname, skip_first_timing=skip_first_timing, section=section, periodic=periodic)

  def show_timer_total(self, sname, section=None):
    section = section or self.default_timers_section
    ctimer = self.timers[section][sname]
    cnt = ctimer['COUNT']
    val = ctimer['MEAN'] * cnt
    self.P("  {} = {:.3f} in {} laps".format(sname, val, cnt))
    return

  def _format_timer(self, key, section, was_recently_seen,
                   summary='mean',
                   show_levels=True,
                   show_max=True,
                   show_last=True,
                   show_count=True,
                   div=None,
                   threshold_no_show=None,
                   max_key_size=30,
                   ):

    if threshold_no_show is None:
      threshold_no_show = DEFAULT_THRESHOLD_NO_SHOW

    ctimer = self.timers[section].get(key, None)

    if ctimer is None:
      return

    mean_time = ctimer['MEAN']
    np_laps = np.array(ctimer['LAPS'])
    if len(np_laps) > 0:
      laps_mean = np_laps.mean()
      laps_std = np_laps.std()
      laps_zcount = (np_laps <= ZERO_THRESHOLD).sum()
      laps_nzcount = len(np_laps) - laps_zcount
      laps_nz_mean = np_laps.sum() / laps_nzcount if laps_nzcount > 0 else -1
      laps_low_cnt = (np_laps <= max(ZERO_THRESHOLD, laps_mean - laps_std)).sum()
      laps_low_prc =  laps_low_cnt / np_laps.shape[0] * 100
    else:
      # not mandatory but nice for forever opened 1 time timers
      laps_mean = -1
      laps_std = -1
      laps_zcount = -1
      laps_nzcount = -1
      laps_nz_mean = -1
      laps_low_cnt = -1
      laps_low_prc =  -1
      # end not mandatory

    count = ctimer['COUNT']
    
    if mean_time < threshold_no_show:
      return

    max_time = ctimer['MAX']
    current_time = np_laps[-1] if len(np_laps) > 0 else -1 # ctimer['END'] - ctimer['START']

    if not was_recently_seen:
      key = '[' + key[:max_key_size] + ']'

    if show_levels:
      s_key = '  ' * ctimer['LEVEL'] + key[:max_key_size]
    else:
      s_key = key[:max_key_size]
    msg = None
    if summary in ['mean', 'avg']:
      # self.verbose_log(" {} = {:.4f}s (max lap = {:.4f}s)".format(s_key,mean_time,max_time))
      msg = " {} = {:.4f}s/q:{:.4f}s/nz:{:.4f}s".format(s_key, mean_time, laps_mean, laps_nz_mean)
    else:
      # self.verbose_log(" {} = {:.4f}s (max lap = {:.4f}s)".format(s_key,total, max_time))
      total = mean_time * count
      msg = " {} = {:.4f}s".format(s_key, total)
    if show_max:
      msg += ", max: {:.4f}s".format(max_time)
    if show_last:
      msg += ", lst: {:.4f}s".format(current_time)
    if show_count:
      msg += ", c: {}/L:{:.0f}%".format(count, laps_low_prc)
    if div is not None:
      msg += ", itr(B{}): {:.4f}s".format(div, mean_time / div)
    return msg

  def show_timers(self, indent=4, **kwargs):
    color = kwargs.pop('color', 'n')
    lst_logs = self.format_timers(**kwargs)
    if indent > 0:
      lst_logs = [" " * indent + l for l in lst_logs]
    if len(lst_logs) > 0:
      full_log = "\n".join(lst_logs)      
      self.verbose_log(full_log.lstrip(), color=color)
    return

  def show_timings(self, **kwargs):
    self.show_timers(**kwargs)
    return

  def format_timers(self, summary=None,
                  title=None,
                  show_levels=True,
                  show_max=True,
                  show_last=True,
                  show_count=True,
                  div=None,
                  threshold_no_show=None,
                  selected_sections=None,
                  obsolete_section_time=_OBSOLETE_SECTION_TIME,
                  ):

    if selected_sections is not None:
      assert isinstance(selected_sections, list)

    if threshold_no_show is None:
      threshold_no_show = DEFAULT_THRESHOLD_NO_SHOW

    if summary is None:
      summary = 'mean'

    if title is None:
      title = ''
    
    lst_logs = []
    self.start_show_timer = time()
    try:
      while self.__timer_mutex:
        elapsed_in_show = time() - self.start_show_timer
        if elapsed_in_show > 15:
          raise ValueError("show_timers: Run time exceeded! Mutex is locked for more than 15 seconds.")
        sleep(0.001)
      # end while
      self.__timer_mutex = True
      
      self.start_show_timer = time()
      self.__dfs_stack = deque(maxlen=100)
      
      def dfs(visited, graph, node, was_recently_seen, logs, sect):
        self.__dfs_stack.append(node)
        elapsed_in_show = time() - self.start_show_timer
        
        if elapsed_in_show > 5:
          raise ValueError("show_timers: Run time exceeded! DFS took longer than 5 seconds. Stack: {}".format(self.__dfs_stack))
        
        if node not in visited:
          formatted_node = self._format_timer(
            key=node,
            section=sect,
            was_recently_seen=was_recently_seen,
            summary=summary,
            show_levels=show_levels, show_last=show_last,
            show_max=show_max, show_count=show_count, div=div,
            threshold_no_show=threshold_no_show
          )
          if formatted_node is not None:
            logs.append(formatted_node)
          visited.add(node)
          slow_keys = list(graph[node]["SLOW"].keys())
          fast_keys = list(graph[node]["FAST"].keys())
          for neighbour in slow_keys:
            recently_seen = neighbour in fast_keys
            dfs(visited, graph, neighbour, recently_seen, logs, sect)
          #endfor
        #endif
      #enddef

      if self.DEBUG:
        if len(title) > 0:
          title = ' ' + title
        header = "Timing results{} at {}:".format(title, self.now_str(nice_print=True, short=True))
        if threshold_no_show > 0:
          header += " (discarding entries with time < {})".format(threshold_no_show)
        lst_logs.append(header)

        ## SORTING sections and keeping the default section the first one ..
        keys = list(self.timers.keys())
        if selected_sections is not None:
          keys = selected_sections

        add_back_default_section = False
        if self.default_timers_section in keys:
          add_back_default_section = True
          keys.pop(keys.index(self.default_timers_section))
        keys.sort()
        if add_back_default_section:
          keys = [self.default_timers_section] + keys

        old_sections = []
        for section in keys:
          last_see_ago = None
          if section in self.sections_last_used:
            last_see_ago = time() - self.sections_last_used[section]
            if last_see_ago > obsolete_section_time:
              old_sections.append(section)
              continue
          lst_logs.append("Section '{}'{}".format(
            section, " last seen {:.1f}s ago".format(last_see_ago) if last_see_ago is not None else ""
          ))
          buffer_visited = set()
          dfs(buffer_visited, self.timers_graph[section], "ROOT", True, lst_logs, section)
        if len(old_sections) > 0:
          lst_logs.append("Archived {} sections older than {:.1f} hrs.".format(
            len(old_sections), obsolete_section_time / 3600, 
          ))
      else:
        self.verbose_log("DEBUG not activated!")
    except Exception as exc:
      self.P("EXCEPTION in show_timers: {}. Stacktrace:\n{}".format(exc, traceback.format_exc()), color='r')
    self.__timer_mutex = False
    return lst_logs

  def get_timing_dict(self, skey, section=None):
    section = section or self.default_timers_section
    timers_section = self.timers.get(section, {})
    dct = timers_section.get(skey, {})
    return dct

  def get_timer(self, skey, section=None):
    return self.get_timing_dict(skey, section=section)

  def get_timer_overall_mean(self, skey, section=None):
    tmr = self.get_timer(skey, section=section)
    result = tmr.get('MEAN', 0)
    return result

  def get_timer_mean(self, skey, section=None):
    tmr = self.get_timer(skey, section=section)
    laps = tmr.get('LAPS', [])
    result = np.mean(laps) if len(laps) > 0 else -1
    return result


  def get_timer_count(self, skey, section=None):
    tmr = self.get_timer(skey, section=section)
    result = tmr.get('COUNT', 0)
    return result
  
  def import_timers_section(self, dct_timers, dct_timers_graph, section, overwrite=False):
    if self.__timer_mutex:
      # we skip this import until next time
      self.P("WARNING: Cannot import section '{}' with {} timers while processing sections!".format(
        section, len(dct_timers)
      ), color='r')
      return
    if section in self.timers and not overwrite:
      self.P("WARNING: Cannot import section '{}' with {} timers as there is already a existing section".format(
        section, len(dct_timers)
      ), color='r')
      return False
    self.timers[section] = dct_timers
    self.timers_graph[section] = dct_timers_graph
    self.sections_last_used[section] = time()
    return True
  
  def export_timers_section(self, section=None):
    section = section or self.default_timers_section
    if section not in self.timers:
      self.P("WARNING: Cannot export unexisting timers section '{}'".format(
        section
      ), color='r')
      return None, None
    dct_timers = self.timers[section]
    dct_timers_graph = self.timers_graph[section]
    return dct_timers, dct_timers_graph
