import os
import sys
import traceback
from threading import Lock
from time import localtime, strftime
from time import time as tm


class Logger():
  def __init__(self, silent=False, **kwargs) -> None:
    self.print_lock = Lock()
    self.silent = silent
    return

  def P(self, msg, **kwargs):
    with self.print_lock:
      print(msg, flush=True)
    return

  def D(self, msg, **kwargs):
    if not self.silent:
      self.P(msg, **kwargs)

  def get_unique_id(self, size=8):
    """
    efficient and low-colision function for small unique id generation
    """
    import random
    import string
    alphabet = string.ascii_lowercase + string.digits
    uid = ''.join(random.choices(alphabet, k=size))
    return uid

  def start_timer(self, *args, **kwargs):
    return

  def end_timer(self, *args, **kwargs):
    return

  def stop_timer(self, *args, **kwargs):
    return

  def time_to_str(self, t=None, fmt='%Y-%m-%d %H:%M:%S'):
    if t is None:
      t = tm()
    return strftime(fmt, localtime(t))

  def get_error_info(self, return_err_val=False):
    """
    Returns error_type, file, method, line for last error if available

    Parameters
    ----------
    return_err_val: boolean, optional
      Whether the method returns or not the error message (err_val)

    Returns
    -------
    if not return_err_val:
      (tuple) str, str, str, str : errortype, file, method, line
    else:
      (tuple) str, str, str, str, str : errortype, file, method, line, err message
    """
    err_type, err_val, err_trace = sys.exc_info()
    if False:
      # dont try this at home :) if you want to pickle a logger instance after
      # `get_error_info` was triggered, then it won't work because `self._last_extracted_error`
      # contain an object of type `traceback` and tracebacks cannot be pickled
      self._last_extracted_error = err_type, err_val, err_trace
    # endif
    if err_type is not None:
      str_err = err_type.__name__
      stack_summary = traceback.extract_tb(err_trace)
      last_error_frame = stack_summary[-1]
      fn = os.path.splitext(os.path.split(last_error_frame.filename)[-1])[0]
      lineno = last_error_frame.lineno
      func_name = last_error_frame.name
      if not return_err_val:
        return str_err, 'File: ' + fn, 'Func: ' + func_name, 'Line: ' + str(lineno)
      else:
        return str_err, 'File: ' + fn, 'Func: ' + func_name, 'Line: ' + str(lineno), str(err_val)
    else:
      return "", "", "", "", ""

  def dict_pretty_format(self, d, indent=4, as_str=True, display_callback=None, display=False, limit_str=250):
    assert isinstance(d, dict), "`d` must be dict"
    if display and display_callback is None:
      display_callback = self.P
    lst_data = []

    def deep_parse(dct, ind=indent):
      for ki, key in enumerate(dct):
        # dct actually can be dict or list
        str_key = str(key) if not isinstance(key, str) else '"{}"'.format(key)
        if isinstance(dct, dict):
          value = dct[key]
          lst_data.append(' ' * ind + str(str_key) + ' : ')
        else:
          value = key
        if isinstance(value, dict):
          if lst_data[-1][-1] in ['[', ',']:
            lst_data.append(' ' * ind + '{')
          else:
            lst_data[-1] = lst_data[-1] + '{'
          deep_parse(value, ind=ind + indent)
          lst_data.append(' ' * ind + '}')
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
          lst_data[-1] = lst_data[-1] + '['
          deep_parse(value, ind=ind + indent)
          lst_data.append(' ' * ind + ']')
        else:
          str_value = str(value) if not isinstance(value, str) else '"{}"'.format(value)
          if isinstance(value, str) and len(str_value) > limit_str:
            str_value = str_value[:limit_str]
          lst_data[-1] = lst_data[-1] + str_value

        if ki < (len(dct) - 1):
          lst_data[-1] = lst_data[-1] + ','
      return

    deep_parse(dct=d, ind=0)

    displaybuff = "{\n"
    for itm in lst_data:
      displaybuff += '  ' + itm + '\n'
    displaybuff += "}"

    if display_callback is not None:
      displaybuff = "Dict pretty formatter:\n" + displaybuff
      display_callback(displaybuff)
    if as_str:
      return displaybuff
    else:
      return lst_data

  def camel_to_snake(self, s):
    import re
    if s.isupper():
      result = s.lower()
    else:
      s = re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
      s = s.replace('__', '_')
      result = s
    return result
