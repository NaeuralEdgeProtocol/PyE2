from PyE2 import Session, CustomPluginTemplate
from PyE2.default.instance import CustomWebApp01

# this tutorial can be run only on the local edge node
# because it uses ngrok to expose the fastapi server
# and this requires an ngrok auth token


def hello_world(plugin, name: str = "naeural_developer"):
  # name is a query parameter
  return f"Hello, {name}!"


def get_uuid(plugin: CustomPluginTemplate):
  return f"New uuid: {plugin.uuid()}!"


def get_addr(plugin: CustomPluginTemplate):
  return plugin.node_addr


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
  session = Session()

  session.wait_for_any_node()

  node = session.get_active_nodes()[0]

  instance: CustomWebApp01
  pipeline, instance = session.create_web_app(
    node=node,
    name="naeural_predict_app",
    signature=CustomWebApp01,

    ngrok_edge_label="ADD_YOUR_EDGE_LABEL_HERE",
    use_ngrok=False,
    ngrok_enabled=False,
    port=8080,
  )

  # GET request on <domain>/hello_world?name=naeural_developer
  instance.add_new_endpoint(hello_world)

  # GET request on <domain>/get_uuid
  instance.add_new_endpoint(get_uuid, method="get")

  # GET request on <domain>/get_addr
  instance.add_new_endpoint(get_addr, method="get")

  # POST request on <domain>/forecasting (with body as json with 2 keys: series and steps)
  instance.add_new_endpoint(forecasting, method="post")

  # add an html file to the web app, accessible at <domain>/
  instance.add_new_html_endpoint(
    html_path="tutorials/8. custom_code_fastapi_assets/index.html",
    web_app_file_name="index.html",
    endpoint_route="/",
  )

  pipeline.deploy()

  session.run(close_pipelines=True)
