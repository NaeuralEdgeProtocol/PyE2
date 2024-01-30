import os
import sys


def find_dotenv(
    filename: str = '.env',
) -> str:
  """
  Search the `.env` file in cwd and the directories of the files from the callstack.
  Returns path to the first env file if found, or an empty string otherwise
  """

  cwd = os.getcwd()

  files_checked_queue = []
  files_checked_queue.append(cwd)

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


def load_dotenv(dotenv_path=None, usecwd=False, verbose=False):
  """Load environment variables from a .env file."""
  if dotenv_path is None:
    dotenv_path = find_dotenv()
  if not os.path.exists(dotenv_path):
    if verbose:
      search_path = os.getcwd() if usecwd else os.path.abspath(os.path.dirname(__file__))
      print(f"Error: `{dotenv_path or '.env'}` file not found. Search path: `{search_path}` (use cwd: {usecwd})")
    return

  if verbose:
    print("Loading {}...".format(dotenv_path))
  with open(dotenv_path, 'r') as f:
    for line in f:
      line = line.strip()
      if not line or line.startswith('#') or '=' not in line:
        continue
      key, value = line.split('=', 1)
      if verbose:
        print("  Setting '{}'".format(key))
      os.environ[key] = value
  return
