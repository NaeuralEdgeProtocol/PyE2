try:
  from libraries import _PluginsManagerMixin
except:
  # we run this without libraries
  from .plugins_manager_mixin import _PluginsManagerMixin
  pass
