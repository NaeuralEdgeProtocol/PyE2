import os
import sys


def _walk_to_root(path: str):
  """
  Yield directories starting from the given directory up to the root
  """
  if not os.path.exists(path):
    raise IOError('Starting path not found')

  if os.path.isfile(path):
    path = os.path.dirname(path)

  last_dir = None
  current_dir = os.path.abspath(path)
  while last_dir != current_dir:
    yield current_dir
    parent_dir = os.path.abspath(os.path.join(current_dir, os.path.pardir))
    last_dir, current_dir = current_dir, parent_dir


def find_dotenv(
    filename: str = '.env',
    raise_error_if_not_found: bool = False,
    usecwd: bool = False,
) -> str:
  """
  Search in increasingly higher folders for the given file

  Returns path to the file if found, or an empty string otherwise
  """

  def _is_interactive():
    """ Decide whether this is running in a REPL or IPython notebook """
    main = __import__('__main__', None, None, fromlist=['__file__'])
    return not hasattr(main, '__file__')

  if usecwd or _is_interactive() or getattr(sys, 'frozen', False):
    # Should work without __file__, e.g. in REPL or IPython notebook.
    path = os.getcwd()
  else:
    # will work for .py files
    frame = sys._getframe()
    current_file = __file__

    while frame.f_code.co_filename == current_file:
      assert frame.f_back is not None
      frame = frame.f_back
    frame_filename = frame.f_code.co_filename
    path = os.path.dirname(os.path.abspath(frame_filename))

  for dirname in _walk_to_root(path):
    check_path = os.path.join(dirname, filename)
    if os.path.isfile(check_path):
      return check_path

  if raise_error_if_not_found:
    raise IOError('File not found')

  return ''


def load_dotenv(dotenv_path=None):
  """Load environment variables from a .env file."""
  if dotenv_path is None:
    dotenv_path = find_dotenv()
  if not os.path.exists(dotenv_path):
    raise ValueError(f"Error: {dotenv_path} file not found. Please check your bare-metal deployment.")

  print("Loading {}...".format(dotenv_path))
  with open(dotenv_path, 'r') as f:
    for line in f:
      line = line.strip()
      if not line or line.startswith('#') or '=' not in line:
        continue
      key, value = line.split('=', 1)
      print("  Setting '{}'".format(key))
      os.environ[key] = value
  return
