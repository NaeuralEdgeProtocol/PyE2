from time import sleep
from PyE2 import Session


class LLMChat():
  def __init__(self, node, pipeline_name) -> None:
    self.node = node
    self.pipeline_name = pipeline_name
    self.default_context = {
      "STRUCT_DATA": [{
        "request": "",
        "history": [],
        "system_info":
          "You are a python programmer assistant. Be as concise and correct as possible. Write only the code without explanations."
      }]
    }
    self.pipeline = None
    self.context = self.default_context
    self.can_read_command = True

    self.sess = None
    return

  def instance_on_data(self, pipeline, payload):
    if payload.get('INFERENCES') is None:
      return
    response = payload['INFERENCES'][0]['text']
    request = payload['DATA']['request']
    self.context['STRUCT_DATA'][0]['history'].append({
      'request': request,
      'response': response
    })
    pipeline.P(response)
    self.can_read_command = True
    return

  def send_command(self, request):
    """
    Send a command to the target pipeline with the request
    as the user text in the chat round.

    Parameters
    ----------
    request: str, the users chat text

    Returns
    -------
    None
    """
    self.context['STRUCT_DATA'][0]['request'] = request

    to_send = {
      "STRUCT_DATA": [self.context["STRUCT_DATA"][0]]
    }
    self.pipeline.send_pipeline_command(to_send)  # , payload={"UUID": self.pipeline.log.get_unique_id()}
    return

  def main(self):
    self.sess = Session()

    self.sess.P("Please wait until the Execution Engine sends a heartbeat in order to attach to the desired plugin instance.")
    self.sess.wait_for_node(self.node)

    self.pipeline = self.sess.create_or_attach_to_pipeline(
      node=self.node,
      name=self.pipeline_name,
      data_source='OnDemandTextInput',
    )

    self.pipeline.create_or_attach_to_plugin_instance(
      instance_id="default",
      signature="code_assist_01",
      ai_engine="code_generator",
      startup_ai_engine_params={
        "MODEL_NAME": "codellama/CodeLlama-7b-Instruct-hf",
        "MODEL_WEIGHTS_SIZE": 4
      },
      on_data=self.instance_on_data
    )

    self.pipeline.deploy(timeout=30)

    self.sess.P("To stop this app, press `q`")
    self.sess.P("To start a new conversation press `s`")

    while True:
      if not self.can_read_command:
        sleep(0.5)
        continue
      # endif
      command = input("> ")
      if command == 'q':
        break
      if command == 's':
        self.context = self.default_context
        continue
      self.can_read_command = False
      self.send_command(command)
    # endwhile

    self.sess.P("Main thread exiting...")
    self.sess.close(close_pipelines=True, wait_close=True)
    return


if __name__ == '__main__':
  NODE_ID = 'hydra_3_llm'
  PIPELINE_NAME = 'llm'

  data_getter = LLMChat(NODE_ID, PIPELINE_NAME)
  data_getter.main()
