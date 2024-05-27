"""
This is a simple example of how to use the PyE2 library.

In this example, we connect to the network, choose a node and
    deploy a plugin with custom code that will run in real time.
    
For this example, we search for prime numbers in parallel using more than one node.
"""
from PyE2 import Session, CustomPluginTemplate


def custom_code_worker(plugin: CustomPluginTemplate):
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


def custom_code_filter_new_data_entries(plugin: CustomPluginTemplate, job_id, collected_data, data):
  """
  Process the real time data from the worker.

  Parameters
  ----------
  collected_data : dict
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


def custom_code_all_finished(plugin: CustomPluginTemplate, collected_data):
  """
  This method must return True if all the workers finished their jobs.

  Parameters
  ----------
  collected_data : dict
      All the data collected from the workers. 
      This is a list of data shards returned by `self.process_real_time_worker_data` method, in the format defined by the user. 
  """
  collected_primes_so_far = []
  for _, lst_data in collected_data.items():
    collected_primes_so_far.extend(lst_data)

  return len(collected_primes_so_far) > plugin.cfg_total_primes


def custom_code_merge_output(plugin: CustomPluginTemplate, worker_data):
  """
  Merge the output of the workers. This method must call the `self.create_golden_payload` method.

  Parameters
  ----------
  worker_data : list[list[Any]]
      List of data from the workers. The list elements are in the expected order.
  """
  collected_primes_so_far = []
  for _, lst_data in worker_data.items():
    collected_primes_so_far.extend(lst_data)

  return collected_primes_so_far


def on_data(pipeline, full_payload):
  progress = full_payload.get('PROGRESS')
  data = full_payload.get('DATA')
  len_data = 0
  if data:
    data.sort()
    len_data = len(data)

  pipeline.P(f"Progress: {progress} -- Found: {len_data} -- Primes: {data}\n\n")


if __name__ == "__main__":
  s = Session()

  node = "stefan-box-ee"
  s.wait_for_node(node)

  # This should be in #132
  p = s.create_or_attach_to_pipeline(
    node_id=node,
    name="run_distributed",
    data_source="Void"
  )

  p.create_distributed_custom_plugin_instance(
    instance_id="run_distributed",
    chain_dist_template="UNIQUE_LISTS_AGGREGATOR",
    custom_code_process_current_results=custom_code_filter_new_data_entries,
    custom_code_all_finished=custom_code_all_finished,
    custom_code_merge_output=custom_code_merge_output,
    custom_code_worker=custom_code_worker,
    worker_pipeline_config={
      'stream_type': "Void",
    },
    worker_plugin_config={
      "PROCESS_DELAY": 1,
    },
    no_workers=2,
    total_primes=300,
    on_data=on_data
  )

  p.deploy()

  s.run(wait=True, close_pipelines=True)
