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
from time import sleep
from time import time as tm
import traceback

from ..bc import DefaultBlockEngine

from ..utils.code import CodeUtils

from ..const import comms as comm_ct
from ..io_formatter import IOFormatterWrapper
from .logger import Logger
from .payload import Payload
from .pipeline import Pipeline


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
      "PEM_FILE": "e2.pem",
      "PASSWORD": None,
      "PEM_LOCATION": "data"
  }

  def __init__(self, *, host, port, user, pwd, name='pySDK', config={}, filter_workers=None, log=None, on_payload=None, on_notification=None, on_heartbeat=None, silent=True, blockchain_config=BLOCKCHAIN_CONFIG, **kwargs) -> None:
    """
    A Session is a connection to a communication server which provides the channel to interact with nodes from the AiXpand network.
    A Session manages `Pipelines` and handles all messages received from the communication server.
    The Session handles all callbacks that are user-defined and passed as arguments in the API calls.  

    Parameters
    ----------
    host : str
        The hostname of the server
    port : int
        The port
    user : str
        The user name
    pwd : str
        The password
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
    """
    if log is None:
      log = Logger(silent=silent)

    super(GenericSession, self).__init__()

    # maybe read config from file?
    self._config = {**self.default_config, **config}
    self.log = log
    self.name = name

    self._online_boxes = {}
    self._last_seen_boxes = {}
    self.online_timeout = 60
    self.filter_workers = filter_workers

    self._fill_config(host, port, user, pwd, name)

    self.custom_on_payload = on_payload
    self.custom_on_heartbeat = on_heartbeat
    self.custom_on_notification = on_notification

    self.on_payload = self._on_payload_default
    self.on_heartbeat = self._on_heartbeat_default
    self.on_notification = self._on_notification_default

    self.payload_instance_callbacks = []
    self.notification_instance_callbacks = []

    self.payload_pipeline_callbacks = []
    self.notification_pipeline_callbacks = []
    self.heartbeat_pipeline_callbacks = []
    self.own_pipelines = []

    self.connected = False

    self.formatter_wrapper = IOFormatterWrapper(log)

    try:
      self.bc_engine = DefaultBlockEngine(
        log=log,
        name=self.name,
        config=blockchain_config,
      )
    except:
      raise ValueError("Failure in private blockchain setup:\n{}".format(traceback.format_exc()))

    return

  @property
  def server(self):
    return self._config[comm_ct.HOST]

  def _fill_config(self, host, port, user, pwd, name):
    if self._config.get(comm_ct.SB_ID, None) is None:
      self._config[comm_ct.SB_ID] = name

    if self._config.get(comm_ct.USER, None) is None:
      self._config[comm_ct.USER] = user

    if self._config.get(comm_ct.PASS, None) is None:
      self._config[comm_ct.PASS] = pwd

    if self._config.get(comm_ct.HOST, None) is None:
      self._config[comm_ct.HOST] = host

    if self._config.get(comm_ct.PORT, None) is None:
      self._config[comm_ct.PORT] = port
    return

  def _parse_message(self, dict_msg: dict):
    formatter = self.formatter_wrapper \
        .get_required_formatter_from_payload(dict_msg)
    if formatter is not None:
      dict_msg = formatter.decode_output(dict_msg)
    return dict_msg

  def _maybe_ignore_message(self, e2id):
    return self.filter_workers is not None and e2id not in self.filter_workers

  def _track_online_node(self, e2id):
    self._last_seen_boxes[e2id] = tm()
    return

  def _on_heartbeat_default(self, dict_msg: dict):
    # extract relevant data from the message
    msg_eeid = dict_msg['EE_ID']

    if dict_msg.get("HEARTBEAT_VERSION") == "v2":
      str_data = CodeUtils().decompress_text(dict_msg["ENCODED_DATA"])
      data = json.loads(str_data)
      dict_msg = {**dict_msg, **data}

    msg_active_configs = dict_msg.get('CONFIG_STREAMS')
    if msg_active_configs is None:
      return

    # default action
    self._track_online_node(msg_eeid)
    self._online_boxes[msg_eeid] = {
        config['NAME']: config for config in msg_active_configs}

    if self._maybe_ignore_message(msg_eeid):
      return

    self.D("Received hb from: {}".format(msg_eeid))

    # call the custom callback, if defined
    if self.custom_on_heartbeat is not None:
      self.custom_on_heartbeat(self, msg_eeid, dict_msg)

    return

  def _on_notification_default(self, dict_msg: dict):
    # extract relevant data from the message
    msg_eeid = dict_msg['EE_ID']
    msg_stream = dict_msg.get('STREAM_NAME', None)
    notification_type = dict_msg.get("NOTIFICATION_TYPE")
    notification = dict_msg.get("NOTIFICATION")

    # default action
    self._track_online_node(msg_eeid)

    if self._maybe_ignore_message(msg_eeid):
      return

    color = None
    if notification_type != "NORMAL":
      color = 'r'
    self.D("Received notification {} from <{}/{}>: {}"
           .format(
              notification_type,
              msg_eeid,
              msg_stream,
              notification),
           color=color)

    # call the pipeline defined callbacks, if any
    for pipeline, callback in self.notification_pipeline_callbacks:
      if msg_eeid == pipeline.e2id and msg_stream == pipeline.name:
        callback(pipeline, Payload(dict_msg))

    # call the custom callback, if defined
    if self.custom_on_notification is not None:
      self.custom_on_notification(self, msg_eeid, Payload(dict_msg))

    return

  # TODO: maybe convert dict_msg to Payload object
  #       also maybe strip the dict from useless info for the user of the sdk
  #       Add try-except + sleep
  def _on_payload_default(self, dict_msg: dict) -> None:
    # extract relevant data from the message
    msg_eeid = dict_msg['EE_ID']
    msg_pipeline = dict_msg.get('STREAM', None)
    msg_signature = dict_msg.get('SIGNATURE', '').upper()
    msg_instance = dict_msg.get('INSTANCE_ID', None)
    msg_data = dict_msg

    self._track_online_node(msg_eeid)

    if self._maybe_ignore_message(msg_eeid):
      return

    for pipeline, callback in self.payload_pipeline_callbacks:
      if msg_eeid == pipeline.e2id and msg_pipeline == pipeline.name:
        callback(pipeline, msg_signature, msg_instance, Payload(msg_data))

    for pipeline, signature, instance, callback in self.payload_instance_callbacks:
      if msg_eeid == pipeline.e2id and msg_pipeline == pipeline.name and msg_signature == signature and msg_instance == instance:
        callback(pipeline, Payload(msg_data))

    if self.custom_on_payload is not None:
      self.custom_on_payload(self, msg_eeid, msg_pipeline, msg_signature, msg_instance, Payload(msg_data))

    return

  def _send_command_to_box(self, command, worker, payload):
    msg_to_send = {
        'EE_ID': worker,
        'SB_ID': worker,
        'ACTION': command,
        'PAYLOAD': payload,
        'INITIATOR_ID': self.name
    }
    self.bc_engine.sign(msg_to_send, use_digest=True)
    self._send_payload(worker, msg_to_send)

  def remove_pipeline_callbacks(self, pipeline) -> None:
    instance_indexes = [i for i, t in enumerate(
        self.payload_instance_callbacks) if t[0] == pipeline][::-1]
    for i in instance_indexes:
      self.payload_instance_callbacks.pop(i)

    pipeline_index = [i for i, t in enumerate(
        self.payload_pipeline_callbacks) if t[0] == pipeline][0]
    self.payload_pipeline_callbacks.pop(pipeline_index)
    return

  def remove_instance_callback(self, pipeline, signature, instance_id):
    instance_index = None

    for i, (cb_pipeline, cb_signature, cb_instance_id, _) in enumerate(self.payload_instance_callbacks):
      if cb_pipeline == pipeline and cb_signature == signature and cb_instance_id == instance_id:
        instance_index = i
        break

    self.payload_instance_callbacks.pop(instance_index)
    return

  def send_command_update_pipeline(self, worker, stream_config):
    self._send_command_to_box('UPDATE_CONFIG', worker, stream_config)

  def send_command_delete_pipeline(self, worker, stream_name):
    self._send_command_to_box('ARCHIVE_CONFIG', worker, stream_name)

  def _send_payload(self, to, payload):
    raise NotImplementedError

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
    self.log.D(*args, **kwargs)
    return

  def connect(self) -> None:
    """
    Connect to the communication server using the credentials provided when creating this instance.
    """
    raise NotImplementedError

  def maybe_reconnect(self) -> None:
    """
    Attempt reconnecting to the communication server if an unexpected disconnection ocurred,
    using the credentials provided when creating this instance.

    This method should be called in a user-defined main loop.
    This method is called in `run` method, in the main loop.
    """
    raise NotImplementedError

  def create_pipeline(self, *, e2id, name, data_source, config={}, plugins=[], on_data, on_notification=None, max_wait_time=0, **kwargs) -> Pipeline:
    """
    Create a new pipeline on a node. A pipeline is the equivalent of the "config file" used by the Hyperfy dev team internaly.

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
        Name of the AiXpand node that will handle this pipeline.  
    name : str
        Name of the pipeline. This is good to be kept unique, as it allows multiple parties to overwrite each others configurations.
    data_source : str
        This is the name of the DCT plugin, which resembles the desired functionality of the acquisition.
    on_data : Callable[[Pipeline, str, str, dict], None]
        Callback that handles messages received from any plugin instance. 
        As arguments, it has a reference to this Pipeline object, the signature and the instance of the plugin
        that sent the message and the payload itself.
        This callback acts as a default payload processor and will be called even if for a given instance
        the user has defined a specific callback.
    plugins : list
        List of dictionaries which contain the configurations of each plugin instance that is desired to run on the box. Defaults to []. Should be left [], and instances should be created with the api.
    config : dict, optional
        This is the dictionary that contains the configuration of the acquisition source, by default {}
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
    found = False
    while (tm() - _start) < max_wait_time:
      avail_workers = self.get_active_nodes()
      if e2id in avail_workers:
        found = True
        break
      sleep(0.1)

    if not found:
      self.P("WARNING: could not find worker '{}' in {:.1f}s. The job may not have a valid active worker.".format(
          e2id, tm() - _start
      ), color='r')
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

  def close_own_pipelines(self):
    """
    Close all pipelines that were created by or attached to this session.
    """
    # iterate through all CREATED pipelines from this session and close them
    for pipeline in self.own_pipelines:
      pipeline.close()
    return

  def close(self, close_pipelines=False, **kwargs):
    """
    Close the session, releasing all resources and closing all threads

    Parameters
    ----------
    close_pipelines : bool, optional
        close all the pipelines created by or attached to this session (basically calling `.close_own_pipelines()` for you), by default False
    """
    if close_pipelines:
      self.close_own_pipelines()
    return

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

  def attach_to_pipeline(self, e2id, pipeline_name, on_data, on_notification=None, max_wait_time=0, **kwargs) -> Pipeline:
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
    pipeline_name : str
        Name of the existing pipeline.
    on_data : Callable[[Pipeline, str, str, dict], None]
        Callback that handles messages received from any plugin instance. 
        As arguments, it has a reference to this Pipeline object, the signature and the instance of the plugin
        that sent the message and the payload itself.
        This callback acts as a default payload processor and will be called even if for a given instance
        the user has defined a specific callback.
    on_notification : Callable[[Pipeline, dict], None], optional
        Callback that handles notifications received from any plugin instance. 
        As arguments, it has a reference to this Pipeline object, along with the payload itself. 
        This callback acts as a default payload processor and will be called even if for a given instance
        the user has defined a specific callback.
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
    while (tm() - _start) < max_wait_time:
      avail_workers = self.get_active_nodes()
      if e2id in avail_workers and e2id in self._online_boxes:
        break
      sleep(0.1)

    if e2id not in self.get_active_nodes():
      raise Exception("Unable to attach to pipeline. Node does not exist")

    if pipeline_name not in self._online_boxes[e2id]:
      raise Exception("Unable to attach to pipeline. Pipeline does not exist")

    pipeline_config = {
        k.lower(): v for k, v in self._online_boxes[e2id][pipeline_name].items()}
    data_source = pipeline_config['type']
    return Pipeline(self, self.log, e2id=e2id, config={}, data_source=data_source, create_pipeline=False, on_data=on_data, on_notification=on_notification, **pipeline_config, **kwargs)

  def run(self, wait=True, close_session=True, close_pipelines=False):
    """
    This simple method will lock the main thread in a loop.
    This method can call `self.connect()`.
    This method can close the session and can close all pipelines when doing so.

    Parameters
    ----------
    wait : bool, float
        If `True`, will wait forever.
        If `False`, will not wait at all
        If type `float`, will wait said amount of seconds (Default value = True)
    close_session : bool, optional
        If `True` will close the session when the loop is exited. The default is True.
    close_pipelines : bool, optional
        If `True` will close all pipelines initiated by this session when the loop is exited. The default is True.
    """
    if not self.connected:
      self.connect()

    _start_timer = tm()
    try:
      while (isinstance(wait, bool) and wait) or (tm() - _start_timer) < wait:
        self.maybe_reconnect()
        sleep(0.1)
    except KeyboardInterrupt:
      self.P("CTRL+C detected. Stopping loop.", color='r')

    if close_session:
      self.close(close_pipelines=close_pipelines)
    return
