from time import time

from ..plugins_manager_mixin import _PluginsManagerMixin
from ..const import PAYLOAD_DATA
from ..io_formatter.default import Aixp1Formatter, Cavi2Formatter, DefaultFormatter


class IOFormatterWrapper(_PluginsManagerMixin):
  FORMATTER_CLASSES = [DefaultFormatter, Cavi2Formatter, Aixp1Formatter]

  def __init__(self, log, plugin_search_locations=['plugins.io_formatters'], plugin_search_suffix='Formatter', **kwargs):
    super(IOFormatterWrapper, self).__init__()
    self._dct_formatters = {}
    self.log = log
    self.plugin_search_locations = plugin_search_locations
    self.plugin_search_suffix = plugin_search_suffix

    self._last_search_invalid_formatter = {}

    self.__init_formatters()
    return

  def __init_formatters(self):
    formatter_names_and_classes = [(cls.__name__.lower().split('formatter')[0], cls) for cls in self.FORMATTER_CLASSES]
    for formatter_name, formatter_class in formatter_names_and_classes:
      try:
        self._dct_formatters[formatter_name] = formatter_class(log=self.log, signature=formatter_name)
        self.D("Successfully created IO formatter {}.".format(formatter_name))
      except Exception as exc:
        msg = "Exception '{}' when initializing io_formatter plugin {}".format(exc, formatter_name)
        self.P(msg, color='r')

    return

  def _get_formatter_name_from_payload(self, msg):
    return msg.get(PAYLOAD_DATA.EE_FORMATTER, msg.get(PAYLOAD_DATA.SB_IMPLEMENTATION, ''))

  def _get_plugin_class(self, name):
    _module_name, _class_name, _class_def, _class_config = self._get_module_name_and_class(
        locations=self.plugin_search_locations,
        name=name,
        suffix=self.plugin_search_suffix,
        safe_locations=[],
    )

    if _class_def is None:
      msg = "Error loading io_formatter plugin '{}'".format(name)
      self.D(msg, color='r')
    return _class_def

  def formatter_ready(self, name):
    return name in self._dct_formatters or name is None or name == ''

  def get_formatter_by_name(self, name):
    return self._create_formatter(name)

  def _create_formatter(self, name):
    # TODO: change name to maybe_create_formatter
    if name is None or name == '':
      # check if we want to create a default formatter
      return self._dct_formatters['default']

    if name in self._dct_formatters:
      # formatter already created
      if self._dct_formatters[name] is None:
        # formatter is not available
        if name not in self._last_search_invalid_formatter:
          self._last_search_invalid_formatter[name] = 0
        if time() - self._last_search_invalid_formatter[name] < 10 * 60:
          return self._dct_formatters[name]
      else:
        return self._dct_formatters[name]
    # end if name in self._dct_formatters

    self.D("Creating formatter '{}'".format(name))
    _cls = self._get_plugin_class(name)

    formatter = None

    if _cls is not None:
      formatter = _cls(log=self.log, signature=name.lower())
      self.D("Successfully created IO formatter {}.".format(name))
    else:
      self._last_search_invalid_formatter[name] = time()
    self._dct_formatters[name] = formatter
    return formatter

  def get_required_formatter_from_payload(self, payload):
    name = self._get_formatter_name_from_payload(payload)
    return self._create_formatter(name)

  def D(self, *args, **kwargs):
    return self.log.D(*args, **kwargs)

  def P(self, *args, **kwargs):
    return self.log.P(*args, **kwargs)
