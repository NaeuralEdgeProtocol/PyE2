from ...base import Instance


class ChainDistCustomJob01(Instance):
  signature = "PROCESS_REAL_TIME_COLLECTED_DATA_CUSTOM_EXEC_CHAIN_DIST"

  def add_custom_code_callbacks(
      self,
      main_node_process_real_time_collected_data: callable,
      main_node_finish_condition: callable,
      main_node_finish_condition_kwargs: dict,
      main_node_aggregate_collected_data: callable,
      worker_node_code: callable,
    ):
    self.update_instance_config(
      config={
        "CUSTOM_CODE_PROCESS_REAL_TIME_COLLECTED_DATA": self.pipeline._get_base64_code(main_node_process_real_time_collected_data),
        "CUSTOM_CODE_FINISH_CONDITION": self.pipeline._get_base64_code(main_node_finish_condition),
        "CUSTOM_CODE_AGGREGATE_COLLECTED_DATA": self.pipeline._get_base64_code(main_node_aggregate_collected_data),
        "CUSTOM_CODE_REMOTE_NODE": self.pipeline._get_base64_code(worker_node_code),
        "FINISH_CONDITION_KWARGS": main_node_finish_condition_kwargs
      }
    )
    return

  def add_worker_node_configuration(
      self,
      worker_node_pipeline_config: dict = None,
      worker_node_plugin_config: dict = None,
    ):
    self.update_instance_config(
      config={
        "NODE_PIPELINE_CONFIG": worker_node_pipeline_config or {'stream_type': "Void", },
        "NODE_PLUGIN_CONFIG": worker_node_plugin_config or {},
      }
    )
    return

  def add_main_node_configuration(
      self,
      nr_worker_nodes: int,
      specific_worker_nodes: list = None,
      worker_node_timeout: int = 150,
      cancel_all_jobs_on_exception: bool = False,
    ):
    self.update_instance_config(
      config={
        "NR_REMOTE_NODES": nr_worker_nodes,
        "SPECIFIC_REMOTE_NODES": specific_worker_nodes,
        "REMOTE_NODE_TIMEOUT": worker_node_timeout,
        "CANCEL_ALL_JOBS_ON_EXCEPTION": cancel_all_jobs_on_exception,
      }
    )
    return
