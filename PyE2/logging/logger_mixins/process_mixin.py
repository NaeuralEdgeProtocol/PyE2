import os
import sys

class _ProcessMixin(object):
  """
  Mixin for process functionalities that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_ProcessMixin, self).__init__()
    self._close_callback = None
    return

  @staticmethod
  def runs_from_ipython():
    try:
      __IPYTHON__
      return True
    except NameError:
      return False

  @staticmethod
  def runs_with_debugger():
    gettrace = getattr(sys, 'gettrace', None)
    if gettrace is None:
      return False
    else:
      return not gettrace() is None

  @staticmethod
  def get_current_process_memory(mb=True):
    import psutil
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / pow(1024, 2 if mb else 3)
    return mem

  def _default_close_callback(self, sig, frame):
    self.P("SIGINT/Ctrl-C received. Script closing")
    if self._close_callback is None:
      self.P(
        "WARNING: `register_close_callback` received and will force close. Please provide a callback where you can stop the script loop and deallocate nicely.")
      sys.exit(0)
    else:
      self._close_callback()
    return

  def register_close_callback(self, func=None):
    """
    will register a SIGINT/Ctrl-C callback or will default to the one in Logger
    """
    import signal
    if func is None:
      self.P(
        "WARNING: register_close_callback received NO callback. The script will not behave nice. Please provide a callback where you can stop the script nicely. ")
    self._close_callback = func
    signal.signal(signal.SIGINT, self._default_close_callback)
    self.P("Registered {} SIGINT/Ctrl-C callback".format('custom' if func else 'default'))
    return
