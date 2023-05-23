"""
Copyright 2019-2022 Lummetry.AI (Knowledge Investment Group SRL). All Rights Reserved.


* NOTICE:  All information contained herein is, and remains
* the property of Knowledge Investment Group SRL.  
* The intellectual and technical concepts contained
* herein are proprietary to Knowledge Investment Group SRL
* and may be covered by Romanian and Foreign Patents,
* patents in process, and are protected by trade secret or copyright law.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Knowledge Investment Group SRL.


@copyright: Lummetry.AI
@author: Lummetry.AI - Laurentiu
@project: 
@description:
"""

import os
import inspect
import importlib
import traceback

from pkgutil import iter_modules

from copy import deepcopy

from ...const import payload as ct


class _PluginsManagerMixin:

  def __init__(self):
    super(_PluginsManagerMixin, self).__init__()
    return

  def _get_plugin_by_name(self, lst_plugins_locations, name):
    name = self.log.camel_to_snake(name)
    for loc in lst_plugins_locations:
      candidate = loc + '.' + name
      self.D("    Trying '{}'".format(candidate))
      try:
        found = importlib.util.find_spec(candidate)
        if found is not None:
          return candidate
      except:
        self.D("      Invalid package: '{}'".format(candidate))
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
        _safe_module_name = self._get_plugin_by_name(safe_locations, simple_name)

    if safe_imports is not None and not isinstance(safe_imports, list):
      safe_imports = [safe_imports]

    # not a safe module so we search in normal locations
    if _safe_module_name is None:
      _user_module_name = self._get_plugin_by_name(locations, simple_name)
      _module_name = _user_module_name
    else:
      is_safe_plugin = True
      _module_name = _safe_module_name

    if _module_name is None:
      if verbose >= 1:
        self.P("Error with finding plugin '{}' in locations '{}'".format(simple_name, locations), color='r')
      return _module_name, _class_name, _cls_def, _config_dict

    self.D("  Found {} plugin '{}'".format(
        'safe' if is_safe_plugin else 'user', name),
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
          self.P("ERROR: Could not find class match for {}. Available classes are: {}".format(
              simple_name, [x[0] for x in classes]
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
      self.D("  Plugin '{}' loaded and code checked from {}".format(name, _found_location), color='g')
    except:
      str_err = traceback.format_exc()
      msg = "Error preparing {} with module {}:\n{}".format(
          name, _module_name, str_err)
      self.P(msg, color='error')

    return module, _class_name, _cls_def, _config_dict
