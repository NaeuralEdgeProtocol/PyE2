"""
This is a simple example of how to use the PyE2 SDK.

In this example, we connect to the network, choose a node and
    deploy a plugin with custom code that will run in real time.
    
For this example, we search for prime numbers using more than one thread.
"""
from PyE2 import Session, CustomPluginTemplate


def plugin_custom_code(plugin: CustomPluginTemplate):
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

  random_numbers = plugin.np.random.randint(0, 100, 10)

  are_primes = plugin.threadapi_map(is_prime, random_numbers, n_threads=2)

  prime_numbers = []
  for i in range(len(random_numbers)):
    if are_primes[i]:
      prime_numbers.append(random_numbers[i])

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
    custom_code=plugin_custom_code,
    process_delay=10,
    on_data=on_data
  )

  p.deploy()

  s.run(wait=60, close_pipelines=True)
