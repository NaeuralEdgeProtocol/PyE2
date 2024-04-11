import os

class _ResourceSizeMixin(object):
  """
  Mixin for resource size functionalities that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_ResourceSizeMixin, self).__init__()

  @staticmethod
  def compute_size_units(size):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    unit = units[i]
    while size >= 1024 and i < len(units) - 1:
      i += 1
      size /= 1024
      unit = units[i]

    size = round(size, 3)
    return size, unit

  @staticmethod
  def cast_size_units(size,
                      initial_unit,
                      target_unit):
    assert initial_unit in ['B', 'KB', 'MB', 'GB', 'TB']
    assert target_unit in ['B', 'KB', 'MB', 'GB', 'TB']

    if initial_unit == 'TB':
      size_bytes = size * (2 ** 40)
    elif initial_unit == 'GB':
      size_bytes = size * (2 ** 30)
    elif initial_unit == 'MB':
      size_bytes = size * (2 ** 20)
    elif initial_unit == 'KB':
      size_bytes = size * (2 ** 10)
    elif initial_unit == 'B':
      size_bytes = size

    if target_unit == 'TB':
      target_size = size_bytes / (2 ** 40)
    elif target_unit == 'GB':
      target_size = size_bytes / (2 ** 30)
    elif target_unit == 'MB':
      target_size = size_bytes / (2 ** 20)
    elif target_unit == 'KB':
      target_size = size_bytes / (2 ** 10)
    elif target_unit == 'B':
      target_size = size_bytes

    return target_size

  def get_file_size(self, fn=None, target='data'):
    file_path = os.path.join(self.get_target_folder(target=target), fn)
    size = os.path.getsize(file_path)
    return self.compute_size_units(size)

  @staticmethod
  def get_folder_size(start_path=None):
    if start_path is None:
      start_path = '.'

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
      for f in filenames:
        fp = os.path.join(dirpath, f)
        # skip if it is symbolic link
        if not os.path.islink(fp):
          try:
            total_size += os.path.getsize(fp)
          except:
            pass

    return _ResourceSizeMixin.compute_size_units(total_size)
