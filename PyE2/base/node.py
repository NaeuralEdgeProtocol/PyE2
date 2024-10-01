from time import time

from ..const import COMMANDS, ENVIRONMENT, HB, PAYLOAD_DATA, STATUS_TYPE
from .payload import Payload
from .pipeline import Pipeline


class Node:
  def __init__(
      self,
      session,
      log,
      online_timeout: int,
      node_addr: str = None,
    ) -> None:
    from .generic_session import GenericSession

    self.__session: GenericSession = session
    self.log = log
    self.node_addr = node_addr
    self.online_timeout = online_timeout

    self._dct_pipelines: dict[str, Pipeline] = {}  # TODO: create pipeline objects

    self.on_data_callbacks = []
    self.temporary_on_data_callbacks = {}
    self.on_notification_callbacks = []
    self.temporary_on_notification_callbacks = {}
    self.on_heartbeat_callbacks = []
    self.temporary_on_heartbeat_callbacks = {}

    self._last_heartbeat = None
    self._last_seen_time = None

    self.created_pipelines = []

    return

  def _on_payload(self, dict_msg, msg_pipeline, msg_signature, msg_instance) -> None:
    for pipeline_name, pipeline in self._dct_pipelines.items():
      if msg_pipeline == pipeline_name:
        pipeline._on_data(msg_signature, msg_instance, Payload(dict_msg))
      # endif msg_pipeline == pipeline_name
    # endfor pipeline_name, pipeline in self._dct_pipelines.items()

    ### User callbacks ###
    for callback in self.on_data_callbacks:
      callback(self, self.node_addr, pipeline_name, msg_signature, msg_instance, dict_msg)
    # endfor callback in self.on_data_callbacks
    for callback in self.temporary_on_data_callbacks.values():
      callback(self, self.node_addr, pipeline_name, msg_signature, msg_instance, dict_msg)
    # endfor callback in self.temporary_on_data_callbacks.values()
    ### User callbacks ###
    return

  def _on_notification(self, dict_msg, msg_pipeline, msg_signature, msg_instance) -> None:
    for pipeline_name, pipeline in self._dct_pipelines.items():
      if msg_pipeline == pipeline_name:
        pipeline._on_notification(msg_signature, msg_instance, dict_msg)
      # endif msg_pipeline == pipeline_name
    # endfor pipeline_name, pipeline in self._dct_pipelines.items()

    ### User callbacks ###
    for callback in self.on_notification_callbacks:
      callback(self, self.node_addr, pipeline_name, msg_signature, msg_instance, dict_msg)
    # endfor callback in self.on_notification_callbacks
    for callback in self.temporary_on_notification_callbacks.values():
      callback(self, self.node_addr, pipeline_name, msg_signature, msg_instance, dict_msg)
    # endfor callback in self.temporary_on_notification_callbacks.values()
    ### User callbacks ###
    return

  def _on_heartbeat(self, dict_msg) -> None:
    self._last_heartbeat = dict_msg
    self._last_seen_time = time()

    ### Sync pipeline configurations ###
    msg_active_configs = dict_msg.get(HB.CONFIG_STREAMS)
    if msg_active_configs is None:
      return
    # endif msg_active_configs is None

    for config in msg_active_configs:
      pipeline_name = config[PAYLOAD_DATA.NAME]
      pipeline: Pipeline = self._dct_pipelines.get(pipeline_name, None)

      if pipeline is not None:
        pipeline._sync_configuration_with_remote({k.upper(): v for k, v in config.items()})
      else:
        self._dct_pipelines[pipeline_name] = self.__create_pipeline_from_config(config)
    # endfor config in msg_active_configs
    ### Sync pipeline configurations ###

    ### User callbacks ###
    for callback in self.on_data_callbacks:
      callback(self, self.node_addr, dict_msg)
    # endfor callback in self.on_data_callbacks
    for callback in self.temporary_on_data_callbacks.values():
      callback(self, self.node_addr, dict_msg)
    # endfor callback in self.temp_on_data_callbacks.values()
    ### User callbacks ###
    return

  def __create_pipeline_from_config(self, config):
    pipeline_config = {k.lower(): v for k, v in config.items()}
    name = pipeline_config.pop('name', None)
    plugins = pipeline_config.pop('plugins', None)

    pipeline = Pipeline(
      log=self.log,
      node=self,
      name=name,
      config={},
      plugins=plugins,
      is_attached=True,
      existing_config=pipeline_config,
    )

    return pipeline

  # Public properties
  if True:
    @property
    def session(self):
      return self.__session

    @property
    def id(self) -> str:
      return self._last_heartbeat.get(PAYLOAD_DATA.EE_ID, None)

    @property
    def address(self) -> str:
      return self.node_addr

    @property
    def is_supervisor(self) -> bool:
      return self._last_heartbeat.get(HB.EE_IS_SUPER, False)

    @property
    def last_heartbeat(self) -> dict:
      return self._last_heartbeat

    @property
    def last_seen_time(self) -> float:
      return self._last_seen_time

    @property
    def is_allowed(self) -> bool:
      node_whitelist = self._last_heartbeat.get(HB.EE_WHITELIST, [])
      node_secured = self._last_heartbeat.get(HB.SECURED, False)

      not_secured = not node_secured
      in_whitelist = self.bc_engine.address_no_prefix in node_whitelist
      is_self = self.__session.bc_engine.address == self.node_addr

      return not_secured or in_whitelist or is_self

    @property
    def is_online(self) -> bool:
      return self._last_seen_time is not None and time() - self._last_seen_time < self.online_timeout

    @property
    def active_pipelines(self) -> dict:
      return self._dct_pipelines

  # Public API
  if True:
    def P(self, *args, **kwargs):
      """
      Print info to stdout.
      """
      return self.log.P(*args, **kwargs)

    def D(self, *args, **kwargs):
      """
      Call the `Logger.D` method.
      If using the default Logger, this call will print debug info to stdout if `silent` is set to `False`.
      The logger object is passed from the Session object to the Pipeline object when creating
      it with `create_pipeline` or `attach_to_pipeline`.
      """
      return self.session.D(*args, **kwargs)

    def create_pipeline(self, *,
                        name,
                        data_source="Void",
                        config={},
                        plugins=[],
                        on_data=None,
                        on_notification=None,
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
      node : str
          Address or Name of the Naeural edge node that will handle this pipeline.
      name : str
          Name of the pipeline. This is good to be kept unique, as it allows multiple parties to overwrite each others configurations.
      data_source : str, optional
          This is the name of the DCT plugin, which resembles the desired functionality of the acquisition. Defaults to Void.
      config : dict, optional
          This is the dictionary that contains the configuration of the acquisition source, by default {}
      plugins : list, optional
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
      **kwargs :
          The user can provide the configuration of the acquisition source directly as kwargs.

      Returns
      -------
      Pipeline
          A `Pipeline` object.

      """

      pipeline = Pipeline(
          self.log,
          node=self,
          name=name,
          config=config,
          plugins=plugins,
          on_data=on_data,
          on_notification=on_notification,
          is_attached=False,
          type=data_source,
          **kwargs
      )
      self.created_pipelines.append(pipeline)
      self._dct_pipelines[name] = pipeline
      return pipeline

    def attach_to_pipeline(self, *,
                           name,
                           on_data=None,
                           on_notification=None
                           ) -> Pipeline:
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

      if name not in self._dct_pipelines:
        raise Exception("Unable to attach to pipeline. Pipeline does not exist")

      pipeline: Pipeline = self._dct_pipelines[name]

      if on_data is not None:
        pipeline._add_on_data_callback(on_data)
      if on_notification is not None:
        pipeline._add_on_notification_callback(on_notification)

      self.created_pipelines.append(pipeline)

      return pipeline

    def create_or_attach_to_pipeline(self, *,
                                     name,
                                     data_source,
                                     config={},
                                     plugins=[],
                                     on_data=None,
                                     on_notification=None,
                                     **kwargs) -> Pipeline:
      """
      Create a new pipeline on a node, or attach to an existing pipeline on an Naeural edge node.

      Parameters
      ----------
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
\      **kwargs :
          The user can provide the configuration of the acquisition source directly as kwargs.

      Returns
      -------
      Pipeline
          A `Pipeline` object.
      """

      pipeline = None
      try:
        pipeline = self.attach_to_pipeline(
          name=name,
          on_data=on_data,
          on_notification=on_notification,
        )

        possible_new_configuration = {
          **config,
          **{k.upper(): v for k, v in kwargs.items()}
        }

        if len(plugins) > 0:
          possible_new_configuration['PLUGINS'] = plugins

        if len(possible_new_configuration) > 0:
          pipeline.update_full_configuration(config=possible_new_configuration)
      except Exception as e:
        self.D("Failed to attach to pipeline: {}".format(e))
        pipeline = self.create_pipeline(
          name=name,
          data_source=data_source,
          config=config,
          plugins=plugins,
          on_data=on_data,
          on_notification=on_notification,
          **kwargs
        )

      return pipeline

    def deploy(self, timeout=10, with_confirmation=True, wait_confirmation=True):
      # TODO: implement this
      return

  # Available node commands
  if True:
    def stop(self):
      """
      Stop the node.

      The node will return a status code indicating that the Node was stopped.
      """
      raise NotImplementedError

    def restart_host(self):
      """
      Stop the node.

      The node will return a status code indicating the host to restart.
      (This behavior should be implemented by the user on the host)
      """
      raise NotImplementedError

    def request_simple_heartbeat(self):
      """
      Request a simple heartbeat from the node.

      Useful when one wants to quickly confirm that a change was made.
      """
      raise NotImplementedError

    def request_timers_only_heartbeat(self):
      """
      Request a heartbeat from the node, containing timers.

      Useful when one wants to check the performance of the node.
      """
      raise NotImplementedError

    def request_full_heartbeat(self):
      """
      Request a full heartbeat from the node.

      Useful when one wants to check the logs of the node.
      """
      raise NotImplementedError

    def reload_configuration_from_disk(self):
      """
      Reload the configuration of the node from disk.

      Useful when one edited the configuration locally and wants to reload it.
      """
      raise NotImplementedError

    def reset_whitelist_commands_to_default(self):
      """
      Reset the whitelist commands to default.

      Useful when one wants to reset the whitelist commands to default.
      """
      raise NotImplementedError

    def archive_all_pipelines(self):
      """
      Archive all pipelines on the node.

      Useful when one wants to stop all pipelines.
      """
      raise NotImplementedError

    def delete_all_pipelines(self):
      """
      Delete all pipelines on the node.

      Useful when one wants to stop all pipelines.
      """
      raise NotImplementedError

  # Available node plugin commands
  if True:
    def get_performance_history(self, *, node=None, steps=1, time_window_hours=1):
      """
      Get the performance history of a node.

      Useful when one wants to get resource utilization of a node.
      """
      raise NotImplementedError

    def get_plugin_default_configuration(self, plugin_name, plugin_type):
      """
      Get the default configuration of a plugin.

      Useful when one wants to know if a plugin exists on a node 
      and get the default configuration of that plugin.
      """
      raise NotImplementedError

    def check_update(self):
      """
      Check if the node has an update available.
      """
      raise NotImplementedError

    def get_node_config(self):
      """
      Get the configuration of the node (the config startup).
      """
      raise NotImplementedError

    def update_node_config(self, config):
      """
      Update the configuration of the node (the config startup).
      """
      raise NotImplementedError

    def get_whitelist_addresses(self):
      """
      Get the whitelist addresses of the node.

      The whitelist addresses are the addresses that are allowed to send commands to the node.
      """
      raise NotImplementedError

    def enable_local_communication(self):
      """
      Enable local communication on the node.
      """
      raise NotImplementedError

    def disable_local_communication(self):
      """
      Disable local communication on the node.
      """
      raise NotImplementedError
