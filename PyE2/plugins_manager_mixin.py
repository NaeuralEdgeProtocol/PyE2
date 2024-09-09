import os
import inspect
import importlib
import sys
import traceback

from pkgutil import iter_modules

from copy import deepcopy

from .code_cheker.base import BaseCodeChecker

class _PluginsManagerMixin:

  def __init__(self):
    super(_PluginsManagerMixin, self).__init__()
    self.code_checker = BaseCodeChecker()
    return
  
  @property
  def is_secured(self):
    val = self.log.config_data.get("SECURED", False)
    return val in [True, 'True', 'true', '1', 1]

  def __get_avail_plugins(self, locations, debug=True):
    """
    WARNING: This function is deprecated and should not be used. Now `_get_plugin_by_name` will 
             works without this helper function.
             
             The function has been changed from protected to private and should NOT be used. Was
             left here only for documentation purposes
    """
    if not isinstance(locations, list):
      locations = [locations]    
    names, modules = [], []
    for plugins_location in locations:
      path = plugins_location.replace('.', '/')
      if False:
        # if we use path-based search we will have a big issue with compiled modules!
        path = os.path.join(self.log.code_base_folder, path) # code base can be in another folder !
        if not os.path.isdir(path):
          self.P("*** attemped to search for plugins in a invalid folder: {}".format(path), color='error')
          continue
        all_files = os.listdir(path)
        files = [os.path.splitext(x)[0] for x in all_files if '.py' in x and '__init__' not in x]
      else:
        found_modules = iter_modules([path])
        files = [x.name for x in found_modules]
      if debug:
        self.P("  Found {} in '{}'".format(files, path))
      modules += [plugins_location + '.' + x for x in files]
      names += [x.replace('_', '').lower() for x in files]

    return names, modules

  def get_package_base_path(self, package_name):
    """
    Return the file path of an installed package parent directory.
    
    :param package_name: The name of the installed package.
    :return: The path to the package parent.
    """
    spec = importlib.util.find_spec(package_name)
    if spec is not None and spec.submodule_search_locations:
      return os.path.dirname(spec.submodule_search_locations[0])
    else:
      self.P("Package '{}' not found.".format(package_name), color='r')
    return None

  def _get_plugin_by_name(self, lst_plugins_locations, name, search_in_packages=None, safe=False):
    name = self.log.camel_to_snake(name)

    if search_in_packages is None:
      search_in_packages = []

    total_sub_locations = []
    # First we extract all the sublocations for each package

    for package in search_in_packages:
      package_path = self.get_package_base_path(package)
      if package_path is None:
        continue

      for location in lst_plugins_locations:
        base_location_name = location.split('.')[0]
        # if the location is not in the package we skip it (locations should begin with the package name)
        # TODO: review this please
        if base_location_name != package:
          continue

        root_location = location.replace('.', os.path.sep)
        package_root_location = os.path.join(package_path, root_location)
        sub_locations = self.log.get_all_subfolders(package_root_location, as_package=True)
        sub_locations = [x.replace(package_path.replace(os.path.sep, '.').strip('.'), '').strip('.') for x in sub_locations]
        sub_locations.append(location)
        total_sub_locations += sub_locations
      # end for package locations
    # end for package

    # Then we extract all the sublocations for local files
    for location in lst_plugins_locations:
      root_location = location.replace('.', os.path.sep)
      sub_locations = self.log.get_all_subfolders(root_location, as_package=True)
      total_sub_locations += sub_locations
    # endfor local

    # we remove duplicates
    total_sub_locations = list(set(total_sub_locations))
    lst_plugins_locations = lst_plugins_locations + total_sub_locations
    for loc in lst_plugins_locations:
      if loc.endswith('__pycache__'):
        continue
      candidate = loc + '.' + name
      try:
        found = importlib.util.find_spec(candidate)
        # if found something
        # and that thing can be loaded
        if found is not None and found.loader is not None:
          self.P("    Trying {}: '{}' -> FOUND!".format("[SAFE]" if safe else "[UNSAFE]", candidate))
          return candidate
        else:
          self.P("    Trying {}: '{}' -> NOT found.".format("[SAFE]" if safe else "[UNSAFE]", candidate))
      except ModuleNotFoundError:
        self.P("      Invalid package: '{}'".format(candidate))
    return
  
    
  def _perform_module_safety_check(self, module, safe_imports=None):
    good = True
    msg = ''
    str_code = inspect.getsource(module)
    self.P("  Performing code safety check on module `{}`:".format(module.__name__), color='m')
    errors = self.code_checker.check_code_text(str_code, safe_imports=safe_imports)
    if errors is not None:      
      info = "  ERROR: Unsafe code in {}:\n{}".format(
        module.__name__, '\n'.join(
          ['  *** ' + msg + 'at line(s): {}'.format(v) for msg, v in errors.items()]
          ))
      self.P(info, color='error')
      self._create_notification(
            notif="EXCEPTION", # ct.STATUS_TYPE.STATUS_EXCEPTION, -- TODO: review & change after planning dependency tree
            msg="Unsafe code in `{}`".format(module.__name__),
            info=info,
            modulename=module.__name__,
            autocomplete_info=True,
            printed=True,
          )
      if self.is_secured:
        good = False
        msg = info
      else:
        self.P("   ********* Pluging accepted due to UNSECURED node. **************", color='error')
        good = True
    else:
      self.P("   * * * Module '{}' code check successful * * *".format(module.__name__), color='g')
    # endif bad code
    self.P("  Finished performing code safety check on module `{}`".format(module.__name__), color='m')
    return good, msg

  def _perform_class_safety_check(self, classdef):
    good = True
    msg = ''
    str_code = inspect.getsource(classdef)
    self.P("  Performing class code safety check on class `{}`".format(classdef.__name__), color='m')
    ### TODO: finish code analysis using BaseCodeChecker
    self.P("  Finished class code safety check on class `{}`".format(classdef.__name__), color='m')
    return good, msg

  def _get_module_name_and_class(self, 
                                 locations, 
                                 name,
                                 search_in_packages=None,
                                 suffix=None, 
                                 verbose=1, 
                                 safety_check=False, 
                                 safe_locations=None, 
                                 safe_imports=None,
                                 class_safety_check=False,                                  
                                 ):
    if not isinstance(locations, list):
      locations = [locations]
      

    _class_name, _cls_def, _config_dict = None, None, None
    simple_name = name.replace('_','')

    if suffix is None:
      suffix = ''

    suffix = suffix.replace('_', '')
        
    _safe_module_name = None
    is_safe_plugin = False
    # first search is safe locations always!
    if safe_locations is not None:
      if not isinstance(safe_locations, list):
        safe_locations = [safe_locations]
      if len(safe_locations) > 0:
        _safe_module_name = self._get_plugin_by_name(safe_locations, name, search_in_packages=search_in_packages, safe=True)
        
    if safe_imports is not None and not isinstance(safe_imports, list):
      safe_imports = [safe_imports]
    
    # not a safe module so we search in normal locations
    if _safe_module_name is None:
      # in packages you should have only safe locations
      _user_module_name = self._get_plugin_by_name(locations, name, search_in_packages=None, safe=False)
      _module_name = _user_module_name
    else:
      is_safe_plugin = True 
      _module_name = _safe_module_name
    
    
    if _module_name is None:
      if verbose >= 1:
        self.P("Error with finding plugin '{}' in locations '{}'".format(name, locations), color='r')
      return _module_name, _class_name, _cls_def, _config_dict

    self.P("  Found {} plugin '{}'".format(
      'safe' if is_safe_plugin else 'user', _module_name), 
      color='g' if is_safe_plugin else 'm'
    )
    
    safety_check = False if is_safe_plugin else safety_check
    class_safety_check = False if is_safe_plugin else class_safety_check

    module = None
    try:
      if _module_name in sys.modules:
        del sys.modules[_module_name]
      module = importlib.import_module(_module_name)
      if module is not None and safety_check:
        is_good, msg = self._perform_module_safety_check(module, safe_imports=safe_imports)
        if not is_good:
          err_msg = "CODE SAFETY VIOLATION: {}".format(msg)
          raise ValueError(err_msg)
      classes = inspect.getmembers(module, inspect.isclass)
      for _cls in classes:
        if _cls[0].upper() == simple_name.upper() + suffix.upper():
          _class_name, _cls_def = _cls
      if _class_name is None:
        if verbose >= 1:
          self.P("ERROR: Could not find class match for {} (suffix: {}). Available classes are: {}".format(
            simple_name, suffix, [x[0] for x in classes]
          ), color='r')
      _config_dict_from_file = getattr(module, "_CONFIG", {})
      _version = getattr(module, "__VER__", None) or getattr(module, "__VER__", None)
      _version = _version or "0.0.0"
      # incredibly enough if we do not deepcopy somehow data will be overriden and
      # used in subsequent imports: basically the module remains in the memory
      # and the changed dict will be created at subsequent importlib.import !
      # change below to False to replicate issue !
      if isinstance(_config_dict_from_file, dict) and True: 
        _config_dict = deepcopy(_config_dict_from_file)
      else:
        _config_dict = _config_dict_from_file
      
      _config_dict['MODULE_VERSION'] = _version # added module version if available to the config dict
        
      if _cls_def is not None and class_safety_check:
        is_good, msg = self._perform_class_safety_check(_cls_def)
        if not is_good:
          raise ValueError("Unsafe class code exception: {}".format(msg))     
      _found_location = ".".join(_module_name.split('.')[:-1])
      self.P("  Plugin '{}' loaded and code checked from {}".format(name, _found_location), color='g')
    except:
      str_err = traceback.format_exc()
      msg = "Error preparing {} with module {}:\n{}".format(
        name, _module_name, str_err)
      self.P(msg, color='error')
      module, _class_name, _cls_def, _config_dict = None, None, None, None

    return module, _class_name, _cls_def, _config_dict
