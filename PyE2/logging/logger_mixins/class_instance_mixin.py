import inspect

class _ClassInstanceMixin(object):
  """
  Mixin for class instance functionalities that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_ClassInstanceMixin, self).__init__()

  @staticmethod
  def get_class_instance_methods(obj, spacing=20):
    methodList = []
    for method_name in dir(obj):
      try:
        if callable(getattr(obj, method_name)):
          methodList.append(str(method_name))
      except:
        methodList.append(str(method_name))
    processFunc = (lambda s: ' '.join(s.split())) or (lambda s: s)
    for method in methodList:
      try:
        print(str(method.ljust(spacing)) + ' ' + processFunc(str(getattr(obj, method).__doc__)[0:90]))
      except:
        print(method.ljust(spacing) + ' ' + ' getattr() failed')
    return


  @staticmethod
  def get_class_instance_params(obj, n=None):
    """
    Parameters
    ----------
    obj : any type
      the inspected object.
    n : int, optional
      the number of params that are returned. The default is None
      (all params returned).

    Returns
    -------
    out_str : str
      the description of the object 'obj' in terms of parameters values.
    """

    out_str = obj.__class__.__name__ + "("
    n_added_to_log = 0
    for _iter, (prop, value) in enumerate(vars(obj).items()):
      if type(value) in [int, float, bool]:
        out_str += prop + '=' + str(value) + ','
        n_added_to_log += 1
      elif type(value) in [str]:
        out_str += prop + "='" + value + "',"
        n_added_to_log += 1

      if n is not None and n_added_to_log >= n:
        break
    # endfor

    out_str = out_str[:-1] if out_str[-1] == ',' else out_str
    out_str += ')'
    return out_str

  @staticmethod
  def get_object_params(*args, **kwargs):
    print("DeprecationWarning! `get_object_params` is deprecated. Please use `get_class_instance_params` instead")
    return _ClassInstanceMixin.get_class_instance_params(*args, **kwargs)

  @staticmethod
  def get_object_methods(*args, **kwargs):
    print("DeprecationWarning! `get_object_methods` is deprecated. Please use `get_class_instance_methods` instead")
    return _ClassInstanceMixin.get_class_instance_methods(*args, **kwargs)

  @staticmethod
  def get_class_methods(cls, include_parent=True):
    lst_methods = inspect.getmembers(cls, predicate=inspect.isfunction)

    if not include_parent:
      lst_methods = list(filter(
        lambda x: cls.__name__ in x[1].__qualname__,
        lst_methods
      ))

    return lst_methods



