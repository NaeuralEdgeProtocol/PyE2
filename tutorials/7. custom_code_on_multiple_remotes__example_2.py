"""
This is a simple example of how to use the PyE2 SDK.

In this example, we connect to the network, choose a node and
    deploy a plugin with custom code that will run in real time.
    
For this example, we search for prime numbers in parallel using more than one node.
"""
from PyE2 import Session, CustomPluginTemplate


def custom_code_remote_node(plugin: CustomPluginTemplate):
  """
  The custom code that will be executed on the main thread.

  Parameters
  ----------
  plugin : CustomPluginTemplate
      The plugin instance. It will be replaced with the plugin instance object on the remote side.

  Returns
  -------
  list
      The result of the custom code.
      In our case, the list of prime numbers found in the random numbers generated.
  """

  def is_prime(n):
    if n <= 1:
      return False
    for i in range(2, int(plugin.np.sqrt(n)) + 1):
      if n % i == 0:
        return False
    return True

  random_numbers = plugin.np.random.randint(0, 5000, 20)

  are_primes = plugin.threadapi_map(is_prime, random_numbers, n_threads=2)

  prime_numbers = []
  for i in range(len(random_numbers)):
    if are_primes[i]:
      prime_numbers.append(random_numbers[i])

  return prime_numbers


def custom_code_keep_uniques_in_all_data(plugin: CustomPluginTemplate, job_id, collected_data, data):
  """
  Process the real time data from the worker.

  Parameters
  ----------
  job_id : int
      The id of the worker.
  collected_data : dict[int, list[Any]]
      The data collected from all the workers up to this point.
  data : Any
      The data from the worker.

  Returns
  -------
  processed_data : Any | None
      The processed data. If None, the data is ignored.
  """
  # plugin.chain_dist_aggregate_unique_lists(collected_data, data)
  collected_primes_so_far = []
  for _, lst_data in collected_data.items():
    collected_primes_so_far.extend(lst_data)

  new_primes = []

  for prime in data:
    if prime not in collected_primes_so_far:
      new_primes.append(prime)
  return new_primes


def custom_code_all_data_more_than_X(plugin: CustomPluginTemplate, collected_data):
  """
  This method must return True if all the workers finished their jobs.

  Parameters
  ----------
  collected_data : dict
      All the data collected from the workers. 
      This is a list of data shards returned by `self.process_real_time_collected_data` method, in the format defined by the user. 

  Returns
  -------
  bool
      True if the condition is met, False otherwise.
  """
  collected_primes_so_far = []
  for _, lst_data in collected_data.items():
    collected_primes_so_far.extend(lst_data)

  return len(collected_primes_so_far) > plugin.cfg_total_primes


def custom_code_aggregate_collected_data_from_all_workers(plugin: CustomPluginTemplate, collected_data):
  """
  Merge the output of the workers. This method must call the `self.create_golden_payload` method.

  Parameters
  ----------
  collected_data : list[list[Any]]
      List of data from the workers. The list elements are in the expected order.

  Returns
  -------
  Any
      The final data to be returned by the plugin.
  """
  collected_primes_so_far = []
  for _, lst_data in collected_data.items():
    collected_primes_so_far.extend(lst_data)

  return collected_primes_so_far


final_result = []


def on_data(pipeline, full_payload):
  global final_result
  progress = full_payload.get('PROGRESS')
  data = full_payload.get('DATA')
  len_data = 0
  if data:
    data.sort()
    len_data = len(data)

  pipeline.P(f"Progress: {progress} -- Found: {len_data} -- Primes: {data}\n\n")

  if progress == 100:
    pipeline.P("FINISHED\n\n")
    final_result = data
  return


if __name__ == "__main__":
  s = Session()

  s.wait_for_any_node()

  node = s.get_active_nodes()[0]

  # This should be in #132
  p = s.create_or_attach_to_pipeline(
    node=node,
    name="run_distributed",
    data_source="Void"
  )

  p.create_chain_dist_custom_plugin_instance(
    instance_id="run_distributed",
    main_node_process_real_time_collected_data=custom_code_keep_uniques_in_all_data,
    main_node_finish_condition=custom_code_all_data_more_than_X,
    main_node_aggregate_collected_data=custom_code_aggregate_collected_data_from_all_workers,

    worker_node_code=custom_code_remote_node,
    node_pipeline_config={
      'stream_type': "Void",
    },
    node_plugin_config={
      "PROCESS_DELAY": 1,
    },
    nr_remote_worker_nodes=2,
    total_primes=100,
    on_data=on_data
  )

  p.deploy()

  # process incoming messages until the finish condition is met
  s.run(wait=lambda: len(final_result) == 0, close_pipelines=True, close_session=True)

  s.P("Final result has {} observations".format(len(final_result)), color='g')
