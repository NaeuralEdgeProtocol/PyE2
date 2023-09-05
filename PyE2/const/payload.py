# -*- coding: utf-8 -*-
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
@author: Lummetry.AI - AID
@project: Execution Engine
@description:
Created on Sat Oct 15 10:01:35 2022

"""

from ..io_formatter import consts as lib_io_formatter_ct

TLBR_POS = 'TLBR_POS'
PROB_PRC = 'PROB_PRC'
TYPE = 'TYPE'

NOTIFICATION_TYPE = 'NOTIFICATION_TYPE'
STATUS_TYPE_KEY = NOTIFICATION_TYPE

# Notification types


class STATUS_TYPE:
  STATUS_NORMAL = 'NORMAL'
  STATUS_EXCEPTION = 'EXCEPTION'
  STATUS_EMAIL = 'EMAIL'
  STATUS_ABNORMAL_FUNCTIONING = 'ABNORMAL FUNCTIONING'


class NOTIFICATION_CODES:
  PIPELINE_OK = 1
  PLUGIN_OK = 2

  PIPELINE_FAILED = -1
  PLUGIN_FAILED = -2


class COMMANDS:
  COMMANDS = 'COMMANDS'
  RESTART = 'RESTART'
  STATUS = 'STATUS'
  STOP = 'STOP'
  UPDATE_CONFIG = 'UPDATE_CONFIG'
  DELETE_CONFIG = 'DELETE_CONFIG'
  UPDATE_PIPELINE_INSTANCE = 'UPDATE_PIPELINE_INSTANCE'
  ARCHIVE_CONFIG = 'ARCHIVE_CONFIG'
  DELETE_CONFIG_ALL = 'DELETE_CONFIG_ALL'
  ARCHIVE_CONFIG_ALL = 'ARCHIVE_CONFIG_ALL'
  ACTIVE_PLUGINS = 'ACTIVE_PLUGINS'
  RELOAD_CONFIG_FROM_DISK = 'RELOAD_CONFIG_FROM_DISK'
  FULL_HEARTBEAT = 'FULL_HEARTBEAT'
  TIMERS_ONLY_HEARTBEAT = 'TIMERS_ONLY_HEARTBEAT'
  SIMPLE_HEARTBEAT = 'SIMPLE_HEARTBEAT'

  FINISH_ACQUISITION = 'FINISH_ACQUISITION'


class PAYLOAD_DATA:
  INITIATOR_ID = lib_io_formatter_ct.PAYLOAD_DATA.INITIATOR_ID
  SESSION_ID = lib_io_formatter_ct.PAYLOAD_DATA.SESSION_ID
  STREAM_NAME = 'STREAM_NAME'
  NAME = 'NAME'
  INSTANCE_CONFIG = 'INSTANCE_CONFIG'
  SIGNATURE = 'SIGNATURE'
  INSTANCE_ID = 'INSTANCE_ID'
  TIME = 'TIME'
  EE_TIMESTAMP = 'EE_TIMESTAMP'
  EE_TIMEZONE = 'EE_TIMEZONE'
  EE_TZ = 'EE_TZ'
  SB_TIMESTAMP = EE_TIMESTAMP
  EE_MESSAGE_ID = 'EE_MESSAGE_ID'
  SB_MESSAGE_ID = EE_MESSAGE_ID
  EE_TOTAL_MESSAGES = 'EE_TOTAL_MESSAGES'
  SB_TOTAL_MESSAGES = EE_TOTAL_MESSAGES
  EE_FORMATTER = lib_io_formatter_ct.PAYLOAD_DATA.EE_FORMATTER
  SB_IMPLEMENTATION = lib_io_formatter_ct.PAYLOAD_DATA.SB_IMPLEMENTATION
  EE_EVENT_TYPE = 'EE_EVENT_TYPE'
  SB_EVENT_TYPE = 'SB_EVENT_TYPE'
  EE_PAYLOAD_PATH = 'EE_PAYLOAD_PATH'

  NOTIFICATION = 'NOTIFICATION'
  INFO = 'INFO'

  TAGS = 'TAGS'

  ID_TAGS = 'ID_TAGS'
