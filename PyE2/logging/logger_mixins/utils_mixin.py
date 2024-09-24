import os
import re
import itertools
import sys
import pickle
import hashlib
import numpy as np
import traceback
from queue import Queue

from collections import OrderedDict, deque, defaultdict

from io import BytesIO, TextIOWrapper


class _UtilsMixin(object):
  """
  Mixin for functionalities that do not belong to any mixin that are attached to `pye2.Logger`.

  This mixin cannot be instantiated because it is built just to provide some additional
  functionalities for `pye2.Logger`

  In this mixin we can use any attribute/method of the Logger.
  """

  def __init__(self):
    super(_UtilsMixin, self).__init__()

  @staticmethod
  def get_function_parameters(function):
    import inspect
    signature = inspect.signature(function)
    parameters = signature.parameters

    all_params = []
    required_params = []
    optional_params = []

    for k, v in parameters.items():
      if k == 'self':
        continue

      all_params.append(k)

      if v.default is inspect._empty:
        required_params.append(k)
      else:
        optional_params.append(k)

    return all_params, required_params, optional_params

  @staticmethod
  def string_diff(seq1, seq2):
    return sum(1 for a, b in zip(seq1, seq2) if a != b) + abs(len(seq1) - len(seq2))

  @staticmethod
  def flatten_2d_list(lst):
    return _UtilsMixin.flatten_nd_list(lst, 2)
    # return list(itertools.chain.from_iterable(lst))

  @staticmethod
  def flatten_3d_list(lst):
    return _UtilsMixin.flatten_nd_list(lst, 3)

  @staticmethod
  def flatten_nd_list(lst, n):
    for _ in range(n - 1):
      if len(lst) == 0 or not isinstance(lst[0], list):
        break
      lst = list(itertools.chain.from_iterable(lst))
    return lst
  
  
  def _get_obj_size_graph(self, lst_obj_size_result, min_size_threshold=104_857):
    """
    Returns a graph as a dict, where de dependency is given by two fields: 'CHILDREN' and 'PARENT'

    Parameters
    ----------
    lst_obj_size_result : list
      list resulted from a `get_obj_size` call.
    
    Returns
    -------
    graph : dict
      graph as a dict, where de dependency is given by the fields: 'CHILDREN' and 'PARENT'
    
    """
    graph = {
      'PARENT': None,
      'CHILDREN': []
    }
    
    curr_node_at_level = {
      0: graph
    }
    
    for obj in lst_obj_size_result:
      level = obj.pop('LEVEL')
      
      node = {
        'PARENT': curr_node_at_level[level-1],
        'CHILDREN': [],
        **obj
      }
      curr_node_at_level[level-1]['CHILDREN'].append(node)
      curr_node_at_level[level] = node
    
    # now prune the graph, removing all children that are below a certain size
    processing_nodes = Queue()
    for kid in graph['CHILDREN']:
      processing_nodes.put(kid)
      
    while not processing_nodes.empty():
      node = processing_nodes.get()
      big_kids = [kid for kid in node['CHILDREN'] if kid['SIZE'] > min_size_threshold]
      node['CHILDREN'] = big_kids
      for kid in node['CHILDREN']:
        processing_nodes.put(kid)
    
    return graph

  def _get_graph_leaves(self, graph):
    """
    Returns a list with all the leaves from a given graph.
    The graph must be a dict with a key `CHILDREN`

    Parameters
    ----------
    graph : dict
        The graph of the object dependency

    Returns
    -------
    list
        All the leaves from a given graph
    """
    leaves = []
    processing_nodes = Queue()
    for kid in graph['CHILDREN']:
      processing_nodes.put(kid)
    
    while not processing_nodes.empty():
      node = processing_nodes.get()
      if len(node['CHILDREN']) == 0:
        leaves.append(node)
      else:
        for kid in node['CHILDREN']:
          processing_nodes.put(kid)

    return leaves

  def _get_top_k_biggest_leaves(self, lst_objects, k):
    """
    Sort a list of objects and return the biggest ones

    Parameters
    ----------
    lst_objects : list
        a list of objects that have a key `SIZE`
    k : int
        the max number of elements returned

    Returns
    -------
    list
        The top k biggest objects, sorted
    """
    sorted_objects = sorted(lst_objects, key=lambda d: d['SIZE'], reverse=True)
    return sorted_objects[:k]

  def _get_path_to_leaf(self, obj):
    """
    Returns the path from the graphs root to this node

    Parameters
    ----------
    obj : dict
        A node in the graph

    Returns
    -------
    list
        The path from the root to the current node
    """
    path = []
    while obj is not None and 'NAME' in obj:
      path.append({
        'NAME': obj['NAME'],
        'SIZE': obj['SIZE']
      })
      obj = obj['PARENT']
    
    path.reverse()
    return path
  
  def get_obj_size_issues(self, lst_obj_size_result, topk=3, MB=True):
    """
    Returns the top k paths from the generated memory tree with worst memory loads

    Parameters
    ----------
    lst_obj_size_result : list
      list resulted from a `get_obj_size` call.
      
    topk : int, optional
      Get biggest `topk` memory consumers. The default is 3.
      
    MB : bool, optional
      Return values in MB or bytes. Default MB  
  

    Returns
    -------
    None.
    
    
    Example
    -------
    
      > lst_tree = get_obj_size(orchestrator)
      > get_obj_size_issues(lst_tree, topk=2, MB=True)
      [
        [{"orchestrator" : 5.11}, {"monitor": 4.20}, {"box-32" : 4.02}, {"hearbeatsbuff" : 3.91}, {"_deque" : 3.89}],
        [{"orchestrator" : 5.11}, {"bizman": 0.71}, {"plugins" : 0.69}, {"plugin-instance-1" : 0.69}, {"buffer" : 0.69}],
      ]

    """
    
    graph = self._get_obj_size_graph(lst_obj_size_result)
    leaves = self._get_graph_leaves(graph)
    topk_leaves = self._get_top_k_biggest_leaves(leaves, topk)
    result = [self._get_path_to_leaf(l) for l in topk_leaves]
    if MB:
      for path in result:
        for obj in path:
          obj['SIZE'] = float(f"{(obj['SIZE'] / 1_048_576):.02f}")

    return result

  def _obsolete_get_obj_size(self, obj, return_tree=False, excluded_obj_props=[], exclude_obj_props_like=[], as_list=True):
    """
    Recursively (dfs) finds size of objects
    
    obj: anything
      this is the root object
      
      
    return_tree:
      returns the whole object tree
    
    ======= 
    returns:
      the tree size 
      
    usage:
      
      ...
      objA = Class1()
      objB = Class2(owner=objA) # some var contain objA in objB
      
      # simple usage
      sizeObjB = log.get_obj_size(objB) # this includes size of objA
      
      ...      
    
    Observation: 
      quick implementation of multi-level dict results in mem exceptions
      TODO: try a better algo
    
    """
    self._obj_tree = OrderedDict()
    self._obj_level = 0
    with self.managed_lock_resource('get_obj_size'):
      try:
        result = self._helper_get_obj_size(
          obj=obj, 
          name='Base: {}'.format(obj.__class__.__name__),
          excluded_obj_props=excluded_obj_props,
          exclude_obj_props_like=exclude_obj_props_like,
        )  
        if return_tree:
          if as_list:
            tree = [v for k,v in self._obj_tree.items()]
          else:
            tree = self._obj_tree
          result = result, tree
          self._obj_tree = None
      except:
        result = 0
    return result
    
    
  def _helper_get_obj_size(self, obj, name='unk', excluded_obj_props=[], exclude_obj_props_like=[]):
    EXCLUDED_TYPES = (
      str, bytes, bytearray, np.ndarray,
    )
    EXCLUDED_STRINGS = [
      'lock', 'mappingproxy', 'Thread',
    ]
    size = 0
    obj_id = id(obj)
    if obj_id in self._obj_tree or obj_id == id(self._obj_tree):
      return 0
    
    size = sys.getsizeof(obj)
    
    self._obj_level += 1
    self._obj_tree[obj_id] = {
      'NAME'   : name,
      'SIZE'   : size,
      'CLASS'  : obj.__class__.__name__,
      'LEVEL'  : self._obj_level,
    }
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    if isinstance(obj, EXCLUDED_TYPES) or obj.__class__.__name__ in EXCLUDED_STRINGS:
      # we do not want to go deeper in these objects... yet
      pass
    elif obj.__class__.__name__ == 'Tensor':
      if str(obj.device) == 'cpu':
        size += obj.nelement() * obj.element_size()
    elif isinstance(obj, dict):
      keys = list(obj.keys())
      # add just the values
      size += sum([self._helper_get_obj_size(obj=obj[k], name=str(k)) for k in keys])
    elif isinstance(obj, (list, deque)) and len(obj) > 0 and isinstance(obj[0], (int, float)) and isinstance(obj[-1], (int, float)):
      size += (len(obj) * ((sys.getsizeof(obj[0]) + sys.getsizeof(obj[-1])) / 2))
    elif hasattr(obj, '__dict__'): # this is a object
      # we take all the properties of the object
      keys = list(obj.__dict__.keys())
      # add just the values
      for obj_prop in keys:
        excluded = obj_prop in excluded_obj_props
        excluded = excluded or any([x in obj_prop for x in exclude_obj_props_like])        
        if not excluded:
          size += self._helper_get_obj_size(
            obj=obj.__dict__[obj_prop], 
            name=str(obj_prop),
            excluded_obj_props=excluded_obj_props,
            )
    elif hasattr(obj, '__iter__'):
      try:
        temp_size = len(obj)
        temp_list = list(obj)
        size += sum([self._helper_get_obj_size(temp_list[i]) for i in range(temp_size)])
      except Exception as e:
        with open(os.path.join(self.get_data_folder(), 'obj_tree_error.txt'), 'wt') as fh:
          for k,v in self._obj_tree.items():
            fh.write('\n{}'.format(v))
        print('Except:\n{}'.format(traceback.format_exc()))
    if obj_id in self._obj_tree:
      self._obj_tree[obj_id]['SIZE'] = size
    self._obj_level -= 1
    return size 


  def get_obj_size(
      self, 
      obj, 
      name='<root>', 
      level=0, 
      top_consumers=40, 
      return_tree=False,
      excluded_obj_props=[], 
      exclude_obj_props_like=[],
    ):
    """
    Calculate the memory footprint of an object, and its sub-objects, and generate info about the object.
  
    Parameters
    ----------
    obj : any
        The object to calculate the memory footprint of.
        
    name : str, optional
        The name of the object, by default '<root>'.
        
    level : int, optional
        The nesting level of the object, by default 0.
        
    top_consumers : int, optional
        Nr of top memory consumers (above level 2)
  
    Returns
    -------
    int
        Memory size in bytes
    
    list of dict
        A list of dictionaries with information about each object visited during the search. 
        Each dictionary includes the object's name, class name, nesting level, own size, total size, and maximum child level.
        
    list of dict
        A list of the top 5 biggest objects that don't have more than 2 nested levels below them.
  
    Notes
    -----
    This function ignores objects of certain types for performance reasons (e.g., str, bytes, bytearray, np.ndarray), 
    and also objects of certain classes (e.g., 'lock', 'mappingproxy', 'Thread').
    """
    with self.managed_lock_resource('get_obj_size'):
      
      EXCLUDED_TYPES = (
        str, bytes, bytearray, np.ndarray,
      )
      EXCLUDED_STRINGS = [
        'lock', 'mappingproxy', 'Thread',
      ]
        
      root_id = id(obj)
    
      # Stack for DFS traversal of object's attributes and 
      # post-order processing (children before parents)
      stack = [(obj, name, level, root_id, False)]
    
      # Info about each object, indexed by object id
      objects_info = OrderedDict()
    
      # Children objects for each object, indexed by object id
      children = defaultdict(list)
      
      total_mem = 0
      
      while stack:
        obj, name, level, obj_id, processed = stack.pop()
    
        if processed:
          # All children have been processed, compute total size
          total_size = objects_info[obj_id]['OBJ_SIZE'] + sum(objects_info[child]['SIZE'] for child in children[obj_id])
          objects_info[obj_id]['SIZE'] = total_size
        else:
          class_name = obj.__class__.__name__
    
          obj_size = 0
          if class_name == 'Tensor':
            if hasattr(obj, 'device') and str(obj.device) == 'cpu':
              obj_size = obj.nelement() * obj.element_size()
          else:
            obj_size = sys.getsizeof(obj)
          
          total_mem += obj_size
    
          # Store the object's info
          objects_info[obj_id] = {
            'NAME': name,
            'CLASS_NAME': obj.__class__.__name__,
            'LEVEL': level,
            'OBJ_SIZE': obj_size,
            'SIZE': 0  # Will be updated later
          }
    
          # Add this node back to the stack for post-order processing
          stack.append((obj, name, level, obj_id, True))
    
          if class_name not in EXCLUDED_STRINGS and not isinstance(obj, EXCLUDED_TYPES):
            new_objects = []
    
            if hasattr(obj, '__dict__'):
              prop_list = list(obj.__dict__.keys())
              for attr_name in prop_list:
                excluded = attr_name in excluded_obj_props
                excluded = excluded or any([x in attr_name for x in exclude_obj_props_like])        
                if not excluded:
                  attr_value = obj.__dict__[attr_name]
                  new_objects.append((attr_value, f'{name}.{attr_name}'))
              #endfor
            elif isinstance(obj, (list, tuple, set, deque)):
              list_obj = list(obj)
              obj_len = len(list_obj)
              for i in range(obj_len):
                item = list_obj[i]
                new_objects.append((item, f'{name}[{i}]'))
              #endfor
            elif isinstance(obj, dict):
              key_list = list(obj.keys())
              for k in key_list:
                v = obj[k]
                new_objects.append((v, f'{name}["{k}"]'))
              #endfor  
            for new_obj, new_name in new_objects:
              new_id = id(new_obj)
              if new_id not in objects_info:
                stack.append((new_obj, new_name, level + 1, new_id, False))
                children[obj_id].append(new_id)
            #endfor
    
          #endif type checking
        #endif processed checking
      #endwhile DFS

    
      # Compute the total memory of the root object
      root_object_total_memory = objects_info[root_id]['SIZE']

      
      if total_size != root_object_total_memory:
        self.P("WARNING: MEMORY CALCULATION INCONSISTENCY!", color='r')
    
      if return_tree:
        # List of objects info
        objects_info_list = [
          x for x in objects_info.values() if x['CLASS_NAME'] not in ['str', 'int', 'float']]
    
        # Filter objects that have at most two levels of objects beneath them and get the top 5 biggest ones
        top_5_objects = sorted(
          [info for obj_id, info in objects_info.items() if info['LEVEL'] >= 2],
          key=lambda x: x['SIZE'],
          reverse=True
        )[:top_consumers]
    # endwith lock
    
    if return_tree:
      result = root_object_total_memory, objects_info_list, top_5_objects
    else:
      result = total_mem
    return result


  @staticmethod
  def find_documentation(class_name, *args):
    # setup the environment
    old_stdout = sys.stdout
    sys.stdout = TextIOWrapper(BytesIO(), sys.stdout.encoding)
    # write to stdout or stdout.buffer
    help(class_name)
    # get output
    sys.stdout.seek(0)  # jump to the start
    out = sys.stdout.read()  # read output
    # restore stdout
    sys.stdout.close()
    sys.stdout = old_stdout

    out_splitted = out.split('\n')
    filtered_doc = list(filter(lambda x: all([_str in x for _str in args]),
                               out_splitted))

    return filtered_doc

  @staticmethod
  def common_start(*args):
    """ returns the longest common substring from the beginning of passed `args` """

    def _iter():
      for t in zip(*args):
        s = set(t)
        if len(s) == 1:
          yield list(s)[0]
        else:
          return

    return ''.join(_iter())

  @staticmethod
  def distance_euclidean(np_x, np_y):
    return np.sqrt(np.sum((np_x - np_y) ** 2, axis=1))

  @staticmethod
  def code_version(lst_dirs=['.'], lst_exclude=[]):
    import re
    import pandas as pd
    from pandas.util import hash_pandas_object
    from pathlib import Path

    assert len(lst_dirs) > 0
    assert all([os.path.isdir(x) for x in lst_dirs])
    assert all([os.path.isdir(x) for x in lst_exclude])
    dct_temp = {}
    dct = {'FILE': [], 'VER': []}
    for d in lst_dirs:
      for orig_file in Path(d).rglob('**/*.py'):
        try:
          orig_file = str(orig_file)
          if any([x in orig_file for x in lst_exclude]):
            continue
          # endif
          file = orig_file
          file_ver = '{}_ver'.format(re.sub(r'[^\w\s]', '', file))
          for x in ['/', '\\']:
            file = file.replace(x, '.')
          file = file.replace('.py', '')
          for key in ['__version__', '__VER__']:
            try:
              cmd = 'from {} import {} as {}'.format(file, key, file_ver)
              exec(cmd, dct_temp)
            except:
              pass
              # endfor

          if file_ver in dct_temp:
            dct['FILE'].append(orig_file)
            dct['VER'].append(dct_temp[file_ver])
          # endif
        except Exception as e:
          pass
      # endfor
    # endfor
    df = pd.DataFrame(dct).sort_values('FILE').reset_index(drop=True)
    return df, hex(hash_pandas_object(df).sum())

  @staticmethod
  def natural_sort(l):
    import re
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)

  @staticmethod
  def hash_object(obj, size=None):
    """
    Uses md5 to get the hash of any pickleable object

    Parameters:
    -----------
    obj : any pickleable object, mandatory

    Returns:
    ---------
    md5 hash : str

    """
    p = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
    result = hashlib.md5(p).hexdigest()
    return result if size is None else result[:size]
  
  
  @staticmethod
  def get_uid(size=8):
    """
    Uses uuid4 to generate a unique ID and extract part of the id
    """
    from uuid import uuid4
    str_id = str(uuid4())
    str_id = str_id.replace('-','')
    return str_id[:size]
    


  @staticmethod
  def shorten_name(s):
    return _UtilsMixin.name_abbreviation(s)


  @staticmethod
  def name_abbreviation(s):
    name_split = []
    if '_' not in s:
      # try to split by uppercase - for example VideoStream should become ["VIDEO", "STREAM"]
      name_split = re.findall('[A-Z][a-z]*', s)
      name_split = [x.upper() for x in name_split]
    #endif

    name_split = name_split or s.upper().split('_')
    prefix = name_split[0][:2]
    if len(name_split) < 2:
      pass
    elif len(name_split) < 3:
      prefix += name_split[1][:2]
    else:
      lst = []
      for i in range(1, len(name_split)):
        if name_split[i].isdigit():
          lst.append(name_split[i][:2])
        else:
          lst.append(name_split[i][:1])
      #endfor
      prefix += ''.join(lst)
    #endif
    return prefix
  
  @staticmethod
  def get_short_name(s):
    return _UtilsMixin.name_abbreviation(s)
    
  
