from PyE2 import CustomPluginTemplate, Session
from PyE2.default.instance import CustomWebApp01

# this tutorial can be run only on the local edge node
# because it uses ngrok to expose the fastapi server
# and this requires an ngrok auth token

# See https://naeural-013.ngrok.app/docs


def hello_world(plugin, name: str = "naeural_developer"):
  # name is a query parameter
  return f"Hello, {name}! I am {plugin.e2_addr}"


def get_uuid(plugin: CustomPluginTemplate):
  return f"New uuid: {plugin.uuid()}!"


def get_addr(plugin: CustomPluginTemplate):
  return plugin.node_addr


def predict(plugin: CustomPluginTemplate, series: list[int], steps: int) -> list:
  result = plugin.basic_ts_fit_predict(series, steps)
  result = list(map(int, result))
  return result


if __name__ == "__main__":
  session = Session()

  node = "INSERT_YOUR_NODE_ADDRESS_HERE"
  session.wait_for_node(node)

  instance: CustomWebApp01
  pipeline, instance = session.create_web_app(
    node=node,
    name="naeural_predict_app",
    signature=CustomWebApp01,

    ngrok_edge_label="INSERT_YOUR_NGROK_EDGE_LABEL_HERE",
    use_ngrok=True,
  )

  # GET request on <domain>/hello_world?name=naeural_developer
  instance.add_new_endpoint(hello_world)

  # GET request on <domain>/get_uuid
  instance.add_new_endpoint(get_uuid, method="get")

  # GET request on <domain>/get_addr
  instance.add_new_endpoint(get_addr, method="get")

  # POST request on <domain>/forecasting (with body as json with 2 keys: series and steps)
  instance.add_new_endpoint(predict, method="post")

  # add an html file to the web app, accessible at <domain>/
  instance.add_new_html_endpoint(
    html_path="tutorials/8. custom_code_fastapi_assets/index.html",
    web_app_file_name="index.html",
    endpoint_route="/",
  )

  pipeline.deploy()

  session.run(close_pipelines=True)
