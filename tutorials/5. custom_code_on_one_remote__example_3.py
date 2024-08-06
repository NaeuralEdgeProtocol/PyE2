"""
This is a simple example of how to use the PyE2 SDK.

In this example, we connect to the network, choose a node and
    deploy a plugin with custom code that will run in real time.
    
For this example, we search for prime numbers using more than one thread.
"""
from PyE2 import Session, CustomPluginTemplate


def plugin_custom_code_map(plugin: CustomPluginTemplate):
  """
  The custom code that will be executed on the main thread.
  This is the first flavor of the prime generator code that uses the threading API.
  In this scenario, we use the threadapi_map method to run the code in parallel.

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

  random_numbers = plugin.np.random.randint(0, 100, 10)

  are_primes = plugin.threadapi_map(is_prime, random_numbers, n_threads=2)

  prime_numbers = []
  for i in range(len(random_numbers)):
    if are_primes[i]:
      prime_numbers.append(random_numbers[i])

  return prime_numbers


def plugin_custom_code_run(plugin: CustomPluginTemplate):
  """
  The custom code that will be executed on the main thread.
  This is the second flavor of the prime generator code that uses the threading API.
  In this scenario, we use the threadapi_run method to run the code in parallel.

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

  random_numbers = plugin.np.random.randint(0, 100, 10)

  def get_prime_numbers(thread_id, max_threads):
    start_idx = thread_id * len(random_numbers) // max_threads
    end_idx = (thread_id + 1) * len(random_numbers) // max_threads

    data_slice = random_numbers[start_idx:end_idx]
    prime_numbers: list[int] = []

    for n in data_slice:
      is_prime = True
      if n <= 1:
        is_prime = False
      else:
        for i in range(2, int(plugin.np.sqrt(n)) + 1):
          if n % i == 0:
            is_prime = False
            break
        # end for
      if is_prime:
        prime_numbers.append(n)

    return prime_numbers

  prime_numbers: list[list[int]] = plugin.threadapi_run(get_prime_numbers, n_threads=4)

  prime_numbers: list[int] = [item for sublist in prime_numbers for item in sublist]

  return prime_numbers


def on_data(pipeline, result, full_payload):
  print("Data received: ", result)


if __name__ == "__main__":
  s = Session()

  s.wait_for_any_node()

  node = s.get_active_nodes()[0]

  p = s.create_or_attach_to_pipeline(
    node=node,
    name="run_threading_api",
    data_source="Void"
  )

  p.create_or_attach_to_custom_plugin_instance(
    instance_id="run_threading_api_01",
    custom_code=plugin_custom_code_map,
    process_delay=10,
    on_data=on_data
  )

  p.create_or_attach_to_custom_plugin_instance(
    instance_id="run_threading_api_02",
    custom_code=plugin_custom_code_run,
    process_delay=10,
    on_data=on_data
  )

  p.deploy()

  s.run(wait=60, close_pipelines=True)
