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

import os

from ..utils.code import CodeUtils
from .instance import Instance

WAIT_FOR_WORKER = 15


class Pipeline(object):
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

  def __init__(self, session, log, *, e2id, name, data_source, config={}, plugins=[], on_data=None, on_notification=None, create_pipeline=True, **kwargs) -> None:
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
    e2id : str
        Name of the AiXpand node that will handle this pipeline.  
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
    create_pipeline : bool
        This is used internally to allow the user to create or attach to a pipeline, and then use the same
        objects in the same way, by default True
    **kwargs : dict
        The user can provide the configuration of the acquisition source directly as kwargs.
    """
    self.log = log
    self.session = session
    self.e2id = e2id
    self.name = name
    self.data_source = data_source

    self.config = {**config, **kwargs}
    self.config = {k.upper(): v for k, v in self.config.items()}

    self.on_data_callbacks = []
    self.on_notification_callbacks = []

    if on_data is not None:
      self.on_data_callbacks.append(on_data)
    if on_notification is not None:
      self.on_notification_callbacks.append(on_notification)

    self.lst_plugin_instances = []

    self.__init_plugins(plugins)
    self.__maybe_create_new_pipeline_on_box(create_pipeline=create_pipeline)
    return

  # Utils
  if True:
    def __init_plugins(self, plugins):
      """
      Initialize the plugins list. This method is called at the creation of the pipeline and is used to create the instances of the plugins that are part of the pipeline.

      Parameters
      ----------
      plugins : List | None

      """
      if plugins is None:
        return

      for dct_signature_instances in plugins:
        signature = dct_signature_instances['SIGNATURE']
        instances = dct_signature_instances['INSTANCES']
        for dct_instance in instances:
          params = {k: v for k, v in dct_instance.items()}
          instance_id = params.pop('INSTANCE_ID')
          instance = Instance(self, instance_id, signature, params=params)
          self.lst_plugin_instances.append(instance)
        # end for dct_instance
      # end for dct_signature_instances
      return

    def __maybe_create_new_pipeline_on_box(self, *, create_pipeline=True):
      """
      Create a new pipeline on the AiXpand node. 
      This method is called at the creation of the pipeline and is used to create the pipeline on the AiXpand node.

      Parameters
      ----------
      create_pipeline : bool, optional
          If True, will send a message to the AiXpand node to create this pipeline, by default True
      """
      if create_pipeline:
        self.session._send_command_create_pipeline(
          worker=self.e2id,
          pipeline_config=self.__get_pipeline_config()
        )
      return

    def __get_pipeline_config(self):
      """
      Construct the pipeline configuration dictionary.

      Returns
      -------
      dict
          The pipeline configuration dictionary.
      """
      pipeline_config = {
        'NAME': self.name,
        'DEFAULT_PLUGIN': False,
        'PLUGINS': self.__construct_plugins_list(),
        'TYPE': self.data_source,
        **self.config,
      }
      return pipeline_config

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

    def __send_update_config_to_box(self):
      """
      Send an update pipeline configuration command to the AiXpand node.
      """
      self.session._send_command_update_pipeline_config(
          worker=self.e2id,
          pipeline_config=self.__get_pipeline_config()
      )
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

  # Message handling
  if True:
    def _on_data(self, signature, instance_id, data):
      """
      Handle the data received from the AiXpand node. This method is called by the Session object when a message is received from the AiXpand node.
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
      Handle the notification received from the AiXpand node. This method is called by the Session object when a notification is received from the AiXpand node.

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
    def start_plugin_instance(self, *, signature, instance_id, params={}, on_data=None, on_notification=None, **kwargs) -> Instance:
      """
      Create a new instance of a desired plugin, with a given configuration. This instance is attached to this pipeline, 
      meaning it processes data from this pipelines data source. Parameters can be passed either in the `params` dict, or as `kwargs`.

      Parameters
      ----------
      signature : str
          The name of the plugin signature. This is the name of the desired overall functionality.
      instance_id : str
          The name of the instance. There can be multiple instances of the same plugin, mostly with different parameters
      params : dict, optional
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

      # TODO: maybe wait for a confirmation?
      for instance in self.lst_plugin_instances:
        if instance.instance_id == instance_id and instance.signature == signature:
          raise Exception("plugin {} with instance {} already exists".format(signature, instance_id))

      # create the new instance and add it to the list
      instance = Instance(self, instance_id, signature, on_data, on_notification, params, **kwargs)
      self.lst_plugin_instances.append(instance)

      # send an update config command to the box to create the instance there
      self.__send_update_config_to_box()

      # add the callbacks to the session
      if on_data is not None:
        instance._add_on_data_callback(on_data)
      if on_notification is not None:
        instance._add_on_notification_callback(on_notification)

      self.P("Starting plugin {}:{}".format(signature, instance_id), verbosity=1)
      self.D("with params {}".format(params), verbosity=2)

      return instance

    def stop_plugin_instance(self, instance):
      """
      Stop a plugin instance from this pipeline. 


      Parameters
      ----------
      instance : Instance
          The instance to be stopped.

      """

      if instance is None:
        raise Exception("instance is None")

      if instance not in self.lst_plugin_instances:
        raise Exception("plugin  <{}/{}> does not exist on this pipeline".format(instance.signature, instance.instance_id))

      # remove the instance from the list
      self.lst_plugin_instances.remove(instance)

      # send an update config command to the box to remove the instance there
      self.__send_update_config_to_box()

      return

    def start_custom_plugin(self, *, instance_id, plain_code: str = None, plain_code_path: str = None, custom_code: str = None, params={}, on_data=None, on_notification=None, **kwargs) -> Instance:
      """
      Create a new custom execution instance, with a given configuration. This instance is attached to this pipeline, 
      meaning it processes data from this pipelines data source. The code used for the custom instance must be provided
      either as a string, or as a path to a file. Parameters can be passed either in the params dict, or as kwargs.
      The custom plugin instance will run periodically. If one desires to execute a custom code only once, use `wait_exec`.

      Parameters
      ----------
      instance_id : str
          The name of the instance. There can be multiple instances of the same plugin, mostly with different parameters
      plain_code : str, optional
          A string containing the entire code that is to be executed remotely on an AiXp node. Defaults to None.
      plain_code_path : str, optional
          A string containing the path to the code that is to be executed remotely on an AiXp node. Defaults to None.
      custom_code : str | Callable[[CustomPluginTemplate], Any], optional
          A string containing the entire code, a path to a file containing the code as a string or a function with the code.
          This code will be executed remotely on an AiXp node. Defaults to None.
      params : dict, optional
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

      if plain_code is None and plain_code_path is None and custom_code is None:
        raise Exception(
            "Need to specify at least one of the following: plain_code, plain_code_path, custom_code")

      if plain_code is not None and plain_code_path is not None and custom_code is not None:
        raise Exception(
            "Need to specify at most one of the following: plain_code, plain_code_path, custom_code")

      if custom_code is None:
        self.P("Warning: custom_code is None. Using plain_code or plain_code_path. In the future support for " +
               "plain_code and plain_code_path will be removed. Use custom_code instead.", color="y", verbosity=0)

      if plain_code_path is not None:
        with open(plain_code_path, "r") as fd:
          plain_code = "".join(fd.readlines())

      if custom_code is not None:
        if isinstance(custom_code, str):
          # it is a path
          if os.path.exists(custom_code):
            with open(custom_code, "r") as fd:
              plain_code = "".join(fd.readlines())
          # it is a string
          else:
            plain_code = custom_code

        elif callable(custom_code):
          # we have a function
          plain_code = CodeUtils().get_function_source_code(custom_code)
        else:
          raise Exception("custom_code is not a string or a callable")
        # endif get plain code

      b64code = CodeUtils().code_to_base64(plain_code)

      def callback(pipeline, data): return self.__custom_exec_on_data(pipeline, instance_id, on_data, data)

      return self.start_plugin_instance(
          signature='CUSTOM_EXEC_01',
          instance_id=instance_id,
          params={
              'CODE': b64code,
              **params
          },
          on_data=callback,
          on_notification=on_notification,
          **kwargs
      )

    def stop_custom_instance(self, instance):
      """
      Stop a custom execution instance from this pipeline.
      This method is an alias for `stop_plugin_instance`.

      Parameters
      ----------
      instance : Instance
          The instance to be stopped.

      """
      self.stop_plugin_instance(instance)

    def wait_exec(self, *, plain_code: str = None, plain_code_path: str = None, params={}):
      """
      Create a new REST-like custom execution instance, with a given configuration. This instance is attached to this pipeline, 
      meaning it processes data from this pipelines data source. The code used for the custom instance must be provided either as a string, or as a path to a file. Parameters can be passed either in the params dict, or as kwargs.
      The REST-like custom plugin instance will execute only once. If one desires to execute a custom code periodically, use `start_custom_plugin`.

      Parameters
      ----------
      plain_code : str, optional
          A string containing the entire code that is to be executed remotely on an AiXp node, by default None
      plain_code_path : str, optional
          A string containing the path to the code that is to be executed remotely on an AiXp node, by default None
      params : dict, optional
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

      if plain_code is None and plain_code_path is None:
        raise Exception(
            "Need to specify at least one of the following: plain_code, plain_code_path")

      if plain_code is None:
        with open(plain_code_path, "r") as fd:
          plain_code = "".join(fd.readlines())

      finished = False
      result = None
      error = None

      def on_data(pipeline, data):
        nonlocal finished
        nonlocal result
        nonlocal error

        if 'rest_execution_result' in data['specificValue'] and 'rest_execution_error' in data['specificValue']:
          result = data['specificValue']['rest_execution_result']
          error = data['specificValue']['rest_execution_error']
          finished = True
        return

      b64code = CodeUtils().code_to_base64(plain_code)
      instance_id = self.name + "_rest_custom_exec_synchronous_0"
      params = {
          'REQUEST': {
              'DATA': {
                  'CODE': b64code,
              },
              'TIMESTAMP': self.log.time_to_str()
          },
          'RESULT_KEY': 'REST_EXECUTION_RESULT',
          'ERROR_KEY': 'REST_EXECUTION_ERROR',
          **params
      }

      instance = self.start_plugin_instance(
          signature='REST_CUSTOM_EXEC_01',
          instance_id=instance_id,
          params=params,
          on_data=on_data
      )
      while not finished:
        pass

      # stop the stream
      instance.close()

      return result, error

    def close(self):
      """
      Close the pipeline, stopping all the instances associated with it.
      """
      # remove callbacks
      self.session._send_command_archive_pipeline(self.e2id, self.name)
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
      return self.log.D(*args, **kwargs)

    def attach_to_instance(self, signature, instance_id, on_data=None, on_notification=None) -> Instance:
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
      found_instance = None
      for instance in self.lst_plugin_instances:
        if instance.instance_id == instance_id and instance.signature == signature:
          found_instance = instance
          break

      if found_instance is None:
        raise Exception(f"Unable to attach to instance. Instance <{signature}/{instance_id}> does not exist")

      # add the callbacks to the session
      if on_data is not None:
        instance._add_on_data_callback(on_data)

      if on_notification is not None:
        instance._add_on_notification_callback(on_notification)

      return found_instance

    def attach_to_custom_instance(self, instance_id, on_data=None, on_notification=None) -> Instance:
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

      return self.attach_to_instance("CUSTOM_EXEC_01", instance_id, callback, on_notification)

    def detach_from_instance(self, instance: Instance):
      # search for the instance in the list
      if instance is None:
        raise Exception("instance is None")

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
      self.config = {
          **self.config,
          **config,
          **kwargs
      }
      self.__send_update_config_to_box()

      return

    def batch_update_instances(self, lst_updates):
      """
      Update the configuration of multiple instances at once.
      This method is useful when one wants to update the configuration of multiple instances at once, 
        while only sending one message to the AiXpand node.

      Example:
      ```
      instance1 : Instance
      instance2 : Instance

      config1 : dict
      config2 : dict

      update1 = instance1.update_instance_config(config1)
      update2 = instance2.update_instance_config(config2)

      lst_updates = [update1, update2]
      pipeline.batch_update_instances(lst_updates)
      ```

      Parameters
      ----------
      lst_updates : List[dict]
          A list of dictionaries containing the updates for each instance.
      """
      self.session._send_command_batch_update_instance_config(self.e2id, lst_updates)

    def send_pipeline_command(self, command, payload={}, command_params={}):
      # TODO: test if this is oke like this
      """
      Send a pipeline command to the AiXpand node.

      Parameters
      ----------
      command : str
          The name of the command.
      payload : dict, optional
          The payload of the command, by default {}
      command_params : dict, optional
          The parameters of the command, by default {}
      """
      self.session._send_command_pipeline_command(self.e2id, self.name, command, payload, command_params)
      return
