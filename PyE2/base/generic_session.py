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
@author: Lummetry\.AI - Stefan Saraev
@project: 
@description:
"""

import json
import os
import traceback
from collections import deque
from threading import Thread
from time import sleep
from time import time as tm
from datetime import datetime as dt

from ..bc import DefaultBlockEngine
from ..const import PAYLOAD_DATA, COMMANDS, HB, STATUS_TYPE, ENVIRONMENT
from ..const import comms as comm_ct
from ..io_formatter import IOFormatterWrapper
from ..utils import load_dotenv
from ..utils.code import CodeUtils
from .logger import Logger
from .payload import Payload
from .pipeline import Pipeline

# TODO: add support for remaining commands from EE


class GenericSession(object):
  """
  A Session is a connection to a communication server which provides the channel to interact with nodes from the AiXpand network.
  A Session manages `Pipelines` and handles all messages received from the communication server.
  The Session handles all callbacks that are user-defined and passed as arguments in the API calls.  
  """
  default_config = {
      "CONFIG_CHANNEL": {
          "TOPIC": "lummetry/{}/config"
      },
      "CTRL_CHANNEL": {
          "TOPIC": "lummetry/ctrl"
      },
      "NOTIF_CHANNEL": {
          "TOPIC": "lummetry/notif"
      },
      "PAYLOADS_CHANNEL": {
          "TOPIC": "lummetry/payloads"
      },
      "QOS": 0
  }

  BLOCKCHAIN_CONFIG = {
      "PEM_FILE": "_pk_sdk.pem",
      "PASSWORD": None,
      "PEM_LOCATION": "data"
  }

  def __init__(self, *,
               host=None,
               port=None,
               user=None,
               pwd=None,
               name='pySDK',
               config={},
               filter_workers=None,
               log=None,
               on_payload=None,
               on_notification=None,
               on_heartbeat=None,
               silent=True,
               verbosity=1,
               dotenv_path=None,
               blockchain_config=BLOCKCHAIN_CONFIG,
               formatter_plugins_locations=['plugins.io_formatters'],
               **kwargs) -> None:
    """
    A Session is a connection to a communication server which provides the channel to interact with nodes from the AiXpand network.
    A Session manages `Pipelines` and handles all messages received from the communication server.
    The Session handles all callbacks that are user-defined and passed as arguments in the API calls.  

    Parameters
    ----------
    host : str, optional
        The hostname of the server. If None, it will be retrieved from the environment variable AIXP_HOSTNAME
    port : int, optional
        The port. If None, it will be retrieved from the environment variable AIXP_PORT
    user : str, optional
        The user name. If None, it will be retrieved from the environment variable AIXP_USERNAME
    pwd : str, optional
        The password. If None, it will be retrieved from the environment variable AIXP_PASSWORD
    name : str, optional
        The name of this connection, used to identify owned pipelines on a specific AiXpand node.
        The name will be used as `INITIATOR_ID` and `SESSION_ID` when communicating with AiXp nodes, by default 'pySDK'
    config : dict, optional
        Configures the names of the channels this session will connect to.
        If using a Mqtt server, these channels are in fact topics.
        Modify this if you are absolutely certain of what you are doing.
        By default {}
    filter_workers: list, optional
        If set, process the messages that come only from the nodes from this list. 
        Defaults to None
    log : Logger, optional
        A logger object which implements basic logging functionality and some other utils stuff. Can be ignored for now.
        In the future, the documentation for the Logger base class will be available and developers will be able to use
        custom-made Loggers. 
    on_payload : Callable[[Session, str, str, str, str, dict], None], optional
        Callback that handles all payloads received from this network.
        As arguments, it has a reference to this Session object, the node name, the pipeline, signature and instance, and the payload. 
        This callback acts as a default payload processor and will be called even if for a given instance
        the user has defined a specific callback.
    on_notification : Callable[[Session, str, dict], None], optional
        Callback that handles notifications received from this network. 
        As arguments, it has a reference to this Session object, the node name and the notification payload. 
        This callback acts as a default payload processor and will be called even if for a given instance
        the user has defined a specific callback.
        This callback will be called when there are notifications related to the node itself, e.g. when the node runs
        low on memory. 
        Defaults to None.
    on_heartbeat : Callable[[Session, str, dict], None], optional
        Callback that handles heartbeats received from this network.
        As arguments, it has a reference to this Session object, the node name and the heartbeat payload.
        Defaults to None.
    silent : bool, optional
        This flag will disable debug logs, set to 'False` for a more verbose log, by default True
    dotenv_path : str, optional
        Path to the .env file, by default None. If None, the path will be searched in the current working directory and in the directories of the files from the call stack.
    """
    if log is None:
      log = Logger(silent=silent, base_folder='_local_cache')

    super(GenericSession, self).__init__()

    # maybe read config from file?
    self._config = {**self.default_config, **config}
    self.log = log
    self.name = name

    self.__verbosity = verbosity

    self._verbosity = verbosity

    self._online_boxes = {}
    self._last_seen_boxes = {}
    self.online_timeout = 60
    self.filter_workers = filter_workers

    pwd = pwd or kwargs.get('password', kwargs.get('pass', None))
    user = user or kwargs.get('username', None)
    host = host or kwargs.get('hostname', None)
    self.__fill_config(host, port, user, pwd, dotenv_path)

    self.custom_on_payload = on_payload
    self.custom_on_heartbeat = on_heartbeat
    self.custom_on_notification = on_notification

    self.own_pipelines = []

    self.__running_callback_threads = False
    self.__running_main_loop_thread = False
    self.__closed_everything = False

    self.connected = False
    self.__close_pipelines = False

    self.formatter_wrapper = IOFormatterWrapper(log, plugin_search_locations=formatter_plugins_locations)

    self.sdk_main_loop_thread = Thread(target=self.__main_loop, daemon=True)

    self.__start_blockchain(blockchain_config)
    self.__create_user_callback_threads()

    self.startup()
    return

  def startup(self):
    self._connect()
    self.__start_main_loop_thread()

  # Message callbacks
  if True:
    def __create_user_callback_threads(self):
      self._payload_messages = deque()
      self._payload_thread = Thread(
        target=self.__handle_messages,
        args=(self._payload_messages, self.__on_payload),
        daemon=True
      )

      self._notif_messages = deque()
      self._notif_thread = Thread(
        target=self.__handle_messages,
        args=(self._notif_messages, self.__on_notification),
        daemon=True
      )

      self._hb_messages = deque()
      self._hb_thread = Thread(
        target=self.__handle_messages,
        args=(self._hb_messages, self.__on_heartbeat),
        daemon=True
      )

      self.__running_callback_threads = True
      self._payload_thread.start()
      self._notif_thread.start()
      self._hb_thread.start()
      return

    def __parse_message(self, dict_msg: dict):
      """
      Get the formatter from the payload and decode the message
      """
      # check if payload is encrypted
      if dict_msg.get(PAYLOAD_DATA.EE_IS_ENCRYPTED, False):
        encrypted_data = dict_msg.get(PAYLOAD_DATA.EE_ENCRYPTED_DATA, None)
        sender_addr = dict_msg.get(comm_ct.COMM_SEND_MESSAGE.K_SENDER_ADDR, None)

        str_data = self.bc_engine.decrypt(encrypted_data, sender_addr)

        if str_data is None:
          self.D("Cannot decrypt message, dropping..\n{}".format(str_data), verbosity=2)
          return None

        try:
          dict_data = json.loads(str_data)
        except Exception as e:
          self.P("Error while decrypting message: {}".format(e), color='r', verbosity=1)
          self.D("Message: {}".format(str_data), verbosity=2)
          return None

        dict_msg = {**dict_data, **dict_msg}
        dict_msg.pop(PAYLOAD_DATA.EE_ENCRYPTED_DATA, None)
      # end if encrypted

      formatter = self.formatter_wrapper \
          .get_required_formatter_from_payload(dict_msg)
      if formatter is not None:
        return formatter.decode_output(dict_msg)
      else:
        return None

    def __on_message_default_callback(self, message, message_callback) -> None:
      """
      Default callback for all messages received from the communication server.

      Parameters
      ----------
      message : str
          The message received from the communication server
      message_callback : Callable[[dict, str, str, str, str], None]
          The callback that will handle the message.
      """
      dict_msg = json.loads(message)
      # parse the message
      dict_msg_parsed = self.__parse_message(dict_msg)
      if dict_msg_parsed is None:
        return

      try:
        msg_path = dict_msg.get(PAYLOAD_DATA.EE_PAYLOAD_PATH, [None] * 4)
        msg_eeid, msg_pipeline, msg_signature, msg_instance = msg_path
      except:
        self.D("Message does not respect standard: {}".format(dict_msg), verbosity=2)
        return

      message_callback(dict_msg_parsed, msg_eeid, msg_pipeline, msg_signature, msg_instance)
      return

    def __handle_messages(self, message_queue, message_callback):
      """
      Handle messages from the communication server. 
      This method is called in a separate thread.

      Parameters
      ----------
      message_queue : deque
          The queue of messages received from the communication server
      message_callback : Callable[[dict, str, str, str, str], None]
          The callback that will handle the message.
      """
      while self.__running_callback_threads:
        if len(message_queue) == 0:
          sleep(0.01)
          continue
        current_msg = message_queue.popleft()
        self.__on_message_default_callback(current_msg, message_callback)
      # end while self.running

      # process the remaining messages before exiting
      while len(message_queue) > 0:
        current_msg = message_queue.popleft()
        self.__on_message_default_callback(current_msg, message_callback)
      return

    def __maybe_ignore_message(self, e2id):
      """
      Check if the message should be ignored.
      A message should be ignored if the `filter_workers` attribute is set and the message comes from a node that is not in the list.

      Parameters
      ----------
      e2id : str
          The name of the AiXpand node that sent the message.

      Returns
      -------
      bool
          True if the message should be ignored, False otherwise.
      """
      return self.filter_workers is not None and e2id not in self.filter_workers

    def __track_online_node(self, e2id):
      """
      Track the last time a node was seen online.

      Parameters
      ----------
      e2id : str
          The name of the AiXpand node that sent the message.
      """
      self._last_seen_boxes[e2id] = tm()
      return

    def __on_heartbeat(self, dict_msg: dict, msg_eeid, msg_pipeline, msg_signature, msg_instance):
      """
      Handle a heartbeat message received from the communication server.

      Parameters
      ----------
      dict_msg : dict
          The message received from the communication server
      msg_eeid : str
          The name of the AiXpand node that sent the message.
      msg_pipeline : str
          The name of the pipeline that sent the message.
      msg_signature : str
          The signature of the plugin that sent the message.
      msg_instance : str
          The name of the instance that sent the message.
      """
      # extract relevant data from the message

      if dict_msg.get(HB.HEARTBEAT_VERSION) == HB.V2:
        str_data = CodeUtils().decompress_text(dict_msg[HB.ENCODED_DATA])
        data = json.loads(str_data)
        dict_msg = {**dict_msg, **data}

      msg_active_configs = dict_msg.get(HB.CONFIG_STREAMS)
      if msg_active_configs is None:
        return

      # default action
      self._online_boxes[msg_eeid] = {config[PAYLOAD_DATA.NAME]: config for config in msg_active_configs}
      self.__track_online_node(msg_eeid)

      # TODO: move this call in `__on_message_default_callback`
      if self.__maybe_ignore_message(msg_eeid):
        return

      self.D("Received hb from: {}".format(msg_eeid), verbosity=2)

      # call the custom callback, if defined
      if self.custom_on_heartbeat is not None:
        self.custom_on_heartbeat(self, msg_eeid, dict_msg)

      return

    def __on_notification(self, dict_msg: dict, msg_eeid, msg_pipeline, msg_signature, msg_instance):
      """
      Handle a notification message received from the communication server.

      Parameters
      ----------
      dict_msg : dict
          The message received from the communication server
      msg_eeid : str
          The name of the AiXpand node that sent the message.
      msg_pipeline : str
          The name of the pipeline that sent the message.
      msg_signature : str
          The signature of the plugin that sent the message.
      msg_instance : str
          The name of the instance that sent the message.
      """
      # extract relevant data from the message
      notification_type = dict_msg.get(STATUS_TYPE.NOTIFICATION_TYPE)
      notification = dict_msg.get(PAYLOAD_DATA.NOTIFICATION)

      if self.__maybe_ignore_message(msg_eeid):
        return

      color = None
      if notification_type != STATUS_TYPE.STATUS_NORMAL:
        color = 'r'
      self.D("Received notification {} from <{}/{}>: {}"
             .format(
                notification_type,
                msg_eeid,
                msg_pipeline,
                notification),
             color=color,
             verbosity=2,
             )

      # call the pipeline and instance defined callbacks
      for pipeline in self.own_pipelines:
        if msg_eeid == pipeline.e2id and msg_pipeline == pipeline.name:
          pipeline._on_notification(msg_signature, msg_instance, Payload(dict_msg))
          # since we found the pipeline, we can stop searching
          # because the pipelines have unique names
          break

      # call the custom callback, if defined
      if self.custom_on_notification is not None:
        self.custom_on_notification(self, msg_eeid, Payload(dict_msg))

      return

    # TODO: maybe convert dict_msg to Payload object
    #       also maybe strip the dict from useless info for the user of the sdk
    #       Add try-except + sleep
    def __on_payload(self, dict_msg: dict, msg_eeid, msg_pipeline, msg_signature, msg_instance) -> None:
      """
      Handle a payload message received from the communication server.

      Parameters
      ----------
      dict_msg : dict
          The message received from the communication server
      msg_eeid : str
          The name of the AiXpand node that sent the message.
      msg_pipeline : str
          The name of the pipeline that sent the message.
      msg_signature : str
          The signature of the plugin that sent the message.
      msg_instance : str
          The name of the instance that sent the message.
      """
      # extract relevant data from the message
      msg_data = dict_msg

      if self.__maybe_ignore_message(msg_eeid):
        return

      # call the pipeline and instance defined callbacks
      for pipeline in self.own_pipelines:
        if msg_eeid == pipeline.e2id and msg_pipeline == pipeline.name:
          pipeline._on_data(msg_signature, msg_instance, Payload(dict_msg))
          # since we found the pipeline, we can stop searching
          # because the pipelines have unique names
          break

      if self.custom_on_payload is not None:
        self.custom_on_payload(self, msg_eeid, msg_pipeline, msg_signature, msg_instance, Payload(msg_data))

      return

  # Main loop
  if True:
    def __start_blockchain(self, blockchain_config):
      try:
        self.bc_engine = DefaultBlockEngine(
          log=self.log,
          name=self.name,
          config=blockchain_config,
          verbosity=self._verbosity,
        )
      except:
        raise ValueError("Failure in private blockchain setup:\n{}".format(traceback.format_exc()))
      return

    def __start_main_loop_thread(self):
      self._main_loop_thread = Thread(target=self.__main_loop, daemon=True)

      self.__running_main_loop_thread = True
      self._main_loop_thread.start()
      return

    def __maybe_reconnect(self) -> None:
      """
      Attempt reconnecting to the communication server if an unexpected disconnection ocurred,
      using the credentials provided when creating this instance.

      This method should be called in a user-defined main loop.
      This method is called in `run` method, in the main loop.
      """
      if self.connected == False:
        self._connect()
      return

    def __close_own_pipelines(self):
      """
      Close all pipelines that were created by or attached to this session.
      """
      self.P("Closing own pipelines...", verbosity=2)
      # iterate through all CREATED pipelines from this session and close them
      for pipeline in self.own_pipelines:
        pipeline.close()
      return

    def _communication_close(self):
      """
      Close the communication server connection.
      """
      raise NotImplementedError

    def close(self, close_pipelines=False, wait_close=False, **kwargs):
      """
      Close the session, releasing all resources and closing all threads
      Resources are released in the main loop thread, so this method will block until the main loop thread exits.
      This method is blocking.

      Parameters
      ----------
      close_pipelines : bool, optional
          close all the pipelines created by or attached to this session (basically calling `.close_own_pipelines()` for you), by default False
      wait_close : bool, optional
          If `True`, will wait for the main loop thread to exit. Defaults to `False`
      """

      self.__running_main_loop_thread = False
      self.__close_pipelines = close_pipelines

      # wait for the main loop thread to exit
      while not self.__closed_everything and wait_close:
        sleep(0.1)

      return

    def _connect(self) -> None:
      """
      Connect to the communication server using the credentials provided when creating this instance.
      """
      raise NotImplementedError

    def _send_payload(self, to, payload):
      """
      Send a payload to a node.

      Parameters
      ----------
      to : str
          The name of the AiXpand node that will receive the payload.
      payload : dict
          The payload to send.
      """
      raise NotImplementedError

    def __release_callback_threads(self):
      """
      Release all resources and close all threads
      """
      self.__running_callback_threads = False

      self._payload_thread.join()
      self._notif_thread.join()
      self._hb_thread.join()
      return

    def __main_loop(self):
      """
      The main loop of this session. This method is called in a separate thread.
      This method runs on a separate thread from the main thread, and it is responsible for handling all messages received from the communication server.
      We use it like this to avoid blocking the main thread, which is used by the user.
      """
      while self.__running_main_loop_thread:
        self.__maybe_reconnect()
        sleep(0.1)
      # end while self.running

      self.P("Main loop thread exiting...", verbosity=2)
      self.__release_callback_threads()

      if self.__close_pipelines:
        self.__close_own_pipelines()

      self.P("Comms closing...", verbosity=2)
      self._communication_close()
      self.__closed_everything = True
      return

    def run(self, wait=True, close_session=True, close_pipelines=False):
      """
      This simple method will lock the main thread in a loop.

      Parameters
      ----------
      wait : bool, float
          If `True`, will wait forever.
          If `False`, will not wait at all
          If type `float` and > 0, will wait said amount of seconds
          If type `float` and == 0, will wait forever
          Defaults to `True`
      close_session : bool, optional
          If `True` will close the session when the loop is exited.
          Defaults to `True`
      close_pipelines : bool, optional
          If `True` will close all pipelines initiated by this session when the loop is exited.
          This flag is ignored if `close_session` is `False`.
          Defaults to `False`
      """
      _start_timer = tm()
      try:
        while ((isinstance(wait, bool) and wait) or (wait == 0) or (tm() - _start_timer) < wait) and not self.__closed_everything:
          sleep(0.1)
      except KeyboardInterrupt:
        self.P("CTRL+C detected. Stopping loop.", color='r', verbosity=1)

      if close_session:
        self.close(close_pipelines, wait_close=True)

      return

  # Utils
  if True:
    def __fill_config(self, host, port, user, pwd, dotenv_path):
      """
      Fill the configuration dictionary with the credentials provided when creating this instance.


      Parameters
      ----------
      host : str
          The hostname of the server.
          Can be retrieved from the environment variables AIXP_HOSTNAME, AIXP_HOST 
      port : int
          The port.
          Can be retrieved from the environment variable AIXP_PORT
      user : str
          The user name.
          Can be retrieved from the environment variables AIXP_USERNAME, AIXP_USER
      pwd : str
          The password.
          Can be retrieved from the environment variables AIXP_PASSWORD, AIXP_PASS, AIXP_PWD
      dotenv_path : str, optional
          Path to the .env file, by default None. If None, the path will be searched in the current working directory and in the directories of the files from the call stack.

      Raises
      ------
      ValueError
          Missing credentials
      """

      # this method will search for the credentials in the environment variables
      # the path to env file, if not specified, will be search in the following order:
      #  1. current working directory
      #  2-N. directories of the files from the call stack
      load_dotenv(dotenv_path=dotenv_path, verbose=False)

      user = user or os.getenv(ENVIRONMENT.AIXP_USERNAME) or os.getenv(ENVIRONMENT.AIXP_USER)
      if user is None:
        raise ValueError("Error: No user specified for AiXpand network connection")
      if self._config.get(comm_ct.USER, None) is None:
        self._config[comm_ct.USER] = user

      pwd = pwd or os.getenv(ENVIRONMENT.AIXP_PASSWORD) or os.getenv(
        ENVIRONMENT.AIXP_PASS) or os.getenv(ENVIRONMENT.AIXP_PWD)
      if pwd is None:
        raise ValueError("Error: No password specified for AiXpand network connection")
      if self._config.get(comm_ct.PASS, None) is None:
        self._config[comm_ct.PASS] = pwd

      host = host or os.getenv(ENVIRONMENT.AIXP_HOSTNAME) or os.getenv(ENVIRONMENT.AIXP_HOST)
      if host is None:
        raise ValueError("Error: No host specified for AiXpand network connection")
      if self._config.get(comm_ct.HOST, None) is None:
        self._config[comm_ct.HOST] = host

      port = port or os.getenv(ENVIRONMENT.AIXP_PORT)
      if port is None:
        raise ValueError("Error: No port specified for AiXpand network connection")
      if self._config.get(comm_ct.PORT, None) is None:
        self._config[comm_ct.PORT] = int(port)
      return

    def _send_command_to_box(self, command, worker, payload, show_command=False, **kwargs):
      """
      Send a command to a node.

      Parameters
      ----------
      command : str
          The command to send.
      worker : str
          The name of the AiXpand node that will receive the command.
      payload : dict
          The payload to send.
      show_command : bool, optional
          If True, will print the complete command that is being sent, by default False
      """

      if len(kwargs) > 0:
        self.D("Ignoring extra kwargs: {}".format(kwargs), verbosity=2)

      msg_to_send = {
          comm_ct.COMM_SEND_MESSAGE.K_EE_ID: worker,
          comm_ct.COMM_SEND_MESSAGE.K_ACTION: command,
          comm_ct.COMM_SEND_MESSAGE.K_PAYLOAD: payload,
          comm_ct.COMM_SEND_MESSAGE.K_INITIATOR_ID: self.name,
          comm_ct.COMM_SEND_MESSAGE.K_TIME: dt.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
      }
      self.bc_engine.sign(msg_to_send, use_digest=True)
      if show_command:
        self.P("Sending command '{}' to '{}':\n{}".format(command, worker, json.dumps(msg_to_send, indent=2)),
               color='y',
               verbosity=1
               )
      self._send_payload(worker, msg_to_send)
      return

    def _send_command_create_pipeline(self, worker, pipeline_config, **kwargs):
      self._send_command_to_box(COMMANDS.UPDATE_CONFIG, worker, pipeline_config, **kwargs)
      return

    def _send_command_delete_pipeline(self, worker, pipeline_name, **kwargs):
      # TODO: remove this command calls from examples
      self._send_command_to_box(COMMANDS.DELETE_CONFIG, worker, pipeline_name, **kwargs)
      return

    def _send_command_archive_pipeline(self, worker, pipeline_name, **kwargs):
      self._send_command_to_box(COMMANDS.ARCHIVE_CONFIG, worker, pipeline_name, **kwargs)
      return

    def _send_command_update_pipeline_config(self, worker, pipeline_config, **kwargs):
      self._send_command_to_box(COMMANDS.UPDATE_CONFIG, worker, pipeline_config, **kwargs)
      return

    def _send_command_update_instance_config(self, worker, pipeline, signature, instance_id, instance_config, **kwargs):
      payload = {
        PAYLOAD_DATA.NAME: pipeline,
        PAYLOAD_DATA.SIGNATURE: signature,
        PAYLOAD_DATA.INSTANCE_ID: instance_id,
        PAYLOAD_DATA.INSTANCE_CONFIG: instance_config
      }
      self._send_command_to_box(COMMANDS.UPDATE_PIPELINE_INSTANCE, worker, payload, **kwargs)
      return

    def _send_command_batch_update_instance_config(self, worker, lst_updates, **kwargs):
      for update in lst_updates:
        assert isinstance(update, dict), "All updates must be dicts"
        assert PAYLOAD_DATA.NAME in update, "All updates must have a pipeline name"
        assert PAYLOAD_DATA.SIGNATURE in update, "All updates must have a plugin signature"
        assert PAYLOAD_DATA.INSTANCE_ID in update, "All updates must have a plugin instance id"
        assert PAYLOAD_DATA.INSTANCE_CONFIG in update, "All updates must have a plugin instance config"
        assert isinstance(update[PAYLOAD_DATA.INSTANCE_CONFIG], dict), \
            "All updates must have a plugin instance config as dict"
      self._send_command_to_box(COMMANDS.BATCH_UPDATE_PIPELINE_INSTANCES, worker, lst_updates, **kwargs)

    def _send_command_pipeline_command(self, worker, pipeline, command, payload={}, command_params={}, **kwargs):
      payload = {
        PAYLOAD_DATA.NAME: pipeline,
        COMMANDS.PIPELINE_COMMAND: command,
        # 'COMMAND_PARAMS': command_params, # TODO: check if this is oke
        **payload,
      }
      self._send_command_to_box(COMMANDS.PIPELINE_COMMAND, worker, payload, **kwargs)
      return

    def _send_command_instance_command(self, worker, pipeline, signature, instance_id, command, payload={}, command_params={}, **kwargs):
      payload = {
        COMMANDS.INSTANCE_COMMAND: command,
        **payload,
        COMMANDS.COMMAND_PARAMS: command_params,
      }
      self._send_command_update_instance_config(worker, pipeline, signature, instance_id, payload)
      return

    def _send_command_stop_node(self, worker, **kwargs):
      self._send_command_to_box(COMMANDS.STOP, worker, None, **kwargs)
      return

    def _send_command_restart_node(self, worker, **kwargs):
      self._send_command_to_box(COMMANDS.RESTART, worker, None, **kwargs)
      return

    def _send_command_request_heartbeat(self, worker, full_heartbeat=False, **kwargs):
      command = COMMANDS.FULL_HEARTBEAT if full_heartbeat else COMMANDS.TIMERS_ONLY_HEARTBEAT
      self._send_command_to_box(command, worker, None, **kwargs)

    def _send_command_reload_from_disk(self, worker, **kwargs):
      self._send_command_to_box(COMMANDS.RELOAD_CONFIG_FROM_DISK, worker, None, **kwargs)
      return

    def _send_command_archive_all(self, worker, **kwargs):
      self._send_command_to_box(COMMANDS.ARCHIVE_CONFIG_ALL, worker, None, **kwargs)
      return

    def _send_command_delete_all(self, worker, **kwargs):
      self._send_command_to_box(COMMANDS.DELETE_CONFIG_ALL, worker, None, **kwargs)
      return

  # API
  if True:
    @property
    def server(self):
      """
      The hostname of the server.
      """
      return self._config[comm_ct.HOST]

    def P(self, *args, **kwargs):
      """
      Call the `Logger.P` method. If using the default Logger, this call will print
      info to stdout.

      Parameters
      ----------
      *args :

      msg : obj
          The message to pass to the `Logger.P` method. If using the default Logger, this
          will be the message displayed at the stdout.

      **kwargs :


      Returns
      -------

      """
      verbosity = kwargs.pop('verbosity', 1)
      if verbosity > self._verbosity:
        return
      self.log.P(*args, **kwargs)

    def D(self, *args, **kwargs):
      """
      Call the `Logger.D` method.
      If using the default Logger, this call will print debug info to stdout if `silent` is set to `False`.

      Parameters
      ----------
      *args :

      msg : obj
          The message to pass to the `Logger.P` method. If using the default Logger, this
          will be the message displayed at the stdout.

      **kwargs :


      Returns
      -------

      """
      verbosity = kwargs.pop('verbosity', 1)
      if verbosity > self._verbosity:
        return
      self.log.D(*args, **kwargs)
      return

    def create_pipeline(self, *,
                        e2id,
                        name,
                        data_source,
                        config={},
                        plugins=[],
                        on_data=None,
                        on_notification=None,
                        max_wait_time=0,
                        **kwargs) -> Pipeline:
      """
      Create a new pipeline on a node. A pipeline is the equivalent of the "config file" used by the Hyperfy dev team internally.

      A `Pipeline` is a an object that encapsulates a one-to-many, data acquisition to data processing, flow of data.

      A `Pipeline` contains one thread of data acquisition (which does not mean only one source of data), and many
      processing units, usually named `Plugins`. 

      An `Instance` is a running thread of a `Plugin` type, and one may want to have multiple `Instances`, because each can be configured independently.

      As such, one will work with `Instances`, by referring to them with the unique identifier (Pipeline, Plugin, Instance).

      In the documentation, the following refer to the same thing:
        `Pipeline` == `Stream`

        `Plugin` == `Signature`

      This call can busy-wait for a number of seconds to listen to heartbeats, in order to check if an AiXpand node is online or not.
      If the node does not appear online, a warning will be displayed at the stdout, telling the user that the message that handles the
      creation of the pipeline will be sent, but it is not guaranteed that the specific node will receive it.

      Parameters
      ----------
      e2id : str
          Name of the AiXpand node that will handle this pipeline.
      name : str
          Name of the pipeline. This is good to be kept unique, as it allows multiple parties to overwrite each others configurations.
      data_source : str
          This is the name of the DCT plugin, which resembles the desired functionality of the acquisition.
      config : dict, optional
          This is the dictionary that contains the configuration of the acquisition source, by default {}
      plugins : list
          List of dictionaries which contain the configurations of each plugin instance that is desired to run on the box. 
          Defaults to []. Should be left [], and instances should be created with the api.
      on_data : Callable[[Pipeline, str, str, dict], None], optional
          Callback that handles messages received from any plugin instance. 
          As arguments, it has a reference to this Pipeline object, the signature and the instance of the plugin
          that sent the message and the payload itself.
          This callback acts as a default payload processor and will be called even if for a given instance
          the user has defined a specific callback.
          Defaults to None.
      on_notification : Callable[[Pipeline, dict], None], optional
          Callback that handles notifications received from any plugin instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself. 
          This callback acts as a default payload processor and will be called even if for a given instance
          the user has defined a specific callback.
          Defaults to None.
      max_wait_time : int, optional
          The maximum time to busy-wait, allowing the Session object to listen to node heartbeats
          and to check if the desired node is online in the network, by default 0.
      **kwargs :
          The user can provide the configuration of the acquisition source directly as kwargs.

      Returns
      -------
      Pipeline
          A `Pipeline` object.

      """
      _start = tm()
      found = e2id in self.get_active_nodes()
      while (tm() - _start) < max_wait_time and not found:
        sleep(0.1)
        avail_workers = self.get_active_nodes()
        found = e2id in avail_workers
      # end while

      if not found:
        self.P("WARNING: could not find worker '{}' in {:.1f}s. The job may not have a valid active worker.".format(
            e2id, tm() - _start
        ), color='r', verbosity=1)
      pipeline = Pipeline(
          self,
          self.log,
          e2id=e2id,
          name=name,
          data_source=data_source,
          config=config,
          plugins=plugins,
          on_data=on_data,
          on_notification=on_notification,
          **kwargs
      )
      self.own_pipelines.append(pipeline)
      return pipeline

    def get_active_nodes(self):
      """
      Get the list of all AiXp nodes that sent a message since this session was created, and that are considered online

      Parameters
      ----------

      Returns
      -------
      list
          List of names of all the AiXp nodes that are considered online

      """
      return [k for k, v in self._last_seen_boxes.items() if tm() - v < self.online_timeout]

    def get_active_pipelines(self, e2id):
      """
      Get a dictionary with all the pipelines that are active on this AiXp node

      Parameters
      ----------
      e2id : str
          name of the AiXp node

      Returns
      -------
      dict
          The key is the name of the pipeline, and the value is the entire config dictionary of that pipeline.

      """
      return self._online_boxes.get(e2id, None) if e2id in self.get_active_nodes() else None

    def attach_to_pipeline(self, *,
                           e2id,
                           name,
                           on_data=None,
                           on_notification=None,
                           max_wait_time=0,
                           **kwargs) -> Pipeline:
      """
      Create a Pipeline object and attach to an existing pipeline on an AiXpand node.
      Useful when one wants to treat an existing pipeline as one of his own,
      or when one wants to attach callbacks to various events (on_data, on_notification).

      A `Pipeline` is a an object that encapsulates a one-to-many, data acquisition to data processing, flow of data.

      A `Pipeline` contains one thread of data acquisition (which does not mean only one source of data), and many
      processing units, usually named `Plugins`. 

      An `Instance` is a running thread of a `Plugin` type, and one may want to have multiple `Instances`, because each can be configured independently.

      As such, one will work with `Instances`, by reffering to them with the unique identifier (Pipeline, Plugin, Instance).

      In the documentation, the following reffer to the same thing:
        `Pipeline` == `Stream`

        `Plugin` == `Signature`

      This call can busy-wait for a number of seconds to listen to heartbeats, in order to check if an AiXpand node is online or not.
      If the node does not appear online, a warning will be displayed at the stdout, telling the user that the message that handles the
      creation of the pipeline will be sent, but it is not guaranteed that the specific node will receive it.


      Parameters
      ----------
      e2id : str
          Name of the AiXpand node that handles this pipeline.  
      name : str
          Name of the existing pipeline.
      on_data : Callable[[Pipeline, str, str, dict], None], optional
          Callback that handles messages received from any plugin instance. 
          As arguments, it has a reference to this Pipeline object, the signature and the instance of the plugin
          that sent the message and the payload itself.
          This callback acts as a default payload processor and will be called even if for a given instance
          the user has defined a specific callback.
          Defaults to None.
      on_notification : Callable[[Pipeline, dict], None], optional
          Callback that handles notifications received from any plugin instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself. 
          This callback acts as a default payload processor and will be called even if for a given instance
          the user has defined a specific callback.
          Defaults to None.
      max_wait_time : int, optional
          The maximum time to busy-wait, allowing the Session object to listen to node heartbeats
          and to check if the desired node is online in the network, by default 0.
      **kwargs :
          The user can provide the configuration of the acquisition source directly as kwargs.

      Returns
      -------
      Pipeline
          A `Pipeline` object.

      Raises
      ------
      Exception
          Node does not exist (it is considered offline because the session did not receive any heartbeat)
      Exception
          Node does not host the desired pipeline 
      """

      _start = tm()
      found = e2id in self.get_active_nodes()
      while (tm() - _start) < max_wait_time and not found:
        sleep(0.1)
        avail_workers = self.get_active_nodes()
        found = e2id in avail_workers
      # end while

      if not found:
        raise Exception("Unable to attach to pipeline. Node does not exist")

      if name not in self._online_boxes[e2id]:
        raise Exception("Unable to attach to pipeline. Pipeline does not exist")

      pipeline_config = {
          k.lower(): v for k, v in self._online_boxes[e2id][name].items()}
      data_source = pipeline_config['type']

      pipeline = Pipeline(
        session=self,
        log=self.log,
        e2id=e2id,
        data_source=data_source,
        create_pipeline=False,
        on_data=on_data,
        on_notification=on_notification,
        **pipeline_config,
        **kwargs
      )

      self.own_pipelines.append(pipeline)

      return pipeline
