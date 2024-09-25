import io
import zlib
import sys
import base64
import traceback
import re
import inspect
import ctypes
import threading
import queue

from .checker import ASTChecker, CheckerConstants

__VER__ = '0.6.1'

UNALLOWED_DICT = {
  'import ': {
    'error': 'Imports are not allowed in plugin code ',
    'type': 'import',
  },

  'from ': {
    'error': 'Imports are not allowed in plugin code ',
    'type': 'import',
  },

  'globals': {
    'error': 'Global vars access is not allowed in plugin code ',
    'type': CheckerConstants.var,
  },

  '__builtins__': {
    'error': '__builtins__ access is not allowed in plugin code ',
    'type': CheckerConstants.var,
  },

  'locals': {
    'error': 'Local vars dict access is not allowed in plugin code ',
    'type': CheckerConstants.var,
  },

  'memoryview': {
    'error': 'Pointer handling is unsafe in plugin code ',
    'type': CheckerConstants.var,
  },

  'log': {
    'error': 'Logger object cannot be used directly in plugin code - please use API ',
    'type': CheckerConstants.attr,
  },

  'vars': {
    'error': 'Usage of `vars(obj)` is not allowed in plugin code ',
    'type': CheckerConstants.var,
  },

  'dir': {
    'error': 'Usage of `dir(obj)` is not allowed in plugin code ',
    'type': CheckerConstants.var,
  },

  'global_shmem': {
    'error': 'Usage of `global_shmem` is not allowed in plugin code ',
    'type': CheckerConstants.attr,
  },

  'plugins_shmem': {
    'error': 'Usage of `plugins_shmem` is not allowed in plugin code ',
    'type': CheckerConstants.attr,
  },

  'config_data': {
    'error': 'Usage of `config_data` is not allowed in plugin code ',
    'type': CheckerConstants.attr,
  },

  '_default_config': {
    'error': 'Usage of `_default_config` is not allowed in plugin code ',
    'type': CheckerConstants.attr,
  },

  '__traceback__': {
    'error': 'Usage of `__traceback__` as an attribute is not allowed in plugin code ',
    'type': CheckerConstants.attr,
  },

  '_upstream_config': {
    'error': 'Usage of `_upstream_config` is not allowed in plugin code ',
    'type': CheckerConstants.attr,
  },

  'exec': {
    'error': 'Usage of `exec()` is not allowed in plugin code ',
    'type': CheckerConstants.var,
  },

  'eval': {
    'error': 'Usage of `eval()` is not allowed in plugin code ',
    'type': CheckerConstants.var,
  },

  'getattr': {
    'error': 'Usage of `getattr()` is not allowed in plugin code ',
    'type': CheckerConstants.var,
  },

  'open': {
    'error': 'Usage of `open()` is not allowed in plugin code ',
    'type': CheckerConstants.var,
  }
}

RESULT_VARS = ['__result', '_result', 'result']


class CodeExecutionTimeoutError(Exception):
  pass


