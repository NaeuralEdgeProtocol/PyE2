"""
This is a simple example of how to use the PyE2 SDK.

In this example, we connect to the network, choose a node and
    deploy a plugin with custom code that will run in real time.
    
For this example, we search for prime numbers using more than one thread.

The difference from previous example is that we define the custom code that will run in parallel
  on the client size, and we send it to the remote side as base64 code.
"""
from PyE2 import Session, CustomPluginTemplate, method_to_base64


def remote_code_is_prime(plugin: CustomPluginTemplate, data: int):
  """
  Code that will be executed remote and in parallel, on multiple threads.

  Parameters
  ----------
  plugin : CustomPluginTemplate
      The plugin instance. It will be replaced with the plugin instance object on the remote side. 
  data : int
      The data that will be processed by the remote code.
      In our case, it will be a random number, but it can be anything

  Returns
  -------
  bool
      The result of this code.
      In our case, True if the number is prime, False otherwise
  """
  n = data

  if n <= 1:
    return False
  for i in range(2, int(n**0.5) + 1):
    if n % i == 0:
      return False
  return True


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
  base64_custom_method = plugin.cfg_threading_custom_code

  random_numbers = plugin.np.random.randint(0, 100, 10)

  are_primes = plugin.threadapi_base64_code_run(base64_custom_method, random_numbers)

  return [n for n, is_prime in zip(random_numbers, are_primes) if is_prime]


def on_data(pipeline, result, full_payload):
  print("Data received: ", result)


if __name__ == "__main__":
  s = Session()

  s.wait_for_any_node()

  node = s.get_active_nodes()[0]

  p = s.create_or_attach_to_pipeline(
    node_id=node,
    name="run_threading_api",
    data_source="Void"
  )

  p.create_or_attach_to_custom_plugin_instance(
    instance_id="run_threading_api_01",
    custom_code=plugin_custom_code,
    process_delay=10,

    # we convert the code that will be executed on multiple threads to base64
    # to send it to the remote side
    threading_custom_code=method_to_base64(remote_code_is_prime),
    on_data=on_data
  )

  p.deploy()

  s.run(wait=60, close_pipelines=True)
