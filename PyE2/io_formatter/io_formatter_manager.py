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


from ..const import PAYLOAD_DATA
from ..io_formatter.default import Cavi2Formatter, DefaultFormatter


class IOFormatterWrapper():
  FORMATTER_CLASSES = [DefaultFormatter, Cavi2Formatter]

  def __init__(self, log, **kwargs):
    super(IOFormatterWrapper, self).__init__()
    self._dct_formatters = {}
    self.log = log

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
        self.D(msg, color='r')

    return

  def _get_formatter_name_from_payload(self, msg):
    return msg.get(PAYLOAD_DATA.EE_FORMATTER, msg.get(PAYLOAD_DATA.SB_IMPLEMENTATION, ''))

  def get_required_formatter_from_payload(self, payload):
    name = self._get_formatter_name_from_payload(payload)

    if name is None or name == '':
      # No formatter specified in payload. Using default formatter.
      return self._dct_formatters['default']

    formatter = self._dct_formatters.get(name)

    if formatter is None:
      self.P("Formatter '{}' not found in the list of available formatters.".format(name))

    return formatter

  def D(self, *args, **kwargs):
    return self.log.D(*args, **kwargs)

  def P(self, *args, **kwargs):
    return self.log.P(*args, **kwargs)
