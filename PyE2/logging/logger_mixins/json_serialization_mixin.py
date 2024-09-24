import json
import yaml
import os
import numpy as np
import traceback
import datetime 

from collections import OrderedDict 

from copy import deepcopy

def copy_docstring(original):
  """
  Decorator to copy the docstring of another function to the decorated function.

  Parameters
  ----------
  original : function
      The function from which to copy the docstring.

  Returns
  -------
  callable
      A decorator that assigns the original docstring to the decorated function.
  """
  def decorator(target):
    target.__doc__ = original.__doc__
    return target
  return decorator


def replace_nan_inf(data, inplace=False):
  assert isinstance(data, (dict, list)), "Only dictionaries and lists are supported"
  if inplace:
    d = data
  else:
    d = deepcopy(data)    
  stack = [d]
  while stack:
    current = stack.pop()
    for key, value in current.items():
      if isinstance(value, dict):
        stack.append(value)
      elif isinstance(value, list):
        for item in value:
          if isinstance(item, dict):
            stack.append(item)
      elif isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        current[key] = None
  return d 

class SimpleNPJson(json.JSONEncoder):
  """
  Used to help jsonify numpy arrays or lists that contain numpy data types,
  and handle datetime.
  """
  def default(self, obj):
    if isinstance(obj, np.integer):
      return int(obj)
    elif isinstance(obj, np.floating):
      return float(obj)
    elif isinstance(obj, np.ndarray):
      return obj.tolist()
    elif isinstance(obj, datetime.datetime):
      return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif "torch" in str(type(obj)):
      return str(obj)
    else:
      return super(SimpleNPJson, self).default(obj)

class NPJson(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, np.integer):
      return int(obj)
    elif isinstance(obj, np.floating):
      return float(obj)
    elif isinstance(obj, np.ndarray):
      return obj.tolist()
    elif isinstance(obj, datetime.datetime):
      return obj.strftime("%Y-%m-%d %H:%M:%S")
    elif "torch" in str(type(obj)):
      return str(obj)
    else:
      return super(NPJson, self).default(obj)

  def iterencode(self, o, _one_shot=False):
    """Encode the given object and yield each string representation as available."""
    if self.check_circular:
      markers = {}
    else:
      markers = None
    if self.ensure_ascii:
      _encoder = json.encoder.encode_basestring_ascii
    else:
      _encoder = json.encoder.encode_basestring
    
    def floatstr(o, allow_nan=self.allow_nan, _repr=float.__repr__, _inf=json.encoder.INFINITY, _neginf=-json.encoder.INFINITY):
      if o != o:  # Check for NaN
        text = 'null'
      elif o == _inf:
        text = 'null'
      elif o == _neginf:
        text = 'null'
      else:
        return repr(o).rstrip('0').rstrip('.') if '.' in repr(o) else repr(o)

      if not allow_nan:
        raise ValueError("Out of range float values are not JSON compliant: " + repr(o))
      
      return text

    _iterencode = json.encoder._make_iterencode(
      markers, self.default, _encoder, self.indent, floatstr,
      self.key_separator, self.item_separator, self.sort_keys,
      self.skipkeys, _one_shot
    )
    return _iterencode(o, 0)


