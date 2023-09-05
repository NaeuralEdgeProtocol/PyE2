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

# from core import constants as ct


from ..io_formatter import consts as ct
from ..io_formatter.mixins import _PluginsManagerMixin


class IOFormatterWrapper(_PluginsManagerMixin):

  def __init__(self, log, **kwargs):
    super(IOFormatterWrapper, self).__init__()
    self._dct_formatters = {}
    self.log = log
    return

  def _get_plugin_class(self, name):
    _module_name, _class_name, _class_def, _class_config = self._get_module_name_and_class(
        locations=ct.PLUGIN_SEARCH.LOC_IO_FORMATTER_PLUGINS,
        name=name,
        suffix=ct.PLUGIN_SEARCH.SUFFIX_IO_FORMATTER_PLUGINS,
        safe_locations=ct.PLUGIN_SEARCH.LOC_SAFE_FORMATTER_PLUGINS,
    )

    if _class_def is None:
      msg = "Error loading io_formatter plugin '{}'".format(name)
      self.D(msg, color='r')
      # self._create_notification(
      #     notif=ct.STATUS_TYPE.STATUS_EXCEPTION,
      #     msg=msg,
      #     info="No code/script defined for io_formatter plugin '{}' in {}".format(
      #         name, ct.PLUGIN_SEARCH.LOC_IO_FORMATTER_PLUGINS)
      # )
    # endif

    return _class_def

  def formatter_ready(self, name):
    return name in self._dct_formatters

  def get_formatter_by_name(self, name):
    if name not in self._dct_formatters:
      self._create_formatter(name)
    formatter = self._dct_formatters.get(name)
    return formatter

  def _create_formatter(self, name):
    self.D("Creating formatter '{}'".format(name))
    _cls = self._get_plugin_class(name)

    try:
      formatter = _cls(log=self.log, signature=name.lower())
    except Exception as exc:
      msg = "Exception '{}' when initializing io_formatter plugin {}".format(
          exc, name)
      self.D(msg, color='r')
      # self._create_notification(
      #     notif=ct.STATUS_TYPE.STATUS_EXCEPTION,
      #     msg=msg,
      #     autocomplete_info=True
      # )
      raise exc
    # end try-except

    self._dct_formatters[name] = formatter
    self.D("Successfully created IO formatter {}.".format(name))
    return formatter

  def _get_formatter_name_from_payload(self, msg):
    return msg.get(ct.PAYLOAD_DATA.EE_FORMATTER, msg.get(ct.PAYLOAD_DATA.SB_IMPLEMENTATION, ''))

  def get_required_formatter_from_payload(self, payload):
    name = self._get_formatter_name_from_payload(payload)
    formatter = None
    if name is not None and name != '':
      if not self.formatter_ready(name):
        msg = "Creating formatter '{}' for decoding message originating <{}:{}>".format(
            name,
            payload.get(ct.PAYLOAD_DATA.INITIATOR_ID),
            payload.get(ct.PAYLOAD_DATA.SESSION_ID)
        )
        self.D(msg)
        if False:
          # debug log the payload in question
          self.D(self.log.dict_pretty_format(payload))
      formatter = self.get_formatter_by_name(name)
    return formatter

  def D(self, *args, **kwargs):
    return self.log.D(*args, **kwargs)

  def P(self, *args, **kwargs):
    return self.log.P(*args, **kwargs)
