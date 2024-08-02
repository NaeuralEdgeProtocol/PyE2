from ...base import Instance


class CustomWebApp01(Instance):
  signature = "CUSTOM_CODE_FASTAPI_01"

  def get_proposed_endpoints(self):
    from copy import deepcopy
    proposed_config = self._get_proposed_config_dictionary()
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