class BaseCodeChecker:
  """
  This class should be used either as a associated object for code checking or
  as a mixin for running code
  """

  def __init__(self):
    super(BaseCodeChecker, self).__init__()
    self.printed_lines = []
    self.__exec_code_lock = threading.Lock()
    return

  def __msg(self, m, color='d'):
    if hasattr(self, 'P'):
      self.P(m, color=color)
    elif hasattr(self, 'log'):
      self.log.P(m, color=color)
    else:
      print(m)
    return

  def _is_safe_import(self, code, safe_imports):
    if safe_imports is None:
      return False
    for imp in safe_imports:
      if imp in code:
        return True
    return False

  def _check_unsafe_code(self, code, safe_imports=None):
    checker = ASTChecker(UNALLOWED_DICT, safe_imports)
    errors = checker.validate(code)
    if len(errors) == 0:
      return None
    return errors

  # PUB

  def check_code_text(self, code, safe_imports=None):
    return self._check_unsafe_code(code, safe_imports=safe_imports)

  def str_to_base64(self, str, verbose=False, compress=False):
    l_i = len(str)
    l_c = -1
    b_str = bytes(str, 'utf-8')
    if compress:
      b_str = zlib.compress(b_str, level=9)
      l_c = sys.getsizeof(b_str)
    b_encoded = base64.b64encode(b_str)
    str_encoded = b_encoded.decode('utf-8')
    l_b64 = len(str_encoded)
    if verbose:
      self.__msg("Initial/Compress/B64: {}/{}/{}".format(
        l_i, l_c, l_b64), color='g'
      )
    return str_encoded

  def code_to_base64(self, code, verbose=False, compress=True, return_errors=False):
    if verbose:
      self.__msg("Processing:\n{}".format(code), color='y')
    errors = self._check_unsafe_code(code)
    if errors is not None:
      err_msg = "Cannot serialize code due to: '{}'".format(errors)
      self.__msg(err_msg, color='r')
      return None if not return_errors else (None, err_msg)
    self.__msg("Code checking succeeded", color='g')
    str_encoded = self.str_to_base64(code, verbose=verbose, compress=compress)
    return str_encoded if not return_errors else (str_encoded, None)

  def base64_to_code(self, b64code, decompress=True):
    decoded = None
    try:
      b_decoded = base64.b64decode(b64code)
      if decompress:
        b_decoded = zlib.decompress(b_decoded)
      s_decoded = b_decoded.decode('utf-8')
      decoded = s_decoded
    except:
      pass
    return decoded

  def prepare_b64code(self, str_b64code, check_for_result=True, result_vars=RESULT_VARS):
    errors, code = None, None
    code = self.base64_to_code(str_b64code)
    to_check_code = code
    if code is not None:
      if self._can_encapsulate_code_in_method(code):
        # we have a return statement in the code,
        # so we need to encapsulate the code in a function
        to_check_code = self._encapsulate_code_in_method(
          exec_code__code=code,
          exec_code__arguments=[]
        )
      # endif can encapsulate code in method
      errors = self._check_unsafe_code(to_check_code)
    if errors is None:
      if code is None:
        errors = 'Provided ascii data is not a valid base64 object'
      # endif no valid code provided
    # endif no errors
    return code, errors

  def _add_line_after_each_line(self, code, codeline='plugin.sleep(0.001)'):
    lines = code.splitlines()
    refactor = []
    has_loop = False
    for line in lines:
      rstripped = line.rstrip()
      stripped = line.lstrip()
      is_loop = stripped.startswith(('while', 'for'))
      has_loop = has_loop or is_loop
      if is_loop and rstripped[-1] != ':':
        parts = line.split(':')
        if len(parts) > 0:
          line = parts[0] + ': ' + codeline + ';' + parts[1]
          has_loop = False  # loop solved
      elif has_loop and not is_loop:
        nspc = len(line) - len(stripped)
        spc = nspc * ' '
        refactor.append(spc + codeline)
        has_loop = False  # loop solved
      # endif
      refactor.append(line)
    str_refactor = '\n'.join(refactor)
    return str_refactor

  def _can_encapsulate_code_in_method(self, exec_code__code):
    return re.search(r'\breturn\b', exec_code__code) is not None

  def _encapsulate_code_in_method(self, exec_code__code, exec_code__arguments):
    for i in range(len(exec_code__arguments)):
      __var = exec_code__arguments[i]
      if isinstance(__var, tuple):
        exec_code__arguments[i] = f"{__var[0]}={__var[1]}"
    exec_code__arguments = ', '.join(exec_code__arguments)

    if re.search(r'\breturn\b', exec_code__code) is not None:
      # we have a return statement in the code,
      # so we need to encapsulate the code in a function
      # 1. indent the code
      exec_code__code = "\n".join(['  ' + l for l in exec_code__code.splitlines()])
      # 2. add the function definition
      exec_code__code = "{}\n{}".format(
        f"def __exec_code__({exec_code__arguments}):",
        exec_code__code,
      )
    return exec_code__code

  def custom_print(self, print_queue, *args, **kwargs):
    """
    Custom print function that will be used in the plugin code.
    """
    # redirect the print to the plugin cache
    outstream = io.StringIO()
    print(*args, file=outstream, **kwargs)
    printed_value = outstream.getvalue()
    print_queue.put(printed_value)
    # print to the console
    print(f'[CUST_CODE_PRINT]{printed_value}')
    return

  def execute_code(self, code, local_vars, output_queue, print_queue):
    exec_code__result_var = None
    exec_code__warnings = []

    local_vars['print'] = lambda *args, **kwargs: self.custom_print(print_queue, *args, **kwargs)
    try:
      # Execute the code
      with self.__exec_code_lock:
        exec(code, local_vars)

        # Capture result variables
        for _var in local_vars.get('exec_code__result_vars', []):
          if _var in local_vars:
            exec_code__result_var = local_vars[_var]
            break
        # endfor all result vars
      # endwith lock
      # Put the results in the queue
      output_queue.put({
        "result_var": exec_code__result_var,
        "warnings": exec_code__warnings,
        "error": None
      })
    except Exception as e:
      output_queue.put({
        "result_var": None,
        "warnings": exec_code__warnings,
        "error": traceback.format_exc()
      })

  def __code_exec_stop_thread(self, thread):
    """
    Stop the specified thread.
    Parameters
    ----------
    thread : threading.Thread
        The thread to stop.
    """
    tid = thread.ident
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(SystemExit))
    if res == 0:
      raise ValueError("Invalid thread ID")
    elif res > 1:
      # If it modifies more than one thread, something went wrong, so revert it
      ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), 0)
      raise SystemError("PyThreadState_SetAsyncExc failed")

  def execute_code_with_timeout(self, code, timeout, local_vars=None):
    if local_vars is None:
      local_vars = {}

    # Queue to collect output
    output_queue = queue.Queue()
    print_queue = queue.Queue()

    # Create a separate thread for code execution
    thread = threading.Thread(target=self.execute_code, args=(code, local_vars, output_queue, print_queue))
    thread.daemon = True
    # process = multiprocessing.Process(target=self.execute_code, args=(code, local_vars, output_queue, print_queue))

    # Start the process
    # process.start()
    thread.start()

    # Wait for the process to complete or timeout
    # process.join(timeout)
    thread.join(timeout)

    # If process is still alive after timeout, terminate it
    if thread.is_alive():
      # process.terminate()
      # thread.join()
      # TODO: maybe still send partial results or prints?
      self.__code_exec_stop_thread(thread)

      return {
        "result_var": None,
        "warnings": [],
        "printed_lines": [],
        "error": f"Code execution took longer than {timeout} seconds."
      }
    # endif process is still alive

    printed_lines = []
    while not print_queue.empty():
      printed_lines.append(print_queue.get())
    # Get the output from the queue
    if not output_queue.empty():
      exec_result = output_queue.get()
      exec_result['printed_lines'] = printed_lines
      return exec_result

    return {
      "result_var": None,
      "warnings": [],
      "printed_lines": printed_lines,
      "error": "No result returned."
    }

  def exec_code(self, str_b64code, debug=False, result_vars=None, self_var=None, modify=True, return_printed=False, timeout=None):
    exec_code__result_vars = result_vars or RESULT_VARS
    exec_code__warnings = []
    exec_code__result_var = None

    # Prepare the code
    exec_code__code, exec_code__errors = self.prepare_b64code(str_b64code, result_vars=exec_code__result_vars)

    if exec_code__errors:
        self.__msg(f"Cannot execute remote code: {exec_code__errors}", color='r')
        return exec_code__result_var, exec_code__errors, exec_code__warnings

    # Optionally modify the code
    if modify:
        exec_code__code = self._add_line_after_each_line(code=exec_code__code)

    if debug:
        self.__msg(f"DEBUG EXEC: Executing:\n{exec_code__code}")

    # Add `self` to locals if specified
    local_vars = locals().copy()
    if self_var and isinstance(self_var, str) and len(self_var) > 3:
        local_vars[self_var] = self

    # Handle encapsulating the code in a method if needed
    if self._can_encapsulate_code_in_method(exec_code__code):
        exec_code__code = self._encapsulate_code_in_method(exec_code__code, exec_code__arguments=[self_var])
        exec_code__code = f"{exec_code__code}\nresult = __exec_code__({self_var})"

    # Prepare to capture printed output
    self.printed_lines = []
    local_vars['print'] = self.custom_print

    # Execute the code with a timeout
    exec_result = self.execute_code_with_timeout(exec_code__code, timeout, local_vars=local_vars)

    exec_code__result_var = exec_result.get("result_var")
    exec_code__errors = exec_result.get("error")
    exec_code__warnings.extend(exec_result.get("warnings"))

    # Collect results
    res = (exec_code__result_var, exec_code__errors, exec_code__warnings)

    if return_printed:
        res += (exec_result.get("printed_lines", []),)

    return res

  def _get_method_from_custom_code(self, str_b64code, debug=False, result_vars=RESULT_VARS, self_var=None, modify=True, method_arguments=[]):
    exec_code__result_vars = result_vars
    exec_code__debug = debug
    exec_code__self_var = self_var
    exec_code__modify = modify
    exec_code__warnings = []
    exec_code__code, exec_code__errors = self.prepare_b64code(
      str_b64code,
      result_vars=exec_code__result_vars,
    )
    exec_code__result_var = None
    has_result = False
    if exec_code__errors is not None:
      self.__msg("Cannot execute remote code: {}".format(exec_code__errors), color='r')
      return exec_code__result_var, exec_code__errors, exec_code__warnings

    # code does not have any safety errors
    if exec_code__modify:
      exec_code__code = self._add_line_after_each_line(code=exec_code__code)
    if exec_code__debug:
      self.__msg("DEBUG EXEC: Executing: \n{}".format(exec_code__code))
    if exec_code__self_var is not None and isinstance(exec_code__self_var, str) and len(exec_code__self_var) > 3:
      locals()[exec_code__self_var] = self

    try:
      if self._can_encapsulate_code_in_method(exec_code__code):
        # we have a return statement in the code,
        # so we need to encapsulate the code in a function
        exec_code__code = self._encapsulate_code_in_method(
          exec_code__code=exec_code__code,
          exec_code__arguments=method_arguments
        )
        exec_code__code = "{}\n{}".format(
          exec_code__code,
          f"result = __exec_code__"
        )
      else:
        # in this case we want to have our code in a method
        # so we will break here
        exec_code__errors = ["Cannot encapsulate code in method. No return statement found."]
        return exec_code__result_var, exec_code__errors, exec_code__warnings
      # endif can encapsulate code in method

      exec(exec_code__code)
      if exec_code__debug:
        self.__msg("DEBUG EXEC: locals(): \n{}".format(locals()))
      for _var in exec_code__result_vars:
        if _var in locals():
          if exec_code__debug:
            self.__msg("DEBUG EXEC: Extracting var '{}' from {}".format(_var, locals()))
          exec_code__result_var = locals().get(_var)
          has_result = True
          break
      if not has_result:
        exec_code__warnings.append("No result variable is set. Possible options: {}".format(exec_code__result_vars))
    except Exception as e:
      exec_code__result_var = None
      if hasattr(self, 'log'):
        exec_code__errors = list(self.log.get_error_info())
        exec_code__errors.append(traceback.format_exc())
      else:
        exec_code__errors = str(e)
    # end try-except
    return exec_code__result_var, exec_code__errors, exec_code__warnings

  def method_to_base64(self, func, verbose=False):
    code = self.get_function_source_code(func)
    return self.code_to_base64(code, verbose=verbose)

  def get_function_source_code(self, func):
    """
    Get the source code of a function and remove the indentation.

    Parameters
    ----------
    func : Callable
        The function.

    Returns
    -------
    str
        The source code of the function.
    """
    plain_code = inspect.getsourcelines(func)[0]
    plain_code = plain_code[1:]
    first_code_line = 0
    # ignore empty lines at the beginning, but keep them
    while plain_code[first_code_line].strip() == '':
      first_code_line += 1
    indent = len(plain_code[first_code_line]) - len(plain_code[first_code_line].lstrip())
    plain_code = '\n'.join([line.rstrip()[indent:] for line in plain_code])

    return plain_code
