from PyE2 import Session, CustomPluginTemplate, Pipeline
from PyE2 import DistributedCustomCodePresets as Presets


def local_brute_force_prime_number_generator():
  from concurrent.futures import ThreadPoolExecutor
  import numpy as np

  def is_prime(n):
    if n <= 1:
      return False
    for i in range(2, int(np.sqrt(n)) + 1):
      if n % i == 0:
        return False
    return True

  thread_pool = ThreadPoolExecutor(max_workers=4)

  random_numbers = np.random.randint(1, 5000, 20)
  are_primes = list(thread_pool.map(is_prime, random_numbers))

  prime_numbers = []
  for i in range(len(random_numbers)):
    if are_primes[i]:
      prime_numbers.append(random_numbers[i])

  return prime_numbers


def worker_brute_force_prime_number_generator(plugin: CustomPluginTemplate):
  def is_prime(n):
    if n <= 1:
      return False
    for i in range(2, int(plugin.np.sqrt(n)) + 1):
      if n % i == 0:
        return False
    return True

  random_numbers = plugin.np.random.randint(1, 5000, 20)
  are_primes = plugin.threadapi_map(is_prime, random_numbers, n_threads=4)

  prime_numbers = []
  for i in range(len(random_numbers)):
    if are_primes[i]:
      prime_numbers.append(random_numbers[i])

  return prime_numbers


final_result = []


def locally_process_partial_results(pipeline: Pipeline, full_payload):
  global final_result
  progress = full_payload.get('PROGRESS')
  data = full_payload.get('DATA')
  len_data = 0
  if data:
    data.sort()
    len_data = len(data)

  pipeline.P(f"Found: {len_data} -- Primes: {data}\n\n")

  if progress == 100:
    pipeline.P("FINISHED\n\n")
    final_result = data
  return


if __name__ == "__main__":
  s = Session()

  s.wait_for_any_node()

  node = s.get_active_nodes()[0]

  # define the job
  s.create_chain_dist_custom_job(
    node=node,
    main_node_process_real_time_collected_data=Presets.PROCESS_REAL_TIME_COLLECTED_DATA__KEEP_UNIQUES_IN_AGGREGATED_COLLECTED_DATA,
    main_node_finish_condition=Presets.FINISH_CONDITION___AGGREGATED_DATA_MORE_THAN_X,
    main_node_finish_condition_kwargs={
      "X": 100
    },
    main_node_aggregate_collected_data=Presets.AGGREGATE_COLLECTED_DATA___AGGREGATE_COLLECTED_DATA,
    nr_remote_worker_nodes=2,

    worker_node_code=worker_brute_force_prime_number_generator,
    worker_node_plugin_config={
      "MAX_INT": 5000,
    },

    on_data=locally_process_partial_results,
    # if True, we wait until our node confirms that it received the job
    deploy=True
  )

  # process incoming messages until the finish condition is met
  s.run(wait=lambda: len(final_result) == 0, close_pipelines=True, close_session=True)

  s.P("Final result has {} observations".format(len(final_result)), color='g')
