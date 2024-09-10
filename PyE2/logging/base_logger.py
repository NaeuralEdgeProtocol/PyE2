import os
import sys
import json
import shutil
import codecs
import textwrap
import numpy as np
import traceback
import socket
import threading
import re

from time import time as tm
from time import strftime, localtime, strptime, mktime
from collections import OrderedDict
from datetime import datetime as dt
from datetime import timedelta, timezone, tzinfo
from dateutil import tz
from pathlib import Path

from .tzlocal import get_localzone_name



from .._ver import __VER__

_HTML_START = "<HEAD><meta http-equiv='refresh' content='5' ></HEAD><BODY><pre>"
_HTML_END = "</pre></BODY>"

COLORS = {
  'n': "\x1b[1;37m", # normal white
  'd': "\x1b[0;37m", # grey white
  'r': "\x1b[1;31m",
  'g': "\x1b[1;32m",
  'y': "\x1b[1;33m",
  'b': "\x1b[1;34m",
  'm': "\x1b[1;35m",
  'a': "\x1b[41m",
  'e': "\x1b[41m",
  'w': "\x1b[1;31m", # warning == red

  '__end__': "\x1b[0m",
}

_LOGGER_LOCK_ID = '_logger_print_lock' 

class BaseLogger(object):

  def __init__(self, lib_name="",
              lib_ver="",
              config_file="",
              config_data={},
              base_folder=None,
              app_folder=None,
              show_time=True,
              config_file_encoding=None,
              no_folders_no_save=False,
              max_lines=None,
              HTML=False,
              DEBUG=True,
              data_config_subfolder=None,
              check_additional_configs=False,
              append_spaces=True,
              default_color='n',
              ):

    super(BaseLogger, self).__init__()
    if os.name == 'nt':
      os.system('color')
    self.__lib__ = lib_name
    self.append_spaces = append_spaces
    self.show_time = show_time
    self.no_folders_no_save = no_folders_no_save
    self.max_lines = max_lines
    self.HTML = HTML
    self.DEBUG = DEBUG
    self.log_suffix = lib_name
    self.default_color = default_color
    self.__first_print = False
    
    self._lock_table = OrderedDict({
      _LOGGER_LOCK_ID: threading.Lock(),
      })
    
    self._lock_table_mutex = threading.Lock()

    self._base_folder = base_folder
    self._app_folder = app_folder
    self._normalize_path_sep()

    self.check_additional_configs = check_additional_configs
    self.data_config_subfolder = data_config_subfolder

    self.__version__ = __VER__
    self.version = self.__version__
    self.file_prefix = None
    self.refresh_file_prefix()

    self.last_time = tm()
    self.start_timestamp = tm()
    self.utc_offset = self.get_utc_offset()
    
    try:
      self.timezone = get_localzone_name()
    except Exception as exc:
      self.timezone = str(exc)
      
    self.app_log = list()
    self.err_log = list()
    self.split_part = 1
    self.split_err_part = 1
    self.config_data = None
    self.__init_config_data = config_data if config_data is not None else {}
    self.MACHINE_NAME = None
    self.COMPUTER_NAME = None
    self.processor_platform = None
    self.python_version = sys.version.split(' ')[0]
    self.python_major = int(self.python_version.split('.')[0])
    self.python_minor = int(self.python_version.split('.')[1])
    if self.python_major < 3:
      msg = "ERROR: Python 2 or lower detected. Run will fail!"
      print(msg)
      raise ValueError(msg)
      
    _ = self.get_machine_name()
    
    
    # START: bundling -- se also properties
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        print('  Running in a PyInstaller bundle')
        self.__is_bundled = True
        self.__bundle_path = sys._MEIPASS
    else:
        print('  Running in a normal Python process')
        self.__is_bundled = False
        self.__bundle_path = None
    # END: bundling -- se also properties
    
    self.analyze_processor_platform()
    
    self._save_enabled = False
    if not self.no_folders_no_save:
      try:
        self._configure_data_and_dirs(config_file, config_file_encoding)        
        self._save_enabled = True
      except:
        self.P("Failed to configure data and dirs. No log persistance possible.\n{}".format(
          traceback.format_exc()
          ), color='r'
        )
        self.no_folders_no_save = True
      #endtry config data and dirs
    #endif 
    
    self._generate_log_path()
    self._generate_error_log_path()
    self._check_additional_configs()
    
    self.git_branch = self.get_active_git_branch()
    self.conda_env = self.get_conda_env()

    if lib_ver == "":
      lib_ver = __VER__
    ver = "v{}".format(lib_ver) if lib_ver != "" else ""
    self.verbose_log(
      "PyE2 [{} {}] initialized on machine [{}][{}].".format(
        self.__lib__, ver, self.MACHINE_NAME, self.get_processor_platform(),
      ),
      color='green'
    )
    self.verbose_log("  Timezone: {}.".format(self.timezone),color='green')


    if self.DEBUG:
      self.P('  DEBUG is enabled in Logger', color='g')
    else:
      self.P('  WARNING: Debug is NOT enabled in Logger, some functionalities are DISABLED', color='y')

    return
  
  def get_unique_id(self, size=8):
    """
    efficient and low-colision function for small unique id generation
    """
    import string
    import random
    alphabet = string.ascii_lowercase + string.digits
    uid = ''.join(random.choices(alphabet, k=size))
    return uid
  
  @property
  def is_bundled(self):
    return self.__is_bundled
  
  @property
  def bundle_path(self):
    return self.__bundle_path
    
  
  def is_running(self, verbose=True):
    return self.same_script_already_running(verbose=verbose)
  
  @staticmethod
  def version_to_int(version):
    comps = version.split('.')
    val = 0
    power = 3
    for i, comp in enumerate(comps):
      v = int(comp)
      v = v * 100**power
      power -= 1
      val += v
    return val
    
  @staticmethod
  def get_packages(as_text=False, indent=0, as_dict=False, mandatory={}):
    """
    Will return the currently installed (and visible) packages

    Parameters
    ----------
    as_text : bool, optional
      If true return as text. The default is False.
      
    indent : int, optional
      If return text then return it with indent. The default is 0.
      
    mandatory : dict, optional
      Will raise error if any packages from the dict of key:ver are missing. The default is {}.
      
    as_dict: bool, optional
      Return as package_name:ver dict the result. Default False

    Returns
    -------
    packs : list/str/dict
      the list of packages as list of str, a full text to show or a dict of name:ver.

    """
    import pkg_resources
    def ver_to_int(version, package=None):
      comps = version.split('.')
      val = 0
      power = 3
      try:
        for i, comp in enumerate(comps):
          v = int(comp)
          v = v * 100**power
          power -= 1
          val += v
      except:
        BaseLogger.print_color("Failed to convert version '{}' to int for package `{}`, version so far: {}".format(version, package, val), color='r')
      return val    
    
    raw_packs = [x for x in pkg_resources.working_set]
    maxlen = max([len(x.key) for x in raw_packs]) + 1
    lst_pack_ver = [(x.key, x.version) for x in raw_packs]
    lst_pack_ver = sorted(lst_pack_ver, key=lambda x:x[0])
    dct_packs = OrderedDict(lst_pack_ver)
    
    if len(mandatory) > 0:      
      for mandatory_pack in mandatory:
        if mandatory_pack not in dct_packs:
          msg = "Mandatory package `{}:{}` is missing. Please check your deployment!".format(
            mandatory_pack, mandatory[mandatory_pack])
          BaseLogger.print_color(msg, color='r')          
          raise ValueError(msg)
        mandatory_ver = ver_to_int(mandatory[mandatory_pack])
        package_ver = ver_to_int(dct_packs[mandatory_pack], package=mandatory_pack)
        if  mandatory_ver > package_ver:
          msg = "Mandatory installed package `{}:{}` ({}) below required version `{}` ({}). Please check your deployment!".format(
            mandatory_pack, dct_packs[mandatory_pack], package_ver, mandatory[mandatory_pack], mandatory_ver)
          BaseLogger.print_color(msg, color='r')
          raise ValueError(msg)        
    #endif check for packages and versions
    
    if as_dict:
      result = dct_packs
    else:
      result = []
      for x in lst_pack_ver:
        result.append("{}{}".format(x[0] + ' ' * (maxlen - len(x[0])), x[1] + ' ' * (14 - len(x[1]))))
        if x[0] in mandatory:
          result[-1] = result[-1] + ' ==> OK ({} > {})'.format(x[1], mandatory[x[0]])
      if as_text:
        fmt = "\n{}".format(' ' * indent)
        result = ' ' * indent + fmt.join(result)
    return result  
    
  
  def same_script_already_running(self, verbose=True):
    import psutil
    CMD = 'python'
    script_file = sys.argv[0]
    if script_file == '':
      self.P("Cannot get script file name", color='r')
      return False
    for q in psutil.process_iter():
      if q.name().startswith(CMD):
        if (
            len(q.cmdline())>1 and 
            script_file in q.cmdline()[1] and 
            q.pid != os.getpid()
            ):
          if verbose:
            self.P("Python '{}' process is already running".format(script_file), color='m')
          return True
    return False
  
  @staticmethod
  def replace_secrets(dct_config, pattern='$EE_'):
    matches = []
    missing = []
    stack = [dct_config]
  
    while stack:
      current = stack.pop()
      if isinstance(current, dict):
        for key, value in current.items():
          if isinstance(value, str) and value.startswith(pattern):
            matches.append(value)
            env_var_name = value[1:] 
            if env_var_name not in os.environ:
              missing.append(env_var_name)
            else:
              current[key] = os.environ[env_var_name]
          elif isinstance(value, (dict, list)):
            stack.append(value)
      elif isinstance(current, list):
        for item in current:
          if isinstance(item, (dict, list)):
            stack.append(item)
    if len(missing) > 0:
      raise ValueError('Required environment configuration for keys {} was not found in current envirnoment. Please setup your docker or bare-metal config to provide this missing key(s)'.format(
        ",".join(['"' + x + '"' for x in missing])
      ))
    return matches  
  
  
  
  def lock_process(self, str_lock_name, nt_file_lock=False):
    if os.name == 'nt':
      # windows
      if nt_file_lock:
        # naive lock ...
        self.P("Attempting to create file lock '{}'".format(str_lock_name), color='m')
        fn = str_lock_name + '.lock'
        if os.path.isfile(fn):
          self.P("Another Windows process has already acquired file lock '{}'".format(str_lock_name), color='r')
          return None
        else:
          str_stamp = self.time_to_str()
          with open(fn, "wt") as fh:
            fh.write("LOCKED AT {}".format(str_stamp))
          self.P("Current Windows process has acquired file lock '{}'".format(fn))
          return fn
      else:
        # nice lock but not always working (if not superuser...)
        from win32event import CreateMutex
        from win32api import GetLastError
        from winerror import ERROR_ALREADY_EXISTS
        str_lock_name = "Global\\" + str_lock_name.replace("\\","")
        self.P("Attempting to create lock on current Windows process for id '{}'".format(str_lock_name), color='m')
        
        try:
          mutex_handle = CreateMutex(None, 1, str_lock_name)
          err = GetLastError()
        except:
          self.P("Exception in process locking id '{}'".format(str_lock_name), color='r')
          err = ERROR_ALREADY_EXISTS
          
        if err == ERROR_ALREADY_EXISTS:
          # maybe show some text
          self.P("Another Windows process has already acquired id '{}'".format(str_lock_name), color='r')
          return None
        else:
          # maybe show some text
          self.P("Current Windows process has acquired id '{}':{} ({})".format(
            str_lock_name, mutex_handle, err), color='g')
          return mutex_handle    
    else:
      import platform
      str_platform = platform.system()
      if str_platform.lower() == 'darwin':
        # macos
        self.P("Running on MacOS. Skipping mutex and checking if script is running", color='m')
        if self.same_script_already_running():
          return None        
        return -1
      else:         
        import socket
        self.P("Attempting to create lock on current Linux process for id '{}'".format(str_lock_name), color='m')
        _lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
          _lock_socket.bind('\0' + str_lock_name)
          # maybe show some text
          self.P("Current Linux process has acquired id '{}': {}".format(
            str_lock_name, _lock_socket), color='g')
          return _lock_socket
        except Exception as err:
          # maybe show some text
          self.P("Another Linux process has already acquired id '{}'. Error: {}".format(
            str_lock_name, err), color='r')
          return None
      # end if platform
    # end if not windows
    return
  
  def maybe_unlock_windows_file_lock(self, str_lock_name):
    if os.name == 'nt' and str_lock_name is not None and isinstance(str_lock_name, str):
      self.P("Attempting to unlock windows lock file...")
      if os.path.isfile(str_lock_name):
        os.remove(str_lock_name)
        self.P("Released windows file lock {}".format(str_lock_name))
      else:
        self.P("Unknown file lock '{}'".format(str_lock_name))
    return
  
  def analyze_processor_platform(self):
    import platform
    import subprocess
    import re
    str_system = platform.system()
    if str_system == "Windows":
      self.processor_platform = platform.processor()
    elif str_system == "Darwin":
      os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
      command ="sysctl -n machdep.cpu.brand_string"
      self.processor_platform = subprocess.check_output(command, shell=True).strip().decode('utf-8')
    elif str_system == "Linux":
      command = "cat /proc/cpuinfo"
      all_info = subprocess.check_output(command, shell=True).decode().strip()
      for line in all_info.split("\n"):
        if "model name" in line:
          self.processor_platform = re.sub( ".*model name.*:", "", line,1)    
          break
    return
  
  def get_processor_platform(self):
    return self.processor_platform
    
  
  def lock_resource(self, str_res):
    """
    Possible critical failure:
    
    1. base plugin runs try stuff etc
    2. plugin runs lock
    3. threading.Lock() fails
    4. base plugin runs except
    5. except locks in log (no output) due to _lock_table_mutex.acquire(blocking=True)
    6. any thread running lock_reource will hang with NO LOG OUTPUT
    """
    result = None
    self._lock_table_mutex.acquire(blocking=True)
    try:
      if str_res not in self._lock_table:      
        self._lock_table[str_res] = threading.Lock()
    except:
      print("**************************************************************\nPANIC: Failed to create lock for resource '{}'\n**************************************************************".format(str_res))
    finally:
      self._lock_table_mutex.release()

    if str_res in self._lock_table:      
      self._lock_table[str_res].acquire(blocking=True)
      result = self._lock_table[str_res]
      
    return result
  
  def unlock_resource(self, str_res):
    if str_res in self._lock_table:
      self._lock_table[str_res].release()
    return
  
  def lock_logger(self):
    self.lock_resource(_LOGGER_LOCK_ID)
    return
  
  def unlock_logger(self):
    self.unlock_resource(_LOGGER_LOCK_ID)
    
  def get_file_path(self, fn, folder, subfolder_path=None, force=False):
    lfld = self.get_target_folder(target=folder)
    if lfld is None:
      datafile = fn
    else:
      datafolder = lfld
    if subfolder_path is not None:
      datafolder = os.path.join(datafolder, subfolder_path.lstrip('/'))
    datafile = os.path.join(datafolder, fn)
    if os.path.isfile(datafile) or force:
      return datafile
    return 
    

  @property
  def session_id(self):
    return self.file_prefix
  
  
  def cleanup_timestamped_files(self, folder, keep=5):
    if os.path.isdir(folder):
      files = [x for x in os.listdir(folder) if len(x) > 6 and x[:6].isnumeric()]
      if len(files) > keep:
        files = sorted(files)
        n_delete = len(files) - keep
        to_delete = files[:n_delete]
        self.P("Cleaning {} timestamped files between {} and {}, preserving {} in '{}'...".format(
          n_delete, to_delete[0], to_delete[-1], keep, folder), color='y'
        )
        for fn in to_delete:
          os.remove(os.path.join(folder, fn))
          print(".", flush=True, end='')
        print("Done.\r", flush=True, end='')
      #endif delete extra files
    #endif folder valir
    return


  def maybe_cleanup_timestamped_files(self, folder, keep=4):
    return self.cleanup_timestamped_files(folder=folder, keep=keep)
  
  
  def cleanup_logs(self, archive_older_than_days=2, MAX_ARCHIVE_SIZE=5*1024**2):
    if self.no_folders_no_save:
      return
    self.P("Cleaning logs older than {} days...".format(archive_older_than_days), color='y')
    str_old_date = (dt.today() - timedelta(days=archive_older_than_days)).strftime('%Y%m%d')
    int_old_date = int(str_old_date)
    logs = os.listdir(self._logs_dir)
    archive_list = []
    show_list = []
    base_fn = "_logs_archive"
    zip_fn = os.path.join(self._logs_dir, base_fn + '.zip')
    if os.path.isfile(zip_fn):
      stats = os.stat(zip_fn)
      if stats.st_size > MAX_ARCHIVE_SIZE:
        self.P("  Current archive larger than {:.1f} MB. Renaming and marking for manual deletion".format(
          MAX_ARCHIVE_SIZE / 1024**2), color='y'
        )
        new_fn = os.path.join(self._logs_dir, base_fn + '_' + self.file_prefix.split('_')[0] + '.zip')
        if os.path.isfile(new_fn):
          self.P("  Something is strange, file already exists. Deleting...")
          try:
            os.unlink(new_fn)
          except:
            self.P("    Failed to remove {}:\n{}".format(new_fn, traceback.format_exc()), color='r')
        try:
          os.rename(zip_fn, new_fn)
        except:
          self.P("  Archiving logs file failed:\n{}".format(
            traceback.format_exc()
          ), color='r')
      #endif file to large
    #endif already exists
    for fn in logs:
      if fn[-4:] == '.txt':
        str_date = fn[:8]
        int_date = None
        if len(str_date) == 8:
          try:
            int_date = int(str_date)
          except:
            pass
        if int_date is not None and int_date < int_old_date:
          full_fn = os.path.join(self._logs_dir, fn)
          archive_list.append(full_fn)
          show_list.append(fn)
        
    if len(archive_list) > 0:
      self.P("  Archiving {} logs...".format(len(archive_list)), color='y')
      self.add_files_to_zip(zip_fn, archive_list)
      for full_fn in archive_list:
        os.remove(full_fn)
    else:
      self.P("  Nothing to clean.")
    return
                    


  def _logger(self, logstr, show=True, noprefix=False, show_time=False, color=None):
    """
    log processing method
    """
    self.lock_logger()
    # now that we have locking in place we no longer need to cancel in-thread logging    
    # if not self.is_main_thread:
    #   return
    self.start_timer('_logger', section='LOGGER_internal')

    elapsed = tm() - self.last_time

    self.start_timer('_logger_add_log', section='LOGGER_internal')
    self._add_log(
      logstr, show=show,
      noprefix=noprefix,
      show_time=show_time,
      color=color
    )
    self.end_timer('_logger_add_log', section='LOGGER_internal')

    self.start_timer('_logger_save_log', section='LOGGER_internal')
    if self._save_enabled:
      self._save_log(
        log=self.app_log,
        log_file=self.log_file
      )
      self._save_log(
        log=self.err_log,
        log_file=self.log_e_file
      )
    self.end_timer('_logger_save_log', section='LOGGER_internal')
    
    self.last_time = tm()
    self._check_log_size()

    self.end_timer('_logger', section='LOGGER_internal')    
    self.unlock_logger()
    return elapsed

  def _normalize_path_sep(self):
    if self._base_folder is not None:
      if os.path.sep == '\\':
        self._base_folder = self._base_folder.replace('/', '\\')
      else:
        self._base_folder = self._base_folder.replace('\\', '/')
      #endif
    #endif

    if self._app_folder is not None:
      if os.path.sep == '\\':
        self._app_folder = self._app_folder.replace('/', '\\')
      else:
        self._app_folder = self._app_folder.replace('\\', '/')
      #endif
    #endif

    return

  def print_on_columns(self, *objects, nr_print_columns=4, nr_print_chars=12, header=None, color=None):
    if header:
      self.P(header, color=color)

    print_columns = [[] for _ in range(nr_print_columns)]

    crt_column = 0
    _fmt = "{:>" + str(nr_print_chars) + "}"

    nr_labels_per_column = int(np.ceil(len(objects) / nr_print_columns))
    for i, obj in enumerate(objects):
      if i // nr_labels_per_column != crt_column:
        crt_column += 1

      print_columns[crt_column].append(_fmt.format(obj[:nr_print_chars]))
    # endfor

    for i in range(nr_labels_per_column):
      str_line = ''
      for j in range(nr_print_columns):
        if i >= len(print_columns[j]):
          continue

        str_line += print_columns[j][i] + '    '

      self.P(str_line, noprefix=True, color=color)
    # endfor
    return

  def _add_log(self, logstr, show=True, noprefix=False, show_time=False, color=None):
    if type(logstr) != str:
      logstr = str(logstr)
    if logstr == "":
      logstr = " "
    if 'WARNING' in logstr and color is None:
      color = 'warning'
    if 'ERROR' in logstr and color is None:
      color = 'error'
    elapsed = tm() - self.last_time
    nowtime = dt.now()
    prefix = ""
    strnowtime = nowtime.strftime("[{}][%y-%m-%d %H:%M:%S]".format(self.__lib__))
    if self.show_time and (not noprefix):
      prefix = strnowtime
    if logstr[0] == "\n":
      logstr = logstr[1:]
      prefix = "\n" + prefix
    res_log = logstr
    if len(logstr) == 0 or logstr[0] != '[':
      prefix = prefix + ' '
    logstr = prefix + logstr
    if show_time:
      logstr += " [{:.2f}s]".format(elapsed)
    print_logstr = logstr
    if show:
      if self.append_spaces:
        spaces = " " * max(60 - len(print_logstr), 0)
      else:
        spaces = ''
      print_logstr = print_logstr + spaces
      if color is None:
        color = self.default_color
        if not self.__first_print:
          BaseLogger.print_color("<Logging with default color: {}>".format(color), color=color)
          self.__first_print = True
      #endif use default color
      BaseLogger.print_color(print_logstr, color=color)
    if color.lower()[0] in ['e', 'r']:
      self.err_log.append(logstr)
    self.app_log.append(logstr)
      
    #endif
    return

  def _save_log(self, log, log_file, DEBUG_ERRORS=False):  
    """ Generic method that saves logs to a specific file

    Args:
        log (list): The log list to save
        log_file (str): The path to the desired file in which to save the log.
        DEBUG_ERRORS (bool, optional): Print exceptions regarding opening the file and writing to it. Defaults to False.
    """
    if self.no_folders_no_save or self._save_enabled is False:
      return

    nowtime = dt.now()
    strnowtime = nowtime.strftime("[{}][%Y-%m-%d %H:%M:%S] ".format(self.__lib__))
    stage = 0
    try:
      log_output = codecs.open(log_file, "w", "utf-8")  # open(self.log_file, 'w+')
      stage += 1
      if self.HTML:
        log_output.write(_HTML_START)
        stage += 1
        iter_list = reversed(log)
      else:
        iter_list = log
      for log_item in iter_list:
        # if self.HTML:
        #  log_output.write("%s<BR>\n" % log_item)
        # else:
        log_output.write("{}\n".format(log_item))
        stage += 1
      if self.HTML:
        log_output.write(_HTML_END)
        stage += 1
      log_output.close()
      stage += 1
    except:
      if DEBUG_ERRORS:
        print(strnowtime + "LogWErr S: {} [{}]".format(stage,
                                                       sys.exc_info()[0]), flush=True)
    return

  def _check_log_size(self):
    if self.max_lines is None:
      return

    if len(self.app_log) >= self.max_lines:
      self._add_log("Ending log part {}".format(self.split_part))
      self._save_log(
        log=self.app_log,
        log_file=self.log_file
      )
      self.app_log = []
      self.split_part += 1
      self._generate_log_path()
      self._add_log("Starting log part {}".format(self.split_part))
      self._save_log(
        log=self.app_log,
        log_file=self.log_file
      )    
    if len(self.err_log) >= self.max_lines:
      self._add_log("Ending error log part {}".format(self.split_err_part))
      self._save_log(
        log=self.err_log,
        log_file=self.log_e_file
      )
      self.err_log = []
      self.split_err_part += 1
      self._generate_error_log_path()
      self._add_log("Starting error log part {}".format(self.split_err_part))
      self._save_log(
        log=self.err_log,
        log_file=self.log_e_file
      )
      return

  def verbose_log(self, str_msg, show_time=False, noprefix=False, color=None):
    return self._logger(
      str_msg,
      show=True,
      show_time=show_time,
      noprefix=noprefix, color=color
    )

  def P(self, str_msg, show_time=False, noprefix=False, color=None, boxed=False, **kwargs):
    return self.p(str_msg, show_time=show_time, noprefix=noprefix, color=color, boxed=boxed, **kwargs)

  def D(self, str_msg, show_time=False, noprefix=False, color=None, **kwargs):
    if False:
      return self.P(str_msg, show_time=show_time, noprefix=noprefix, color=color, **kwargs)

  @staticmethod
  def Pr(str_msg, show_time=False, noprefix=False):
    if type(str_msg) != str:
      str_msg = str(str_msg)
    print("\r" + str_msg, flush=True, end='')

  def __convert_to_box(self, str_msg, box_char='#', indent=None, **kwargs):
    lst_msg_lines = str_msg.split('\n')
    max_line_len = max(map(len, lst_msg_lines))

    center = 4 if max_line_len > 80 else 10
    box_line_len = center + 1 + max_line_len + 1 + center
    default_indent = 4 if box_line_len > 100 else 20
    indent = indent if indent is not None else default_indent
    str_indent = ' ' * indent

    msg = box_char * 3 + 'IMPORTANT' + box_char * 3 + '\n\n'
    msg += str_indent + box_char * box_line_len + '\n'
    msg += str_indent + box_char + (box_line_len - 2) * ' ' + box_char + '\n'

    for line in lst_msg_lines:
      left_box_edge = str_indent + box_char
      right_box_edge = box_char

      left_shift = ' ' * center
      right_shift = ' ' * (center + max_line_len - len(line)) # adjust for different line lengths
      shifted_line = left_shift + line + right_shift
      msg += left_box_edge + shifted_line + right_box_edge + '\n'
    # end for

    msg += str_indent + box_char + (box_line_len - 2) * ' ' + box_char + '\n'
    msg += str_indent + box_char * box_line_len + '\n'

    return msg

  def p(self, str_msg, show_time=False, noprefix=False, color=None, boxed=False, **kwargs):
    if boxed:
      msg = self.__convert_to_box(str_msg, **kwargs)
      self._logger(msg, show=True, noprefix=noprefix, color=color)
    else:
      return self._logger(
        str_msg,
        show=True,
        show_time=show_time,
        noprefix=noprefix, color=color
      )

  def Pmd(self, s=''):
    print_func = None
    try:
      from IPython.display import Markdown, display
      def print_func(s):
        display(Markdown(s))
    except:
      pass
    if type(s) != str:
      s = str(s)

    if print_func is not None:
      self._add_log(
        logstr=s,
        show=False,
        noprefix=False,
        show_time=False,
      )
      print_func(s)
    else:
      self.P(s)
    return

  def Pmdc(self, s=''):
    print_func = None
    try:
      from IPython.display import Markdown, display
      def print_func(s):
        display(Markdown(s))
    except:
      pass
    if type(s) != str:
      s = str(s)

    if print_func is not None:
      self._add_log(
        logstr=s,
        show=False,
        noprefix=False,
        show_time=False,
      )
      print_func('<strong>' + s + '</strong>')
    else:
      self.P(s)
    return

  def print_pad(self, str_msg, str_text, n=3):
    if type(str_msg) != str:
      str_msg = str(str_msg)
    if type(str_text) != str:
      str_text = str(str_text)
    str_final = str_msg + "\n" + textwrap.indent(str_text, n * " ")
    self._logger(str_final, show=True, show_time=False)
    return

  def log(self, str_msg, show=False, show_time=False, color=None):
    return self._logger(str_msg, show=show, show_time=show_time, color=color)

  def _generate_log_path(self):
    if self.no_folders_no_save:
      return
    part = '{:03d}'.format(self.split_part)
    lp = self.file_prefix
    ls = self.log_suffix
    if self.HTML:
      self.log_file = lp + '_' + ls + '_' + part + '_log_web.html'
    else:
      self.log_file = lp + '_' + ls + '_' + part + '_log.txt'
      
    self.log_file = os.path.join(self._logs_dir, self.log_file)
    path_dict = {}
    path_dict['CURRENT_LOG'] = self.log_file
    file_path = os.path.join(self._logs_dir, self.__lib__ + '.txt')
    with open(file_path, 'w') as fp:
      json.dump(path_dict, fp, sort_keys=True, indent=4)
    self._add_log("{} log changed to {}...".format(file_path, self.log_file))
    return

  def _generate_error_log_path(self):
    if self.no_folders_no_save:
      return
    part = '{:03d}'.format(self.split_err_part)
    lp = self.file_prefix
    ls = self.log_suffix
    if self.HTML:
      self.log_e_file = lp + '_' + ls + '_' + part + '_error_log_web.html'
    else:
      self.log_e_file = lp + '_' + ls + '_' + part + '_error_log.txt'
      
    self.log_e_file = os.path.join(self._logs_dir, self.log_e_file)
    path_dict = {}
    path_dict['CURRENT_E_LOG'] = self.log_e_file
    file_path = os.path.join(self._logs_dir, self.__lib__ + '.txt')
    with open(file_path, 'w') as fp:
      json.dump(path_dict, fp, sort_keys=True, indent=4)
    self._add_log("{} error log changed to {}...".format(file_path, self.log_e_file))
    return

  def _get_cloud_base_folder(self, base_folder):
    upper = base_folder.upper()
    google = "GOOGLE" in upper
    dropbox = "DROPBOX" in upper

    if google and not "/DATA/" in upper:
      base_folder = self.get_google_drive()
    if dropbox and not "/DATA/" in upper:
      base_folder = self.get_dropbox_drive()
    return base_folder

  def _configure_data_and_dirs(self, config_file, config_file_encoding=None):
    if self.no_folders_no_save:
      return

    if config_file != "":
      if config_file_encoding is None:
        f = open(config_file)
      else:
        f = open(config_file, encoding=config_file_encoding)
      
      try:
        self.config_data = json.load(f, object_pairs_hook=OrderedDict)
      except:
        msg = "Failed to load config file '{}'".format(config_file)
        self.P(msg, color='r', boxed=True)
        self.P("Exception details:\n{}".format(traceback.format_exc()), color='r')
        self.config_data = {}

      if self._base_folder is None and self._app_folder is None:
        assert ("BASE_FOLDER" in self.config_data.keys())
        assert ("APP_FOLDER" in self.config_data.keys())
        self._base_folder = self.config_data["BASE_FOLDER"]
        self._app_folder = self.config_data["APP_FOLDER"]
      #endif no defaults for base/app folders

      print("Loaded config [{}]".format(config_file), flush=True)
      self.config_file = config_file
    else:
      self.config_data = {
        'BASE_FOLDER' : self._base_folder,
        'APP_FOLDER' : self._app_folder
      }
      self.config_file = "default_config.txt"
    #endif have or not config file
    
    self.config_data = {
      **self.config_data,
      **self.__init_config_data,
    }
    
    matches = self.replace_secrets(self.config_data)
    print("  Config modified with following env vars: {}".format(matches))

    self._base_folder = self.expand_tilda(self._base_folder)
    self._base_folder = self._get_cloud_base_folder(self._base_folder)
    self._root_folder = os.path.abspath(self._base_folder)
    self._base_folder = os.path.join(self._base_folder, self._app_folder)
    print("BASE: {}".format(self._base_folder), flush=True)

    self._normalize_path_sep()

    if not os.path.isdir(self._base_folder):
      print("{color_start}WARNING! Invalid app base folder '{base_folder}'! We create it automatically!{color_end}".format(
        color_start=COLORS['r'],
        base_folder=self._base_folder,
        color_end=COLORS['__end__']
      ), flush=True)
    #endif

    self._logs_dir = os.path.join(self._base_folder, self.get_logs_dir_name())
    self._outp_dir = os.path.join(self._base_folder, self.get_output_dir_name())
    self._data_dir = os.path.join(self._base_folder, self.get_data_dir_name())
    self._modl_dir = os.path.join(self._base_folder, self.get_models_dir_name())

    self._setup_folders([
      self._outp_dir,
      self._logs_dir,
      self._data_dir,
      self._modl_dir
    ])

    return

  @staticmethod
  def get_logs_dir_name():
    return '_logs'

  @staticmethod
  def get_output_dir_name():
    return '_output'

  @staticmethod
  def get_data_dir_name():
    return '_data'

  @staticmethod
  def get_models_dir_name():
    return '_models'
  
  
  @staticmethod
  def get_all_files_in_folder(root_folder=None):
    """
    Walks through all directories and sub-directories of the given root_folder and returns a list of all file paths.

    Parameters
    ----------
    root_folder : str
      The path of the folder you want to walk through. Default `None` will generate 
      all files in current folder

    Returns
    -------
    List[str]
      A list containing the paths of all files in the folder and its subfolders.
    """
    
    if root_folder is None:
      root_folder = os.getcwd()
    
    file_paths = []
    
    for dirpath, dirnames, filenames in os.walk(root_folder):
      for filename in filenames:
        full_path = os.path.join(dirpath, filename)
        file_paths.append(full_path)
    
    return file_paths

  @staticmethod
  def get_all_subfolders(root_folder=None, as_package=False):
    """
    Walks through all directories and sub-directories of the given root_folder and returns a list of all subfolder paths.

    Parameters
    ----------
    root_folder : str
      The path of the folder you want to walk through. Default `None` will generate 
      all subfolders in current folder

    Returns
    -------
    List[str]
      A list containing the paths of all files in the folder and its subfolders.
    """
    
    if root_folder is None:
      root_folder = os.getcwd()
    
    folder_paths = []
    
    for dirpath, dirnames, filenames in os.walk(root_folder):
      for dirname in dirnames:
        full_path = os.path.join(dirpath, dirname)
        if as_package:
          full_path = full_path.replace('/', '.').replace('\\', '.')
        folder_paths.append(full_path)
    
    return folder_paths
  
  
  
  def get_code_base_folder(self):
    if getattr(sys, 'frozen', False):
      # Running in a bundled exe
      folder = sys._MEIPASS
    else:
      # Running in a normal Python environment
      folder = self.root_folder
    return folder  
  
  @property
  def code_base_folder(self):
    return self.get_code_base_folder()

  def _setup_folders(self, folder_list):
    self.folder_list = folder_list
    for folder in folder_list:
      if not os.path.isdir(folder):
        print("Creating folder [{}]".format(folder))
        os.makedirs(folder)
    return

  def update_config(self, dict_newdata=None):
    """
     saves config file with current config_data dictionary
    """
    if dict_newdata is not None:
      for key in dict_newdata:
        self.config_data[key] = dict_newdata[key]
    with open(self.config_file, 'w') as fp:
      json.dump(self.config_data, fp, indent=4)
    self.P("Config file '{}' has been updated.".format(self.config_file))
    return
  
  
  def update_config_values(self, dct_newdata):
    self.P("Selective update of config file '{}' on {}".format(self.config_file, list(dct_newdata.keys())))
    with open(self.config_file, 'r') as fp:
      dct_cache_config = json.load(fp, object_pairs_hook=OrderedDict)
    for k,v in dct_newdata.items():
      old_value = dct_cache_config[k]
      dct_cache_config[k] = v
      self.P("  Modified '{}'='{}' => '{}'='{}'".format(k, old_value, k, v))
    with open(self.config_file, 'w') as fp:
      json.dump(dct_cache_config, fp, indent=4)
    self.P("Config file '{}' has been updated.".format(self.config_file))
    return


  def _check_additional_configs(self):
    additional_configs = []
    
    if not self.check_additional_configs:
      return 

    check_dir = self.get_data_folder()
    if self.data_folder_additional_configs is not None:
      check_dir = self.get_data_subfolder(self.data_folder_additional_configs)
      if check_dir is None:
        self.P("Additional configs folder '{}' not found in '{}'"
               .format(self.data_folder_additional_configs, self.get_data_folder()[-50:]))
        return

    data_files = list(filter(lambda x: os.path.isfile(os.path.join(check_dir, x)), os.listdir(check_dir)))
    data_files = list(filter(lambda x: any(ext in x for ext in ['.txt', 'json']), data_files))

    for f in data_files:
      if any(x in f for x in ['config', 'cfg', 'conf']):
        fn = self.get_data_file(f)
        self.P("Found additional config in '{}'".format(fn))
        dct_config = json.load(open(fn), object_pairs_hook=OrderedDict)
        self.replace_secrets(dct_config)
        additional_configs.append(dct_config)

    if len(additional_configs) > 0:
      dct_final = {}
      for d in additional_configs:
        dct_final.update(d)
      for k, v in dct_final.items():
        if k in self.config_data:
          self.P("[WARNING] Overriding key '{}'".format(k))
        self.config_data[k] = v
    return

  def raise_error(self, error_message):
    self.P("ERROR: {}".format(error_message))
    raise ValueError(str(error_message))

  def get_config_value(self, key, default=0):
    if key in self.config_data.keys():
      _val = self.config_data[key]
    else:
      # create key if does not exist
      _val = default
      self.config_data[key] = _val
    return _val

  def clear_folder(self, folder, include_subfolders=False):
    self.P("Clearing {}".format(folder))
    for the_file in os.listdir(folder):
      file_path = os.path.join(folder, the_file)
      try:
        if os.path.isfile(file_path):
          self.P("  Deleting {}".format(file_path[-30:]))
          os.unlink(file_path)
        elif os.path.isdir(file_path) and include_subfolders:
          self.P("  Removing ...{} subfolder".format(file_path[-30:]))
          shutil.rmtree(file_path)
      except Exception as e:
        self.P("{}".format(e))

  def clear_model_folder(self, include_subfolders=False):
    folder = self.get_models_folder()
    self.clear_folder(folder, include_subfolders=include_subfolders)

  def clear_log_folder(self, include_subfolders=False):
    folder = self._logs_dir
    self.clear_folder(folder, include_subfolders=include_subfolders)

  def clear_output_folder(self, include_subfolders=False):
    folder = self.get_output_folder()
    self.clear_folder(folder, include_subfolders=include_subfolders)

  def clear_all_results(self):
    self.P("WARNING: removing all files from models, logs and output!")
    self.clear_log_folder()
    self.clear_model_folder()
    self.clear_output_folder()

  def get_base_folder(self):
    return self._base_folder if hasattr(self, '_base_folder') else ''

  @property
  def base_folder(self):
    return self.get_base_folder()

  @property
  def root_folder(self):
    return self._root_folder

  @property
  def app_folder(self):
    return self._app_folder

  def get_data_folder(self):
    return self._data_dir if hasattr(self, '_data_dir') else ''

  def get_logs_folder(self):
    return self._logs_dir if hasattr(self, '_logs_dir') else ''

  def get_output_folder(self):
    return self._outp_dir if hasattr(self, '_outp_dir') else ''

  def get_models_folder(self):
    return self._modl_dir if hasattr(self, '_modl_dir') else ''

  def get_target_folder(self, target):
    if target is None:
      return

    if target.lower() in ['data', '_data', 'data_dir', 'dat']:
      return self.get_data_folder()

    if target.lower() in ['logs', 'log', 'logs_dir', 'log_dir', '_log', '_logs']:
      return self.get_logs_folder()

    if target.lower() in ['models', 'model', '_models', '_model', 'model_dir', 'models_dir', 'modl']:
      return self.get_models_folder()

    if target.lower() in ['output', '_output', 'output_dir', 'outp', '_outp']:
      return self.get_output_folder()

    self.P("Inner folder of type '{}' not found".format(target))
    return
  
  
  def get_subfolder(self, where, subfolder, force_create=False):
    folder = self.get_target_folder(target=where)
    path = os.path.join(folder, subfolder)
    if force_create:
      os.makedirs(path, exist_ok=True)
    if os.path.isdir(path):
      return path
    return None
    

  def get_data_subfolder(self, _dir, force_create=False):
    return self.get_subfolder(where='data', subfolder=_dir, force_create=force_create)

  def get_models_subfolder(self, _dir, force_create=False):
    return self.get_subfolder(where='models', subfolder=_dir, force_create=force_create)
  
  def get_output_subfolder(self, _dir, force_create=False):
    return self.get_subfolder(where='output', subfolder=_dir, force_create=force_create)

  def get_path_from_node(self, dct):
    if 'PARENT' in dct:
      path = self.get_path_from_node(dct['PARENT'])
      os.path.join(path, dct['PATH'])
      return path
    elif 'USE_DROPBOX' in dct and int(dct['USE_DROPBOX']) == 1:
      return os.path.join(self.get_base_folder(), dct['PATH'])
    else:
      return dct['PATH']

  def get_root_subfolder(self, folder):
    fld = os.path.join(self._root_folder, folder)
    if os.path.isdir(fld):
      return fld
    else:
      return None

  def get_base_subfolder(self, folder):
    fld = os.path.join(self._base_folder, folder)
    if os.path.isdir(fld):
      return fld
    else:
      return None

  def get_root_file(self, str_file):
    fn = os.path.join(self._root_folder, str_file)
    assert os.path.isfile(fn), "File not found: {}".format(fn)
    return fn

  def get_base_file(self, str_file):
    fn = os.path.join(self.get_base_folder(), str_file)
    assert os.path.isfile(fn), "File not found: {}".format(fn)
    return fn

  def get_file_from_folder(self, s_folder, s_file):
    s_fn = os.path.join(self.get_base_folder(), s_folder, s_file)
    if not os.path.isfile(s_fn):
      s_fn = None
    return s_fn

  def get_data_file(self, s_file):
    """
    returns full path of a data file or none is file does not exist
    """
    fpath = os.path.join(self.get_data_folder(), s_file)
    if not os.path.isfile(fpath):
      fpath = None
    return fpath

  def get_model_file(self, s_file):
    """
    returns full path of a data file or none is file does not exist
    """
    fpath = os.path.join(self.get_models_folder(), s_file)
    if not os.path.isfile(fpath):
      fpath = None
    return fpath

  def get_models_file(self, s_file):
    return self.get_model_file(s_file)

  def get_output_file(self, s_file):
    fpath = os.path.join(self.get_output_folder(), s_file)
    if not os.path.isfile(fpath):
      fpath = None
    return fpath

  def check_folder(self, sub_folder, root=None):
    if root is None:
      root = self.get_base_folder()
    sfolder = os.path.join(root, sub_folder)
    if sfolder not in self.folder_list:
      self.folder_list.append(sfolder)

    if not os.path.isdir(sfolder):
      self.verbose_log(" Creating folder [...{}]".format(sfolder[-40:]))
      os.makedirs(sfolder)
    return sfolder

  def check_folder_data(self, sub_folder):
    root = self.get_data_folder()
    return self.check_folder(sub_folder, root)

  def check_folder_models(self, sub_folder):
    root = self.get_models_folder()
    return self.check_folder(sub_folder, root)

  def check_folder_output(self, sub_folder):
    root = self.get_output_folder()
    return self.check_folder(sub_folder, root)

  @staticmethod    
  def is_url_friendly(s):
    """
    Check if a string is URL-friendly.

    Parameters
    ----------
    s : str
      The string to be checked for URL-friendliness.

    Returns
    -------
    bool
      True if the string is URL-friendly, False otherwise.
    """
    # Regular expression for matching only letters, numbers, underscores, and hyphens
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, s))  

  @staticmethod
  def get_folders(path):
    lst = [os.path.join(path, x) for x in os.listdir(path)]
    return [x for x in lst if os.path.isdir(x)]

  @staticmethod
  def expand_tilda(path):
    if '~' in path:
      path = path.replace('~', os.path.expanduser('~'))
    return path

  def refresh_file_prefix(self):
    self.file_prefix = dt.now().strftime("%Y%m%d_%H%M%S")
    return

  @staticmethod
  def now_str(nice_print=False, short=False):
    if nice_print:
      if short:        
        return dt.now().strftime("%Y-%m-%d %H:%M:%S")
      else:
        return dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
      if short:
        return dt.now().strftime("%Y%m%d%H%M%S") 
      else:
        return dt.now().strftime("%Y%m%d%H%M%S%f")
      
  @staticmethod
  def get_utc_offset(as_string=True):

    # Get the local timezone
    local_timezone = tz.tzlocal()
    # Get the current datetime in the local timezone
    now = dt.now(local_timezone)
    # Get the timezone offset in minutes
    offset_minutes = now.utcoffset().total_seconds() / 60
    # Get the timezone offset in hours
    offset_hours = offset_minutes / 60
    if as_string:
      result = "UTC{}{}".format("+" if offset_hours >= 0 else "-", int(offset_hours)) 
    else:
      result = offset_hours
    return result
  
  
  @staticmethod
  def utc_to_local(remote_datetime, remote_utc, fmt='%Y-%m-%d %H:%M:%S', as_string=False):
    """
    Given a "remote" datetime (in datetime or str format) and a string or int denoting an offset 
    will return local datetime as a datetime object.

    Parameters
    ----------
    remote_datetime: datetime or str or tzinfo
      The remote datetime
      
    remote_utc: int or str
      The UTC offset of the remote datetime as int or as string - i.e. "UTC+3" or even "+3"

    Returns
    -------
      datetime      
    """
    if remote_utc is None:
      remote_utc = 'UTC+3'
    if isinstance(remote_utc, str):
      remote_utc = tz.gettz(remote_utc)
    elif isinstance(remote_utc, int):
      utc_offset = remote_utc
      remote_utc = tz.tzoffset(None, timedelta(hours=utc_offset))
    elif not isinstance(remote_utc, tzinfo):
      raise ValueError("Unknown remote_utc type: {}".format(type(remote_utc)))

    if isinstance(remote_datetime, str):
      remote_datetime = dt.strptime(remote_datetime, fmt)

    remote_datetime = remote_datetime.replace(tzinfo=remote_utc)
    local_timezone = tz.tzlocal()
    local_datetime = remote_datetime.astimezone(local_timezone)
    local_datetime = local_datetime.replace(tzinfo=None)
    if as_string:
      local_datetime = local_datetime.strftime(fmt)
    return local_datetime
  
  @staticmethod
  def str_to_sec(s):
    res = None
    try:
      import time
      x = time.strptime(s,'%H:%M:%S')
      res = timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
    except:
      pass
    return res  
  
  
  @staticmethod
  def time_to_str(t=None, fmt='%Y-%m-%d %H:%M:%S'):
    if t is None:
      t = tm()
    return strftime(fmt, localtime(t))
  
  
  def elapsed_to_str(self, elapsed=None, show_days=False):
    """
    Pretty format a number of seconds

    Parameters
    ----------
    elapsed : float, optional
      The amount of time in seconds. The default is None and will use Logger init start as reference.
    show_days : bool, optional
      Show in days, hours, etc instead of HH:MM:SS. The default is False.

    Returns
    -------
    s : str
      Formatted time.

    """
    if elapsed is None:
      elapsed = tm() - self.start_timestamp
    
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    if show_days:
      s = str(timedelta(seconds=int(elapsed)))
    else:
      s = "{:0>2}:{:0>2}:{:0>2}".format(int(hours),int(minutes),int(seconds))
    return s


  @staticmethod
  def str_to_time(s, fmt='%Y-%m-%d %H:%M:%S'):
    return mktime(strptime(s, fmt))
  
  
  @staticmethod
  def str_to_date(s, fmt='%Y-%m-%d %H:%M:%S'):
    return dt.strptime(s, fmt)


  @staticmethod
  def now_str_fmt(fmt=None):
    if fmt is None:
      fmt = '%Y-%m-%d %H:%M:%S.%f'

    return dt.now().strftime(fmt)

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

  @staticmethod
  def tqdm_enumerate(_iter):
    from tqdm import tqdm
    i = 0
    for y in tqdm(_iter):
      yield i, y
      i += 1

  @staticmethod
  def set_nice_prints(linewidth=500,
                      precision=3,
                      np_precision=None,
                      df_precision=None,
                      suppress=False):

    if np_precision is None:
      np_precision = precision
    if df_precision is None:
      df_precision = precision
    np.set_printoptions(precision=np_precision)
    np.set_printoptions(floatmode='fixed')
    np.set_printoptions(linewidth=linewidth)
    np.set_printoptions(suppress=suppress)

    try:
      import pandas as pd
      pd.set_option('display.max_rows', 500)
      pd.set_option('display.max_columns', 500)
      pd.set_option('display.width', 1000)
      pd.set_option('display.max_colwidth', 1000)
      _format = '{:.' + str(df_precision) + 'f}'
      pd.set_option('display.float_format', lambda x: _format.format(x))
    except:
      pass

    return

  @staticmethod
  def get_google_drive():
    home_dir = os.path.expanduser("~")
    valid_paths = [
      os.path.join(home_dir, "Google Drive"),
      os.path.join(home_dir, "GoogleDrive"),
      os.path.join(os.path.join(home_dir, "Desktop"), "Google Drive"),
      os.path.join(os.path.join(home_dir, "Desktop"), "GoogleDrive"),
      os.path.join("C:/", "GoogleDrive"),
      os.path.join("C:/", "Google Drive"),
      os.path.join("D:/", "GoogleDrive"),
      os.path.join("D:/", "Google Drive"),
    ]

    drive_path = None
    for path in valid_paths:
      if os.path.isdir(path):
        drive_path = path
        break

    if drive_path is None:
      raise Exception("Couldn't find google drive folder!")

    return drive_path

  @staticmethod
  def get_dropbox_drive():
    # TODO: change this to not be restricted by the folder name
    home_dir = os.path.expanduser("~")
    valid_paths = [
      os.path.join(home_dir, "Lummetry.AI Dropbox/DATA"),
      os.path.join(home_dir, "Lummetry.AIDropbox/DATA"),
      os.path.join(os.path.join(home_dir, "Desktop"), "Lummetry.AI Dropbox/DATA"),
      os.path.join(os.path.join(home_dir, "Desktop"), "Lummetry.AIDropbox/DATA"),
      os.path.join("C:/", "Lummetry.AI Dropbox/DATA"),
      os.path.join("C:/", "Lummetry.AIDropbox/DATA"),
      os.path.join("D:/", "Lummetry.AI Dropbox/DATA"),
      os.path.join("D:/", "Lummetry.AIDropbox/DATA"),
      os.path.join(home_dir, "Dropbox/DATA"),
      os.path.join(os.path.join(home_dir, "Desktop"), "Dropbox/DATA"),
      os.path.join("C:/", "Dropbox/DATA"),
      os.path.join("D:/", "Dropbox/DATA"),
    ]

    drive_path = None
    for path in valid_paths:
      if os.path.isdir(path):
        drive_path = path
        break

    if drive_path is None:
      raise Exception("Couldn't find google drive folder!")

    return drive_path

  @staticmethod
  def get_dropbox_subfolder(sub_folder):
    drop_root = BaseLogger.get_dropbox_drive()
    full = os.path.join(drop_root, sub_folder)
    if os.path.isdir(full):
      return full
    else:
      return None
    
  @staticmethod
  def print_color(s, color=None):
    color = color or 'n'
    color = color.lower()[0]
    color_start = COLORS[color] if color in COLORS else COLORS['n']
    color_end = COLORS['__end__']
    print('\r' + color_start + s + color_end, flush=True)
    return

  @staticmethod
  def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    Credits: django 3.1
    """
    from importlib import import_module
    try:
      module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
      raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
      return getattr(module, class_name)
    except AttributeError as err:
      raise ImportError(
        'Module "%s" does not define a "%s" attribute/class' % \
        (module_path, class_name)
      ) from err

  def get_machine_name(self):
    """
    if socket.gethostname().find('.')>=0:
        name=socket.gethostname()
    else:
        name=socket.gethostbyaddr(socket.gethostname())[0]
    """

    self.MACHINE_NAME = socket.gethostname()
    self.COMPUTER_NAME = self.MACHINE_NAME
    return self.MACHINE_NAME


  def _link(self, src_path, target_subpath, is_dir, target=None):
    """
    Creates a symbolic link.

    Parameters:
    ----------
    src_path: str, mandatory
      Symlink src full path

    target_subpath: str, mandatory
      Subpath in the target directory of the logger

    is_dir: bool, mandatory
      Whether is directory or file

    target: str, optional
      Target directory of the logger (data, models, output or logs)
      The default is None ('data')
    """
    if target is None:
      target = 'data'

    if not os.path.exists(src_path):
      self.verbose_log("ERROR! Could not create symlink, because '{}' does not exist".format(src_path))
      return

    target_path = self.get_target_folder(target)
    if target_path is None:
      return

    target_path = os.path.join(target_path, target_subpath)
    if os.path.exists(target_path):
      return

    target_path_parent = Path(target_path).parent
    if not os.path.exists(target_path_parent):
      os.makedirs(target_path_parent)

    os.symlink(
      src_path, target_path,
      target_is_directory=is_dir
    )

    return

  def link_file(self, src_path, target_subpath, target=None):
    self._link(src_path, target_subpath, is_dir=False, target=target)
    return

  def link_folder(self, src_path, target_subpath, target=None):
    self._link(src_path, target_subpath, is_dir=True, target=target)
    return

  @property
  def is_main_thread(self):
    return threading.current_thread() is threading.main_thread()
  
  @staticmethod
  def get_os_name():
    import platform
    return platform.platform()
    
  @staticmethod
  def get_conda_env():
    folder = os.environ.get("CONDA_PREFIX", None)
    env = None
    if folder is not None and len(folder) > 0:
      try:
        env = os.path.split(folder)[-1]
      except:
        env = None
    return env

  @staticmethod
  def get_active_git_branch():
    fn = './.git/HEAD'
    if os.path.isfile(fn):
      with open(fn, 'r') as f:
        content = f.readlines()
      for line in content:
        if line.startswith('ref:'):
          return line.partition('refs/heads/')[2].replace('\n','')
    else:
      return None
  
  
  def dict_show(self, d):
    self.dict_pretty_format(d=d, display=True)
    return

  def show_dict(self, d):
    self.dict_pretty_format(d=d, display=True)
    return
  
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
          str_value = str(value) if not isinstance(value,str) else '"{}"'.format(value)
          if isinstance(value,str) and len(str_value) > limit_str:
            str_value = str_value[:limit_str]
          lst_data[-1] = lst_data[-1] + str_value

        if ki < (len(dct) - 1):
          lst_data[-1] = lst_data[-1] + ','            
      return
    
    deep_parse(dct=d,ind=0)
    
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
      
  def get_log_files(self):
    return [os.path.join(self._logs_dir, x) for x in os.listdir(self._logs_dir) if '.txt' in x.lower()]
  
  
  def camel_to_snake(self, s):
    import re    
    if s.isupper():
      result = s.lower()
    else:
      s = re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
      s = s.replace('__', '_')
      result = s
    return result

  @staticmethod
  def match_template(json_data: dict, template: dict) -> bool:
    """
    Check if all keys (including subkeys) within the template can be found with the same values in the given JSON.

    Parameters
    ----------
    json_data : dict
      The JSON (dict) to check against the template.
    template : dict
      The template JSON (dict) containing the keys and values to match.

    Returns
    -------
    bool
      True if the JSON matches the template, False otherwise.
    """
    # Initialize the stack with the top-level dictionaries from json_data and template
    stack = [(json_data, template)]

    # Process each pair of current data and template dictionaries/lists from the stack
    while stack:
      current_data, current_tmpl = stack.pop()

      # Check if current_tmpl is a dictionary
      if isinstance(current_tmpl, dict):
        for key, value in current_tmpl.items():
          # If the key is not in current_data, return False
          if key not in current_data:
            return False

          # If the value in the template is a dictionary, add the corresponding pair to the stack
          if isinstance(value, dict):
            if not isinstance(current_data[key], dict):
              return False
            stack.append((current_data[key], value))

          # If the value in the template is a list, process each item in the list
          elif isinstance(value, list):
            if not isinstance(current_data[key], list):
              return False

            tmpl_list = value
            data_list = current_data[key]

            # For each item in the template list, ensure there is a matching item in the data list
            for tmpl_item in tmpl_list:
              matched = False
              for data_item in data_list:
                # If both are dictionaries, add them to the stack for further processing
                if isinstance(tmpl_item, dict) and isinstance(data_item, dict):
                  stack.append((data_item, tmpl_item))
                  matched = True
                  break
                # If both are lists, add them to the stack for further processing
                elif isinstance(tmpl_item, list) and isinstance(data_item, list):
                  stack.append((data_item, tmpl_item))
                  matched = True
                  break
                # If they are of the same type and equal, mark as matched
                elif tmpl_item == data_item:
                  matched = True
                  break
              # If no matching item is found, return False
              if not matched:
                return False

          # If the value is not a dictionary or list, directly compare the values
          elif current_data[key] != value:
            return False

      # Check if current_tmpl is a list
      elif isinstance(current_tmpl, list):
        for tmpl_item in current_tmpl:
          matched = False
          for data_item in current_data:
            # If both are dictionaries, add them to the stack for further processing
            if isinstance(tmpl_item, dict) and isinstance(data_item, dict):
              stack.append((data_item, tmpl_item))
              matched = True
              break
            # If both are lists, add them to the stack for further processing
            elif isinstance(tmpl_item, list) and isinstance(data_item, list):
              stack.append((data_item, tmpl_item))
              matched = True
              break
            # If they are of the same type and equal, mark as matched
            elif tmpl_item == data_item:
              matched = True
              break
          # If no matching item is found, return False
          if not matched:
            return False

    # If all checks passed, return True
    return True
