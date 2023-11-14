"""
Copyright (C) 2017-2021 Andrei Damian, andrei.damian@me.com,  All rights reserved.

This software and its associated documentation are the exclusive property of the creator. 
Unauthorized use, copying, or distribution of this software, or any portion thereof, 
is strictly prohibited.

Parts of this software are licensed and used in software developed by Knowledge Investment Group SRL.
Any software proprietary to Knowledge Investment Group SRL is covered by Romanian and  Foreign Patents, 
patents in process, and are protected by trade secret or copyright law.

Dissemination of this information or reproduction of this material is strictly forbidden unless prior 
written permission from the author.

"""

import os
import inspect
import importlib
import traceback

from pkgutil import iter_modules

from copy import deepcopy


class _PluginsManagerMixin:

  def __init__(self):
    super(_PluginsManagerMixin, self).__init__()
    return

  @property
  def is_secured(self):
    return self.log.config_data.get("SECURED", False)

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
        path = os.path.join(self.log.code_base_folder, path)  # code base can be in another folder !
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

  def _get_plugin_by_name(self, lst_plugins_locations, name, safe=False):
    name = self.log.camel_to_snake(name)
    # the root location is supposed to be the first position in the list
    root_location = lst_plugins_locations[0].replace('.', '/')
    sub_locations = self.log.get_all_subfolders(root_location, as_package=True)
    lst_plugins_locations = sub_locations + lst_plugins_locations
    for loc in lst_plugins_locations:
      candidate = loc + '.' + name
      try:
        found = importlib.util.find_spec(candidate)
        if found is not None:
          self.P("    Trying {}: '{}' -> FOUND!".format("[SAFE]" if safe else "[UNSAFE]", candidate))
          return candidate
        else:
          self.P("    Trying {}: '{}' -> NOT found.".format("[SAFE]" if safe else "[UNSAFE]", candidate))
      except ModuleNotFoundError:
        self.P("      Invalid package: '{}'".format(candidate))
    return

  def _get_module_name_and_class(self,
                                 locations,
                                 name,
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
    simple_name = name.replace('_', '')

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
        _safe_module_name = self._get_plugin_by_name(safe_locations, name, safe=True)

    if safe_imports is not None and not isinstance(safe_imports, list):
      safe_imports = [safe_imports]

    # not a safe module so we search in normal locations
    if _safe_module_name is None:
      _user_module_name = self._get_plugin_by_name(locations, name, safe=False)
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
      module = importlib.import_module(_module_name)
      classes = inspect.getmembers(module, inspect.isclass)
      for _cls in classes:
        if _cls[0].upper() == simple_name.upper() + suffix.upper():
          _class_name, _cls_def = _cls
      if _class_name is None:
        if verbose >= 1:
          self.P("ERROR: Could not find class match for {} (suffix: {}). Available classes are: {}".format(
            simple_name, suffix, [x[0] for x in classes]
          ), color='r')
      _config_dict_from_file = getattr(module, "_CONFIG", None)
      # incredibly enough if we do not deepcopy somehow data will be overriden and
      # used in subsequent imports: basically the module remains in the memory
      # and the changed dict will be created at subsequent importlib.import !
      # change below to False to replicate issue !
      if isinstance(_config_dict_from_file, dict) and True:
        _config_dict = deepcopy(_config_dict_from_file)
      else:
        _config_dict = _config_dict_from_file

      _found_location = ".".join(_module_name.split('.')[:-1])
      self.P("  Plugin '{}' loaded and code checked from {}".format(name, _found_location), color='g')
    except:
      str_err = traceback.format_exc()
      msg = "Error preparing {} with module {}:\n{}".format(
        name, _module_name, str_err)
      self.P(msg, color='error')
      module, _class_name, _cls_def, _config_dict = None, None, None, None

    return module, _class_name, _cls_def, _config_dict
