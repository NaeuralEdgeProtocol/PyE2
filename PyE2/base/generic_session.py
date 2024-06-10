import json
import os
import traceback
from collections import deque
from datetime import datetime as dt
from threading import Thread
from time import sleep
from time import time as tm

from ..bc import DefaultBlockEngine
from ..const import COMMANDS, ENVIRONMENT, HB, PAYLOAD_DATA, STATUS_TYPE
from ..const import comms as comm_ct
from ..base_decentra_object import BaseDecentrAIObject
from ..io_formatter import IOFormatterWrapper
from ..logging import Logger
from ..utils import load_dotenv
from ..utils.code import CodeUtils
from .payload import Payload
from .pipeline import Pipeline
from .transaction import Transaction

# TODO: add support for remaining commands from EE


class GenericSession(BaseDecentrAIObject):
  """
  A Session is a connection to a communication server which provides the channel to interact with nodes from the Naeural network.
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
      "QOS": 0,
      "CERT_PATH": None,
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
               encrypt_comms=False,
               config={},
               filter_workers=None,
               log: Logger = None,
               on_payload=None,
               on_notification=None,
               on_heartbeat=None,
               silent=True,
               verbosity=1,
               dotenv_path=None,
               show_commands=False,
               blockchain_config=BLOCKCHAIN_CONFIG,
               bc_engine=None,
               formatter_plugins_locations=['plugins.io_formatters'],
               **kwargs) -> None:
    """
    A Session is a connection to a communication server which provides the channel to interact with nodes from the Naeural network.
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
        The name of this connection, used to identify owned pipelines on a specific Naeural edge node.
        The name will be used as `INITIATOR_ID` and `SESSION_ID` when communicating with Naeural edge nodes, by default 'pySDK'
    config : dict, optional
        Configures the names of the channels this session will connect to.
        If using a Mqtt server, these channels are in fact topics.
        Modify this if you are absolutely certain of what you are doing.
        By default {}
    filter_workers: list, optional
        If set, process the messages that come only from the nodes from this list.
        Defaults to None
    show_commands : bool
        If True, will print the commands that are being sent to the Naeural edge nodes.
        Defaults to False
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

    # TODO: maybe read config from file?
    self._config = {**self.default_config, **config}

    self.log = log
    self.name = name

    self._verbosity = verbosity
    self.encrypt_comms = encrypt_comms

    self._online_boxes: dict[str, Pipeline] = {}
    self._dct_can_send_to_node: dict[str, bool] = {}
    self._last_seen_boxes = {}
    self._box_addr = {}
    self.online_timeout = 60
    self.filter_workers = filter_workers
    self.__show_commands = show_commands

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

    self.sdk_main_loop_thread = Thread(target=self.__main_loop, daemon=True)
    self.__formatter_plugins_locations = formatter_plugins_locations

    self.__bc_engine = bc_engine
    self.__blockchain_config = blockchain_config

    self.__open_transactions: list[Transaction] = []

    self.__create_user_callback_threads()
    super(GenericSession, self).__init__(log=log, DEBUG=not silent, create_logger=True)
    return

  def startup(self):
    self.__start_blockchain(self.__bc_engine, self.__blockchain_config)
    self.formatter_wrapper = IOFormatterWrapper(self.log, plugin_search_locations=self.__formatter_plugins_locations)

    self._connect()
    self.__start_main_loop_thread()
    super(GenericSession, self).startup()

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
      self._hb_thread.start()
      self._notif_thread.start()
      self._payload_thread.start()
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
        msg_node_id, msg_pipeline, msg_signature, msg_instance = msg_path
      except:
        self.D("Message does not respect standard: {}".format(dict_msg), verbosity=2)
        return

      message_callback(dict_msg_parsed, msg_node_id, msg_pipeline, msg_signature, msg_instance)
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

    def __maybe_ignore_message(self, node_id):
      """
      Check if the message should be ignored.
      A message should be ignored if the `filter_workers` attribute is set and the message comes from a node that is not in the list.

      Parameters
      ----------
      node_id : str
          The name of the Naeural edge node that sent the message.

      Returns
      -------
      bool
          True if the message should be ignored, False otherwise.
      """
      return self.filter_workers is not None and node_id not in self.filter_workers

    def __track_online_node(self, node_id, ee_address):
      """
      Track the last time a node was seen online.

      Parameters
      ----------
      node_id : str
          The name of the Naeural edge node that sent the message.
      """
      self._last_seen_boxes[node_id] = tm()
      self._box_addr[node_id] = ee_address
      return

    def __track_allowed_node(self, node_id, dict_msg):
      """
      Track if this session is allowed to send messages to node.

      Parameters
      ----------
      node_id : str
          The name of the Naeural edge node that sent the message.
      dict_msg : dict
          The message received from the communication server.
      """
      node_whitelist = dict_msg.get(HB.EE_WHITELIST, [])
      node_secured = dict_msg.get(HB.SECURED, False)

      self._dct_can_send_to_node[node_id] = not node_secured or self.bc_engine.address_no_prefix in node_whitelist
      return

    def __on_heartbeat(self, dict_msg: dict, msg_node_id, msg_pipeline, msg_signature, msg_instance):
      """
      Handle a heartbeat message received from the communication server.

      Parameters
      ----------
      dict_msg : dict
          The message received from the communication server
      msg_node_id : str
          The name of the Naeural edge node that sent the message.
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
      if msg_node_id not in self._online_boxes:
        self._online_boxes[msg_node_id] = {}
      for config in msg_active_configs:
        pipeline_name = config[PAYLOAD_DATA.NAME]
        pipeline: Pipeline = self._online_boxes[msg_node_id].get(pipeline_name, None)
        if pipeline is not None:
          pipeline.update_full_configuration({k.upper(): v for k, v in config.items()})
        else:
          self._online_boxes[msg_node_id][pipeline_name] = self.__create_pipeline_from_config(msg_node_id, config)

      ee_address = dict_msg[HB.EE_ADDR]
      self.__track_online_node(msg_node_id, ee_address)

      # TODO: move this call in `__on_message_default_callback`
      if self.__maybe_ignore_message(msg_node_id):
        return

      # pass the heartbeat message to open transactions
      no_transactions = len(self.__open_transactions)
      for idx in range(no_transactions):
        self.__open_transactions[idx].handle_heartbeat(dict_msg)

      self.D("Received hb from: {}".format(msg_node_id), verbosity=2)

      self.__track_allowed_node(msg_node_id, dict_msg)

      # call the custom callback, if defined
      if self.custom_on_heartbeat is not None:
        self.custom_on_heartbeat(self, msg_node_id, dict_msg)

      return

    def __on_notification(self, dict_msg: dict, msg_node_id, msg_pipeline, msg_signature, msg_instance):
      """
      Handle a notification message received from the communication server.

      Parameters
      ----------
      dict_msg : dict
          The message received from the communication server
      msg_node_id : str
          The name of the Naeural edge node that sent the message.
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

      if self.__maybe_ignore_message(msg_node_id):
        return

      color = None
      if notification_type != STATUS_TYPE.STATUS_NORMAL:
        color = 'r'
      self.D("Received notification {} from <{}/{}>: {}"
             .format(
                notification_type,
                msg_node_id,
                msg_pipeline,
                notification),
             color=color,
             verbosity=2,
             )

      # call the pipeline and instance defined callbacks
      for pipeline in self.own_pipelines:
        if msg_node_id == pipeline.node_id and msg_pipeline == pipeline.name:
          pipeline._on_notification(msg_signature, msg_instance, Payload(dict_msg))
          # since we found the pipeline, we can stop searching
          # because the pipelines have unique names
          break

      # pass the notification message to open transactions
      no_transactions = len(self.__open_transactions)
      for idx in range(no_transactions):
        self.__open_transactions[idx].handle_notification(dict_msg)

      # call the custom callback, if defined
      if self.custom_on_notification is not None:
        self.custom_on_notification(self, msg_node_id, Payload(dict_msg))

      return

    # TODO: maybe convert dict_msg to Payload object
    #       also maybe strip the dict from useless info for the user of the sdk
    #       Add try-except + sleep
    def __on_payload(self, dict_msg: dict, msg_node_id, msg_pipeline, msg_signature, msg_instance) -> None:
      """
      Handle a payload message received from the communication server.

      Parameters
      ----------
      dict_msg : dict
          The message received from the communication server
      msg_node_id : str
          The name of the Naeural edge node that sent the message.
      msg_pipeline : str
          The name of the pipeline that sent the message.
      msg_signature : str
          The signature of the plugin that sent the message.
      msg_instance : str
          The name of the instance that sent the message.
      """
      # extract relevant data from the message
      msg_data = dict_msg

      if self.__maybe_ignore_message(msg_node_id):
        return

      # call the pipeline and instance defined callbacks
      for pipeline in self.own_pipelines:
        if msg_node_id == pipeline.node_id and msg_pipeline == pipeline.name:
          pipeline._on_data(msg_signature, msg_instance, Payload(dict_msg))
          # since we found the pipeline, we can stop searching
          # because the pipelines have unique names
          break

      # pass the payload message to open transactions
      no_transactions = len(self.__open_transactions)
      for idx in range(no_transactions):
        self.__open_transactions[idx].handle_payload(dict_msg)

      if self.custom_on_payload is not None:
        self.custom_on_payload(self, msg_node_id, msg_pipeline, msg_signature, msg_instance, Payload(msg_data))

      return

  # Main loop
  if True:
    def __start_blockchain(self, bc_engine, blockchain_config):
      if bc_engine is not None:
        self.bc_engine = bc_engine
        return

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

    def __handle_open_transactions(self):
      no_transactions = len(self.__open_transactions)

      solved_transactions = [i for i in range(no_transactions) if self.__open_transactions[i].is_solved()]
      solved_transactions.reverse()
      for idx in solved_transactions:
        self.__open_transactions[idx].callback()
        self.__open_transactions.pop(idx)
      return

    @property
    def _connected(self):
      """
      Check if the session is connected to the communication server.
      """
      raise NotImplementedError

    def __maybe_reconnect(self) -> None:
      """
      Attempt reconnecting to the communication server if an unexpected disconnection ocurred,
      using the credentials provided when creating this instance.

      This method should be called in a user-defined main loop.
      This method is called in `run` method, in the main loop.
      """
      if self._connected == False:
        self._connect()
      return

    def __close_own_pipelines(self, wait=True):
      """
      Close all pipelines that were created by or attached to this session.

      Parameters
      ----------
      wait : bool, optional
          If `True`, will wait for the transactions to finish. Defaults to `True`
      """
      # iterate through all CREATED pipelines from this session and close them
      transactions = []

      for pipeline in self.own_pipelines:
        transactions.extend(pipeline._close())

      self.P("Closing own pipelines: {}".format([p.name for p in self.own_pipelines]))

      if wait:
        self.wait_for_transactions(transactions)
        self.P("Closed own pipelines.")
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

      if close_pipelines:
        self.__close_own_pipelines(wait=wait_close)

      self.__running_main_loop_thread = False

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
          The name of the Naeural edge node that will receive the payload.
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
        self.__handle_open_transactions()
        sleep(0.1)
      # end while self.running

      self.P("Main loop thread exiting...", verbosity=2)
      self.__release_callback_threads()

      self.P("Comms closing...", verbosity=2)
      self._communication_close()
      self.__closed_everything = True
      return

    def run(self, wait=True, close_session=True, close_pipelines=False):
      """
      This simple method will lock the main thread in a loop.

      Parameters
      ----------
      wait : bool, float, callable
          If `True`, will wait forever.
          If `False`, will not wait at all
          If type `float` and > 0, will wait said amount of seconds
          If type `float` and == 0, will wait forever
          If type `callable`, will call the function until it returns `False`
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
        bool_loop_condition = isinstance(wait, bool) and wait
        number_loop_condition = isinstance(wait, (int, float)) and (wait == 0 or (tm() - _start_timer) < wait)
        callable_loop_condition = callable(wait) and wait()
        while (bool_loop_condition or number_loop_condition or callable_loop_condition) and not self.__closed_everything:
          sleep(0.1)
          bool_loop_condition = isinstance(wait, bool) and wait
          number_loop_condition = isinstance(wait, (int, float)) and (wait == 0 or (tm() - _start_timer) < wait)
          callable_loop_condition = callable(wait) and wait()
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

      possible_user_values = [
        user,
        os.getenv(ENVIRONMENT.AIXP_USERNAME),
        os.getenv(ENVIRONMENT.AIXP_USER),
        os.getenv(ENVIRONMENT.EE_USERNAME),
        os.getenv(ENVIRONMENT.EE_USER),
        self._config.get(comm_ct.USER),
      ]

      user = next((x for x in possible_user_values if x is not None), None)

      if user is None:
        env_error = "Error: No user specified for Naeural network connection. Please make sure you have the correct credentials in the environment variables within the .env file or provide them as params in code (not recommended due to potential security issue)."
        raise ValueError(env_error)
      if self._config.get(comm_ct.USER, None) is None:
        self._config[comm_ct.USER] = user

      possible_password_values = [
        pwd,
        os.getenv(ENVIRONMENT.AIXP_PASSWORD),
        os.getenv(ENVIRONMENT.AIXP_PASS),
        os.getenv(ENVIRONMENT.AIXP_PWD),
        os.getenv(ENVIRONMENT.EE_PASSWORD),
        os.getenv(ENVIRONMENT.EE_PASS),
        os.getenv(ENVIRONMENT.EE_PWD),
        self._config.get(comm_ct.PASS),
      ]

      pwd = next((x for x in possible_password_values if x is not None), None)

      if pwd is None:
        raise ValueError("Error: No password specified for Naeural network connection")
      if self._config.get(comm_ct.PASS, None) is None:
        self._config[comm_ct.PASS] = pwd

      possible_host_values = [
        host,
        os.getenv(ENVIRONMENT.AIXP_HOSTNAME),
        os.getenv(ENVIRONMENT.AIXP_HOST),
        os.getenv(ENVIRONMENT.EE_HOSTNAME),
        os.getenv(ENVIRONMENT.EE_HOST),
        self._config.get(comm_ct.HOST),
        "r9092118.ala.eu-central-1.emqxsl.com",
      ]

      host = next((x for x in possible_host_values if x is not None), None)

      if host is None:
        raise ValueError("Error: No host specified for Naeural network connection")
      if self._config.get(comm_ct.HOST, None) is None:
        self._config[comm_ct.HOST] = host

      possible_port_values = [
        port,
        os.getenv(ENVIRONMENT.AIXP_PORT),
        os.getenv(ENVIRONMENT.EE_PORT),
        self._config.get(comm_ct.PORT),
        8883,
      ]

      port = next((x for x in possible_port_values if x is not None), None)

      if port is None:
        raise ValueError("Error: No port specified for Naeural network connection")
      if self._config.get(comm_ct.PORT, None) is None:
        self._config[comm_ct.PORT] = int(port)

      possible_cert_path_values = [
        os.getenv(ENVIRONMENT.AIXP_CERT_PATH),
        os.getenv(ENVIRONMENT.EE_CERT_PATH),
        self._config.get(comm_ct.CERT_PATH),
      ]

      cert_path = next((x for x in possible_cert_path_values if x is not None), None)
      if cert_path is not None and self._config.get(comm_ct.CERT_PATH, None) is None:
        self._config[comm_ct.CERT_PATH] = cert_path
      return

    def _send_command_to_box(self, command, worker, payload, show_command=False, session_id=None, **kwargs):
      """
      Send a command to a node.

      Parameters
      ----------
      command : str
          The command to send.
      worker : str
          The name of the Naeural edge node that will receive the command.
      payload : dict
          The payload to send.
      show_command : bool, optional
          If True, will print the complete command that is being sent, by default False
      """

      show_command = show_command or self.__show_commands

      if len(kwargs) > 0:
        self.D("Ignoring extra kwargs: {}".format(kwargs), verbosity=2)

      critical_data = {
        comm_ct.COMM_SEND_MESSAGE.K_ACTION: command,
        comm_ct.COMM_SEND_MESSAGE.K_PAYLOAD: payload,
      }

      # This part is duplicated with the creation of payloads
      encrypt_payload = self.encrypt_comms
      worker_address = self._get_worker_address(worker)
      if encrypt_payload and worker_address is not None:
        # TODO: use safe_json_dumps
        str_data = json.dumps(critical_data)
        str_enc_data = self.bc_engine.encrypt(str_data, worker_address)
        critical_data = {
          comm_ct.COMM_SEND_MESSAGE.K_EE_IS_ENCRYPTED: True,
          comm_ct.COMM_SEND_MESSAGE.K_EE_ENCRYPTED_DATA: str_enc_data,
        }
      else:
        critical_data[comm_ct.COMM_SEND_MESSAGE.K_EE_IS_ENCRYPTED] = False
        if encrypt_payload:
          critical_data[comm_ct.COMM_SEND_MESSAGE.K_EE_ENCRYPTED_DATA] = "Error! No receiver address found!"

      # endif
      msg_to_send = {
          **critical_data,
          comm_ct.COMM_SEND_MESSAGE.K_EE_ID: worker,
          comm_ct.COMM_SEND_MESSAGE.K_SESSION_ID: session_id or self.name,
          comm_ct.COMM_SEND_MESSAGE.K_INITIATOR_ID: self.name,
          comm_ct.COMM_SEND_MESSAGE.K_SENDER_ADDR: self.bc_engine.address,
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

    def _send_command_update_instance_config(self, worker, pipeline_name, signature, instance_id, instance_config, **kwargs):
      payload = {
        PAYLOAD_DATA.NAME: pipeline_name,
        PAYLOAD_DATA.SIGNATURE: signature,
        PAYLOAD_DATA.INSTANCE_ID: instance_id,
        PAYLOAD_DATA.INSTANCE_CONFIG: {k.upper(): v for k, v in instance_config.items()}
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
      self._send_command_to_box(COMMANDS.BATCH_UPDATE_PIPELINE_INSTANCE, worker, lst_updates, **kwargs)

    def _send_command_pipeline_command(self, worker, pipeline_name, command, payload={}, command_params={}, **kwargs):
      payload = {
        PAYLOAD_DATA.NAME: pipeline_name,
        COMMANDS.PIPELINE_COMMAND: command,
        COMMANDS.COMMAND_PARAMS: command_params,
        **payload,
      }
      self._send_command_to_box(COMMANDS.PIPELINE_COMMAND, worker, payload, **kwargs)
      return

    def _send_command_instance_command(self, worker, pipeline_name, signature, instance_id, command, payload={}, command_params={}, **kwargs):
      payload = {
        COMMANDS.INSTANCE_COMMAND: command,
        **payload,
        COMMANDS.COMMAND_PARAMS: command_params,
      }
      self._send_command_update_instance_config(worker, pipeline_name, signature, instance_id, payload, **kwargs)
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

    def _get_worker_address(self, worker):
      return self._box_addr.get(worker)

    def _register_transaction(self, session_id: str, lst_required_responses: list = None, timeout=0, on_success_callback: callable = None, on_failure_callback: callable = None) -> Transaction:
      """
      Register a new transaction.

      Parameters
      ----------
      session_id : str
          The session id.
      lst_required_responses : list[Response], optional
          The list of required responses, by default None
      timeout : int, optional
          The timeout, by default 0
      on_success_callback : _type_, optional
          The on success callback, by default None
      on_failure_callback : _type_, optional
          The on failure callback, by default None
      Returns
      -------
      Transaction
          The transaction object
      """
      transaction = Transaction(
        log=self.log,
        session_id=session_id,
        lst_required_responses=lst_required_responses or [],
        timeout=timeout,
        on_success_callback=on_success_callback,
        on_failure_callback=on_failure_callback,
      )

      self.__open_transactions.append(transaction)
      return transaction

    def __create_pipeline_from_config(self, node, config):
      pipeline_config = {k.lower(): v for k, v in config.items()}
      name = pipeline_config.pop('name', None)
      plugins = pipeline_config.pop('plugins', None)

      pipeline = Pipeline(
        is_attached=True,
        session=self,
        log=self.log,
        node_id=node,
        name=name,
        plugins=plugins,
        existing_config=pipeline_config,
      )

      return pipeline

  # API
  if True:
    @ property
    def server(self):
      """
      The hostname of the server.
      """
      return self._config[comm_ct.HOST]

    def create_pipeline(self, *,
                        node_id,
                        name,
                        data_source,
                        config={},
                        plugins=[],
                        on_data=None,
                        on_notification=None,
                        max_wait_time=0,
                        **kwargs) -> Pipeline:
      """
      Create a new pipeline on a node. A pipeline is the equivalent of the "config file" used by the Naeural edge node team internally.

      A `Pipeline` is a an object that encapsulates a one-to-many, data acquisition to data processing, flow of data.

      A `Pipeline` contains one thread of data acquisition (which does not mean only one source of data), and many
      processing units, usually named `Plugins`.

      An `Instance` is a running thread of a `Plugin` type, and one may want to have multiple `Instances`, because each can be configured independently.

      As such, one will work with `Instances`, by referring to them with the unique identifier (Pipeline, Plugin, Instance).

      In the documentation, the following refer to the same thing:
        `Pipeline` == `Stream`

        `Plugin` == `Signature`

      This call can busy-wait for a number of seconds to listen to heartbeats, in order to check if an Naeural edge node is online or not.
      If the node does not appear online, a warning will be displayed at the stdout, telling the user that the message that handles the
      creation of the pipeline will be sent, but it is not guaranteed that the specific node will receive it.

      Parameters
      ----------
      node_id : str
          Name of the Naeural edge node that will handle this pipeline.
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
      found = node_id in self.get_active_nodes()
      while (tm() - _start) < max_wait_time and not found:
        sleep(0.1)
        avail_workers = self.get_active_nodes()
        found = node_id in avail_workers
      # end while

      if not found:
        self.P("WARNING: could not find worker '{}' in {:.1f}s. The job may not have a valid active worker.".format(
            node_id, tm() - _start
        ), color='r', verbosity=1)
      pipeline = Pipeline(
          self,
          self.log,
          node_id=node_id,
          name=name,
          type=data_source,
          config=config,
          plugins=plugins,
          on_data=on_data,
          on_notification=on_notification,
          is_attached=False,
          **kwargs
      )
      self.own_pipelines.append(pipeline)
      return pipeline

    def get_active_nodes(self):
      """
      Get the list of all Naeural edge nodes that sent a message since this session was created, and that are considered online

      Returns
      -------
      list
          List of names of all the Naeural edge nodes that are considered online

      """
      return [k for k, v in self._last_seen_boxes.items() if tm() - v < self.online_timeout]

    def get_allowed_nodes(self):
      """
      Get the list of all active Naeural edge nodes to whom this session can send messages

      Returns
      -------
      list[str]
          List of names of all the active Naeural edge nodes to whom this session can send messages
      """
      active_nodes = self.get_active_nodes()
      return [node for node in self._dct_can_send_to_node if self._dct_can_send_to_node[node] and node in active_nodes]

    def get_active_pipelines(self, node_id):
      """
      Get a dictionary with all the pipelines that are active on this Naeural edge node

      Parameters
      ----------
      node_id : str
          name of the Naeural edge node

      Returns
      -------
      dict
          The key is the name of the pipeline, and the value is the entire config dictionary of that pipeline.

      """
      return self._online_boxes.get(node_id, None) if node_id in self.get_active_nodes() else None

    def attach_to_pipeline(self, *,
                           node_id,
                           name,
                           on_data=None,
                           on_notification=None,
                           max_wait_time=0) -> Pipeline:
      """
      Create a Pipeline object and attach to an existing pipeline on an Naeural edge node.
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

      This call can busy-wait for a number of seconds to listen to heartbeats, in order to check if an Naeural edge node is online or not.
      If the node does not appear online, a warning will be displayed at the stdout, telling the user that the message that handles the
      creation of the pipeline will be sent, but it is not guaranteed that the specific node will receive it.


      Parameters
      ----------
      node_id : str
          Name of the Naeural edge node that handles this pipeline.
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
      found = node_id in self.get_active_nodes()
      while (tm() - _start) < max_wait_time and not found:
        sleep(0.1)
        avail_workers = self.get_active_nodes()
        found = node_id in avail_workers
      # end while

      if not found:
        raise Exception("Unable to attach to pipeline. Node does not exist")

      if name not in self._online_boxes[node_id]:
        raise Exception("Unable to attach to pipeline. Pipeline does not exist")

      pipeline = self._online_boxes[node_id][name]

      self.own_pipelines.append(pipeline)

      return pipeline

    def create_or_attach_to_pipeline(self, *,
                                     node_id,
                                     name,
                                     data_source,
                                     config={},
                                     plugins=[],
                                     on_data=None,
                                     on_notification=None,
                                     max_wait_time=0,
                                     **kwargs) -> Pipeline:
      """
      Create a new pipeline on a node, or attach to an existing pipeline on an Naeural edge node.

      Parameters
      ----------
      node_id : str
          Name of the Naeural edge node that will handle this pipeline.
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

      pipeline = None
      try:
        pipeline = self.attach_to_pipeline(
          node_id=node_id,
          name=name,
          on_data=on_data,
          on_notification=on_notification,
          max_wait_time=max_wait_time,
          **kwargs
        )

        possible_new_configuration = {
          **config,
          **kwargs
        }

        if len(plugins) > 0:
          possible_new_configuration['PLUGINS'] = plugins

        if len(possible_new_configuration) > 0:
          pipeline.update_full_configuration(config=possible_new_configuration)
      except Exception as e:
        self.D("Failed to attach to pipeline: {}".format(e))
        pipeline = self.create_pipeline(
          node_id=node_id,
          name=name,
          data_source=data_source,
          config=config,
          plugins=plugins,
          on_data=on_data,
          on_notification=on_notification,
          **kwargs
        )

      return pipeline

    def wait_for_transactions(self, transactions):
      """
      Wait for the transactions to be solved.

      Parameters
      ----------
      transactions : list[Transaction]
          The transactions to wait for.
      """
      while any([not transaction.is_finished() for transaction in transactions]):
        sleep(0.1)
      return

    def wait_for_any_node(self, timeout=15):
      """
      Wait for any node to appear online.

      Parameters
      ----------
      timeout : int, optional
          The timeout, by default 15

      Returns
      -------
      bool
          True if any node is online, False otherwise.
      """
      self.P("Waiting for any node to appear online...")
      _start = tm()
      found = len(self.get_active_nodes()) > 0
      while (tm() - _start) < timeout and not found:
        sleep(0.1)
        found = len(self.get_active_nodes()) > 0
      # end while

      if found:
        self.P("Found nodes {} online.".format(self.get_active_nodes()))
      else:
        self.P("No nodes found online in {:.1f}s.".format(tm() - _start), color='r')
      return found

    def wait_for_node(self, node_id, /, timeout=15):
      """
      Wait for a node to appear online.

      Parameters
      ----------
      node_id : str
          The name of the Naeural edge node.
      timeout : int, optional
          The timeout, by default 15

      Returns
      -------
      bool
          True if the node is online, False otherwise.
      """

      self.P("Waiting for node '{}' to appear online...".format(node_id))
      _start = tm()
      found = node_id in self.get_active_nodes() or node_id in self._box_addr.values()
      while (tm() - _start) < timeout and not found:
        sleep(0.1)
        found = node_id in self.get_active_nodes() or node_id in self._box_addr.values()
      # end while

      if found:
        self.P("Node '{}' is online.".format(node_id))
      else:
        self.P("Node '{}' did not appear online in {:.1f}s.".format(node_id, tm() - _start), color='r')
      return found

    def create_chain_dist_custom_job(
      self,
      main_node_process_real_time_collected_data,
      main_node_finish_condition,
      main_node_finish_condition_kwargs,
      main_node_aggregate_collected_data,
      worker_node_code,
      nr_remote_worker_nodes,
      node_id=None,
      node_addr=None,
      worker_node_plugin_config={},
      worker_node_pipeline_config={},
      on_data=None,
      on_notification=None,
      deploy=False,
    ):

      if node_id is None and node_addr is None:
        raise ValueError("Either node_id or node_addr must be provided.")

      if node_id is None:
        node_id = {n_a: n_id for n_id, n_a in self._box_addr.items()}.get(node_addr, None)

      if node_id is None:
        raise ValueError("Node address not found.")

      pipeline: Pipeline = self.create_pipeline(
        node_id=node_id,
        name=self.log.get_unique_id(),
        data_source="Void"
      )

      instance = pipeline.create_chain_dist_custom_plugin_instance(
        main_node_process_real_time_collected_data=main_node_process_real_time_collected_data,
        main_node_finish_condition=main_node_finish_condition,
        finish_condition_kwargs=main_node_finish_condition_kwargs,
        main_node_aggregate_collected_data=main_node_aggregate_collected_data,
        worker_node_code=worker_node_code,
        nr_remote_worker_nodes=nr_remote_worker_nodes,
        worker_node_plugin_config=worker_node_plugin_config,
        worker_node_pipeline_config=worker_node_pipeline_config,
        on_data=on_data,
        on_notification=on_notification,
      )

      if deploy:
        pipeline.deploy()

      return pipeline, instance
