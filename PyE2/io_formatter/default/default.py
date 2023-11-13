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

# local dependencies
from ...io_formatter.base import BaseFormatter


class DefaultFormatter(BaseFormatter):

  def __init__(self, log, **kwargs):
    super(DefaultFormatter, self).__init__(
        log=log, prefix_log='[DEFAULT-FMT]', **kwargs)
    return

  def startup(self):
    pass

  def _encode_output(self, output):
    return output

  def _decode_output(self, encoded_output):
    return encoded_output

  def _decode_streams(self, dct_config_streams):
    return dct_config_streams
