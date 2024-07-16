from PyE2 import Session, CustomPluginTemplate
from PyE2.default.instance import CustomCodeFastAPI01

# this tutorial can be run only on the local edge node
# because it uses ngrok to expose the fastapi server
# and this requires an ngrok auth token


def hello_world(plugin, name):
  # name is a query parameter
  return f"Hello, {name}!"


def get_uuid(plugin: CustomPluginTemplate):
  return f"New uuid: {plugin.uuid()}!"


def forecasting(plugin: CustomPluginTemplate, body=None):
  # body is NOT a query parameter
  # body is a json object (it is the body of the POST request)

  # given a series of data and a number of steps,
  # predict the next `steps` values in the series
  if body is None:
    return None

  if not isinstance(body, dict):
    return None

  series = body.get("series", None)
  if series is None:
    return None

  steps = body.get("steps", None)
  if steps is None:
    return None

  result = plugin.basic_ts_fit_predict(series, steps)
  result = list(map(int, result))
  return result


if __name__ == "__main__":
  sess = Session()

  node = "naeural-1"

  sess.wait_for_node(node)

  pipeline = sess.create_or_attach_to_pipeline(
    node_id=node,
    name="custom_code_fastapi_example",
    data_source="Void"
  )

  instance: CustomCodeFastAPI01 = pipeline.create_or_attach_to_plugin_instance(
    signature=CustomCodeFastAPI01,
    instance_id="tutorial",
    use_ngrok=True,
    ngrok_edge_label="ADD_YOUR_EDGE_LABEL_HERE",
  )

  # GET request on <domain>/hello_world?name=naeural_developer
  instance.add_new_endpoint(hello_world)

  # GET request on <domain>/get_uuid
  instance.add_new_endpoint(get_uuid, method="get")

  # POST request on <domain>/forecasting (with body as json with 2 keys: series and steps)
  instance.add_new_endpoint(forecasting, method="post")

  pipeline.deploy()

  sess.run(close_pipelines=True)
