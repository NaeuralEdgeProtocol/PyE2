class CustomPluginTemplate:
  @property
  def BytesIO():
    """
    provides access to BytesIO class from io package
    """
    raise NotImplementedError

  def D(self, s, t, color, prefix, kwargs):
    raise NotImplementedError

  def DefaultDotDict(self, args):
    """
    Returns a `DefaultDotDict` object that is a `dict` where you can use keys with dot 
    using the default initialization
    
    Inputs
    ------
    
      pass a `lambda: <type>` always
    
    Returns
    -------
      DefaultDotDict : class
     
    Example
    -------
     ```
       dct_dot = self.DefaultDotDict(lambda: str)
       dct_dot.test1 = "test"       
       print(dct_dot.test1)
       print(dct_dot.test2)
     ```
    """
    raise NotImplementedError

  @property
  def ElementTree():
    """
    provides access to ElementTree class from xml.etree package
    """
    raise NotImplementedError

  def NestedDefaultDotDict(self, args):
    """
    Returns a `NestedDefaultDotDict` object that is a `defaultdict(dict)` where you can use keys with dot
    
    Returns
    -------
      defaultdict : class
     
    Example
    -------
     ```
      dct_dot1 = self.NestedDefaultDotDict()
      dct_dot1.test.a = "test"   
      print(dct_dot1.test.a)
       
      dct_dot2 = self.NestedDefaultDotDict({'test' : {'a' : 100, 'b' : {'c' : 200}}})
      print(dct_dot2.test.a)
      print(dct_dot2.test.b.c)
      print(dct_dot2.test.b.unk)
        
    """
    raise NotImplementedError

  def NestedDotDict(self, args):
    """
    Returns a `NestedDotDict` object that is a `dict` where you can use keys with dot
    
    Returns
    -------
      defaultdict : class
     
    Example
    -------
     ```
       dct_dot = self.NestedDotDict({'test' : {'a' : 100}})
       dct_dot.test.a = "test"   
       print(dct_dot.test.a)
    """
    raise NotImplementedError

  @property
  def OrderedDict():
    """
    Returns the definition for `OrderedDict`
    
    Returns
    -------
    OrderedDict : class
      `OrderedDict` from standard python `collections` package.
      
    Example
    -------
        ```
        dct_A = self.OrderedDict({'a': 1})
        dct_A['b'] = 2
        ```
    """
    raise NotImplementedError

  def P(self, s, t, color, prefix, kwargs):
    raise NotImplementedError

  @property
  def PIL():
    """
    provides access to PIL package
    """
    raise NotImplementedError

  @property
  def actual_plugin_resolution():
    raise NotImplementedError

  def add_alerter_observation(self, value, alerter):
    raise NotImplementedError

  def add_config_data(self, new_config_data):
    raise NotImplementedError

  def add_debug_info(self, value, key):
    """
    Add debug info to the witness. The information will be stored in a new line.
    
    Parameters
    ----------
    value : Any
        The info to be shown
    key : str
        The key that identifies this debug line
    """
    raise NotImplementedError

  def add_error(self, msg):
    raise NotImplementedError

  def add_info(self, msg):
    raise NotImplementedError

  def add_inputs(self, inp):
    raise NotImplementedError

  def add_payload(self, payload):
    """
    Adds a payload in the plugin instance output queue. If used inside plugins
    plese do NOT return the payload from _process as the payload will be duplicated
    
    Parameters
    ----------
    payload : GeneralPayload or dict
      the payload
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def add_payload_by_fields(self, kwargs):
    """
    Adds a payload in the plugin instance output queue based on fields rather than
    on a already created payload object.
    If used inside plugins plese do NOT return the payload from _process as the payload
    will be duplicated
    
    Parameters
    ----------
    **kwargs : dict
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def add_to_inputs_deque(self, data):
    raise NotImplementedError

  def add_track_id(self, id, alerter):
    raise NotImplementedError

  def add_track_ids(self, ids, alerter):
    raise NotImplementedError

  def add_warning(self, msg):
    raise NotImplementedError

  def aggregation_add_to_buffer(self, obj):
    raise NotImplementedError

  def alerter_add_observation(self, value, alerter):
    """
    Add a new numerical value observation to the given alerter state machine instance
    
    Parameters
    ----------
    value : float
      The value to be added that can be a percentage or a number or elements - depeding of the configuration of the alerter
      that has been given via "ALERT_MODE".
    alerter : str, optional
      The identifier of the given alerter state machine. The default is 'default'.
    
    Returns
    -------
    TYPE
      None.
    """
    raise NotImplementedError

  def alerter_create(self, alerter, raise_time, lower_time, value_count, raise_thr, lower_thr, alert_mode, alert_mode_lower, reduce_value, reduce_threshold, show_version):
    raise NotImplementedError

  def alerter_get_current_frame_state(self, observation, alerter):
    """
    This function returns the possible next alerter position based on the current alerter state and the current observation.
    
    If the current observation can change the alerter state from A to B, the function returns the position of the state B.
    (this ensures that an alertable observation will be saved to the alertable state, no matter the current alerter state)
    
    If the current observation cannot change the alerter state from A to B, the function returns the position of the state A.
    
    Parameters
    ----------
    observation : float
        The current observation
    
    alerter : str, optional
        The alerter name, by default 'default'
    
    Returns
    -------
    int
        The possible next alerter position
    """
    raise NotImplementedError

  def alerter_get_last_alert_duration(self, alerter):
    """
        
        
    """
    raise NotImplementedError

  def alerter_get_last_value(self, alerter):
    raise NotImplementedError

  def alerter_hard_reset(self, state, alerter):
    raise NotImplementedError

  def alerter_hard_reset_all(self):
    raise NotImplementedError

  def alerter_in_confirmation(self, alerter):
    raise NotImplementedError

  def alerter_is_alert(self, alerter):
    """
    Returns `True` if the current state of the given `alerter` state machine is "raised"
    
    Parameters
    ----------
    alerter : str, optional
      Identifier of the given alerter instance. The default is 'default'.
    
    Returns
    -------
    TYPE
      bool.
    """
    raise NotImplementedError

  def alerter_is_new_alert(self, alerter):
    """
    Returns `True` if the current state of the given `alerter` state machine has just changed from "lowered" to "raised"
    
    Parameters
    ----------
    alerter : str, optional
      Identifier of the given alerter instance. The default is 'default'.
    
    Returns
    -------
    TYPE
      bool.
    """
    raise NotImplementedError

  def alerter_is_new_lower(self, alerter):
    """
    Returns `True` if the current state of the given `alerter` state machine has just changed from "raised" to "lowered"
    
    Parameters
    ----------
    alerter : str, optional
      Identifier of the given alerter instance. The default is 'default'.
    
    Returns
    -------
    TYPE
      bool.
    """
    raise NotImplementedError

  def alerter_is_new_raise(self, alerter):
    """
    Returns `True` if the current state of the given `alerter` state machine has just changed from "lowered" to "raised"
    
    Parameters
    ----------
    alerter : str, optional
      Identifier of the given alerter instance. The default is 'default'.
    
    Returns
    -------
    TYPE
      bool.
    """
    raise NotImplementedError

  def alerter_maybe_create(self, alerter, kwargs):
    raise NotImplementedError

  def alerter_maybe_force_lower(self, max_raised_time, alerter):
    """
    Forces the given alerter to reset to "lowered" status if the current state is "raised"
    
    Parameters
    ----------
    alerter : str, optional
      Identifier of the given alerter instance. The default is 'default'.
      
    max_raised_time: float, optional
      The number of seconds after the raised alerter is forced to lower its status
    
    Returns
    -------
    TYPE
      bool.
    """
    raise NotImplementedError

  def alerter_setup_values(self, alerter):
    raise NotImplementedError

  def alerter_status_changed(self, alerter):
    """
    Returns `True` if the current state of the given `alerter` state machine has just changed
    
    Parameters
    ----------
    alerter : str, optional
      Identifier of the given alerter instance. The default is 'default'.
    
    Returns
    -------
    TYPE
      bool.
    """
    raise NotImplementedError

  def alerter_status_dict(self, alerter):
    raise NotImplementedError

  def alerter_time_from_last_change(self, alerter):
    """
    Returns the number of seconds from the last change of the given alerter state machine
    
    Parameters
    ----------
    alerter : str, optional
      Identifier of the given alerter instance. The default is 'default'.
    
    Returns
    -------
    TYPE
      bool.
    """
    raise NotImplementedError

  @property
  def alerters_names():
    raise NotImplementedError

  def archive_config_keys(self, keys, defaults):
    """
    Method that allows resetting of a list of keys and saving the current value as `_LAST` keys
    
    Parameters
    ----------
    keys : list
      List of keys to be archived.
    
    defaults: list
      List of default values for all keys. Default is None
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def audit_dump_audit_data(self):
    raise NotImplementedError

  def audit_error(self, msg, img, kwargs):
    raise NotImplementedError

  def audit_log(self, msg, img, kwargs):
    raise NotImplementedError

  def audit_warning(self, msg, img, kwargs):
    raise NotImplementedError

  def base64_to_code(self, b64code, decompress):
    raise NotImplementedError

  def base64_to_str(self, b64, decompress):
    """
    Transforms a base64 encoded string into a normal string
    
    Parameters
    ----------
    b64 : str
        the base64 encoded string
        
    decompress : bool, optional
        if True, the string will be decompressed after decoding. The default is False.
    
    Returns
    -------
    str: the decoded string
    """
    raise NotImplementedError

  def basic_ts_create(self, series_min, train_hist, train_periods):
    """
    Returns a basic time-series prediction model instance
    
    Parameters
    ----------
    series_min : int, optional
      Minimal accepted number of historical steps. The default is 100.
    train_hist : int, optional
      The training window size. The default is None.
    train_periods : int, optional
      how many windows to use. The default is None.
    
    Returns
    -------
    BasicSeriesModel() object
    
    
    Example
    -------
      ```
        # init model
        model = plugin.basic_ts_create(...)
      ```
    """
    raise NotImplementedError

  def basic_ts_fit_predict(self, data, steps):
    """
    Takes a list of values and directly returns predictions using a basic AR model
    
    
    Parameters
    ----------
    data : list
      list of float values.
    steps : int
      number of prediction steps.
    
    Returns
    -------
    yh : list
      the `steps` predicted values.
    
    
    Example
    -------
      ```
      yh = self.basic_ts_fit_predict(data=[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89], steps=3)
      result = {'preds' : yh}
      ```
    """
    raise NotImplementedError

  def cacheapi_load_json(self, default, verbose):
    """
    Loads object json from the current plugin instance cache folder
    
    Parameters
    ----------
    default : any, optional
        default value, by default {}
    verbose : bool, optional
         show information during process, by default True
    
    Returns
    -------
    any
        the loaded object
    """
    raise NotImplementedError

  def cacheapi_load_pickle(self, default, verbose):
    """
    Loads object from the current plugin instance cache folder
    
    Parameters
    ----------
    default : any, optional
        default value, by default None
    verbose : bool, optional
         show information during process, by default True
    
    Returns
    -------
    any
        the loaded object
    """
    raise NotImplementedError

  def cacheapi_save_json(self, obj, verbose):
    """
    Save object json to the current plugin instance cache folder
    
    Parameters
    ----------
    obj : any
        the json-able object to be saved
        
    verbose : bool, optional
        show information during process, by default True
    """
    raise NotImplementedError

  def cacheapi_save_pickle(self, obj, verbose):
    """
    Save object to the current plugin instance cache folder
    
    Parameters
    ----------
    obj : any
        the picklable object to be saved
    verbose : bool, optional
        show information during process, by default True
    """
    raise NotImplementedError

  @property
  def cfg_alert_tracker_maxlen():
    raise NotImplementedError

  @property
  def cfg_audit_dump_time():
    raise NotImplementedError

  @property
  def cfg_cancel_witness():
    raise NotImplementedError

  @property
  def cfg_collect_payloads_until_seconds_export():
    raise NotImplementedError

  @property
  def cfg_demo_mode():
    raise NotImplementedError

  @property
  def cfg_email_config():
    raise NotImplementedError

  @property
  def cfg_interval_aggregation_seconds():
    raise NotImplementedError

  @property
  def cfg_send_all_alerts():
    raise NotImplementedError

  def chatapi_ask(self, question, persona, user, set_witness, personas_folder):
    """
    Simple single-function API for accessing chat backend. Provides statefullness based on
    provided `user` for the caller plugin instance.
    
    Parameters
    ----------
    question : str
      The question.
    persona : str
      A valid persona.
    user : str
      A user name for tracking your session.
    set_witness : bool, optional
      If `True` then a witness will be generated. The default is True.
    
    Returns
    -------
    result : str
      The response.
    
    
    Example
    -------
      ```
      result = plugin.chatapi_ask(
        question="Who are you?",
        persona='codegen',
        user="John Doe",
      )      
      ```
    """
    raise NotImplementedError

  def check_code_text(self, code, safe_imports):
    raise NotImplementedError

  def check_event_sending(self, alert_ids, alert_state, alerter):
    raise NotImplementedError

  def check_loop_exec_time(self):
    raise NotImplementedError

  def check_mandatory_keys(self, data, mandatory_keys):
    """
    Method used for checking if a certain dictionary has all the mandatory keys or not
    Parameters
    ----------
    data - dictionary
    mandatory_keys - list of mandatory keys
    
    Returns
    -------
    """
    raise NotImplementedError

  def cmdapi_archive_all_pipelines(self, node_address):
    """
    Stop all active pipelines on destination Execution Engine
    
    Parameters
    ----------
    node_address : str, optional
      Address of the target E2 instance. The default is `None` and will run on local E2.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def cmdapi_archive_current_stream(self):
    raise NotImplementedError

  def cmdapi_archive_other_stream_on_current_box(self, stream_name):
    raise NotImplementedError

  def cmdapi_archive_pipeline(self, node_address, name):
    """
    Stop and archive a active pipeline on destination Execution Engine
    
    Parameters
    ----------
    node_address : str, optional
      destination Execution Engine, `None` will default to local Execution Engine. The default is None.
    name : str, optional
      Name of the pipeline. The default is `None` and will point to current pipeline where the plugin instance 
      is executed.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def cmdapi_archive_stream_on_other_box(self, node_address, stream_name):
    raise NotImplementedError

  def cmdapi_batch_update_instance_config(self, lst_updates, node_address):
    """
    Send a batch of updates for multiple plugin instances within their individual pipelines
    
    Parameters
    ----------
    lst_updates : list of dicts
        The list of updates for multiple plugin instances within their individual pipelines
        
    node_address : str, optional
        Destination node, by default None
        
    Returns
    -------
    None.
    
    Example
    -------
    
      ```python
      # in this example we are modifying the config for 2 instances of the same plugin `A_PLUGIN_01`
      # within the same pipeline `test123`
      lst_updates = [
        {
          "NAME" : "test123",
          "SIGNATURE" : "A_PLUGIN_01",
          "INSTANCE_ID" : "A_PLUGIN_01_INSTANCE_01",
          "INSTANCE_CONFIG" : {
            "PARAM1" : "value1",
            "PARAM2" : "value2",
          }
        },
        {
          "NAME" : "test123",
          "SIGNATURE" : "A_PLUGIN_01",
          "INSTANCE_ID" : "A_PLUGIN_01_INSTANCE_02",
          "INSTANCE_CONFIG" : {
            "PARAM1" : "value1",
            "PARAM2" : "value2",
          }
        },
      ] 
      plugin.cmdapi_batch_update_instance_config(lst_updates=lst_updates, node_address=None)
      ```
    """
    raise NotImplementedError

  def cmdapi_finish_current_stream_acquisition(self):
    raise NotImplementedError

  def cmdapi_finish_other_stream_acquisition_on_current_box(self, stream_name):
    raise NotImplementedError

  def cmdapi_finish_stream_acquisition_on_other_box(self, node_address, stream_name):
    raise NotImplementedError

  def cmdapi_register_command(self, node_address, command_type, command_content):
    """
    Send a command to a particular Execution Engine
    
    Parameters
    ----------
    node_address : str
      target Execution Engine.
    command_type : st
      type of the command - can be one of 'RESTART','STATUS', 'STOP', 'UPDATE_CONFIG', 
      'DELETE_CONFIG', 'ARCHIVE_CONFIG', 'DELETE_CONFIG_ALL', 'ARCHIVE_CONFIG_ALL', 'ACTIVE_PLUGINS', 
      'RELOAD_CONFIG_FROM_DISK', 'FULL_HEARTBEAT', 'TIMERS_ONLY_HEARTBEAT', 'SIMPLE_HEARTBEAT',
      'UPDATE_PIPELINE_INSTANCE', etc.
    command_content : dict
      the actual content - can be None for some commands.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def cmdapi_restart_current_box(self):
    raise NotImplementedError

  def cmdapi_restart_other_box(self, node_address):
    raise NotImplementedError

  def cmdapi_send_instance_command(self, pipeline, signature, instance_id, instance_command, node_address):
    """
    Sends a INSTANCE_COMMAND for a particular plugin instance in a given box/pipeline
    
    Parameters
    ----------
    pipeline : str
      Name of the pipeline. 
      
    instance_id: str
      Name of the instance
      
    signature: str
      Name (signature) of the plugin     
      
    instance_command: any
      The configuration for the given box/pipeline/plugin/instance. Can be a string, dict, etc
    
    node_address : str, optional
      destination Execution Engine, `None` will default to local Execution Engine. The default is None.
      
      
    Returns
    -------
    None.
    
    Example:
    --------
    
    
      ```
      pipeline = "test123"
      signature = "A_PLUGIN_01"
      instance_id = "A_PLUGIN_01_INSTANCE_01"
      instance_command = {
        "PARAM1" : "value1",
        "PARAM2" : "value2",
      }
      plugin.cmdapi_send_instance_command(
        pipeline=pipeline,
        signature=signature,
        instance_id=instance_id,
        instance_command=instance_command,
        node_address=None,
      )
      ```
        
    """
    raise NotImplementedError

  def cmdapi_send_pipeline_command(self, command, node_address, pipeline_name):
    """
    Sends a command to a particular pipeline on a particular destination E2 instance
    
    Parameters
    ----------
    command : any
        the command content
    
    node_address : str, optional
        name of the destination e2, by default None (self)
    
    pipeline_name : str, optional
        name of the pipeline, by default None (self)
        
    
    Returns
    -------
    None.
    
    Example
    -------
    
      ```
      # send a command directly to the current pipeline
      plugin.cmdapi_send_pipeline_command(
        command={"PARAM1" : "value1", "PARAM2" : "value2"},
        node_address=None,
        pipeline_name=None,
      )
      ```
    """
    raise NotImplementedError

  def cmdapi_start_metastream_by_config_on_current_box(self, config_metastream, collected_streams):
    raise NotImplementedError

  def cmdapi_start_metastream_by_config_on_other_box(self, node_address, config_metastream, collected_streams):
    raise NotImplementedError

  def cmdapi_start_pipeline(self, config, node_address):
    """
    Sends a start pipeline to a particular destination Execution Engine
    
    Parameters
    ----------
    node_address : str, optional
      destination Execution Engine, `None` will default to local Execution Engine. The default is None
      .
    config : dict
      the pipeline configuration. 
    
    Returns
    -------
    None.
    
    Example:
      
      ```
      config = {
        "NAME" : "test123",
        "TYPE" : "Void",
      }
      ee_id = None # using current processing node
      plugin.cmdapi_start_pipeline(config=config, node_address=ee_addr)
      ```
    """
    raise NotImplementedError

  def cmdapi_start_pipeline_by_params(self, name, pipeline_type, node_address, url, reconnectable, live_feed, plugins, stream_config_metadata, cap_resolution, kwargs):
    """
    Start a pipeline by defining specific pipeline params
    
    Parameters
    ----------
    name : str
      Name of the pipeline.
      
    pipeline_type : str
      type of the pipeline. Will point the E2 instance to a particular Data Capture Thread plugin
      
    node_address : str, optional
      Address of the target E2 instance. The default is `None` and will run on local E2.
      
    url : str, optional
      The optional URL that can be used by the DCT to acquire data. The default is None.
      
    reconnectable : str, optional
      Attempts to reconnect after data stops if 'YES'. 'KEEP_ALIVE' will not reconnect to
      data source but will leave the DCT in a "zombie" state waiting for external pipeline 
      close command.
      The default is 'YES'.
      
    live_feed : bool, optional
      Will always try to generate the real-time datapoint (no queued data). The default is False.
      
    plugins : list of dicts, optional
      Lists all the business plugins with their respective individual instances. The default is None.
      
    stream_config_metadata : dict, optional
      Options (custom) for current DCT. The default is None.
      
    cap_resolution : float, optional
      Desired frequency (in Hz) of the DCT data reading cycles. The default is None.
      
    
    Returns
    -------
    None (actually)
    
    Example
    -------
    
      ```
      name = "test123"
      pipeline_type = "Void"
      plugins = [
        {
          "SIGNATURE" : "A_PLUGIN_01",
          "INSTANCES" : [
            {
              "INSTANCE_ID" : "A_PLUGIN_01_INSTANCE_01",
              "PARAM1" : "value1",
              "PARAM2" : "value2",
            }
          ]
        }
      ]
      plugin.cmdapi_start_pipeline_by_params(
        name=name, 
        pipeline_type=pipeline_type, 
        plugins=plugins,
      )
      ```
    """
    raise NotImplementedError

  def cmdapi_start_simple_custom_pipeline(self, base64code, node_address, name, instance_config, kwargs):
    """
    Starts a CUSTOM_EXEC_01 plugin on a Void pipeline
    
    
    Parameters
    ----------
    base64code : str
      The base64 encoded string that will be used as custom exec plugin.
      
    node_address : str, optional
      The destination processing node. The default is None and will point to current node.
      
    name : str, optional
      Name of the pipeline. The default is None and will be uuid generated.
      
    instance_config / kwargs: dict
      Dict with params for the instance that can be given either as a dict or as kwargs
    
    
    Returns
    -------
    name : str
      returns the name of the pipeline.
      
    
    Example
    -------
    
      ```
      worker = plugin.cfg_destination                     # destination worker received in plugin json command
      worker_code = plugin.cfg_worker_code                # base64 code that will be executed 
      custom_code_param = plugin.cfg_custom_code_param    # a special param expected by the custom code
      pipeline_name = plugin.cmdapi_start_simple_custom_pipeline(
        base64code=worker_code, 
        node_address=worker,
        custom_code_param=pcustom_code_param,
      )
      ```
    """
    raise NotImplementedError

  def cmdapi_start_stream_by_config_on_current_box(self, config_stream):
    raise NotImplementedError

  def cmdapi_start_stream_by_config_on_other_box(self, node_address, config_stream):
    raise NotImplementedError

  def cmdapi_start_stream_by_params_on_current_box(self, name, stream_type, url, reconnectable, live_feed, plugins, stream_config_metadata, cap_resolution, kwargs):
    raise NotImplementedError

  def cmdapi_start_stream_by_params_on_other_box(self, node_address, name, stream_type, url, reconnectable, live_feed, plugins, stream_config_metadata, cap_resolution, kwargs):
    raise NotImplementedError

  def cmdapi_stop_current_box(self):
    raise NotImplementedError

  def cmdapi_stop_current_pipeline(self):
    raise NotImplementedError

  def cmdapi_stop_current_stream(self):
    raise NotImplementedError

  def cmdapi_stop_other_box(self, node_address):
    raise NotImplementedError

  def cmdapi_stop_other_stream_on_current_box(self, stream_name):
    raise NotImplementedError

  def cmdapi_stop_pipeline(self, node_address, name):
    raise NotImplementedError

  def cmdapi_stop_stream_on_other_box(self, node_address, stream_name):
    raise NotImplementedError

  def cmdapi_update_instance_config(self, pipeline, signature, instance_id, instance_config, node_address):
    """
    Sends update config for a particular plugin instance in a given box/pipeline
    
    
    Parameters
    ----------
      
    pipeline : str
      Name of the pipeline. 
      
    signature: str
      Name (signature) of the plugin 
      
    instance_id: str
      Name of the instance
      
    instance_config: dict
      The configuration for the given box/pipeline/plugin/instance
    
    node_address : str, optional
      destination Execution Engine, `None` will default to local Execution Engine. The default is None.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def code_to_base64(self, code, verbose, compress):
    raise NotImplementedError

  @property
  def const():
    """
    Provides access to E2 constants
    
    Returns
    -------
    ct : package
      Use `self.const.ct.CONST_ACME` to acces any required constant
    """
    raise NotImplementedError

  @property
  def consts():
    """
    Provides access to E2 constants
    
    Returns
    -------
    ct : package
      Use `self.consts.CONST_ACME` to acces any required constant
    """
    raise NotImplementedError

  def convert_size(self, size, unit):
    """
    Given a size and a unit, it returns the size in the given unit
    
    Parameters
    ----------
    size : int
        value to be converted
    unit : str
        one of the following: 'KB', 'MB', 'GB'
    
    Returns
    -------
    _type_
        _description_
    """
    raise NotImplementedError

  def copy_simple_data(self, dct_data):
    raise NotImplementedError

  def create_alerter_data(self, alerter):
    raise NotImplementedError

  def create_and_send_payload(self, kwargs):
    """
    Creates a payload and sends it to the output queue.
    If used inside plugins plese do NOT return the payload from _process as the payload
    will be duplicated
    
    Parameters
    ----------
    **kwargs : dict
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def create_basic_ts_model(self, series_min, train_hist, train_periods):
    """
    Returns a basic time-series prediction model instance
    
    Parameters
    ----------
    series_min : int, optional
      Minimal accepted number of historical steps. The default is 100.
    train_hist : int, optional
      The training window size. The default is None.
    train_periods : int, optional
      how many windows to use. The default is None.
    
    Returns
    -------
    BasicSeriesModel() object
    
    
    Example
    -------
      ```
        # init model
        model = plugin.create_basic_ts_model(...)
      ```
    """
    raise NotImplementedError

  def create_config_handlers(self, verbose):
    raise NotImplementedError

  def create_numpy_shared_memory_object(self, mem_name, mem_size, np_shape, np_type, create, is_buffer, kwargs):
    """
    Create a shared memory for numpy arrays. 
    This method returns a `NumpySharedMemory` object that can be used to read/write numpy arrays from/to shared memory.
    Use this method instead of creating the object directly, as it requires the logger to be set.
    
    For a complete set of parameters, check the `NumpySharedMemory` class from `core.utils.system_shared_memory`
    
    Parameters
    ----------
    mem_name : str
        the name of the shared memory
    mem_size : int
        the size of the shared memory. can be ignored if np_shape is provided
    np_shape : tuple
        the shape of the numpy array. can be ignored if mem_size is provided
    np_type : numpy.dtype
        the type of the numpy array
    create : bool, optional
        create the shared memory if it does not exist, by default False
    is_buffer : bool, optional
        if True, the shared memory will be used as a buffer, by default False
    
    
    Returns
    -------
    NumPySharedMemory
        the shared memory object
    """
    raise NotImplementedError

  def create_poseapi_keypoints_getters(self):
    """
    Creates the getters for the keypoints
    To access the index of a keypoint use the following:
    self.poseapi_get_nose_idx # returns 0
    """
    raise NotImplementedError

  def create_sre(self, kwargs):
    """
    Returns a Statefull Rule Engine instance
    
    
    Returns
    -------
    SRE()
    
    
    Example
    -------
      ```
      eng = self.create_sre()  
      # add a data stream
      eng.add_entity(
        entity_id='dev_test_1', 
        entity_props=['f1','f2','f3'],
        entity_rules=['state.f1.val == 0 and state.f2.val == 0 and prev.f2.val==1'],
      )
    
      ```
    """
    raise NotImplementedError

  def create_statefull_rule_engine(self, kwargs):
    """
    Returns a Statefull Rule Engine instance
    
    
    Returns
    -------
    SRE()
    
    
    Example
    -------
      ```
      eng = self.create_statefull_rule_engine()  
      # add a data stream
      eng.add_entity(
        entity_id='dev_test_1', 
        entity_props=['f1','f2','f3'],
        entity_rules=['state.f1.val == 0 and state.f2.val == 0 and prev.f2.val==1'],
      )
    
      ```
    """
    raise NotImplementedError

  @property
  def ct():
    """
    Provides access to E2 constants
    
    Returns
    -------
    ct : package
      Use `self.const.ct.CONST_ACME` to acces any required constant
    """
    raise NotImplementedError

  @property
  def current_exec_iteration():
    """
    Returns the current loop exec iteration
    """
    raise NotImplementedError

  @property
  def current_process_iteration():
    """
    Returns the current process iteration
    """
    raise NotImplementedError

  @property
  def cv2():
    """
    provides access to computer vision library
    """
    raise NotImplementedError

  def dataapi_all_metadata(self):
    """
    API for accessing the concatenated stream metadata and metadata from all inputs
    
    Returns
    -------
    dict
      the concatenated stream metadata and metadata from all inputs
    """
    raise NotImplementedError

  def dataapi_full_input(self):
    """
    Returns
    -------
    dict
      full input, as it comes from upstream (empty dictionary if there is not data from upstream):
      {
        'STREAM_NAME' : 'multi_modal_2_images_one_sensor_stream',
        'STREAM_METADATA' : ...,
        'INPUTS' : [{...}, {...}, {...}],
        'INFERENCES : {
          'object_detection_model' : [
            [{'TLBR_POS' : ...}, {'TLBR_POS' : ...}, {'TLBR_POS' : ...}],
            [{'TLBR_POS' : ...}]
          ],
    
          'anomaly_detection_model' : [
            'True/False'
          ]
        },
        'INFERENCES_META' : {
          'object_detection_model' : {'SYSTEM_TYME' : ..., 'VER' : ..., 'PICKED_INPUT' : 'IMG'},
          'anomaly_detection_model' : {'SYSTEM_TYME' : ..., 'VER' : ..., 'PICKED_INPUT' : 'STRUCT_DATA'}
        }
      }
    """
    raise NotImplementedError

  def dataapi_image(self, full, raise_if_error):
    """
    API for accessing the first image in the 'INPUTS' list
    (shortcut for `dataapi_specific_image`, most of the cases will have a single image on a stream)
    
    Parameters
    ----------
    full : bool, optional
      Passed to `dataapi_specific_image`
      The default value is False
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image`
      The default value is False
    
    Returns
    -------
    dict (if full==True) / np.ndarray (if full==False)
      Returned by `dataapi_specific_image`
    
    Raises
    ------
    IndexError
      when there are no images on the stream if `raise_if_error == True`
    """
    raise NotImplementedError

  def dataapi_image_global_inferences(self, how, raise_if_error):
    """
    API for accessing the first image global inferences
    (shortcut for `dataapi_specific_image_global_inferences`, most of the cases will have a single image on a stream)
    
    Parameters
    ----------
    how : str, optional
      Passed to `dataapi_specific_image_global_inferences`
      The default value is None
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_global_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_global_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_global_inferences`
    """
    raise NotImplementedError

  def dataapi_image_inferences(self, how, mode, raise_if_error):
    """
    API for accessing the first image inferences
    (shortcut for `dataapi_specific_image_inferences`, most of the cases will have a single image on a stream)
    
    Parameters
    ----------
    how : str, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    mode : str, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_inferences`
    """
    raise NotImplementedError

  def dataapi_image_instance_inferences(self, how, raise_if_error):
    """
    API for accessing the first image instance inferences
    (shortcut for `dataapi_specific_image_instance_inferences`, most of the cases will have a single image on a stream)
    
    Parameters
    ----------
    how : str, optional
      Passed to `dataapi_specific_image_instance_inferences`
      The default value is None ('list')
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_instance_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_instance_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_instance_inferences`
    """
    raise NotImplementedError

  def dataapi_image_plugin_inferences(self, how, raise_if_error):
    """
    API for accessing the first image plugin inferences
    (shortcut for `dataapi_specific_image_plugin_inferences`, most of the cases will have a single image on a stream)
    
    Parameters
    ----------
    how : str, optional
      Passed to `dataapi_specific_image_plugin_inferences`
      The default value is None
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_plugin_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_plugin_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_plugin_inferences`
    """
    raise NotImplementedError

  def dataapi_image_plugin_positional_inferences(self, how, raise_if_error):
    """
    API for accessing the first image plugin positional inferences
    (shortcut for `dataapi_specific_image_plugin_positional_inferences`, most of the cases will have a single image on a stream)
    
    Parameters
    ----------
    how : str, optional
      Passed to `dataapi_specific_image_plugin_positional_inferences`
      The default value is None
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_plugin_positional_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_plugin_positional_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_plugin_positional_inferences`
    """
    raise NotImplementedError

  def dataapi_images(self, full):
    """
    API for accessing all the images in the 'INPUTS' list
    Parameters
    ----------
    full : bool, optional
      Specifies whether the images are returned full (the whole input dictionary) or not (just the value of 'IMG' in the input dictionary)
      The default value is False
    
    Returns
    -------
    dict{int : dict} (if full==True) / dict{int : np.ndarray} (if full=False)
      The substreams that have images.
      For the second example in the class docstring ('multi_modal_2_images_one_sensor_stream'), the API will return
        {
          0 : {
            'IMG' : np.ndarray(1),
            'STRUCT_DATA' : None,
            'INIT_DATA' : None,
            'TYPE' : 'IMG',
            'METADATA' : {Dictionary with current input metadata}
          },
    
          1 : {
            'IMG' : np.ndarray(2),
            'STRUCT_DATA' : None,
            'INIT_DATA' : None,
            'TYPE' : 'IMG',
            'METADATA' : {Dictionary with current input metadata}
          }
        } if full==True
    
        or
    
        {
          0 : np.ndarray(1),
          1 : np.ndarray(2)
        } if full==False
    """
    raise NotImplementedError

  def dataapi_images_as_list(self):
    raise NotImplementedError

  def dataapi_images_global_inferences(self):
    """
    Alias for `dataapi_images_inferences`
    """
    raise NotImplementedError

  def dataapi_images_inferences(self):
    """
    API for accessing just the images inferences.
    Filters the output of `dataapi_inferences`, keeping only the AI engines that run on images
    
    Returns
    -------
    dict{str:list}
      the inferences that comes from the images serving plugins configured for the current plugin instance.
    """
    raise NotImplementedError

  def dataapi_images_instance_inferences(self):
    """
    API for accessing the images inferences, filtered by confidence threshold, object types and target zone.
    More specifically, all the instance inferences are the plugin inferences that intersects (based on PRC_INTERSECT)
    with the configured target zone.
    
    Returns
    -------
    dict{str:list}
      filtered images inferences by confidence threshold, object types and target zone
    """
    raise NotImplementedError

  def dataapi_images_plugin_inferences(self):
    """
    API for accessing the images inferences, filtered by confidence threshold and object types.
    More specifically, all the plugin inferences are the global inferences that surpass a configured confidence
    threshold and have a specific type. For example, an object detector basically infers for all the objects in
    COCO dataset. But, a certain plugin may need only persons and dogs.
    
    Returns
    -------
    dict{str:list}
      filtered images inferences by confidence threshold and object types
    """
    raise NotImplementedError

  def dataapi_images_plugin_positional_inferences(self):
    """
    API for accessing the images inferences that have positions (TLBR_POS).
    Returns
    -------
    dict{str:list}
      filtered images inferences by having positions (TLBR_POS)
    """
    raise NotImplementedError

  def dataapi_inference_result(self):
    raise NotImplementedError

  def dataapi_inference_results(self, model_name, idx):
    """
    Returns the inference results for a specific model and a specific input index.
    
    Parameters
    ----------
    model_name : str
      The name of the model for which the inference results are requested.
    
    idx : int, optional
      The index of the input for which the inference results are requested.
      The default value is 0.
    
    Returns
    -------
    list
      The inference results.
    """
    raise NotImplementedError

  def dataapi_inferences(self, squeeze):
    """
    Returns
    -------
    dict{str:list}
      the inferences that come from the serving plugins configured for the current plugin instance. 
      Each key is the name of the serving plugin (AI engine). 
      Each value is a list where each item in the list is an inference.
    
      Example:
        {
          'object_detection_model' : [
            [{'TLBR_POS' : ...}, {'TLBR_POS' : ...}, {'TLBR_POS' : ...}],
            [{'TLBR_POS' : ...}]
          ],
    
          'anomaly_detection_model' : [
            'True/False'
          ]
        }
    """
    raise NotImplementedError

  def dataapi_inferences_by_model(self, model_name):
    """
    Returns the inference results for a specific model.
    
    Parameters
    ----------
    model_name : str
      The name of the model for which the inference results are requested.
    
    Returns
    -------
    list
      The inference results.
    """
    raise NotImplementedError

  def dataapi_inferences_meta(self):
    """
    Returns
    -------
    dict{str:dict}
      the inference metadata that comes from the serving plugins configured for the current plugin instance
    
      Example:
        {
          'object_detection_model' : {'SYSTEM_TYME' : ..., 'VER' : ..., 'PICKED_INPUT' : 'IMG'},
          'anomaly_detection_model' : {'SYSTEM_TYME' : ..., 'VER' : ..., 'PICKED_INPUT' : 'STRUCT_DATA'}
        }
    """
    raise NotImplementedError

  def dataapi_input_metadata(self, raise_if_error):
    """
    API for accessing the metadata of the first input
    (shortcut for `dataapi_specific_input_metadata`, most of the cases will have a single input on a stream)
    
    Parameters
    ----------
    raise_if_error : bool, optional
      Passed to `dataapi_specific_input_metadata`
      The default value is False
    
    Returns
    -------
    dict
      Returned by `dataapi_specific_input_metadata`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_input_metadata`
    """
    raise NotImplementedError

  def dataapi_inputs(self):
    """
    Returns
    -------
    list[dict]
      the inputs of the stream that sends data to the current plugin instance
    """
    raise NotImplementedError

  def dataapi_inputs_metadata(self, as_list):
    """
    API for accessing the concatenated metadata from all inputs (images and structured datas together)
    This is not the same as the stream metadata that points to the overall params of the execution
    pipeline.
    
    Returns
    -------
    dict
      the concatenated metadata from all inputs
    """
    raise NotImplementedError

  def dataapi_plugin_input(self):
    """
    Alias for `self.dataapi_full_input`
    
    Returns
    -------
    dict
      full input, as it comes from upstream (empty dictionary if there is not data from upstream)
    """
    raise NotImplementedError

  def dataapi_received_input(self):
    """
    Returns
    -------
    bool
      whether input received from upstream or not (a plugin can run also without input)
    """
    raise NotImplementedError

  def dataapi_specific_image(self, idx, full, raise_if_error):
    """
    API for accessing a specific image in the 'INPUTS' list
    
    Parameters
    ----------
    idx : int, optional
      The index of the image in the images list
      Attention! If there is a metastream that collects 3 inputs - ['IMG', 'STRUCT_DATA', 'IMG'], for accessing the last
      image, `idx` should be 1!
      The default value is 0
    
    full : bool, optional
      Passed to `dataapi_images`
      The default value is False
    
    raise_if_error : bool, optional
      Whether to raise IndexError or not when the requested index is out of range.
      The default value is False
    
    Returns
    -------
    dict (if full==True) / np.ndarray (if full==False)
      dict -> the whole input dictionary
      np.ndarray -> the value of 'IMG' in the input dictionary
    
    Raises
    ------
    IndexError
      when the requested index is out of range
    """
    raise NotImplementedError

  def dataapi_specific_image_global_inferences(self, idx, how, raise_if_error):
    """
    API for accessing a specific image global inferences
    (shortcut for `dataapi_specific_image_inferences`)
    
    Parameters
    ----------
    idx : int, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    how : str, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_inferences`
    """
    raise NotImplementedError

  def dataapi_specific_image_inferences(self, idx, how, mode, raise_if_error):
    """
    API for accesing inferences for a specific image (global, plugin or instance inferences)
    See `dataapi_images_global_inferences`, `dataapi_images_plugin_inferences`, `dataapi_images_instance_inferences`
    
    Parameters
    ----------
    idx : int, optional
      The index of the image in the images list
      Attention! If there is a metastream that collects 3 inputs - ['IMG', 'STRUCT_DATA', 'IMG'], for accessing the last
      image, `idx` should be 1!
      The default value is 0
    
    how : str, optional
      Could be: 'list' or 'dict'
      Specifies how the inferences are returned. If 'list', then the AI engine information will be lost and all the
      inferences from all the employed AI engines will be concatenated in a list; If 'dict', then the AI engine information
      will be preserved.
      The default value is None ('list')
    
    mode : str, optional
      Could be: 'global', 'plugin' or 'instance'
      Specifies which inferences are requested.
      The default value is None ('instance')
    
    raise_if_error : bool, optional
      Whether to raise IndexError or not when the requested index is out of range.
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      the requested image inferences (global, plugin or instance) in the requested format (dict or list)
    
    Raises
    ------
    IndexError
      when the requested index is out of range
    """
    raise NotImplementedError

  def dataapi_specific_image_instance_inferences(self, idx, how, raise_if_error):
    """
    API for accessing a specific image inferences for the current plugin instance
    (shortcut for `dataapi_specific_image_inferences`)
    
    Parameters
    ----------
    idx : int, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    how : str, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None ('list')
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_inferences`
    """
    raise NotImplementedError

  def dataapi_specific_image_plugin_inferences(self, idx, how, raise_if_error):
    """
    API for accessing a specific image plugin inferences
    (shortcut for `dataapi_specific_image_inferences`)
    
    Parameters
    ----------
    idx : int, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    how : str, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_inferences`
    """
    raise NotImplementedError

  def dataapi_specific_image_plugin_positional_inferences(self, idx, how, raise_if_error):
    """
    API for accessing a specific image plugin positional inferences
    (shortcut for `dataapi_specific_image_inferences`)
    
    Parameters
    ----------
    idx : int, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    how : str, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is None
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_image_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_image_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_image_inferences`
    """
    raise NotImplementedError

  def dataapi_specific_input(self, idx, raise_if_error):
    """
    API for accessing a specific index (by its index in the 'INPUTS' list).
    
    Parameters
    ----------
    idx : int, optional
      The index of the input in the 'INPUTS' list
      The default value is 0.
    
    raise_if_error : bool, optional
      Whether to raise IndexError or not when the requested index is out of range.
      The default value is False
    
    Returns
    -------
    dict
      The requested input / substream.
      For the second example in the class docstring ('multi_modal_2_images_one_sensor_stream'), if `idx==0`, the API will return
        {
          'IMG' : np.ndarray(1),
          'STRUCT_DATA' : None,
          'INIT_DATA' : None,
          'TYPE' : 'IMG',
          'METADATA' : {Dictionary with current input metadata}
        }
    
    Raises
    ------
    IndexError
      when the requested index is out of range
    """
    raise NotImplementedError

  def dataapi_specific_input_init_data(self, idx, raise_if_error):
    """
    API for accessing the initial data of a specific input
    
    Parameters
    ----------
    idx : int, optional
      Passed to `dataapi_specific_input`
      The default value is 0
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_input`
      The default value is False
    
    Returns
    -------
    dict
      the value of "INIT_DATA" key in the requested input
    
    Raises
    ------
    IndexError
      when the requested index is out of range
    """
    raise NotImplementedError

  def dataapi_specific_input_metadata(self, idx, raise_if_error):
    """
    API for accessing the metadata of a specific input
    
    Parameters
    ----------
    idx : int, optional
      Passed to `dataapi_specific_input`
      The default value is 0
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_input`
      The default value is False
    
    Returns
    -------
    dict
      the value of "METADATA" key in the requested input
    
    Raises
    ------
    IndexError
      when the requested index is out of range
    """
    raise NotImplementedError

  def dataapi_specific_struct_data(self, idx, full, raise_if_error):
    """
    API for accessing a specific structured data in the 'INPUTS' list
    
    Parameters
    ----------
    idx : int, optional
      The index of the structured data in the structured datas list
      Attention! If there is a metastream that collects 3 inputs - ['IMG', 'STRUCT_DATA', 'IMG'], for accessing the structured data
      `idx` should be 0!
      The default value is 0
    
    full : bool, optional
      Passed to `dataapi_struct_datas`
      The default value is False
    
    raise_if_error : bool, optional
      Whether to raise IndexError or not when the requested index is out of range.
      The default value is True
    
    Returns
    -------
    dict (if full==True) / object (if full==False)
      dict -> the whole input dictionary
      object -> the value of 'STRUCT_DATA' in the input dictionary
    
    Raises
    ------
    IndexError
      when the requested index is out of range
    """
    raise NotImplementedError

  def dataapi_specific_struct_data_inferences(self, idx, how, raise_if_error):
    """
    API for accesing a specific structured data inferences
    
    Parameters
    ----------
    idx : int, optional
      The index of the structured data in its list
      Attention! If there is a metastream that collects 3 inputs - ['IMG', 'STRUCT_DATA', 'IMG'], for accessing the structured data,
      `idx` should be 0!
      The default value is 0
    
    how : str, optional
      Could be: 'list' or 'dict'
      Specifies how the inferences are returned. If 'list', then the AI engine information will be lost and all the
      inferences from all the employed AI engines will be concatenated in a list; If 'dict', then the AI engine information
      will be preserved.
      The default value is None ('list')
    
    raise_if_error : bool, optional
      Whether to raise IndexError or not when the requested index is out of range.
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      the requested structured data inferences in the requested format (dict or list)
    
    Raises
    ------
    IndexError
      when the requested index is out of range
    """
    raise NotImplementedError

  def dataapi_stream_info(self):
    raise NotImplementedError

  def dataapi_stream_metadata(self):
    """
    This function serves returns all the params that configured the current execution
    pipeline where the plugin instance is executed.
    
    Returns
    -------
    dict
      the metadata of the stream that sends data to the current plugin instance
    """
    raise NotImplementedError

  def dataapi_stream_name(self):
    """
    Returns
    -------
    str
      the name of the stream that sends data to the current plugin instance
    """
    raise NotImplementedError

  def dataapi_struct_data(self, full, raise_if_error):
    """
    API for accessing the first structured data in the 'INPUTS' list
    (shortcut for `dataapi_specific_struct_data`, most of the cases will have a single structured data on a stream)
    
    Parameters
    ----------
    full : bool, optional
      Passed to `dataapi_specific_struct_data`
      The default value is False
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_struct_data`
      The default value is True
    
    Returns
    -------
    dict (if full==True) / object (if full==False)
      Returned by `dataapi_specific_struct_data`
    
    Raises
    ------
    IndexError
      when there are no struct_data on the stream
    """
    raise NotImplementedError

  def dataapi_struct_data_inferences(self, how, raise_if_error):
    """
    API for accesing a the first structured data inferences
    (shortcut for `dataapi_specific_struct_data_inferences`, most of the cases will have a single struct data on a stream)
    
    Parameters
    ----------
    how : str, optional
      Passed to `dataapi_specific_struct_data_inferences`
      The default value is None
    
    raise_if_error : bool, optional
      Passed to `dataapi_specific_struct_data_inferences`
      The default value is False
    
    Returns
    -------
    dict (if how == 'dict') or list (if how == 'list')
      returned by `dataapi_specific_struct_data_inferences`
    
    Raises
    ------
    IndexError
      raised by `dataapi_specific_struct_data_inferences`
    """
    raise NotImplementedError

  def dataapi_struct_datas(self, full):
    """
    API for accessing all the structured datas in the 'INPUTS' list
    
    Parameters
    ----------
    full : bool, optional
      Specifies whether the structured datas are returned full (the whole input dictionary) or not (just the value of 'STRUCT_DATA' in the input dictionary)
      The default value is False
    
    Returns
    -------
    dict{int : dict} (if full==True) / dict{int : object} (if full==False)
      The substreams that have structured data.
      For the second example in the class docstring ('multi_modal_2_images_one_sensor_stream'), the API will return
        {
          0: {
            'IMG' : None,
            'STRUCT_DATA' : an_object,
            'INIT_DATA' : None,
            'TYPE' : 'STRUCT_DATA',
            'METADATA' : {Dictionary with current input metadata}
          }
        } if full==True
    
        or
    
        {
          0 : an_object
        } if full==False
    """
    raise NotImplementedError

  def dataapi_struct_datas_inferences(self):
    """
    API for accessing just the structured datas inferences.
    Filters the output of `dataapi_inferences`, keeping only the AI engines that run on structured datas
    
    Returns
    -------
    dict{str:list}
      the inferences that comes from the structured datas serving plugins configured for the current plugin instance.
    """
    raise NotImplementedError

  @property
  def datetime():
    """
    Proxy for the `datetime.datetime`
    
    Returns
    -------
      datetime : datetime object
      
      
    Example
    -------
      ```
      now = self.datetime.now()
      ```
    """
    raise NotImplementedError

  def datetime_to_str(self, dt, fmt):
    """
    Returns the string representation of current datetime or of a given datetime
    
    Parameters
    ----------
    dt : datetime, optional
      a given datetime. The default is `None` and will generate string for current date.
    fmt : str, optional
      datetime format. The default is '%Y-%m-%d %H:%M:%S'.
    
    Returns
    -------
    str
      the datetime in string format.
      
    
    Example
    -------
      ```
      d1 = self.datetime()
      ...
      str_d1 = self.datetime_to_str(d1)
      result = {'D1' : str_d1}
      ```
    """
    raise NotImplementedError

  def deapi_get_wokers(self, n_workers):
    raise NotImplementedError

  @property
  def deepcopy():
    """
    This method allows us to use the method deepcopy
    """
    raise NotImplementedError

  @property
  def defaultdict():
    """
    provides access to defaultdict class
    
    
    Returns
    -------
      defaultdict : class
      
    Example
    -------
      ```
        dct_integers = self.defaultdict(lambda: 0)
      ```
    """
    raise NotImplementedError

  @property
  def deque():
    """
    provides access to deque class
    """
    raise NotImplementedError

  def dict_to_str(self, dct):
    """
    Transforms a dict into a pre-formatted strig without json package
    
    Parameters
    ----------
    dct : dict
      The given dict that will be string formatted.
    
    Returns
    -------
    str
      the nicely formatted.
      
      
    Example:
    -------
      ```
      dct = {
        'a' : {
          'a1' : [1,2,3]
        },
        'b' : 'abc'
      }
      
      str_nice_dict = self.dict_to_str(dct=dct)
      ```
    """
    raise NotImplementedError

  def diskapi_create_video_file_to_data(self, filename, fps, str_codec, frame_size, universal_codec):
    """
    Shortcut to `_diskapi_create_video_file`
    """
    raise NotImplementedError

  def diskapi_create_video_file_to_models(self, filename, fps, str_codec, frame_size, universal_codec):
    """
    Shortcut to `_diskapi_create_video_file`
    """
    raise NotImplementedError

  def diskapi_create_video_file_to_output(self, filename, fps, str_codec, frame_size, universal_codec):
    """
    Shortcut to `_diskapi_create_video_file`
    """
    raise NotImplementedError

  def diskapi_delete_directory(self, dir_path):
    """
    Delete a directory from disk if safe.
    Parameters
    ----------
    dir_path - string, path to the directory to be deleted
    
    Returns
    -------
    """
    raise NotImplementedError

  def diskapi_delete_file(self, file_path):
    """
    Delete a file from disk if safe.
    Parameters
    ----------
    file_path - string, path to the file to be deleted
    
    Returns
    -------
    """
    raise NotImplementedError

  def diskapi_load_dataframe_from_data(self, filename, decompress, timestamps):
    """
    Shortcut to _diskapi_load_dataframe.
    """
    raise NotImplementedError

  def diskapi_load_dataframe_from_models(self, filename, decompress, timestamps):
    """
    Shortcut to _diskapi_load_dataframe.
    """
    raise NotImplementedError

  def diskapi_load_dataframe_from_output(self, filename, decompress, timestamps):
    """
    Shortcut to _diskapi_load_dataframe.
    """
    raise NotImplementedError

  def diskapi_load_json_from_data(self, filename, verbose):
    """
    Shortcut to _diskapi_load_json.
    """
    raise NotImplementedError

  def diskapi_load_json_from_models(self, filename, verbose):
    """
    Shortcut to _diskapi_load_json.
    """
    raise NotImplementedError

  def diskapi_load_json_from_output(self, filename, verbose):
    """
    Shortcut to _diskapi_load_json.
    """
    raise NotImplementedError

  def diskapi_load_pickle_from_data(self, filename, subfolder, decompress, verbose):
    """
    Shortcut to _diskapi_load_pickle.
    """
    raise NotImplementedError

  def diskapi_load_pickle_from_models(self, filename, subfolder, decompress, verbose):
    """
    Shortcut to _diskapi_load_pickle.
    """
    raise NotImplementedError

  def diskapi_load_pickle_from_output(self, filename, subfolder, decompress, verbose):
    """
    Shortcut to _diskapi_load_pickle.
    """
    raise NotImplementedError

  def diskapi_save_dataframe_to_data(self, df, filename, ignore_index, compress, mode, header, also_markdown, verbose, as_parquet):
    """
    Shortcut to _diskapi_save_dataframe.
    """
    raise NotImplementedError

  def diskapi_save_dataframe_to_models(self, df, filename, ignore_index, compress, mode, header, also_markdown, verbose, as_parquet):
    """
    Shortcut to _diskapi_save_dataframe.
    """
    raise NotImplementedError

  def diskapi_save_dataframe_to_output(self, df, filename, ignore_index, compress, mode, header, also_markdown, verbose, as_parquet):
    """
    Shortcut to _diskapi_save_dataframe.
    """
    raise NotImplementedError

  def diskapi_save_file_output(self, data, filename, subdir, extension):
    """
    Shortcut to _diskapi_save_file.
    Parameters
    ----------
    data - string or list, the data to be saved
    filename - string, the name of the file
    subdir - string, the subfolder in local cache
    extension - string, the extension of the file
    
    Returns
    -------
    bool, True if the file was saved successfully, False otherwise
    """
    raise NotImplementedError

  def diskapi_save_image_output(self, image, filename, subdir, extension):
    """
    Shortcut to _diskapi_save_image.
    Parameters
    ----------
    image - np.ndarray, the image to be saved
    filename - string, the name of the file
    subdir - string, the subfolder in local cache
    extension - string, the extension of the file
    
    Returns
    -------
    bool, True if the image was saved successfully, False otherwise
    """
    raise NotImplementedError

  def diskapi_save_json_to_data(self, dct, filename, indent):
    """
    Shortcut to _diskapi_save_json
    """
    raise NotImplementedError

  def diskapi_save_json_to_models(self, dct, filename, indent):
    """
    Shortcut to _diskapi_save_json
    """
    raise NotImplementedError

  def diskapi_save_json_to_output(self, dct, filename, indent):
    """
    Shortcut to _diskapi_save_json
    """
    raise NotImplementedError

  def diskapi_save_pickle_to_data(self, obj, filename, subfolder, compress, verbose):
    """
    Shortcut to _diskapi_save_pickle.
    """
    raise NotImplementedError

  def diskapi_save_pickle_to_models(self, obj, filename, subfolder, compress, verbose):
    """
    Shortcut to _diskapi_save_pickle.
    """
    raise NotImplementedError

  def diskapi_save_pickle_to_output(self, obj, filename, subfolder, compress, verbose):
    """
    Shortcut to _diskapi_save_pickle.
    """
    raise NotImplementedError

  def diskapi_unzip_dir(self, zip_path, dir_path):
    """
    Unzip a file into a given directory.
    Parameters
    ----------
    zip_path - string, path to .zip file
    dir_path - string, path to directory into which to unzip the input .zip file
    
    Returns
    -------
    string, the path to the unzipped directory
    """
    raise NotImplementedError

  def diskapi_write_video_frame(self, handler, frame):
    """
    Parameters:
    -----------
    handler: _, mandatory
      the handler returned by `diskapi_create_video_file`
    
    frame: np.ndarray, mandatory
      the frame to be written in the video file.
      Must have the the same H,W specified in `diskapi_create_video_file`
    """
    raise NotImplementedError

  def diskapi_zip_dir(self, dir_path, zip_path):
    """
    Zip the contents of an entire folder (with that folder included).
    Parameters
    ----------
    dir_path - string, path of directory to zip
    zip_path - string, path of the output zip file. If None, zip_path will be dir_path + ".zip"
    
    Returns
    -------
    string, the path to the zipped directory
    """
    raise NotImplementedError

  @property
  def docker_branch():
    raise NotImplementedError

  def download(self, url, fn, target, kwargs):
    """
    Dowload wrapper that will download a given file from a url to `_local_cache/_output.
    
    
    TODO: fix to use specific endpoints configs not only from base file_system_manager
    
    Parameters
    ----------
    url : str
      the url where to find the file.
    
    fn : str
      local file name to be saved in `target` folder.
    
    **kwargs : dict
      params for special upload procedures such as minio.
    
    
    Returns
    -------
    res : str
      path of the downloaded file, None if not found.
    
    
    Example
    -------
    
      ```
      res = plugin.download('http://drive.google.com/file-url', 'test.bin')
      if res is not None:
        plugin.P("Downloaded!")
      ```
    """
    raise NotImplementedError

  @property
  def ds_consts():
    """
    Alias for DatasetBuilder class from E2 constants
    Provides access to constants used in DatasetBuilderMixin
    Returns
    -------
    ct.DatasetBuilder : package
      Use `self.ds_consts.CONST_ACME` to access any required constant
    """
    raise NotImplementedError

  @property
  def e2_addr():
    raise NotImplementedError

  @property
  def e2_id():
    raise NotImplementedError

  @property
  def ee_addr():
    raise NotImplementedError

  @property
  def ee_id():
    raise NotImplementedError

  @property
  def ee_ver():
    raise NotImplementedError

  @property
  def eeid():
    raise NotImplementedError

  def end_timer(self, tmr_id, skip_first_timing, kwargs):
    raise NotImplementedError

  def exec_code(self, str_b64code, debug, result_vars, self_var, modify):
    raise NotImplementedError

  @property
  def exec_timestamp():
    raise NotImplementedError

  def execute(self):
    """
    The main execution of a plugin instance.
    This public method should NOT be overwritten under any circumstance
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def filter_inferences(self, data, inferences):
    """
    Method used for filtering the inferences that will be saved.
    This is implemented in order for the plugin developer to be able to custom filter
    the data that will be saved.
    Parameters
    ----------
    inferences - list of inferences
    
    Returns
    -------
    res - list of filtered inferences
    """
    raise NotImplementedError

  def filter_inferences_idx(self, data, inferences):
    """
    Method used for filtering the inferences that will be saved.
    This is implemented in order for the plugin developer to be able to custom filter
    the data that will be saved.
    Parameters
    ----------
    inferences - list of inferences
    
    Returns
    -------
    res - list of filtered inferences indexes
    """
    raise NotImplementedError

  @property
  def first_process_time():
    raise NotImplementedError

  @property
  def float_cache():
    """
    Can be used as a statefull store of the instance - eg `plugin.float_cache[key]` will return 0
    if that key has never been initialized    
    
    
    Returns
    -------
    dict of floats
      Returns a default dict for float values initialized with zeros.
    
    
    Example
    -------
      ```
      self.float_cache['f1'] += val
      if self.float_cache['f1']  >= 100:
        self.P("value 100 passed")
      ```
    """
    raise NotImplementedError

  def full_deque(self, alerter):
    raise NotImplementedError

  @property
  def geometry_methods():
    """
    Proxy for geometry_methods from decentra_vision.geometry_methods
        
    """
    raise NotImplementedError

  @property
  def get_additional_keys():
    raise NotImplementedError

  def get_alerter(self, alerter):
    raise NotImplementedError

  def get_alerter_status(self, alerter):
    raise NotImplementedError

  def get_alive_time(self, as_str):
    """
    Returns plugin alive time
    
    Parameters
    ----------
    as_str : bool, optional
      return as string. The default is False.
    
    Returns
    -------
    result : float or str
    
    
    Example
    -------
      ```
      result = 'Plugin was alive ' + self.get_alive_time(as_str=True)
      ```
    """
    raise NotImplementedError

  @property
  def get_background_period_save():
    raise NotImplementedError

  def get_base64code(self):
    raise NotImplementedError

  def get_cmd_handlers(self, update):
    raise NotImplementedError

  def get_commands_after_exec(self):
    raise NotImplementedError

  def get_current_witness(self, pos, alerter):
    raise NotImplementedError

  def get_current_witness_kwargs(self, pos, alerter, demo_mode):
    raise NotImplementedError

  def get_data_folder(self):
    """
    Provides access to get_data_folder() method from .log
    Returns
    -------
    """
    raise NotImplementedError

  @property
  def get_dataset_builder_params():
    raise NotImplementedError

  def get_dataset_name(self):
    raise NotImplementedError

  def get_debug_objects_summary(self, debug_objects):
    raise NotImplementedError

  def get_default_plugin_vars(self):
    raise NotImplementedError

  def get_errors(self):
    raise NotImplementedError

  def get_exception(self):
    """
    Returns last exception fullstack
    
    Returns
    -------
    string
      The full multi-line stack.
    
    Example:
      ```
      ```
    """
    raise NotImplementedError

  @property
  def get_expand_value():
    raise NotImplementedError

  @property
  def get_generic_path():
    raise NotImplementedError

  @property
  def get_image_crop():
    raise NotImplementedError

  @property
  def get_image_save():
    raise NotImplementedError

  @property
  def get_inference_mapping():
    raise NotImplementedError

  def get_inference_track_tlbr(self, inference):
    """
    Returns the TLBR that will be used for tracking an inference
    This is used in order for the developer to be able to use a different TLBR for tracking
    than the actually detected one (maybe an enlarged one)
    Parameters
    ----------
    inference - dict, inference dictionary
    
    Returns
    -------
    res - list, list of 4 ints representing the TLBR that will be used for tracking
    """
    raise NotImplementedError

  def get_infos(self):
    raise NotImplementedError

  def get_instance_config(self):
    raise NotImplementedError

  def get_instance_id(self):
    raise NotImplementedError

  @property
  def get_label_file_template():
    raise NotImplementedError

  def get_label_template_lines(self):
    raise NotImplementedError

  @property
  def get_label_template_type():
    raise NotImplementedError

  def get_last_payload_data(self):
    raise NotImplementedError

  def get_line_passing_direction(self, object_id, object_type, line, zone1_point, zone2_point, start_point, eps):
    """
    This method will compute the direction of an object if the specified object went from Zone1
    to Zone2, where Zone1 and Zone 2 ar separated by a specified line.
    Parameters
    ----------
    object_id - int, id of the specified object
    object_type - str, type of the specified object
    line - list, list of 2 points that describes the line separating the 2 zones
    zone1_point - list or None, list of 2 int/floats describing a point from Zone1
    - if this is None both zone1_point and zone2_point will be auto-generated
    zone2_point - list or None, list of 2 int/floats describing a point from Zone2
    - if this is None both zone1_point and zone2_point will be auto-generated
    start_point - list or None, list of 2 int/floats describing the starting point of the current object
    - if this is None, we will consider the first appearance of the current object as the start
    
    Returns
    -------
      None if the object stayed in one zone
      (0, 1) or (1, 0) if the object passed through the line,
      with (0, 1) indicating it passing from Zone1 to Zone2
      and (1, 0) otherwise
    """
    raise NotImplementedError

  def get_logs_folder(self):
    """
    Provides access to get_logs_folder() method from .log
    Returns
    -------
    """
    raise NotImplementedError

  @property
  def get_mandatory_keys():
    raise NotImplementedError

  def get_models_file(self, fn):
    """
    Retruns path to models file
    
    :param fn: string - file name
    """
    raise NotImplementedError

  def get_models_folder(self):
    """
    Provides access to get_models_folder() method from .log
    Returns
    -------
    """
    raise NotImplementedError

  def get_movement_relative_to_line(self, object_id, object_type, line, zone1_point, zone2_point, threshold, start_point):
    """
    Returns the point direction movement relative to a line (if no points are given, they are automatically generation).
    
    If the object moved from point A to point B (relative to a line) it returns a tuple with the order (PointA, PointB),
      otherwise it returns the tuple reversed (PointB, PointA)
    """
    raise NotImplementedError

  def get_next_avail_input(self):
    raise NotImplementedError

  def get_node_running_time(self):
    """
    Returns the time since the node was started in seconds
    """
    raise NotImplementedError

  def get_node_running_time_str(self):
    """
    Returns the time since the node was started pretty stringyfied
    """
    raise NotImplementedError

  def get_notifications(self):
    raise NotImplementedError

  @property
  def get_object_max_saves():
    raise NotImplementedError

  def get_output_folder(self):
    """
    Provides access to get_output_folder() method from .log
    Returns
    -------
    """
    raise NotImplementedError

  def get_payload_after_exec(self):
    """
    Gets the payload and resets the internal _payload protected variable
    
    Returns
    -------
    payload : GenericPayload
        returns the current payload
    """
    raise NotImplementedError

  @property
  def get_plugin_default_dataset_builder_params():
    """
    Method that will be used for the plugins where the dataset builder mixin will be enabled by default
    in order to facilitate the configuration of this mixin without ignoring the default ds builder params
    provided in the plugin default config.
    Returns
    -------
    """
    raise NotImplementedError

  def get_plugin_loop_resolution(self):
    raise NotImplementedError

  def get_plugin_queue_memory(self):
    raise NotImplementedError

  def get_plugin_used_memory(self, return_tree):
    raise NotImplementedError

  def get_save_cap_resolution(self):
    raise NotImplementedError

  def get_saved_stats(self):
    """
    Method used for retrieving the saved stats of the dataset builder.
    Returns
    -------
    stats_dict - dictionary containing the saved stats
    """
    raise NotImplementedError

  def get_serving_process_given_ai_engine(self, ai_engine):
    raise NotImplementedError

  def get_serving_processes(self):
    """
    Returns a list of used AI Engines within the current plugin instance based on given configuration
    
    Parameters
    ----------
    None.
    
    Returns
    -------
    result : list
      The list.
    
    
    Example
    -------
      ```
      lst_servers = plugin.get_serving_processes()
      ```
    """
    raise NotImplementedError

  def get_signature(self):
    raise NotImplementedError

  @property
  def get_stats_update_period():
    raise NotImplementedError

  def get_stream_id(self):
    raise NotImplementedError

  def get_target_folder(self, target):
    """
    Provides access to get_target_folder() method from .log
    Parameters
    ----------
    target
    
    Returns
    -------
    """
    raise NotImplementedError

  def get_temperature_sensors(self, as_dict):
    """
    Returns the temperature of the machine if available
    
    Returns
    -------
    dict
      The dictionary contains the following:
      - 'message': string indicating the status of the temperature sensors
      - 'temperatures': dict containing the temperature sensors
    """
    raise NotImplementedError

  def get_timezone(self):
    raise NotImplementedError

  @property
  def get_total_max_saves():
    raise NotImplementedError

  def get_upstream_config(self):
    raise NotImplementedError

  def get_warnings(self):
    raise NotImplementedError

  def get_witness_image(self, img, prepare_witness_kwargs, pre_process_witness_kwargs, draw_witness_image_kwargs, post_process_witness_kwargs):
    """
    This is the wrapper function that should be called from any plug-in.
    It contains the channel reversing and the cv2 required numpy magic and it
    will call the `_draw_witness_image` plug-in specific method
    
    definition of: _draw_witness_image(img_witness, **kwargs)
    
    Parameters
    ----------
    img: np.ndarray
      The starting image. Can be None
    
    prepare_witness_kwargs : dict
      anything we need in _witness_prepare (passed as **prepare_witness_kwargs)
    
    pre_process_witness_kwargs : dict
      anything we need in _witness_pre_process (passed as **pre_process_witness_kwargs)
    
    draw_witness_image_kwargs : dict
      anything we need in _draw_witness_image (passed as **draw_witness_image_kwargs)
    
    post_process_witness_kwargs : dict
      anything we need in _witness_post_process (passed as **post_process_witness_kwargs)
    
    Returns
    -------
    img_witness : ndarray
      The returned image will be in RGB format.
    """
    raise NotImplementedError

  def get_witness_image_zone_only(self, img):
    raise NotImplementedError

  def get_x_file_params(self):
    """
    This method will compute a list of tuples of 2 elements that describe what
    keys to use in order to compute and save data for the X files in our dataset.
    The above-mentioned keys will be found in the data provided either by
    the plugin or the model_serving(we will refer to that as dict).
    Can also be further extended by the plugin developer in order to customise
    the extracted params.
    Returns
    -------
      res - list of format
      [
        (SOURCE_KEY1, PROP_KEY1),
        ..
      ]
      where dict[PROP_KEYi] will be used to extract data from dict[SOURCE_KEYi]
    """
    raise NotImplementedError

  @property
  def get_zip_period():
    raise NotImplementedError

  @property
  def global_shmem():
    raise NotImplementedError

  @property
  def gmt():
    """
    Proxy for geometry_methods from decentra_vision.geometry_methods
        
    """
    raise NotImplementedError

  def high_level_execution_chain(self):
    """
    Standard processing cycle
    """
    raise NotImplementedError

  def img_to_base64(self, img):
    """
    Transforms a numpy image into a base64 encoded image
    
    Parameters
    ----------
    img : np.ndarray
        the input image
    
    Returns
    -------
    str: base64 encoded image
    """
    raise NotImplementedError

  def init_plugins_shared_memory(self, dct_global):
    raise NotImplementedError

  @property
  def initiator_addr():
    raise NotImplementedError

  @property
  def initiator_id():
    raise NotImplementedError

  @property
  def input_queue_size():
    """
    Returns the size of the input queue that is consumed iterativelly
    """
    raise NotImplementedError

  @property
  def inputs():
    raise NotImplementedError

  @property
  def inspect():
    """
    Provides access to `inspect` package
    
    Returns
    -------
    `inspect` package      
    """
    raise NotImplementedError

  @property
  def instance_hash():
    raise NotImplementedError

  @property
  def instance_relative_path():
    raise NotImplementedError

  @property
  def int_cache():
    """
    can be used as a statefull store of the instance - eg `plugin.int_cache[key]` will return 0
    if that key has never been initialized    
    
    
    Returns
    -------
    dict of ints
      Returns a default dict for int values initialized with zeros.
    
    
    Example
    -------
      ```
      self.int_cache['v1'] += 1
      if self.int_cache['v1']  == 100:
        self.P("100 run interations in this plugin")
      ```
    """
    raise NotImplementedError

  def interval_to_local(self, interval, weekday, timezone):
    """
    Method for converting an interval to local time.
    In case the weekday is provided and the interval is crossing the midnight
    this will return a list of 2 intervals, one for each day.
    Parameters
    ----------
    interval : list - list of 2 strings representing the start and end of the interval in format HH:MM
    weekday : int or None - the weekday index starting from 0
    timezone : str or None - the timezone to convert to
    
    Returns
    -------
    res - list of 1 or 2 tuples representing the weekday, start and end of the interval in local time.
    """
    raise NotImplementedError

  @property
  def is_data_limited_and_has_frame():
    raise NotImplementedError

  @property
  def is_debug_mode():
    raise NotImplementedError

  @property
  def is_demo_mode():
    raise NotImplementedError

  @property
  def is_last_data():
    raise NotImplementedError

  @property
  def is_limited_data_finished():
    raise NotImplementedError

  def is_path_safe(self, path):
    """
    Method for checking if a certain path is safe(it's inside the cache directory).
    Parameters
    ----------
    path - string, path to be checked
    
    Returns
    -------
    bool, True if the path is safe, False otherwise
    """
    raise NotImplementedError

  @property
  def is_plugin_stopped():
    raise NotImplementedError

  @property
  def is_plugin_temporary_stopped():
    raise NotImplementedError

  @property
  def is_process_postponed():
    raise NotImplementedError

  @property
  def is_queue_overflown():
    raise NotImplementedError

  @property
  def is_supervisor_node():
    raise NotImplementedError

  def is_valid_datapoint(self, data):
    """
    Method used for checking if the provided data is valid for saving or not.
    This is implemented in order for the plugin developer to be able to custom filter
    the data that will be saved.
    Parameters
    ----------
    data
    
    Returns
    -------
    True if valid, False otherwise
    """
    raise NotImplementedError

  @property
  def iteration():
    raise NotImplementedError

  @property
  def json():
    """
    Provides access to `json` package
    
    Returns
    -------
    `json` package      
    """
    raise NotImplementedError

  def json_dumps(self, dct, replace_nan, kwargs):
    """
    Alias for `safe_json_dumps` for backward compatibility
        
    """
    raise NotImplementedError

  def json_loads(self, json_str, kwargs):
    """
    Parses a json string and returns the dictionary
    """
    raise NotImplementedError

  @property
  def last_payload_time():
    raise NotImplementedError

  @property
  def last_payload_time_str():
    raise NotImplementedError

  @property
  def last_process_time():
    raise NotImplementedError

  @property
  def limited_data_counter():
    raise NotImplementedError

  @property
  def limited_data_crt_time():
    raise NotImplementedError

  @property
  def limited_data_duration():
    raise NotImplementedError

  @property
  def limited_data_finished_flag():
    raise NotImplementedError

  @property
  def limited_data_fps():
    raise NotImplementedError

  @property
  def limited_data_frame_count():
    raise NotImplementedError

  @property
  def limited_data_frame_current():
    raise NotImplementedError

  @property
  def limited_data_process_fps():
    raise NotImplementedError

  @property
  def limited_data_progress():
    raise NotImplementedError

  @property
  def limited_data_remaining_time():
    raise NotImplementedError

  @property
  def limited_data_seconds_elapsed():
    raise NotImplementedError

  @property
  def limited_data_total_counter():
    raise NotImplementedError

  def load_config_file(self, fn):
    """
    Loads a json/yaml config file and returns the config dictionary
    
    Parameters
    ----------
    fn : str
      The filename of the config file
    
    Returns
    -------
    dict
      The config dictionary
    """
    raise NotImplementedError

  @property
  def local_data_cache():
    """
    Can be used as a statefull store of the instance - eg `plugin.state[key]` will return `None`
    if that key has never been initialized    
    
    
    Returns
    -------
    dict
      a default dict.
    
    
    Example
    -------
      ```
      obj = self.local_data_cache['Obj1']
      if obj is None:
        obj = ClassObj1()
        self.local_data_cache['Obj1'] = obj
      ```
    """
    raise NotImplementedError

  def lock_resource(self, str_res):
    """
    Locks a resource given a string. Alias to `self.log.lock_resource`
    
    Parameters
    ----------
    str_res : str
        the resource name
    """
    raise NotImplementedError

  @property
  def loop_paused():
    raise NotImplementedError

  @property
  def loop_timings():
    raise NotImplementedError

  def mainthread_wait_for_plugin(self):
    raise NotImplementedError

  def maybe_archive_upload_last_files(self):
    """
    Method used for archiving and uploading the remaining datapoints (if it's the case) when the plugin instance closes.
    Returns
    -------
    """
    raise NotImplementedError

  def maybe_download(self, url, fn, target, kwargs):
    """
    Enables http/htps/minio download capabilities.
    
    
    Parameters
    ----------
    url : str or list
      The URI or URIs to be used for downloads
      
    fn: str of list
      The filename or filenames to be locally used
      
    target: str
      Can be `output`, `models` or `data`. Default is `output`
    
    kwargs: dict
      if url starts with 'minio:' the function will retrieve minio conn
             params from **kwargs and use minio_download (if needed or forced)
    
    Returns
    -------
      files, messages : list, list
        all the local files and result messages from download process
      
      
    Example
    -------
    """
    raise NotImplementedError

  def maybe_init_ds_builder_saved_stats(self):
    raise NotImplementedError

  def maybe_save_data(self, data, single_file):
    """
    DEPRECATED - please use the persistence API
    """
    raise NotImplementedError

  def maybe_start_thread_safe_drawing(self, name):
    raise NotImplementedError

  def maybe_stop_thread_safe_drawing(self):
    raise NotImplementedError

  def maybe_update_instance_config(self, upstream_config, session_id, modified_by_addr, modified_by_id):
    """
    This method is called by the plugin manager when the instance config has changed.
    IMPORTANT: it runs on the same thread as the BusinessManager so it should not block!
    
    For the particular case when only INSTANCE_COMMAND is modified then the plugin should not reset its state
    """
    raise NotImplementedError

  @property
  def modified_by_addr():
    raise NotImplementedError

  @property
  def modified_by_id():
    raise NotImplementedError

  @property
  def n_plugin_exceptions():
    raise NotImplementedError

  def need_refresh(self):
    raise NotImplementedError

  def needs_update(self, dct_newdict, except_keys):
    """
    Check if we need to perform a config update: if a new dict is different from current config_data
    
    Parameters
    ----------
    dct_newdict : dict
        The new dict to be checked
    except_keys : list
        list of keys to be excluded from check
    
    Returns
    -------
    bool, list
        need to update or not and list of keys that are different
    """
    raise NotImplementedError

  @property
  def net_mon():
    raise NotImplementedError

  @property
  def netmon():
    raise NotImplementedError

  @property
  def network_monitor():
    raise NotImplementedError

  @property
  def node_addr():
    raise NotImplementedError

  @property
  def node_id():
    raise NotImplementedError

  def normalize_text(self, text):
    """
    Uses unidecode to normalize text. Requires unidecode package
    
    Parameters
    ----------
    text : str
      the proposed text with diacritics and so on.
    
    Returns
    -------
    text : str
      decoded text if unidecode was avail
    
    
    
    Example
    -------
      ```
      str_txt = "Ha ha ha, mă bucur că ai întrebat!"
      str_simple = self.normalize_text(str_text)
      ```
    """
    raise NotImplementedError

  def now_in_schedule(self, schedule, weekdays):
    """
    Check if the current time is in a active schedule given the schedule data
    
    
    Parameters
    ----------
    schedule : dict or list
      the schedule.
            
    weekdays : TYPE, optional
      list of weekdays. The default is None.
    
    
    Returns
    -------
    bool
      Returns true if time in schedule.
      
    
    Example
    -------
      ```
      simple_schedule = [["09:00", "12:00"], ["13:00", "17:00"]]
      is_working = self.now_in_schedule(schedule=simple_schedule)
      ```
    """
    raise NotImplementedError

  def now_str(self, nice_print, short):
    """
    Returns current timestamp in string format
    Parameters
    ----------
    nice_print
    short
    
    Returns
    -------
    """
    raise NotImplementedError

  @property
  def np():
    """
    Provides access to numerical processing library
    
    
    Returns
    -------
    np : Numpy package
      
    Example:
      ```
      np_zeros = self.np.zeros(shape=(10,10))
      ```
    """
    raise NotImplementedError

  @property
  def obj_cache():
    """
    Can be used as a statefull store of the instance - eg `plugin.obj_cache[key]` will return `None`
    if that key has never been initialized    
    
    
    Returns
    -------
    dict
      a default dict for objects.
    
    
    Example
    -------
      ```
      obj = self.obj_cache['Obj1']
      if obj is None:
        obj = ClassObj1()
        self.obj_cache['Obj1'] = obj
      ```      
    """
    raise NotImplementedError

  def on_close(self):
    """
    Called at shutdown time in the plugin thread.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def on_command(self, data, kwargs):
    """
    Called when the instance receives new INSTANCE_COMMAND
    
    Parameters
    ----------
    data : any
      object, string, etc.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def on_init(self):
    """
    Called at init time in the plugin thread.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  @property
  def os_environ():
    """
    Returns a copy of the current environment variables based on `os.environ`.
    Important: Changing a value in the returned dictionary does NOT change 
               the value of the actual environment variable.
    
    
    Returns
    -------
    _type_
        _description_
    """
    raise NotImplementedError

  @property
  def os_path():
    """
    Proxy for `os.path` package
    
    
    Returns
    -------
      package
      
      
    Example
    -------
      ```
      fn = self.diskapi_save_dataframe_to_data(df, 'test.csv')
      exists = self.os_path.exists(fn)
      ```
    """
    raise NotImplementedError

  @property
  def outside_working_hours():
    raise NotImplementedError

  def parse_generic_path(self, data):
    """
    Method used to generate the path where the current datapoint will be saved at.
    Parameters
    ----------
    data - dictionary of data from both model serving and payload
    
    Returns
    -------
    """
    raise NotImplementedError

  @property
  def partial():
    """
    Provides access to `functools.partial` method
    
    Returns
    -------
      method
    
    
    Example
    -------
      ```
      fn = self.partial(self.diskapi_save_dataframe_to_data, fn='test.csv')
      ```
    """
    raise NotImplementedError

  def path_exists(self, path):
    """
    TODO: must be reviewed
    """
    raise NotImplementedError

  def pause_loop(self):
    raise NotImplementedError

  def payload_set_data(self, key, val):
    raise NotImplementedError

  def payload_set_value(self, key, val):
    """
    This method allows the addition of data directly in the next outgoing payload
    from the current biz plugin instance
    
    Parameters
    ----------
    key : str
      the name of the key
    val : any
      A value that will be json-ified.
    
    Returns
    -------
    None.
    
    
    Example:
    -------      
      ```
      bool_is_alert = ...
      plugin.payload_set_value("is_special_alert", bool_is_alert)
      ```
    """
    raise NotImplementedError

  @property
  def pd():
    """
    Provides access to pandas library
    
    Returns
    -------
      package
      
      
    Example
    -------
      ```
      df = self.pd.DataFrame({'a' : [1,2,3], 'b':[0,0,1]})      
      ```
    """
    raise NotImplementedError

  def persistence_serialization_load(self, default, verbose):
    raise NotImplementedError

  def persistence_serialization_load_from_serving(self, name, default, verbose):
    raise NotImplementedError

  def persistence_serialization_save(self, obj, verbose):
    raise NotImplementedError

  def persistence_serialization_save_to_serving(self, obj, name, verbose):
    raise NotImplementedError

  def persistence_serialization_update(self, update_callback, verbose):
    raise NotImplementedError

  def persistence_serialization_update_serving(self, update_callback, name, verbose):
    raise NotImplementedError

  def plot_ts(self, vals, vals_pred, title):
    """
    Generates a `default_image` that will be embedded in the plugin response containing
    a time-series plot
    
    
    Parameters
    ----------
    vals : list[float]
      the backlog data.
    vals_pred : list[float], optional
      prediction data. The default is None.
    title : str, optional
      a title for our plot. The default is ''.
    
    Returns
    -------
    msg : str
      a error or success `'Plot ok'` message.
    
    
    Example
    -------
      ```
      vals = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
      steps = 3
      yh = self.basic_ts_fit_predict(data=vals, steps=steps)
      has_plot = self.plot_ts(vals, vals_pred=yh, title='prediction for {} steps'.format(steps))
      result = {'preds' : yh, 'plot_ok' : has_plot}
      ```
    """
    raise NotImplementedError

  @property
  def plugin_id():
    """
    Returns the instance id of the current plugin.
    WARNING: This should be overwridden in the plugin class to return the correct id.
    
    Returns
    -------
    str
      the instance id.
      
    Example
    -------
      ```      
      instance_id = self.instance_id
      ```    
    """
    raise NotImplementedError

  def plugin_loop(self):
    """
    This is BusinessPlugin main execution loop (plugin loop)
    
      - plugin.outside_working_hours and plugin.is_process_postponed need to be handled also
      - main thread execution actually is wrapped in the "execute"
      
      stop precedence:
      PROCESS_DELAY > FORCE_PAUSE > WORKING_HOURS
      
    """
    raise NotImplementedError

  @property
  def plugin_output_path():
    raise NotImplementedError

  @property
  def plugins_shmem():
    raise NotImplementedError

  def poseapi_extract_coords_and_scores(self, tlbr, kpt_with_conf, to_flip, inverse_keypoint_coords):
    """
    Extracts the coordinates and scores of the keypoints from the detection along with
    the height and width of the specified person.
    Parameters
    ----------
    tlbr : np.ndarray or list, [top, left, bottom, right] coordinates of the bounding box
    kpt_with_conf : np.ndarray (N, 3) coordinates  and scores of the keypoints in the format [x, y, score]
    to_flip : bool, whether to flip the keypoints
    inverse_keypoint_coords : bool,
      if True the first value of the coordinates will be scaled by the width and the second by the height
      if False the first value of the coordinates will be scaled by the height and the second by the width
    
    Returns
    -------
    keypoint_coords : np.ndarray (N, 2) coordinates of the keypoints
    keypoint_scores : np.ndarray (N,) scores of the keypoints
    height : int, height of the person
    width : int, width of the person
    """
    raise NotImplementedError

  def poseapi_get_arm_indexes(self):
    """
    Alias for poseapi_get_arm_keypoint_indexes
    """
    raise NotImplementedError

  def poseapi_get_arm_keypoint_indexes(self):
    """
    Returns the indexes of the arm keypoints
    """
    raise NotImplementedError

  def poseapi_get_color(self, idx):
    """
    Returns the color of the keypoint
    COLORCODE:
    - face: purple
    - arms: white for left and black for right
    - legs: light blue for left and dark blue for right
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    tuple : color of the keypoint
    """
    raise NotImplementedError

  def poseapi_get_keypoint_color(self, idx):
    """
    Alias for poseapi_get_color
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    tuple : color of the keypoint
    """
    raise NotImplementedError

  def poseapi_get_leg_indexes(self):
    """
    Alias for poseapi_get_leg_keypoint_indexes
    """
    raise NotImplementedError

  def poseapi_get_leg_keypoint_indexes(self):
    """
    Returns the indexes of the leg keypoints
    """
    raise NotImplementedError

  def poseapi_get_shoulder_indexes(self):
    """
    Alias for poseapi_get_shoulder_keypoint_indexes
    """
    raise NotImplementedError

  def poseapi_get_shoulder_keypoint_indexes(self):
    """
    Returns the indexes of the shoulder keypoints
    """
    raise NotImplementedError

  def poseapi_is_arm_keypoint(self, idx):
    """
    Returns whether the keypoint is an arm keypoint
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is an arm keypoint
    """
    raise NotImplementedError

  def poseapi_is_extremity_keypoint(self, idx):
    """
    Returns whether the keypoint is an extremity keypoint(a hand or a foot).
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is an extremity keypoint
    """
    raise NotImplementedError

  def poseapi_is_face_keypoint(self, idx):
    """
    Returns whether the keypoint is a face keypoint
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is a face keypoint
    """
    raise NotImplementedError

  def poseapi_is_insertion_keypoint(self, idx):
    """
    Returns whether the keypoint is an insertion keypoint(hip or shoulder).
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is an insertion keypoint
    """
    raise NotImplementedError

  def poseapi_is_left_sided(self, idx):
    """
    Returns whether the keypoint is left sided
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is left sided
    """
    raise NotImplementedError

  def poseapi_is_leg_keypoint(self, idx):
    """
    Returns whether the keypoint is a leg keypoint
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is a leg keypoint
    """
    raise NotImplementedError

  def poseapi_is_lower_body_keypoint(self, idx):
    """
    Returns whether the keypoint is a lower body keypoint
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is a lower body keypoint
    """
    raise NotImplementedError

  def poseapi_is_right_sided(self, idx):
    """
    Returns whether the keypoint is right sided
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is right sided
    """
    raise NotImplementedError

  def poseapi_is_upper_body_keypoint(self, idx):
    """
    Returns whether the keypoint is an upper body keypoint
    Parameters
    ----------
    idx : int, index of the keypoint
    
    Returns
    -------
    bool : whether the keypoint is an upper body keypoint
    """
    raise NotImplementedError

  def poseapi_keypoint_indexes(self):
    """
    Returns a dictionary with the indexes of the keypoints and their names
    """
    raise NotImplementedError

  def poseapi_keypoint_name(self, idx):
    """
    Returns the name of the keypoint
    """
    raise NotImplementedError

  def poseapi_keypoints_dict(self):
    """
    Returns a dictionary with the keypoints and their indexes
    """
    raise NotImplementedError

  def post_process_wrapper(self):
    raise NotImplementedError

  def pre_process_wrapper(self):
    raise NotImplementedError

  def prepare_b64code(self, str_b64code, check_for_result, result_vars):
    raise NotImplementedError

  def process(self):
    """
    The main code of the plugin (loop iteration code). Called at each iteration of the plugin loop.
    
    Returns
    -------
    Payload.
    """
    raise NotImplementedError

  def process_wrapper(self):
    raise NotImplementedError

  @property
  def pyplot():
    """
    Returns the matplotlib.pyplot package
    
    Returns
    -------
    plt : package
      the matplotlib.pyplot package.
      
    Example
    -------
      ```
      plt = self.pyplot()
      plt.plot(x, y)
      ```
    """
    raise NotImplementedError

  def pyplot_to_np(self, plt):
    """
    Converts a pyplot image to numpy array
    
    Parameters
    ----------
    plt : pyplot
      the pyplot image.
    
    Returns
    -------
    np.ndarray
      the numpy array image.
      
    Example
    -------
      ```
      plt = self.pyplot()
      plt.plot(x, y)
      img = self.pyplot_to_np(plt)
      ```
    """
    raise NotImplementedError

  def python_version(self):
    """
    Utilitary method for accessing the Python version.
    Returns
    -------
    Version of python
    """
    raise NotImplementedError

  def raise_error(self, error_text):
    """
    logs the error and raises it
    """
    raise NotImplementedError

  @property
  def re():
    """
    Provides access to `re` package
    
    Returns
    -------
    `re` package
    """
    raise NotImplementedError

  @property
  def ready_cfg_handlers():
    raise NotImplementedError

  @property
  def requests():
    """
    Provides access to `requests` package
    
    Returns
    -------
    `requests` package      
    """
    raise NotImplementedError

  def reset_debug_info(self):
    raise NotImplementedError

  def reset_default_plugin_vars(self):
    raise NotImplementedError

  def reset_exec_counter_after_config(self):
    raise NotImplementedError

  def reset_first_process(self):
    raise NotImplementedError

  def reset_plugin_instance(self, kwargs):
    raise NotImplementedError

  def resume_loop(self):
    raise NotImplementedError

  def run_cmd(self, cmd, kwargs):
    raise NotImplementedError

  def run_validation_rules(self, verbose, debug_verbose):
    raise NotImplementedError

  @property
  def runs_in_docker():
    raise NotImplementedError

  def safe_json_dumps(self, dct, replace_nan, kwargs):
    """
    Safe json dumps that can handle numpy arrays and so on
    
    Parameters
    ----------
    dct : dict
        The dict to be dumped
        
    replace_nan : bool, optional
        Replaces nan values with None. The default is False.
    
    Returns
    -------
    str
        The json string
    """
    raise NotImplementedError

  def sanitize_name(self, name):
    """
    Returns a sanitized name that can be used as a variable name
    
    Parameters
    ----------
    name : str
        the proposed name
    
    Returns
    -------
    str
        the sanitized name
    """
    raise NotImplementedError

  def save_config_keys(self, keys):
    """
    Method that allows saving the local config in local cache in order to update a
    specific set of given keys that might have been modified during runtime
    
    Parameters
    ----------
    keys : list
      List of keys to be saved.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  @property
  def save_path():
    raise NotImplementedError

  def search_id(self, id, alerter):
    raise NotImplementedError

  def set_default_image(self, img):
    """
    Sets given image as witness for current payload
    
    Parameters
    ----------
    img : np.ndarray
      the RGB image.
    
    
    Example
    -------
      ```
      img = self.dataapi_image()
      self.set_default_image(img)
      ```
    """
    raise NotImplementedError

  def set_image(self, img):
    raise NotImplementedError

  def set_output_image(self, img):
    raise NotImplementedError

  def set_text_witness(self, text):
    """
    Creates a simple empty witness with given centered text.
    
    Parameters
    ----------
    text : str
      The text that will be in the output. If the text is bigger than the screen 
      it will be displayed on multiple lines
    
    Returns
    -------
    None.
    
    
    Example
    -------
      ```
      self.set_text_witness('Hello world in witness image :)')
      ```
    """
    raise NotImplementedError

  def set_witness_image(self, img):
    """
    Sets given image as witness for current payload
    
    Parameters
    ----------
    img : np.ndarray
      the RGB image.
    
    
    Example
    -------
      ```
      img = self.dataapi_image()
      self.set_witness_image(img)
      ```
    """
    raise NotImplementedError

  def setup_config_and_validate(self, dct_config, verbose):
    raise NotImplementedError

  @property
  def shapely_geometry():
    """
    Provides access to geometry library from shapely package
    
    
    Returns
    -------
    geometry : TYPE
      DESCRIPTION.
    """
    raise NotImplementedError

  def should_progress(self, progress, step):
    """
    Helper function for progress intervals from 5 to 5%. Returns true if param progress hits the value
    else false. Once a `True` is returned it will never again be returned
    
    Parameters
    ----------
    progress : float
      percentage 0-100.
    
    Returns
    -------
    result : bool
      a milestone is reached or not.
    """
    raise NotImplementedError

  def shutdown(self):
    raise NotImplementedError

  def sleep(self, seconds):
    """
    sleeps current job a number of seconds
    """
    raise NotImplementedError

  @property
  def sns():
    """
    Provides access to the seaborn library
    
    Returns
    -------
    sns : package
      the Seaborn package.
    
    Example
    -------
      ```
      self.sns.set()
      self.sns.distplot(distribution)
      ```
    """
    raise NotImplementedError

  def start_thread(self):
    raise NotImplementedError

  @property
  def start_time():
    raise NotImplementedError

  def start_timer(self, tmr_id):
    raise NotImplementedError

  def startup(self):
    raise NotImplementedError

  @property
  def state():
    """
    Alias for `plugin.local_data_cache`
    can be used as a statefull store of the instance - eg `plugin.state[key]` will return `None`
    if that key has never been initialized     
    
    Returns
    -------
    dict
      Full local data cache of the current instance.
    """
    raise NotImplementedError

  def step(self):
    """
    The main code of the plugin (loop iteration code). Called at each iteration of the plugin loop.
    
    Returns
    -------
    None.
    """
    raise NotImplementedError

  def stop_thread(self):
    raise NotImplementedError

  def stop_timer(self, tmr_id, skip_first_timing, periodic):
    raise NotImplementedError

  @property
  def str_cache():
    """
    Can be used as a statefull store of the instance - eg `plugin.str_cache[key]` will return empty string
    if that key has never been initialized    
    
    
    Returns
    -------
    defaultdict
      a defaultdict with empty strings.
    
    
    Example
    -------
     ```
     self.str_cache['s1'] += str(val)[0]
     if len(self.int_cache['s1']) > 10:
       self.P("10 numbers added in the string")
     ```
    """
    raise NotImplementedError

  def str_to_base64(self, txt, compress):
    """
    Transforms a string into a base64 encoded string
    
    Parameters
    ----------
    txt : str
        the input string
        
    compress : bool, optional
        if True, the string will be compressed before encoding. The default is False.
    
    Returns
    -------
    str: base64 encoded string
    """
    raise NotImplementedError

  def str_to_datetime(self, str_time, weekday):
    """
    Convert a string time to a datetime object
    Parameters
    ----------
    str_time : str - time in format HH:MM
    weekday : int or None - the weekday index starting from 0
    
    Returns
    -------
    datetime object with the time set to the provided one
    """
    raise NotImplementedError

  @property
  def str_unique_identification():
    raise NotImplementedError

  @property
  def system_version():
    raise NotImplementedError

  @property
  def system_versions():
    raise NotImplementedError

  @property
  def testing_scorer_config():
    raise NotImplementedError

  @property
  def testing_tester_config():
    raise NotImplementedError

  @property
  def testing_tester_name():
    raise NotImplementedError

  @property
  def testing_tester_y_true_src():
    raise NotImplementedError

  @property
  def testing_upload_result():
    raise NotImplementedError

  def threadapi_base64_code_map(self, base64_code, lst_data, n_threads):
    """
    Run a custom code method in parallel using ThreadPoolExecutor.map
    
    Parameters
    ----------
    base64_code : str
        The base64 encoded custom code method
    lst_data : list
        The list of data to pass to the custom code method
    n_threads : int, optional
        The number of threads to use, by default 1
        If this number is higher than 1/4 of available CPUs, it will be set to 1/4 of available CPUs
    
    Returns
    -------
    list
        The results of the custom code method (similar to list(map(func, lst_data)))
    """
    raise NotImplementedError

  def threadapi_map(self, func, lst_data, n_threads):
    """
    Run a function in parallel using ThreadPoolExecutor.map
    
    Parameters
    ----------
    func : callable
        The function to run in parallel
    lst_data : list
        The list of data to pass to the function
    n_threads : int, optional
        The number of threads to use, by default 1
        If this number is higher than 1/4 of available CPUs, it will be set to 1/4 of available CPUs
    
    Returns
    -------
    list
        The results of the function (similar to list(map(func, lst_data)))
    """
    raise NotImplementedError

  def threadapi_run(self, func, n_threads):
    """
    Run a function in parallel using threads
    
    Parameters
    ----------
    func : callable
        The function to run in parallel
        This function must have the following signature: func(thread_id: int, n_threads: int)
    n_threads : int
        The number of threads to use, by default 1
        If this number is higher than 1/4 of available CPUs, it will be set to 1/4 of available CPUs
    
    Returns
    -------
    list
        A list of results from the function calls, similar to [func(0, n_threads), func(1, n_threads), ... func(n_threads-1, n_threads)]
    """
    raise NotImplementedError

  def time(self):
    """
    Returns current timestamp
    
    Returns
    -------
    time : timestamp (float)
      current timestamp.
      
      
    Example
    -------
      ```
      t1 = self.time()
      ... # do some stuff
      elapsed = self.time() - t1
      ```    
    """
    raise NotImplementedError

  @property
  def time_alive():
    raise NotImplementedError

  @property
  def time_from_last_process():
    raise NotImplementedError

  def time_in_interval_hours(self, ts, start, end):
    """
    Provides access to method `time_in_interval_hours` from .log
    Parameters
    ----------
    ts: datetime timestamp
    start = 'hh:mm'
    end = 'hh:mm'
    
    Returns
    -------
    """
    raise NotImplementedError

  def time_in_schedule(self, ts, schedule, weekdays):
    """
    Check if a given timestamp `ts` is in a active schedule given the schedule data
    
    
    Parameters
    ----------
    ts : float
      the given timestamp.
      
    schedule : dict or list
      the schedule.
            
    weekdays : TYPE, optional
      list of weekdays. The default is None.
    
    
    Returns
    -------
    bool
      Returns true if time in schedule.
      
    
    Example
    -------
      ```
      simple_schedule = [["09:00", "12:00"], ["13:00", "17:00"]]
      is_working = self.time_in_schedule(self.time(), schedule=simple_schedule)
      ```
    """
    raise NotImplementedError

  def time_to_str(self, ts, fmt):
    """
    Alias for `timestamp_to_str`
    
    
    Parameters
    ----------
    ts : float, optional
      The given time. The default is None.
    fmt : str, optional
      The time format. The default is '%Y-%m-%d %H:%M:%S'.
    
    Returns
    -------
    str
      the string formatted time.
      
      
    Example
    -------
      ```
      t1 = self.time()
      ...
      str_t1 = self.time_to_str(t1)
      result = {'T1' : str_t1}
      ```
    """
    raise NotImplementedError

  @property
  def time_with_no_data():
    raise NotImplementedError

  def timebins_append(self, value, key):
    raise NotImplementedError

  def timebins_create_bin(self, key, weekday_names, report_default_empty_value, per_day_of_week_timeslot, warmup_anomaly_models):
    raise NotImplementedError

  def timebins_get_bin(self, key):
    raise NotImplementedError

  def timebins_get_bin_mean(self, key):
    raise NotImplementedError

  def timebins_get_bin_report(self, aggr_func, key):
    raise NotImplementedError

  def timebins_get_bin_size(self, key):
    raise NotImplementedError

  def timebins_get_bin_statistic(self, aggr_func, key):
    raise NotImplementedError

  def timebins_get_previous_bin_statistic(self, aggr_func, key):
    raise NotImplementedError

  def timebins_get_total_size(self, key):
    raise NotImplementedError

  def timebins_is_anomaly(self, key):
    raise NotImplementedError

  def timedelta(self, kwargs):
    """
    Alias of `datetime.timedelta`
    
    
    Parameters
    ----------
    **kwargs : 
      can contain days, seconds, microseconds, milliseconds, minutes, hours, weeks.
    
    
    Returns
    -------
    timedelta object
    
    
    Example
    -------
      ```
        diff = self.timedelta(seconds=10)
      ```
    """
    raise NotImplementedError

  def timer_name(self, name):
    raise NotImplementedError

  def timestamp_to_str(self, ts, fmt):
    """
    Returns the string representation of current time or of a given timestamp
    
    
    Parameters
    ----------
    ts : float, optional
      timestamp. The default is None and will generate string for current timestamp. 
    fmt : str, optional
      format. The default is '%Y-%m-%d %H:%M:%S'.
    
    
    Returns
    -------
    str
      the timestamp in string format.
      
    
    Example
    -------
        
      ```
      t1 = self.time()
      ...
      str_t1 = self.time_to_str(t1)
      result = {'T1' : str_t1}
      ```
    """
    raise NotImplementedError

  @property
  def total_payload_count():
    raise NotImplementedError

  def trace_info(self):
    """
    Returns a multi-line string with the last exception stacktrace (if any)
    
    Returns
    -------
    str.
    """
    raise NotImplementedError

  def trackapi_centroid_history(self, object_id, object_type):
    """
    Public method for accessing the centroid history of a specified object.
    Parameters
    ----------
    object_id - int
    object_type - str
    
    Returns
    -------
    res - list, list of points that signify the provided object's centroid on each appearance.
    """
    raise NotImplementedError

  def trackapi_class_count(self, object_id, object_type, class_name):
    """
    If meta-types are not used than this will just provide the number of appearances.
    Public method for accessing how many times the object was a certain class.
    Parameters
    ----------
    object_id - int
    object_type - str
    class_name - str or list
    
    Returns
    -------
    res - int, how many times the object was a certain class.
    """
    raise NotImplementedError

  def trackapi_class_ratio(self, object_id, object_type, class_name):
    """
    If meta-types are not used than this will just provide 1.
    Public method for accessing the ratio between how many times the object was
    a certain class and the total number of appearances.
    Parameters
    ----------
    object_id - int
    object_type - str
    class_name - str or list
    
    Returns
    -------
    res - float, ratio of class appearances.
    """
    raise NotImplementedError

  def trackapi_in_zone_history(self, object_id, object_type):
    """
    Public method for accessing the history in the target zone of a specified object.
    Parameters
    ----------
    object_id - int
    object_type - str
    
    Returns
    -------
    res - list, list of intervals that the specified object was in the target zone.
    """
    raise NotImplementedError

  def trackapi_in_zone_total_seconds(self, object_id, object_type):
    """
    Public method for accessing the total seconds spent in the target zone by a specified object.
    Parameters
    ----------
    object_id - int
    object_type - str
    
    Returns
    -------
    res - int, total number of seconds spent in the target zone
    """
    raise NotImplementedError

  def trackapi_last_rectangle(self, object_id, object_type):
    """
    Public method for accessing the last seen rectangle of a specified object.
    Parameters
    ----------
    object_id - int
    object_type - str
    
    Returns
    -------
    res - list, last seen rectangle of the specified object in format [top, left, bottom, right]
    """
    raise NotImplementedError

  def trackapi_max_movement(self, object_id, object_type, steps, method):
    """
    Public method for accessing the maximum distance between the
    original position of a specified object and all of its following centroids.
    Parameters
    ----------
    object_id - int
    object_type - str
    steps - int or None, how much further back to check for movement
    - if None this will compute the max movement for the entire history
    - if x - int, this will compute the max movement for the last k steps
    method - str, method used for computing the distance
    - if 'l1' this will return the 'l1' distance
    - if 'l2' this will return the 'l2' distance
    
    Returns
    -------
    res - int or float, max distance the specified object was from its original position
    """
    raise NotImplementedError

  def trackapi_non_class_count(self, object_id, object_type, class_name):
    """
    If meta-types are not used than this will just provide 0.
    Public method for accessing how many times the object was not a certain class.
    Parameters
    ----------
    object_id - int
    object_type - str
    class_name - str or list
    
    Returns
    -------
    res - int, how many times the object was not a certain class.
    """
    raise NotImplementedError

  def trackapi_original_position(self, object_id, object_type):
    """
    Public method for accessing the original position of a specified object.
    Parameters
    ----------
    object_id - int
    object_type - str
    
    Returns
    -------
    res - list, centroid of the current object on its first appearance.
    """
    raise NotImplementedError

  def trackapi_type_history(self, object_id, object_type):
    """
    If meta-types are not used than this will just provide the object's number of appearances.
    Public method for accessing the type history of a specified object as a frequency dictionary.
    Parameters
    ----------
    object_id - int
    object_type - str
    
    Returns
    -------
    res - dict, dictionary providing the number of times the current object appeared as a certain class.
    """
    raise NotImplementedError

  def trackapi_type_history_deque(self, object_id, object_type):
    """
    If meta-types are not used than this will just provide a list full of the same type.
    Public method for accessing the type history of a specified object as a deque.
    Parameters
    ----------
    object_id - int
    object_type - str
    
    Returns
    -------
    res - deque, list of the type that the current object was at each appearance
    """
    raise NotImplementedError

  @property
  def unique_identification():
    raise NotImplementedError

  def unlock_resource(self, str_res):
    """
    Unlocks a resource given a string. Alias to `self.log.unlock_resource`
    
    Parameters
    ----------
    str_res : str
        the resource name
    """
    raise NotImplementedError

  def update_config_data(self, new_config_data):
    raise NotImplementedError

  def update_saved_stats(self):
    """
    Method used for updating the saved stats of the dataset builder.
    Returns
    -------
    """
    raise NotImplementedError

  def update_witness_kwargs(self, witness_args, pos, alerter):
    raise NotImplementedError

  def upload_file(self, file_path, target_path, force_upload, save_db, verbose, kwargs):
    raise NotImplementedError

  def upload_folder(self, folder_path, target_path, force_upload, kwargs):
    raise NotImplementedError

  def upload_logs(self, target_path, force_upload):
    raise NotImplementedError

  def upload_output(self, target_path, force_upload):
    raise NotImplementedError

  @property
  def upstream_inputs_deque():
    raise NotImplementedError

  @property
  def urlparse():
    """
    Provides access to `urlparse` method from `urllib.parse` package
    
    Returns
    -------
    `urlparse` method      
    """
    raise NotImplementedError

  @property
  def urlunparse():
    """
    Provides access to `urlunparse` method from `urllib.parse` package
    
    Returns
    -------
    `urlunparse` method      
    """
    raise NotImplementedError

  @property
  def utils():
    """
    Provides access to methods from core.bussiness.utils.py
    """
    raise NotImplementedError

  def uuid(self, size):
    """
    Returns a unique id.
    
    
    Parameters
    ----------
    size : int, optional
      the number of chars in the uid. The default is 13.
    
    Returns
    -------
    str
      the uid.
      
    
    Example
    -------
    
      ```
        str_uid = self.uuid()
        result = {'generated' : str_uid}
      ```      
    """
    raise NotImplementedError

  def validate(self, raise_if_error, verbose):
    raise NotImplementedError

  def validate_dataset_builder(self):
    raise NotImplementedError

  def validate_points(self):
    raise NotImplementedError

  def validate_prc_intersect(self):
    raise NotImplementedError

  def validate_working_hours(self):
    """
    Method for validating the working hours configuration.
    Returns
    -------
    res - bool - True if the configuration is valid, False otherwise
    """
    raise NotImplementedError

  def vision_plot_detections(self):
    """
    Plots detection on default output image if any
    
    
    Returns
    -------
    None.
    
    
    Example
    -------
      ```
      img = self.dataapi_image()
      if img is not None: # no need to try and plot if there is not image        
        self.vision_plot_detections()
      ```
    """
    raise NotImplementedError

  @property
  def was_last_data():
    raise NotImplementedError

  @property
  def working_hours():
    raise NotImplementedError

  @property
  def working_hours_is_new_shift():
    raise NotImplementedError

  def working_hours_to_local(self, working_hours_schedule, timezone):
    """
    Method for converting the working hours to local time.
    Parameters
    ----------
    working_hours_schedule : list or dict - the working hours schedule
    timezone : str or None - the timezone to convert to
    
    Returns
    -------
    res_working_hours - list or dict with the working hours (and weekdays if necessary) converted to local time
    """
    raise NotImplementedError

  @property
  def yaml():
    """
    Provides access to `yaml` package
    
    Returns
    -------
    `yaml` package      
    """
    raise NotImplementedError
