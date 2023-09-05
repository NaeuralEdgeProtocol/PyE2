"""
Copyright 2019-2023 Lummetry.AI (Knowledge Investment Group SRL). All Rights Reserved.


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
@author: Lummetry.AI - Stefan Saraev
@project: 
@description:
"""


class PLUGIN_SEARCH:
  LOC_IO_FORMATTER_PLUGINS = ['pyE2.PyE2.io_formatter.default',
                              'pyE2.io_formatter.default',
                              'pye2.PyE2.io_formatter.default',
                              'pye2.io_formatter.default',
                              'PyE2.PyE2.io_formatter.default',
                              'PyE2.io_formatter.default']  # maybe include 'io_formatter.default'
  SUFFIX_IO_FORMATTER_PLUGINS = 'Formatter'
  LOC_SAFE_FORMATTER_PLUGINS = []


class PAYLOAD_DATA:
  INITIATOR_ID = 'INITIATOR_ID'
  SESSION_ID = 'SESSION_ID'
  EE_FORMATTER = 'EE_FORMATTER'
  SB_IMPLEMENTATION = 'SB_IMPLEMENTATION'


class FORMATTER_DATA:
  NAME = 'NAME'
  SIGNATURE = 'SIGNATURE'
  STREAM = 'STREAM'
  ID = 'ID'  # ??
  DESCRIPTION = 'DESCRIPTION'
  PLUGIN_INSTANCE_PARAMETER_LIST = 'PLUGIN_INSTANCE_PARAMETER_LIST'
