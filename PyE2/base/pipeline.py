# TODO: for custom plugin, do the plugin verification locally too

import os
from time import sleep, time

from ..code_cheker.base import BaseCodeChecker
from ..const import PAYLOAD_DATA
from .distributed_custom_code_presets import DistributedCustomCodePresets
from .instance import Instance
from .responses import PipelineArchiveResponse, PipelineOKResponse
from .transaction import Transaction


class Pipeline(BaseCodeChecker):
  """
  A `Pipeline` is a an object that encapsulates a one-to-many, data acquisition to data processing, flow of data.

  A `Pipeline` contains one thread of data acquisition (which does not mean only one source of data), and many
  processing units, usually named `Plugins`. 

  An `Instance` is a running thread of a `Plugin` type, and one may want to have multiple `Instances`, because each can be configured independently.

  As such, one will work with `Instances`, by reffering to them with the unique identifier (Pipeline, Plugin, Instance).

  In the documentation, the following reffer to the same thing:
    `Pipeline` == `Stream`

    `Plugin` == `Signature`
  """

  def __init__(self, session, log, *, node_addr, name, config={}, plugins=[], on_data=None, on_notification=None, is_attached=False, existing_config=None, **kwargs) -> None:
    """
    A `Pipeline` is a an object that encapsulates a one-to-many, data acquisition to data processing, flow of data.

    A `Pipeline` contains one thread of data acquisition (which does not mean only one source of data), and many
    processing units, usually named `Plugins`. 

    An `Instance` is a running thread of a `Plugin` type, and one may want to have multiple `Instances`, because each can be configured independently.

    As such, one will work with `Instances`, by referring to them with the unique identifier (Pipeline, Plugin, Instance).

    In the documentation, the following refer to the same thing:
      `Pipeline` == `Stream`

      `Plugin` == `Signature`

    Parameters
    ----------
    session : Session
        The Session object which owns this pipeline. A pipeline must be attached to a Session because that is the only
        way the `on_X` callbacks are called
    log : Logger
        A logger object which implements basic logging functionality and some other utils stuff. Can be ignored for now.
        In the future, the documentation for the Logger base class will be available and developers will be able to use
        custom-made Loggers. 
    node_addr : str
        Address of the Naeural edge node that will handle this pipeline.  
    name : str
        The name of this pipeline.
    data_source : str
        This is the name of the DCT plugin, which resembles the desired functionality of the acquisition.
    config : dict, optional
        This is the dictionary that contains the configuration of the acquisition source, by default {}
    plugins : List | None, optional
        This is the list with manually configured business plugins that will be in the pipeline at creation time.
        We recommend to leave this as `[]` or as `None` and use the API to create plugin instances. 
    on_data : Callable[[Pipeline, str, str, dict], None], optional,
        Callback that handles messages received from any plugin instance. 
        As arguments, it has a reference to this Pipeline object, along with the payload itself.
        This callback acts as a default payload processor and will be called even if for a given instance
        the user has defined a specific callback.
        Defaults to None.
    on_notification : Callable[[Pipeline, dict], None], optional
        Callback that handles notifications received from this instance. 
        As arguments, it has a reference to this Pipeline object, along with the payload itself. 
        This callback acts as a default payload processor and will be called even if for a given instance
        the user has defined a specific callback.
        Defaults to None.
    is_attached : bool
        This is used internally to allow the user to create or attach to a pipeline, and then use the same
        objects in the same way, by default True
    **kwargs : dict
        The user can provide the configuration of the acquisition source directly as kwargs.
    """
    self.log = log
    self.session = session
    self.node_addr = node_addr
    self.name = name

    self.config = {}
    plugins = config.pop('PLUGINS', plugins)

    if is_attached:
      assert existing_config is not None, "When attaching to a pipeline, the existing configuration should be found in the heartbeat of the Naeural edge node."
      assert config == {}, "Cannot provide a configuration when attaching to a pipeline."
      assert len(kwargs) == 0, "Cannot provide a configuration when attaching to a pipeline."
      self.config = {k.upper(): v for k, v in existing_config.items()}
      self.config = self.__pop_ignored_keys_from_config(self.config)
      self.proposed_config = None
    else:
      self.proposed_config = {**config, **kwargs}
      self.proposed_config = {k.upper(): v for k, v in self.proposed_config.items()}
      self.proposed_config = self.__pop_ignored_keys_from_config(self.proposed_config)
    self.__staged_config = None

    self.__was_last_operation_successful = None

    self.proposed_remove_instances = []
    self.__staged_remove_instances = []

    self.on_data_callbacks = []
    self.on_notification_callbacks = []

    if on_data is not None:
      self.on_data_callbacks.append(on_data)
    if on_notification is not None:
      self.on_notification_callbacks.append(on_notification)

    self.lst_plugin_instances: list[Instance] = []

    self.__init_plugins(plugins, is_attached)
    return

  # Utils
  if True:
    def __init_instance(self, signature, instance_id, config, on_data, on_notification, is_attached):
      instance_class = None
      str_signature = None
      if isinstance(signature, str):
        instance_class = Instance
        str_signature = signature.upper()
      else:
        instance_class = signature
        str_signature = instance_class.signature.upper()
      instance = instance_class(self.log,
                                pipeline=self,
                                signature=str_signature,
                                instance_id=instance_id,
                                config=config,
                                on_data=on_data,
                                on_notification=on_notification,
                                is_attached=is_attached
                                )
      self.lst_plugin_instances.append(instance)
      return instance

    def __init_plugins(self, plugins, is_attached):
      """
      Initialize the plugins list. This method is called at the creation of the pipeline and is used to create the instances of the plugins that are part of the pipeline.

      Parameters
      ----------
      plugins : List | None
        The list of plugins, as they are found in the pipeline configuration dictionary in the heartbeat.
      is_attached : bool
        This is used internally to allow the user to create or attach to a pipeline, and then use the same objects in the same way.

      """
      if plugins is None:
        return

      for dct_signature_instances in plugins:
        signature = dct_signature_instances['SIGNATURE']
        instances = dct_signature_instances['INSTANCES']
        for dct_instance in instances:
          config = {k.upper(): v for k, v in dct_instance.items()}
          instance_id = config.pop('INSTANCE_ID')
          self.__init_instance(signature, instance_id, config, None, None, is_attached=is_attached)
        # end for dct_instance
      # end for dct_signature_instances
      return

    def __get_proposed_pipeline_config(self):
      """
      Construct the proposed pipeline configuration dictionary.

      Returns
      -------
      dict
          The proposed pipeline configuration dictionary.
      """

      plugin_dict = self.__construct_plugins_dictionary(skip_instances=self.proposed_remove_instances)

      plugins_list = []
      for signature, instances in plugin_dict.items():
        plugins_list.append({
          'SIGNATURE': signature,
          'INSTANCES': [instance._get_proposed_config_dictionary(full=True) for instance in instances]
        })

      proposed_pipeline_config = {
        'NAME': self.name,
        'DEFAULT_PLUGIN': False,
        'PLUGINS': plugins_list,
        **self.config,
        **(self.proposed_config or {}),
      }
      return proposed_pipeline_config

    def __register_transactions_for_update(self, session_id: str = None, timeout: float = 0) -> list[Transaction]:
      """
      Register transactions for updating the pipeline and instances configuration. 
      This method is called before sending an update pipeline configuration command to the Naeural edge node.

      Parameters
      ----------
      session_id : str, optional
          The session id. A unique id for the session. Defaults to None.

      timeout : int, optional
          The timeout for the transaction. Defaults to 0.

      Returns
      -------
      transactions : list[Transaction]
          The list of transactions generated.
      """
      transactions = []

      # TODO: add different responses for different states of the plugin
      # TODO: maybe this should be introduced as "pre-defined" business plugins, based on a schema
      #       and the user can specify them when creating the pipeline

      for instance in self.lst_plugin_instances:
        if instance._is_tainted():
          transactions.append(self.session._register_transaction(
            session_id=session_id,
            lst_required_responses=instance._get_instance_update_required_responses(),
            timeout=timeout,
            on_success_callback=instance._apply_staged_config,
            # TODO: if the instance was newly added, remove it from the tracked list
            on_failure_callback=instance._discard_staged_config,
          ))
      # end for register to update instances

      for instance in self.proposed_remove_instances:
        transactions.append(self.session._register_transaction(
          session_id=session_id,
          lst_required_responses=instance._get_instance_remove_required_responses(),
          timeout=timeout,
          on_success_callback=lambda: self.__apply_staged_remove_instance(instance),
          on_failure_callback=lambda fail_reason: self.__discard_staged_remove_instance(instance, fail_reason),
        ))
      # end for register to remove instances

      if self.proposed_config is not None:
        required_responses = [
          PipelineOKResponse(self.node_id, self.name),
        ]
        transactions.append(self.session._register_transaction(
          session_id=session_id,
          lst_required_responses=required_responses,
          timeout=timeout,
          on_success_callback=self.__apply_staged_config,
          on_failure_callback=self.__discard_staged_config,
        ))

      return transactions

    def __register_transactions_for_delete(self, session_id: str = None, timeout: float = 0) -> list[Transaction]:
      """
      Register transactions for deleting the pipeline. 
      This method is called before sending a delete pipeline command to the Naeural edge node.

      Parameters
      ----------
      session_id : str, optional
          The session id. A unique id for the session. Defaults to None.

      timeout : int, optional
          The timeout for the transaction. Defaults to 0.

      Returns
      -------
      transactions : list[Transaction]
          The list of transactions generated.
      """
      transactions = []

      required_responses = [
        PipelineArchiveResponse(self.node_id, self.name),
      ]
      transactions.append(self.session._register_transaction(
        session_id=session_id,
        lst_required_responses=required_responses,
        timeout=timeout,
        on_success_callback=self.__set_last_operation_successful,
        on_failure_callback=self.__set_last_operation_failed,
      ))

      return transactions

    def __register_transaction_for_pipeline_command(self, session_id: str = None, timeout: float = 0) -> list[Transaction]:
      """
      Register a transaction for a pipeline command. 
      This method is called before sending a pipeline command to the Naeural edge node.

      Parameters
      ----------
      session_id : str, optional
          The session id. A unique id for the session. Defaults to None.

      timeout : int, optional
          The timeout for the transaction. Defaults to 0.

      Returns
      -------
      transactions : list[Transaction]
          The list of transactions generated.
      """
      transactions = []

      # TODO: implement
      self.__set_last_operation_successful()

      return transactions

    def __construct_plugins_list(self):
      """
      Construct the plugins list that will be in the pipeline configuration dictionary.

      Returns
      -------
      list
          The plugins list that will be in the pipeline configuration dictionary.
      """
      plugins = []
      dct_signature_instances = {}
      for instance in self.lst_plugin_instances:
        signature = instance.signature
        if instance.signature not in dct_signature_instances:
          dct_signature_instances[instance.signature] = []
        dct_signature_instances[instance.signature].append(instance)
      # end for construct dct_signature_instances

      for signature, instances in dct_signature_instances.items():
        plugins.append({
          'SIGNATURE': signature,
          'INSTANCES': [instance._get_config_dictionary() for instance in instances]
        })
      # end for construct plugins list
      return plugins

    def __construct_plugins_dictionary(self, skip_instances=None):
      """
      Construct the plugins dictionary that will be in the pipeline configuration dictionary.

      Returns
      -------
      dict
          The plugins dictionary that will be in the pipeline configuration dictionary.
      """
      # plugins = []
      skip_instances = skip_instances or []
      dct_signature_instances = {}
      for instance in self.lst_plugin_instances:
        if instance in skip_instances:
          continue
        if instance.signature not in dct_signature_instances:
          dct_signature_instances[instance.signature] = []
        dct_signature_instances[instance.signature].append(instance)
      # end for construct dct_signature_instances

      return dct_signature_instances

    def __send_update_config_to_box(self, session_id=None):
      """
      Send an update pipeline configuration command to the Naeural edge node.
      """
      self.session._send_command_update_pipeline_config(
          worker=self.node_addr,
          pipeline_config=self.__get_proposed_pipeline_config(),
          session_id=session_id
      )
      return

    def __batch_update_instances(self, lst_instances, session_id=None):
      """
      Update the configuration of multiple instances at once.
      ```

      Parameters
      ----------
      lst_updates : List[Instance]
          A list of instances.
      """
      lst_updates = []

      for instance in lst_instances:
        lst_updates.append({
          PAYLOAD_DATA.NAME: self.name,
          PAYLOAD_DATA.SIGNATURE: instance.signature,
          PAYLOAD_DATA.INSTANCE_ID: instance.instance_id,
          PAYLOAD_DATA.INSTANCE_CONFIG: instance._get_proposed_config_dictionary(full=False)
        })

      self.session._send_command_batch_update_instance_config(
        worker=self.node_addr,
        lst_updates=lst_updates,
        session_id=session_id
      )

    def __pop_ignored_keys_from_config(self, config):
      """
      Pop the ignored keys from the configuration.

      Parameters
      ----------
      config : dict
          The configuration dictionary.

      Returns
      -------
      dict
          The configuration dictionary without the ignored keys.
      """
      ignored_keys = ["INITIATOR_ADDR", "INITIATOR_ID", "LAST_UPDATE_TIME", "MODIFIED_BY_ADDR", "MODIFIED_BY_ID"]
      return {k: v for k, v in config.items() if k not in ignored_keys}

    def __get_instance_object(self, signature, instance_id):
      """
      Get the instance object by signature and instance id.

      Parameters
      ----------
      signature : str
          The signature of the plugin.
      instance_id : str
          The name of the instance.

      Returns
      -------
      Instance
          The instance object.
      """
      for instance in self.lst_plugin_instances:
        if instance.signature == signature and instance.instance_id == instance_id:
          return instance
      return None

    def __set_last_operation_successful(self):
      """
      Set the last operation successful.
      """
      self.__was_last_operation_successful = True
      return

    def __set_last_operation_failed(self, fail_reason):
      """
      Set the last operation failed.
      """
      self.__was_last_operation_successful = False
      return

    @staticmethod
    def __custom_exec_on_data(self, instance_id, on_data_callback, data):
      """
      Handle the data received from a custom execution instance. This method is called by the Session object when a message is received from a custom execution instance.

      Parameters
      ----------
      instance_id : str
          The name of the instance that sent the message.
      on_data_callback : Callable[[Pipeline, dict, dict], None]
          The callback that handles the message. The first dict is the payload, and the second dict is the entire message.
      data : dict | Payload
          The payload of the message.
      """
      # TODO: use formatter for this message
      # TODO: expose the other fields from data
      exec_data = None

      exec_data = data.get('EXEC_RESULT', data.get('EXEC_INFO'))
      exec_error = data.get('EXEC_ERRORS', 'no keyword error')

      if exec_error is not None:
        self.P("Error received from <CUSTOM_EXEC_01:{}>: {}".format(instance_id, exec_error), color="r", verbosity=1)
      if exec_data is not None:
        on_data_callback(self, exec_data, data)
      return

    def __apply_staged_remove_instance(self, instance: Instance):
      """
      Remove an instance from the pipeline.

      Parameters
      ----------
      instance : Instance
          The instance to be removed.
      """
      instance.config = None
      try:
        self.__staged_remove_instances.remove(instance)
      except:
        self.P("Attempted to remove instance <{}:{}>, but it was not found in the staged remove list. "
               "Most likely the instance deletion used `with_confirmation=False`".format(
                   instance.signature, instance.instance_id), color="r")
      return

    def __discard_staged_remove_instance(self, instance: Instance, fail_reason: str):
      """
      Discard the removal of an instance from the pipeline.

      Parameters
      ----------
      instance : Instance
          The instance to be removed.
      """

      self.P(
        f"Discarding staged removal of instance <{instance.signature}:{instance.instance_id}>. Reason: {fail_reason}", color="r")

      try:
        self.__staged_remove_instances.remove(instance)
      except:
        self.P("Attempted to remove instance <{}:{}>, but it was not found in the staged remove list. "
               "Most likely the instance deletion used `with_confirmation=False`".format(
                   instance.signature, instance.instance_id), color="r")

      self.lst_plugin_instances.append(instance)
      return

    def __apply_staged_config(self, verbose=False):
      """
      Apply the staged configuration to the pipeline.
      """
      if self.__staged_config is None:
        return

      if verbose:
        self.P("Deployed pipeline <{}> on <{}>".format(self.name, self.node_addr), color="g")
      self.__was_last_operation_successful = True

      self.config = {**self.config, **self.__staged_config}
      self.__staged_config = None

      return

    def __apply_staged_instances_config(self, verbose=False):
      """
      Apply the staged configuration to the instances.
      """
      for instance in self.lst_plugin_instances:
        instance._apply_staged_config(verbose=verbose)

      for instance in self.__staged_remove_instances:
        instance.config = None
        self.lst_plugin_instances.remove(instance)

      self.__staged_remove_instances = []
      return

    def __discard_staged_config(self, fail_reason: str):
      """
      Discard the staged configuration for the pipeline.
      """

      self.P(f'Discarding staged configuration for pipeline <{self.name}>. Reason: {fail_reason}', color="r")
      self.__was_last_operation_successful = False

      self.__staged_config = None
      self.__staged_remove_instances = []
      return

    def __stage_proposed_config(self):
      """
      Stage the proposed configuration.
      """
      if self.proposed_config is not None:
        if self.__staged_config is not None:
          raise ValueError(
            "Pipeline configuration has already been staged, waiting for confirmation from Execution Engine")

        self.__staged_config = self.proposed_config
        self.proposed_config = None

      for instance in self.lst_plugin_instances:
        instance._stage_proposed_config()

      self.__staged_remove_instances.extend(self.proposed_remove_instances)
      self.proposed_remove_instances = []

      self.__was_last_operation_successful = None
      return

    def __print_proposed_changes(self):
      """
      Print the proposed changes to the pipeline.
      """

      if self.proposed_config is not None:
        self.P("Proposed changes to pipeline <{}>:".format(self.name), verbosity=1)
        self.P("  - Current config: {}".format(self.config), verbosity=1)
        self.P("  - New pipeline config: {}".format(self.proposed_config), verbosity=1)

      if len(self.proposed_remove_instances) > 0:
        self.P(
          "  - Remove instances: {}".format([instance.instance_id for instance in self.proposed_remove_instances]), verbosity=1)

      for instance in self.lst_plugin_instances:
        if instance._is_tainted():
          self.P("  - Plugin <{}:{}>:".format(instance.signature, instance.instance_id), verbosity=1)
          self.P("    - Current config: {}".format(instance.config), verbosity=1)
          self.P("    - Proposed config: {}".format(instance.proposed_config), verbosity=1)
      return

    def _close(self, timeout=10):
      """
      Close the pipeline.

      Returns
      -------
      list[Transaction]
          The list of transactions generated.
      """
      transactions = self.__register_transactions_for_delete(timeout=timeout)

      self.__was_last_operation_successful = None

      self.session._send_command_archive_pipeline(
        worker=self.node_addr,
        pipeline_name=self.name,
      )

      return transactions

    def _get_base64_code(self, custom_code):
      """
      Get the base64 code.

      Parameters
      ----------
      custom_code : str | callable
          The custom code.

      Returns
      -------
      str
          The base64 code.
      """
      if custom_code is None:
        return None

      if isinstance(custom_code, str):
        # it is a path
        if os.path.exists(custom_code):
          with open(custom_code, "r") as fd:
            plain_code = "".join(fd.readlines())
        # it is a string
        else:
          try:
            method_name = "_DistributedCustomCodePresets__{}".format(custom_code.lower())
            preset_code = getattr(DistributedCustomCodePresets, method_name)
            plain_code = self.get_function_source_code(preset_code)
          except:
            plain_code = custom_code
      elif callable(custom_code):
        # we have a function
        plain_code = self.get_function_source_code(custom_code)
      else:
        raise Exception("custom_code is not a string or a callable")
      # endif get plain code

      return self.code_to_base64(plain_code, verbose=False)

  # Message handling
  if True:
    def _on_data(self, signature, instance_id, data):
      """
      Handle the data received from the Naeural edge node. This method is called by the Session object when a message is received from the Naeural edge node.
      This method will call all the `on_data` callbacks of the pipeline and the instance that received the message.

      Parameters
      ----------
      signature : str
          The signature of the plugin that sent the message.
      instance_id : str
          The name of the instance that sent the message.
      data : dict | Payload
          The payload of the message.
      """
      # call all self callbacks
      for callback in self.on_data_callbacks:
        callback(self, signature, instance_id, data)

      # call all instance callbacks
      self.__call_instance_on_data_callbacks(signature, instance_id, data)
      return

    def _on_notification(self, signature, instance_id, data):
      """
      Handle the notification received from the Naeural edge node. This method is called by the Session object when a notification is received from the Naeural edge node.

      Parameters
      ----------
      signature : str
          The signature of the plugin that sent the notification.
      instance_id : str
          The name of the instance that sent the notification.
      data : dict | Payload
          The payload of the notification.
      """
      # call all self callbacks
      for callback in self.on_notification_callbacks:
        callback(self, data)

      # call all instance callbacks
      self.__call_instance_on_notification_callbacks(signature, instance_id, data)
      return

    def _add_on_data_callback(self, callback):
      """
      Add a new callback to the list of callbacks that handle the data received from the pipeline.

      Parameters
      ----------
      callback : Callable[[Pipeline, str, str, dict], None]
          The callback to add
      """
      self.on_data_callbacks.append(callback)
      return

    def _reset_on_data_callback(self):
      """
      Reset the list of callbacks that handle the data received from the pipeline.
      """
      self.on_data_callbacks = []
      return

    def _add_on_notification_callback(self, callback):
      """
      Add a new callback to the list of callbacks that handle the notifications received from the pipeline.

      Parameters
      ----------
      callback : Callable[[Pipeline, dict], None]
          The callback to add
      """
      self.on_notification_callbacks.append(callback)
      return

    def _reset_on_notification_callback(self):
      """
      Reset the list of callbacks that handle the notifications received from the pipeline.
      """
      self.on_notification_callbacks = []
      return

    def __call_instance_on_data_callbacks(self, signature, instance_id, data):
      """
      Call all the `on_data` callbacks of the instance that sent the message.

      Parameters
      ----------
      signature : str
          The signature of the plugin that sent the payload.
      instance_id : str
          The name of the instance that sent the payload.
      data : dict | Payload
          The payload of the payload.
      """
      for instance in self.lst_plugin_instances:
        if instance.signature == signature and instance.instance_id == instance_id:
          instance._on_data(self, data)
      return

    def __call_instance_on_notification_callbacks(self, signature, instance_id, data):
      """
      Call all the `on_notification` callbacks of the instance that sent the notification.

      Parameters
      ----------
      signature : str
          The signature of the plugin that sent the notification.
      instance_id : str
          The name of the instance that sent the notification.
      data : dict | Payload
          The payload of the notification.
      """
      for instance in self.lst_plugin_instances:
        if instance.signature == signature and instance.instance_id == instance_id:
          instance._on_notification(self, data)
      return

  # API
  if True:
    @property
    def was_last_operation_successful(self):
      """
      Return whether the last operation was successful.

      Returns
      -------
      bool
          True if the last operation was successful, False if it failed, None if the ACK has not been received yet
      """
      return self.__was_last_operation_successful

    def create_plugin_instance(self, *, signature, instance_id, config={}, on_data=None, on_notification=None, **kwargs) -> Instance:
      """
      Create a new instance of a desired plugin, with a given configuration. This instance is attached to this pipeline, 
      meaning it processes data from this pipelines data source. Parameters can be passed either in the `config` dict, or as `kwargs`.

      Parameters
      ----------
      signature : str
          The name of the plugin signature. This is the name of the desired overall functionality.
      instance_id : str
          The name of the instance. There can be multiple instances of the same plugin, mostly with different parameters
      config : dict, optional
          parameters used to customize the functionality. One can change the AI engine used for object detection, 
          or finetune alerter parameters to better fit a camera located in a low light environment.
          Defaults to {}
      on_data : Callable[[Pipeline, dict], None], optional
          Callback that handles messages received from this instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself.
          Defaults to None
      on_notification : Callable[[Pipeline, dict], None], optional
          Callback that handles notifications received from this instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself. 
          Defaults to None

      Returns
      -------
      instance : Instance
          An `Instance` object.

      Raises
      ------
      Exception
          Plugin instance already exists. 
      """
      if isinstance(signature, str):
        str_signature = signature.upper()
      else:
        plugin_template = signature
        str_signature = plugin_template.signature.upper()

      for instance in self.lst_plugin_instances:
        if instance.instance_id == instance_id and instance.signature == str_signature:
          raise Exception("plugin {} with instance {} already exists".format(str_signature, instance_id))

      # create the new instance and add it to the list
      config = {**config, **kwargs}
      instance = self.__init_instance(signature, instance_id, config, on_data, on_notification, is_attached=False)
      return instance

    def __remove_plugin_instance(self, instance):
      """
      Remove a plugin instance from this pipeline. 

      Parameters
      ----------
      instance : Instance
          The instance to be removed.
      """
      if instance is None:
        raise Exception("The provided instance is None. Please provide a valid instance")

      if instance not in self.lst_plugin_instances:
        raise Exception("plugin  <{}/{}> does not exist on this pipeline".format(instance.signature, instance.instance_id))

      self.lst_plugin_instances.remove(instance)
      return

    def remove_plugin_instance(self, instance):
      """
      Stop a plugin instance from this pipeline. 


      Parameters
      ----------
      instance : Instance
          The instance to be stopped.

      """

      self.__remove_plugin_instance(instance)
      self.proposed_remove_instances.append(instance)
      return

    def create_custom_plugin_instance(self, *, instance_id, custom_code: callable, config={}, on_data=None, on_notification=None, **kwargs) -> Instance:
      """
      Create a new custom execution instance, with a given configuration. This instance is attached to this pipeline, 
      meaning it processes data from this pipelines data source. The code used for the custom instance must be provided
      either as a string, or as a path to a file. Parameters can be passed either in the `config` dict, or as kwargs.
      The custom plugin instance will run periodically. If one desires to execute a custom code only once, use `wait_exec`.

      Parameters
      ----------
      instance_id : str
          The name of the instance. There can be multiple instances of the same plugin, mostly with different parameters
      custom_code : Callable[[CustomPluginTemplate], Any], optional
          A string containing the entire code, a path to a file containing the code as a string or a function with the code.
          This code will be executed remotely on an Naeural edge node. Defaults to None.
      config : dict, optional
          parameters used to customize the functionality. One can change the AI engine used for object detection, 
          or finetune alerter parameters to better fit a camera located in a low light environment.
          Defaults to {}
      on_data : Callable[[Pipeline, dict], None], optional
          Callback that handles messages received from this instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself.
          Defaults to None
      on_notification : Callable[[Pipeline, dict], None], optional
          Callback that handles notifications received from this instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itsel. 
          Defaults to None

      Returns
      -------
      instance : Instance
          An `Instance` object.

      Raises
      ------
      Exception
          The code was not provided.
      Exception
          Plugin instance already exists. 
      """

      b64code = self._get_base64_code(custom_code)

      def callback(pipeline, data): return self.__custom_exec_on_data(pipeline, instance_id, on_data, data)
      callback = callback if on_data is not None else None

      return self.create_plugin_instance(
          signature='CUSTOM_EXEC_01',
          instance_id=instance_id,
          config={
              'CODE': b64code,
              **config
          },
          on_data=callback,
          on_notification=on_notification,
          **kwargs
      )

    # TODO: rename this!!!
    def create_chain_dist_custom_plugin_instance(self,
                                                 *,
                                                 main_node_process_real_time_collected_data: any,
                                                 main_node_finish_condition: any,
                                                 main_node_aggregate_collected_data: any,
                                                 worker_node_code: any,
                                                 nr_remote_worker_nodes: int,
                                                 instance_id=None,
                                                 worker_node_pipeline_config={},
                                                 worker_node_plugin_signature='CUSTOM_EXEC_01',
                                                 worker_node_plugin_config={},
                                                 config={},
                                                 on_data=None,
                                                 on_notification=None,
                                                 **kwargs) -> Instance:
      b64code_process_real_time_collected_data = self._get_base64_code(main_node_process_real_time_collected_data)
      b64code_finish_condition = self._get_base64_code(main_node_finish_condition)
      b64code_aggregate_collected_data = self._get_base64_code(main_node_aggregate_collected_data)
      b64code_remote_node = self._get_base64_code(worker_node_code)

      if instance_id is None:
        instance_id = self.name + "_chain_dist_custom_exec_{}".format(self.log.get_unique_id())

      return self.create_plugin_instance(
          signature='PROCESS_REAL_TIME_COLLECTED_DATA_CUSTOM_EXEC_CHAIN_DIST',
          instance_id=instance_id,
          config={
              'CUSTOM_CODE_PROCESS_REAL_TIME_COLLECTED_DATA': b64code_process_real_time_collected_data,
              'CUSTOM_CODE_FINISH_CONDITION': b64code_finish_condition,
              'CUSTOM_CODE_AGGREGATE_COLLECTED_DATA': b64code_aggregate_collected_data,
              'CUSTOM_CODE_REMOTE_NODE': b64code_remote_node,

              'NR_REMOTE_NODES': nr_remote_worker_nodes,

              'NODE_PIPELINE_CONFIG': {
                'stream_type': "Void",
                **worker_node_pipeline_config
              },
              'NODE_PLUGIN_SIGNATURE': worker_node_plugin_signature,
              'NODE_PLUGIN_CONFIG': {
                **worker_node_plugin_config
              },
              **config
          },
          on_data=on_data,
          on_notification=on_notification,
          **kwargs
      )

    def deploy(self, with_confirmation=True, wait_confirmation=True, timeout=10, verbose=False):
      """
      This method is used to deploy the pipeline on the Naeural edge node. 
      Here we collect all the proposed configurations and send them to the Naeural edge node.
      All proposed configs become staged configs.
      After all responses, apply the staged configs to finish the transaction. 
      """
      # generate a unique session id for this deploy operation
      # this session id will be used to track the transactions

      # step 0: print the proposed changes
      if verbose:
        self.__print_proposed_changes()

      # step 1: register transactions for updates
      transactions = []

      if with_confirmation:
        transactions: list[Transaction] = self.__register_transactions_for_update(timeout=timeout)

      # step 1: send the proposed config to the box
      pipeline_config_changed = self.proposed_config is not None
      have_to_remove_instances = len(self.proposed_remove_instances) > 0
      have_new_instances = any([instance._is_tainted() and len(instance.config) == 0
                                for instance in self.lst_plugin_instances])
      if pipeline_config_changed or have_to_remove_instances or have_new_instances:
        # updated pipeline config or deleted instances
        self.__send_update_config_to_box()
      elif any([instance._is_tainted() for instance in self.lst_plugin_instances]):
        # updated instances only
        tainted_instances = [instance for instance in self.lst_plugin_instances if instance._is_tainted()]
        self.__batch_update_instances(tainted_instances)
      else:
        return

      # step 3: stage the proposed config
      self.__stage_proposed_config()

      # step 3: wait for the box to respond
      if with_confirmation and wait_confirmation:
        self.session.wait_for_transactions(transactions)

      # step 4: apply the staged config
      if not with_confirmation:
        self.__apply_staged_config(verbose=verbose)
        self.__apply_staged_instances_config(verbose=verbose)

      self.P("Pipeline <{}> deployed".format(self.name), color="g")

      if with_confirmation and not wait_confirmation:
        return transactions
      return

    def wait_exec(self, *, custom_code: callable, instance_config={}, timeout=10):
      """
      Create a new REST-like custom execution instance, with a given configuration. This instance is attached to this pipeline, 
      meaning it processes data from this pipelines data source. The code used for the custom instance must be provided either as a string, or as a path to a file. Parameters can be passed either in the config dict, or as kwargs.
      The REST-like custom plugin instance will execute only once. If one desires to execute a custom code periodically, use `create_custom_plugin_instance`.

      Parameters
      ----------
      custom_code : Callable[[CustomPluginTemplate], Any], optional
          A string containing the entire code, a path to a file containing the code as a string or a function with the code.
          This code will be executed remotely on an Naeural edge node. Defaults to None.
      config : dict, optional
          parameters used to customize the functionality, by default {}

      Returns
      -------
      Tuple[Any, Any]
          a tuple containing the result of the execution and the error, if any. 
          If the execution completed successfully, the `error` is None, and the `result` is the returned value of the custom code.

      Raises
      ------
      Exception
          The code was not provided.
      Exception
          Plugin instance already exists. 
      """

      b64code = self._get_base64_code(custom_code)

      finished = False
      result = None
      error = None

      def on_data(pipeline, data):
        nonlocal finished
        nonlocal result
        nonlocal error

        if 'REST_EXECUTION_RESULT' in data and 'REST_EXECUTION_ERROR' in data:
          result = data['REST_EXECUTION_RESULT']
          error = data['REST_EXECUTION_ERROR']
          finished = True
        return

      instance_id = self.name + "_rest_custom_exec_synchronous_" + self.log.get_unique_id()
      instance_config = {
          'REQUEST': {
              'DATA': {
                  'CODE': b64code,
              },
              'TIMESTAMP': self.log.time_to_str()
          },
          'RESULT_KEY': 'REST_EXECUTION_RESULT',
          'ERROR_KEY': 'REST_EXECUTION_ERROR',
          **instance_config
      }

      prop_config = self.__get_proposed_pipeline_config()
      if prop_config['TYPE'] == 'Void':
        instance_config['ALLOW_EMPTY_INPUTS'] = True
        instance_config['RUN_WITHOUT_IMAGE'] = True

      self.create_plugin_instance(
          signature='REST_CUSTOM_EXEC_01',
          instance_id=instance_id,
          config=instance_config,
          on_data=on_data
      )

      self.deploy()

      start_time = time()
      while not finished and time() - start_time < timeout:
        sleep(0.1)

      return result, error

    def close(self, wait_confirmation=True, timeout=10):
      """
      Close the pipeline, stopping all the instances associated with it.
      """

      transactions = self._close(timeout=timeout)

      if wait_confirmation:
        self.session.wait_for_transactions(transactions)
      else:
        return transactions
      return

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

    def attach_to_plugin_instance(self, signature, instance_id, on_data=None, on_notification=None) -> Instance:
      """
      Attach to an existing instance on this pipeline. 
      This method is useful when one wishes to attach an 
      `on_data` and `on_notification` callbacks to said instance.

      Parameters
      ----------
      signature : str
          name of the plugin signature.
      instance_id : str
          name of the instance.
      on_data : Callable[[Pipeline, dict], None], optional
          Callback that handles messages received from this instance. As arguments, it has a reference to this Pipeline object, along with the payload itself.
          Defaults to None.
      on_notification : Callable[[Pipeline, dict], None], optional
          Callback that handles notifications received from this instance. As arguments, it has a reference to this Pipeline object, along with the payload itself.
          Defaults to None.

      Returns
      -------
      instance : Instance
          An `Instance` object.

      Raises
      ------
      Exception
          the pipeline does not contain plugins with a given signature.
      Exception
          The pipeline does not contain the desired instance.
      """

      # search for the instance in the list
      plugin_template = None
      if isinstance(signature, str):
        str_signature = signature.upper()
      else:
        plugin_template = signature
        str_signature = plugin_template.signature.upper()
      found_instance = None
      for instance in self.lst_plugin_instances:
        if instance.instance_id == instance_id and instance.signature == str_signature.upper():
          found_instance = instance
          break

      if found_instance is None:
        raise Exception(f"Unable to attach to instance. Instance <{str_signature}/{instance_id}> does not exist")

      # add the callbacks to the session
      if on_data is not None:
        found_instance._add_on_data_callback(on_data)

      if on_notification is not None:
        found_instance._add_on_notification_callback(on_notification)

      if plugin_template is not None:
        found_instance.convert_to_specialized_class(plugin_template)

      return found_instance

    def attach_to_custom_plugin_instance(self, instance_id, on_data=None, on_notification=None) -> Instance:
      """
      Attach to an existing custom execution instance on this pipeline. 
      This method is useful when one wishes to attach an 
      `on_data` and `on_notification` callbacks to said instance.

      Parameters
      ----------
      instance_id : str
          name of the instance.
      on_data : Callable[[Pipeline, str, str, dict], None], optional
          Callback that handles messages received from this instance. As arguments, it has a reference to this Pipeline object, along with the payload itself.
          Defaults to None.
      on_notification : Callable[[Pipeline, dict], None], optional
          Callback that handles notifications received from this instance. As arguments, it has a reference to this Pipeline object, along with the payload itself.
          Defaults to None.

      Returns
      -------
      str
          An identifier for this instance, useful for stopping an instance.

      Raises
      ------
      Exception
          the pipeline does not contain any custom plugin.
      Exception
          The pipeline does not contain the desired instance.
      """

      def callback(pipeline, data): return self.__custom_exec_on_data(pipeline, instance_id, on_data, data)
      callback = callback if on_data is not None else None

      return self.attach_to_plugin_instance("CUSTOM_EXEC_01", instance_id, callback, on_notification)

    def detach_from_instance(self, instance: Instance):
      # search for the instance in the list
      if instance is None:
        raise Exception("The provided instance is None. Please provide a valid instance")

      instance._reset_on_data_callback()
      instance._reset_on_notification_callback()
      return

    def update_acquisition_parameters(self, config={}, **kwargs):
      """
      Update the acquisition parameters of this pipeline.
      Parameters can be passed either in the `config` dict, or as `kwargs`.

      Parameters
      ----------
      config : dict, optional
          The new configuration of the acquisition source, by default {}
      """
      if self.__staged_config is not None:
        raise ValueError("Pipeline configuration has already been staged, waiting for confirmation from Execution Engine")

      if self.proposed_config is None:
        self.proposed_config = {}

      self.proposed_config = {**self.proposed_config, **config, **{k.upper(): v for k, v in kwargs.items()}}
      self.proposed_config = self.__pop_ignored_keys_from_config(self.proposed_config)

      for k, v in self.config.items():
        if k in self.proposed_config:
          if self.proposed_config[k] == v:
            del self.proposed_config[k]

      if len(self.proposed_config) == 0:
        self.proposed_config = None

      return

    def send_pipeline_command(self, command, payload=None, command_params=None, wait_confirmation=True, timeout=10) -> list[Transaction]:
      """
      Send a pipeline command to the Naeural edge node.
      This command can block until the command is confirmed by the Naeural edge node.

      Example:
      --------
      ```python
      pipeline.send_pipeline_command('START', wait_confirmation=True)

      transactions_p1 = pipeline1.send_pipeline_command('START', wait_confirmation=False)
      transactions_p2 = pipeline2.send_pipeline_command('START', wait_confirmation=False)
      # wait for both commands to be confirmed, but after both commands are sent
      session.wait_for_transactions(transactions_p1 + transactions_p2)
      ```

      Parameters
      ----------
      command : str
          The name of the command.
      payload : dict, optional
          The payload of the command, by default {}
      command_params : dict, optional
          The parameters of the command, by default {}
      wait_confirmation : bool, optional
          Whether to wait for the confirmation of the command, by default False
      timeout : int, optional
          The timeout for the transaction, by default 10    

      Returns
      -------
      list[Transaction] | None
          The list of transactions generated, or None if `wait_confirmation` is False.
      """
      transactions = self.__register_transaction_for_pipeline_command(timeout=timeout)

      self.__was_last_operation_successful = None

      self.session._send_command_pipeline_command(
        worker=self.node_addr,
        pipeline_name=self.name,
        command=command,
        payload=payload,
        command_params=command_params,
      )

      if wait_confirmation:
        self.session.wait_for_transactions(transactions)
      else:
        return transactions
      return

    def create_or_attach_to_plugin_instance(self, *, signature, instance_id, config={}, on_data=None, on_notification=None, **kwargs) -> Instance:
      """
      Create a new instance of a desired plugin, with a given configuration, or attach to an existing instance.

      Parameters
      ----------
      signature : str
          The name of the plugin signature. This is the name of the desired overall functionality.
      instance_id : str
          The name of the instance. There can be multiple instances of the same plugin, mostly with different parameters
      config : dict, optional
          parameters used to customize the functionality. One can change the AI engine used for object detection, 
          or finetune alerter parameters to better fit a camera located in a low light environment.
          Defaults to {}
      on_data : Callable[[Pipeline, dict], None], optional
          Callback that handles messages received from this instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself.
          Defaults to None
      on_notification : Callable[[Pipeline, dict], None], optional
          Callback that handles notifications received from this instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself. 
          Defaults to None

      Returns
      -------
      instance : Instance
          An `Instance` object.
      """
      try:
        instance = self.attach_to_plugin_instance(signature, instance_id, on_data, on_notification)
        instance.update_instance_config(config, **kwargs)
      except Exception as e:
        instance = self.create_plugin_instance(
          signature=signature,
          instance_id=instance_id,
          config=config,
          on_data=on_data,
          on_notification=on_notification,
          **kwargs
        )
      return instance

    def create_or_attach_to_custom_plugin_instance(self, *, instance_id, custom_code, config={}, on_data=None, on_notification=None, **kwargs) -> Instance:
      """
      Create a new instance of a desired plugin, with a given configuration, or attach to an existing instance. 

      Parameters
      ----------
      signature : str
          The name of the plugin signature. This is the name of the desired overall functionality.
      instance_id : str
          The name of the instance. There can be multiple instances of the same plugin, mostly with different parameters
      config : dict, optional
          parameters used to customize the functionality. One can change the AI engine used for object detection, 
          or finetune alerter parameters to better fit a camera located in a low light environment.
          Defaults to {}
      on_data : Callable[[Pipeline, dict], None], optional
          Callback that handles messages received from this instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself.
          Defaults to None
      on_notification : Callable[[Pipeline, dict], None], optional
          Callback that handles notifications received from this instance. 
          As arguments, it has a reference to this Pipeline object, along with the payload itself. 
          Defaults to None

      Returns
      -------
      instance : Instance
          An `Instance` object.
      """

      try:
        instance = self.attach_to_custom_plugin_instance(instance_id, on_data, on_notification)
        instance.update_instance_config(config, **kwargs)
      except:
        instance = self.create_custom_plugin_instance(
          instance_id=instance_id,
          custom_code=custom_code,
          config=config,
          on_data=on_data,
          on_notification=on_notification,
          **kwargs
        )
      return instance

    def _sync_configuration_with_remote(self, config={}):
      config.pop('NAME', None)
      config.pop('TYPE', None)
      plugins = config.pop('PLUGINS', {})

      self.config = {**self.config, **config}

      active_plugins = []
      for dct_signature_instances in plugins:
        signature = dct_signature_instances['SIGNATURE']
        instances = dct_signature_instances['INSTANCES']
        for dct_instance in instances:
          instance_id = dct_instance.pop('INSTANCE_ID')
          active_plugins.append((signature, instance_id))
          instance_object = self.__get_instance_object(signature, instance_id)
          if instance_object is None:
            self.__init_instance(signature, instance_id, dct_instance, None, None, is_attached=True)
          else:
            instance_object._sync_configuration_with_remote(dct_instance)
        # end for dct_instance
      # end for dct_signature_instances

      for instance in self.lst_plugin_instances:
        if (instance.signature, instance.instance_id) not in active_plugins:
          self.__remove_plugin_instance(instance)
      # end for instance
      return

    def update_full_configuration(self, config={}):
      """
      Update the full configuration of this pipeline.
      Parameters are passed in the `config` dict.
      We do not support kwargs yet because it makes it difficult to check priority of dictionary, merging values, etc.

      Parameters
      ----------
      config : dict, optional
          The new configuration of the pipeline, by default {}
      """
      if self.__staged_config is not None:
        raise ValueError("Pipeline configuration has already been staged, waiting for confirmation from Execution Engine")

      # pop the illegal to modify keys
      config.pop('NAME', None)
      config.pop('TYPE', None)
      plugins = config.pop('PLUGINS', None)

      self.update_acquisition_parameters(config)

      if plugins is None:
        return

      new_plugins = []
      for dct_signature_instances in plugins:
        signature = dct_signature_instances['SIGNATURE']
        instances = dct_signature_instances['INSTANCES']
        for dct_instance in instances:
          instance_id = dct_instance.pop('INSTANCE_ID')
          new_plugins.append((signature, instance_id))
          instance_object = self.__get_instance_object(signature, instance_id)

          if instance_object is None:
            self.create_plugin_instance(signature=signature, instance_id=instance_id, config=dct_instance)
          else:
            instance_object.update_instance_config(dct_instance)
        # end for dct_instance
      # end for dct_signature_instances

      # now check if we have to remove any instances
      for instance in self.lst_plugin_instances:
        if (instance.signature, instance.instance_id) not in new_plugins:
          self.remove_plugin_instance(instance)
      # end for instance
      return

    @property
    def node_id(self):
      """
      Return the node id of the pipeline.
      """
      return self.session.get_node_name(self.node_addr)
