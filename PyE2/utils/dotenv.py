import os
import sys
import configparser


def find_dotenv(
    filename: str = '.env',
) -> str:
  """
  Search the `.env` file in cwd and the directories of the files from the callstack.
  Returns path to the first env file if found, or an empty string otherwise
  """

  files_checked_queue = [os.getcwd()]

  frame = sys._getframe()
  current_dir = None

  while frame is not None:
    base_dir = os.path.dirname(frame.f_code.co_filename)
    if current_dir != base_dir:
      files_checked_queue.append(base_dir)
      current_dir = base_dir
    # endif
    frame = frame.f_back
  # endwhile

  for path in files_checked_queue:
    check_path = os.path.join(path, filename)
    if os.path.isfile(check_path):
      return check_path
  # endwhile

  return ''


def load_dotenv(dotenv_path=None, *, verbose=False, load_env=True):
  """
  Load environment variables from a .env file.

  Parameters
  ----------
  dotenv_path : str, optional
      Path to the .env file. If not specified, it will search in the current directory of each file from the call stack, by default None
  verbose : bool, optional
      If True, the method will print logs, by default False
  load_env : bool, optional
      If True, the method will load the found variables in the environment, by default True

  Returns
  -------
  dict
      A dictionary containing the variables found in the .env file
  """
  if dotenv_path is None:
    dotenv_path = find_dotenv()
  if not os.path.exists(dotenv_path):
    if verbose:
      print(f"Error: `{dotenv_path or '.env'}` file not found.")
    return

  if verbose:
    print("Loading {}...".format(dotenv_path))
  parser = configparser.ConfigParser()
  with open(dotenv_path, 'r') as f:
    parser.read_string('[data]\n' + f.read())
  dct_data = {k.upper(): v for k, v in parser['data'].items()}

  if load_env:
    for key, value in dct_data.items():
      if verbose:
        print("  Setting '{}'".format(key))
      os.environ[key] = value
  # endif load_env
  return dct_data
