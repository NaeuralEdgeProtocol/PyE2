class DistributedCustomCodePresets():
  PROCESS_REAL_TIME_COLLECTED_DATA__KEEP_UNIQUES_IN_AGGREGATED_COLLECTED_DATA = "PROCESS_REAL_TIME_COLLECTED_DATA__KEEP_UNIQUES_IN_AGGREGATED_COLLECTED_DATA"
  PROCESS_REAL_TIME_COLLECTED_DATA__KEEP_UNIQUES_IN_NODE_COLLECTED_DATA = "PROCESS_REAL_TIME_COLLECTED_DATA__KEEP_UNIQUES_IN_NODE_COLLECTED_DATA"
  PROCESS_REAL_TIME_COLLECTED_DATA__KEEP_IN_NODE_COLLECTED_DATA = "PROCESS_REAL_TIME_COLLECTED_DATA__KEEP_IN_NODE_COLLECTED_DATA"
  FINISH_CONDITION___EACH_NODE_COLLECTED_DATA_MORE_THAN_X = "FINISH_CONDITION___EACH_NODE_COLLECTED_DATA_MORE_THAN_X"
  FINISH_CONDITION___AGGREGATED_DATA_MORE_THAN_X = "FINISH_CONDITION___AGGREGATED_DATA_MORE_THAN_X"
  AGGREGATE_COLLECTED_DATA___AGGREGATE_COLLECTED_DATA = "AGGREGATE_COLLECTED_DATA___AGGREGATE_COLLECTED_DATA"
  AGGREGATE_COLLECTED_DATA___COLLECTED_DATA_PER_NODE = "AGGREGATE_COLLECTED_DATA___COLLECTED_DATA_PER_NODE"

  def __process_real_time_collected_data__keep_uniques_in_aggregated_collected_data(plugin, job_id, collected_data, data):
    all_data = sum(collected_data.values(), [])
    filtered_data = list(set(d for d in data if d not in all_data))
    return filtered_data

  def __process_real_time_collected_data__keep_uniques_in_node_collected_data(plugin, job_id, collected_data, data):
    filtered_data = list(set(d for d in data if d not in collected_data[job_id]))
    return filtered_data

  def __process_real_time_collected_data__keep_in_node_collected_data(plugin, job_id, collected_data, data):
    return data

  def __finish_condition___each_node_collected_data_more_than_x(plugin, collected_data):
    kwargs = plugin.cfg_finish_condition_kwargs
    if kwargs is None:
      raise Exception("`FINISH_CONDITION_KWARGS` must be set!")
    x = kwargs.get("X")
    if x is None:
      raise Exception("`X` must be set in `FINISH_CONDITION_KWARGS`!")
    return all([len(data) > x for data in collected_data])

  def __finish_condition___aggregated_data_more_than_x(plugin, collected_data):
    kwargs = plugin.cfg_finish_condition_kwargs
    if kwargs is None:
      raise Exception("`FINISH_CONDITION_KWARGS` must be set!")
    x = kwargs.get("X")
    if x is None:
      raise Exception("`X` must be set in `FINISH_CONDITION_KWARGS`!")
    return len(sum(collected_data.values(), [])) > x

  def __aggregate_collected_data___aggregate_collected_data(plugin, collected_data):
    return sum(collected_data.values(), [])

  def __aggregate_collected_data___collected_data_per_node(plugin, collected_data):
    return collected_data