class _JSONSerializationMixin(object):
  """
  Mixin for json serialization functionalities that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_JSONSerializationMixin, self).__init__()
    return

  def load_json(self, 
                fname, 
                folder=None, 
                numeric_keys=True, 
                verbose=True, 
                subfolder_path=None, 
                locking=True,
                replace_environment_secrets=None,                
                ):
    assert folder in [None, 'data', 'output', 'models']
    lfld = self.get_target_folder(target=folder)

    if folder is not None:
      if subfolder_path is not None:
        datafile = os.path.join(lfld, subfolder_path.lstrip('/'), fname)
        if verbose:
          self.verbose_log("Loading json '{}' from '{}'/'{}'".format(fname, folder, subfolder_path))
        #endif
      else:
        datafile = os.path.join(lfld, fname)
        if verbose:
          self.verbose_log("Loading json '{}' from '{}'".format(fname, folder))
        #endif
      #endif
    else:
      datafile = fname
      if verbose:
        self.verbose_log("Loading json '{}'".format(fname))
    #endif

    if os.path.isfile(datafile):
      with self.managed_lock_resource(datafile, condition=locking):
        try:
          with open(datafile) as f:
            if not numeric_keys:
              data = json.load(f)
            else:
              data = json.load(f, object_hook=lambda d: {int(k) if k.isnumeric() else k: v for k, v in d.items()})
        except Exception as e:
          self.P("JSON load failed: {}".format(e), color='r')
          data = None
      # endwith conditional lock
      if isinstance(replace_environment_secrets, str) and len(replace_environment_secrets) > 0:
        matches = self.replace_secrets(data)
        if matches is not None and len(matches) > 0:
          self.P("  JSON modified with following env vars: {}".format(matches))
      return data
    else:
      if verbose:
        self.verbose_log("  File not found!", color='r')
    return
  
  
  @staticmethod
  def replace_nan(data, inplace=False):
    return replace_nan_inf(data, inplace=inplace)


  @staticmethod
  def safe_json_dumps(
    dct, 
    replace_nan=False, 
    inplace=False, 
    sort_keys=True, 
    separators=(',',':'), 
    **kwargs
  ):
    """
    Safely dumps a dictionary to json string, replacing nan/inf with None.
    The method also uses deterministic sorting of keys and custom separators.

    Parameters
    ----------
    dct : dict
        The dictionary to be dumped to json
        
    replace_nan : bool, optional  
        If True, replaces nan/inf with None. The default is False.
        
    inplace : bool, optional
        If True, replaces nan/inf with None in the original dictionary. The default is False.
        
    sort_keys : bool, optional  
        If True, sorts the keys of the dictionary. The default is True.
        
    separators : tuple, optional
        The separators to be used for json serialization. The default is (',',':').
    
    **kwargs : dict, optional
        Additional arguments to be passed to json.dumps

    Returns
    -------
    str
        The json string representing the dictionary.
    """
    data = dct  
    if replace_nan:
      # NPjson will actually handle inf/nan -> null but we might 
      # need to replace directly in the received dict if `inplace=True`
      if inplace:
        data = _JSONSerializationMixin.replace_nan(dct, inplace=inplace)
      return json.dumps(
        data, 
        cls=NPJson, 
        sort_keys=sort_keys, 
        separators=separators, 
        **kwargs
      )
    else:      
      return json.dumps(
        data, 
        cls=SimpleNPJson, 
        sort_keys=sort_keys, 
        separators=separators, 
        **kwargs
      )
    

  @staticmethod
  @copy_docstring(safe_json_dumps)
  def safe_dumps_json(
    dct, 
    replace_nan=False, 
    inplace=False, 
    sort_keys=True, 
    separators=(',',':'), 
    **kwargs
  ):
    return _JSONSerializationMixin.safe_json_dumps(
      dct, inplace=inplace, replace_nan=replace_nan, 
      sort_keys=sort_keys, separators=separators,
      **kwargs
    )
  
  @staticmethod
  @copy_docstring(safe_json_dumps)
  def json_dumps(
    dct, 
    replace_nan=False, 
    inplace=False, 
    sort_keys=True, 
    separators=(',',':'), 
    **kwargs
  ):
    return _JSONSerializationMixin.safe_json_dumps(
      dct, inplace=inplace, replace_nan=replace_nan, 
      sort_keys=sort_keys, separators=separators,
      **kwargs
    )
    
    
  def load_config_file(self, fn):
    """
    Loads a json/yaml config file and returns the dictionary.
    """
    dct_config = None
    if os.path.isfile(fn):
      if fn.endswith('.json'):
        self.P("Loading JSON config file: {}".format(fn), color='n')
        with open(fn, 'r') as f:          
          dct_config = json.load(f)
      elif fn.endswith('.yaml') or fn.endswith('.yml'):
        self.P("Loading YAML config file: {}".format(fn), color='n')
        with open(fn, 'r') as f:
          dct_config = yaml.safe_load(f)
      elif fn.endswith('.txt'):
        self.P("Loading JSON config file from .TXT: {}".format(fn), color='n')        
        with open(fn, 'r') as f:
          dct_config =json.load(f)
      else:
        raise ValueError("Unknown config file extension: {}".format(fn))
      #endif json/yaml
      dct_config = OrderedDict(dct_config)
    return dct_config


  def load_dict(self, **kwargs):
    return self.load_json(**kwargs)


  def load_data_json(self, fname, **kwargs):
    return self.load_json(fname, folder='data', **kwargs)
  
  def load_json_from_data(self, fname, subfolder_path=None, **kwargs):
    return self.load_json(fname, folder='data', subfolder_path=subfolder_path, **kwargs)
  
  def thread_safe_save(self, datafile, data_json, folder=None, locking=True, indent=True):
    lfld = ''
    if folder is not None:
      lfld = self.get_target_folder(folder)

    path = os.path.join(lfld, datafile)
    os.makedirs(os.path.split(path)[0], exist_ok=True)

    with self.managed_lock_resource(path, condition=locking):
      try:
        with open(path, 'w') as fp:
          json.dump(
            data_json, 
            fp, 
            sort_keys=True, 
            indent=4 if indent else None, 
            cls=NPJson
          )    
      except Exception as e:
        self.verbose_log("Exception while saving json '{}':\n{}".format(datafile, traceback.format_exc()), color='r')
    # endwith conditional locking
    return path

    
  def save_data_json(self, 
                     data_json, 
                     fname, 
                     subfolder_path=None, 
                     verbose=True, 
                     locking=True):
    save_dir = self._data_dir
    if subfolder_path is not None:
      save_dir = os.path.join(save_dir, subfolder_path.lstrip('/'))
      os.makedirs(save_dir, exist_ok=True)

    datafile = os.path.join(save_dir, fname)
    if verbose:
      self.verbose_log('Saving data json: {}'.format(datafile))
    self.thread_safe_save(datafile=datafile, data_json=data_json, locking=locking)
    return datafile

  def load_output_json(self, fname, **kwargs):
    return self.load_json(fname, folder='output', **kwargs)

  def save_output_json(self, 
                       data_json, 
                       fname, 
                       subfolder_path=None, 
                       verbose=True, 
                       locking=True,
                       indent=True,
                       ):
    save_dir = self._outp_dir
    if subfolder_path is not None:
      save_dir = os.path.join(save_dir, subfolder_path.lstrip('/'))
      os.makedirs(save_dir, exist_ok=True)

    datafile = os.path.join(save_dir, fname)
    if verbose:
      self.verbose_log('Saving output json: {}'.format(datafile))
    self.thread_safe_save(
      datafile=datafile, 
      data_json=data_json, 
      locking=locking,
      indent=indent,
    )
    return datafile

  def load_models_json(self, fname, **kwargs):
    return self.load_json(fname, folder='models', **kwargs)

  def save_models_json(self, 
                       data_json, 
                       fname, 
                       subfolder_path=None, 
                       verbose=True, 
                       locking=True):
    save_dir = self._modl_dir
    if subfolder_path is not None:
      save_dir = os.path.join(save_dir, subfolder_path.lstrip('/'))
      os.makedirs(save_dir, exist_ok=True)

    datafile = os.path.join(save_dir, fname)
    if verbose:
      self.verbose_log('Saving models json: {}'.format(datafile))
    self.thread_safe_save(datafile=datafile, data_json=data_json, locking=locking)
    return datafile

  def save_json(self, dct, fname, locking=True):
    return self.thread_safe_save(datafile=fname, data_json=dct, locking=locking)
  
  def save_json_to_data(self, dct, fname, subfolder_path=None, locking=True):
    return self.save_data_json(data_json=dct, fname=fname, subfolder_path=subfolder_path, locking=locking)

  def load_dict_from_data(self, fn):
    return self.load_data_json(fn)

  def load_dict_from_models(self, fn):
    return self.load_models_json(fn)

  def load_dict_from_output(self, fn):
    return self.load_output_json(fn)

  @staticmethod
  def save_dict_txt(path, dct, indent=True):
    json.dump(dct, open(path, 'w'), sort_keys=True, indent=4 if indent else None)
    return

  @staticmethod
  def load_dict_txt(path):
    """
    This function is NOT thread safe
    """
    with open(path) as f:
      data = json.load(f)
    return data
  
  
  def update_data_json(self,
                       fname, 
                       update_callback,
                       subfolder_path=None, 
                       verbose=False,
                       ):
    assert update_callback is not None, "update_callback must be defined!"
    datafile = self.get_file_path(
      fn=fname,
      folder='data',
      subfolder_path=subfolder_path,
      )
    if datafile is None:
      self.P("update_data_json failed due to missing {}".format(datafile), color='error')
      return False
    with self.managed_lock_resource(datafile):
      result = None
      try:
        data = self.load_data_json(
          fname=fname,
          verbose=verbose,
          subfolder_path=subfolder_path,
          locking=False,
          )
        
        if data is not None:
          data = update_callback(data)
          
          self.save_data_json(
            data_json=data, 
            fname=fname, 
            verbose=verbose,
            subfolder_path=subfolder_path,
            locking=False,
            )
          result = True
      except Exception as e:
        self.P("update_data_json failed: {}".format(e), color='error')
        result = False
      
    # endwith lock
    return result
          