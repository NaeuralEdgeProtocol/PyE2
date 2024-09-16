from ...base import Instance, Pipeline


class CustomWebApp01(Instance):
  signature = "CUSTOM_CODE_FASTAPI_01"

  def get_proposed_endpoints(self):
    from copy import deepcopy
    proposed_config = self._get_proposed_config_dictionary(full=True)
    if "ENDPOINTS" in proposed_config:
      return deepcopy(proposed_config["ENDPOINTS"])
    return deepcopy(self.config.get("ENDPOINTS", []))

  def get_endpoint_fields(self, method: callable):
    import inspect

    name = method.__name__
    args = list(map(str, inspect.signature(method).parameters.values()))[1:]
    base64_code = self.pipeline._get_base64_code(method)

    return name, args, base64_code

  def add_new_endpoint(self, function, method="get"):
    name, args, base64_code = self.get_endpoint_fields(function)
    dct_endpoint = {
      "NAME": name
    }

    proposed_endpoints = self.get_proposed_endpoints()
    lst_pos = [pos for pos, endpoint in enumerate(proposed_endpoints) if endpoint["NAME"] == name]

    if len(lst_pos) > 0:
      dct_endpoint = proposed_endpoints[lst_pos[0]]
    else:
      proposed_endpoints.append(dct_endpoint)
    # endif

    dct_endpoint["CODE"] = base64_code
    dct_endpoint["METHOD"] = method
    dct_endpoint["ARGS"] = args

    self.update_instance_config(config={"ENDPOINTS": proposed_endpoints})

  def get_proposed_assets(self):
    from copy import deepcopy
    proposed_config = self._get_proposed_config_dictionary(full=True)
    if "ASSETS" in proposed_config:
      return deepcopy(proposed_config["ASSETS"])
    return deepcopy(self.config.get("ASSETS", {}))

  def get_proposed_jinja_args(self):
    from copy import deepcopy
    proposed_config = self._get_proposed_config_dictionary(full=True)
    if "JINJA_ARGS" in proposed_config:
      return deepcopy(proposed_config["JINJA_ARGS"])
    return deepcopy(self.config.get("JINJA_ARGS", {}))

  def add_new_file_endpoint(self, str_code, file_name, endpoint_name):
    raise NotImplementedError("This method is not implemented yet.")

  def add_new_html_endpoint(self, html_path, web_app_file_name, endpoint_route):
    str_code = None
    with open(html_path, "r") as file:
      str_code = file.read()

    if str_code is None:
      raise ValueError(f"Could not read the file {html_path}")
    self.pipeline: Pipeline
    base64_html = self.pipeline.str_to_base64(str_code, compress=True)

    proposed_assets = self.get_proposed_assets()
    proposed_jinja_args = self.get_proposed_jinja_args()

    if isinstance(proposed_assets, str):
      proposed_assets = {
        "url": [],
        "operation": "decode",
      }
    elif isinstance(proposed_assets, dict):
      if proposed_assets.get("operation") != "decode":
        proposed_assets["operation"] = "decode"
        proposed_assets["url"] = []

    lst_pos = [pos
               for pos, code_name_pair
               in enumerate(proposed_assets["url"])
               if code_name_pair[1] == 'assets/' + web_app_file_name]

    if len(lst_pos) > 0:
      proposed_assets["url"][lst_pos[0]][0] = base64_html
    else:
      proposed_assets["url"].append([base64_html, 'assets/' + web_app_file_name])
    # endif

    if proposed_jinja_args is None:
      proposed_jinja_args = {
        'html_files': [],
      }
    elif proposed_jinja_args.get('html_files') is None:
      proposed_jinja_args['html_files'] = []

    lst_pos = [pos
               for pos, dict_name_route_method,
               in enumerate(proposed_jinja_args['html_files'])
               if dict_name_route_method['name'] == web_app_file_name]

    dict_name_route_method = {
      "name": web_app_file_name,
      "method": "get"
    }
    if len(lst_pos) > 0:
      dict_name_route_method = proposed_jinja_args['html_files'][lst_pos[0]]
    else:
      proposed_jinja_args['html_files'].append(dict_name_route_method)

    dict_name_route_method["route"] = endpoint_route

    self.update_instance_config(config={"ASSETS": proposed_assets, "JINJA_ARGS": proposed_jinja_args})
