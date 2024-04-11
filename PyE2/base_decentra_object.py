from .logging import Logger


class BaseDecentrAIObject(object):
  """
  Generic class

  Instructions:

    1. use `super().__init__(**kwargs)` at the end of child `__init__`
    2. define `startup(self)` method for the child class and call 
       `super().startup()` at beginning of `startup()` method

      OR

    use `super().__init__(**kwargs)` at beginning of child `__init__` and then
    you can safely proceed with other initilization 

  """

  def __init__(self, log: Logger,
               create_logger=False,
               DEBUG=False,
               show_prefixes=False,
               prefix_log=None,
               log_at_startup=False,
               **kwargs):

    super(BaseDecentrAIObject, self).__init__()

    if (log is None) or not hasattr(log, '_logger'):
      if not create_logger:
        raise ValueError("Logger object is invalid: {}".format(log))
      else:
        log = Logger(DEBUG=DEBUG, base_folder='.', app_folder='_local_cache')
    # endif

    self.log = log
    self.show_prefixes = show_prefixes
    self.prefix_log = prefix_log
    self.config_data = self.log.config_data
    self.DEBUG = DEBUG
    self.log_at_startup = log_at_startup

    if not hasattr(self, '__name__'):
      self.__name__ = self.__class__.__name__
    self.startup()

    return

  def startup(self):
    self.log.set_nice_prints()
    ver = ''
    if hasattr(self, '__version__'):
      ver = 'v.' + self.__version__
    if hasattr(self, 'version'):
      ver = 'v.' + self.version

    if self.log_at_startup:
      self.P("{}{} startup.".format(self.__class__.__name__, ' ' + ver if ver != '' else ''))
    return

  def shutdown(self):
    self.P("Shutdown in progress...")
    _VARS = ['sess', 'session']
    for var_name in _VARS:
      if vars(self).get(var_name, None) is not None:
        self.P("Warning: {} property {} still not none before closing".format(
          self.__class__.__name__, var_name), color='r')
    return

  def P(self, s, t=False, color=None, prefix=False, **kwargs):
    if self.show_prefixes or prefix:
      msg = "[{}] {}".format(self.__name__, s)
    else:
      if self.prefix_log is None:
        msg = "{}".format(s)
      else:
        msg = "{} {}".format(self.prefix_log, s)
      # endif
    # endif

    _r = self.log.P(msg, show_time=t, color=color, **kwargs)
    return _r

  def D(self, s, t=False, color=None, prefix=False, **kwargs):
    _r = -1
    if self.DEBUG:
      if self.show_prefixes:
        msg = "[DEBUG] {}: {}".format(self.__name__, s)
      else:
        if self.prefix_log is None:
          msg = "[DEBUG] {}".format(s)
        else:
          msg = "[DEBUG]{} {}".format(self.prefix_log, s)
        # endif
      # endif
      _r = self.log.P(msg, show_time=t, color=color, prefix=prefix, **kwargs)
    # endif
    return _r

  def start_timer(self, tmr_id):
    if hasattr(self, '_timers_section'):
      return self.log.start_timer(tmr_id, section=self._timers_section)
    else:
      return self.log.start_timer(sname=self.__name__ + '_' + tmr_id)

  def end_timer(self, tmr_id, skip_first_timing=True, **kwargs):
    if hasattr(self, '_timers_section'):
      return self.log.end_timer(tmr_id, section=self._timers_section)
    else:
      return self.log.end_timer(
        sname=self.__name__ + '_' + tmr_id,
        skip_first_timing=skip_first_timing,
        **kwargs
      )

  def raise_error(self, error_text):
    """
    logs the error and raises it
    """
    self.P("{}: {}".format(self.__class__.__name__, error_text))
    raise ValueError(error_text)

  def timer_name(self, name=''):
    tn = ''
    if name == '':
      tn = self.__class__.__name__
    else:
      tn = '{}__{}'.format(self.__class__.__name__, name)
    return tn

  def __repr__(self):
    # Get the name of the class
    class_name = self.__class__.__name__

    # Get public properties (those not starting with "_")
    public_properties = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    # Convert properties to a string representation
    properties_str = ", ".join(f"{k}={v!r}" for k, v in public_properties.items())

    return f"{class_name}({properties_str})"
