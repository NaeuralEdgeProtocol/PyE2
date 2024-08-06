import os
from time import sleep, time

from PyE2 import Payload, Pipeline, Session, load_dotenv


boxes = {}

custom_worker_code = """
_result=None
payload = plugin.dataapi_struct_data()
if payload is not None:
  plugin.P("Received data")

  payload_box_name = payload.get('EE_ID', payload.get('SB_ID'))
  payload_active_plugins = payload.get('ACTIVE_PLUGINS')

  if payload_box_name is not None and payload_active_plugins is not None:


    inst = []

    for active_plugin in payload_active_plugins:
      inst.append((active_plugin['STREAM_ID'], active_plugin['SIGNATURE'], active_plugin['INSTANCE_ID']))

    _result = {
      'BOX' : payload_box_name,
      'INSTANCES' : inst
    }
  else:
    plugin.P(payload)
    plugin.P(payload['EE_EVENT_TYPE'])
    plugin.P(payload_box_name)
    plugin.P(payload_active_plugins)
"""


def instance_on_data(pipeline: Pipeline, data: Payload):
  global boxes
  data['INSTANCES'].sort()
  boxes[data['BOX']] = (data['INSTANCES'], time())
  return


def pipeline_on_notification(pipeline, notification: dict):
  pipeline.P(
      "Received specific notification for pipeline {}".format(pipeline.name))
  return


def sess_on_hb(sess, node, hb):
  act_plug = hb['ACTIVE_PLUGINS']
  for plug in act_plug:
    sess.P((node, plug['STREAM_ID'], plug['SIGNATURE'], plug['INSTANCE_ID']))


load_dotenv()

listener_params = {
  'HOST': os.getenv('AIXP_HOSTNAME'),
  'PORT': int(os.getenv('AIXP_PORT')),
  'USER': os.getenv('AIXP_USERNAME'),
  'PASS': os.getenv('AIXP_PASSWORD'),
  'TOPIC': 'lummetry/ctrl',
}

node_id = 'node_id'
sess = Session(
  on_heartbeat=sess_on_hb
)

pipeline = sess.create_pipeline(
    node=node_id,
    name='test_mqtt',
    data_source='IotQueueListener',
    config={
        'STREAM_CONFIG_METADATA': listener_params,
        "RECONNECTABLE": True,
    },
    plugins=None,
    on_notification=pipeline_on_notification
)

# now start a ciclic process
pipeline.create_custom_plugin_instance(
    instance_id='inst01',
    # plain_code_path="./custom_exec_scripts/custom_exec_tutorial.txt", # you can provide it as a file
    plain_code=custom_worker_code,
    on_data=instance_on_data,
    process_delay=2
)

pipeline.deploy()


def generate_net_map():
  global boxes
  net_map_msgs = ["Printing network map"]
  for box, (instances, last_time) in boxes.items():
    if last_time - time() > 30:
      continue
    net_map_msgs.append(box + ":")
    for i in range(len(instances)):
      (pipeline, signature, instance) = instances[i]

      (o_pipeline, o_signature) = (None, None)
      if i != 0:
        (o_pipeline, o_signature, _) = instances[i - 1]

      same_pipeline = pipeline == o_pipeline
      same_signature = signature == o_signature

      if not same_pipeline:
        net_map_msgs.append(" --- " + pipeline + ":")
      if not same_pipeline or not same_signature:
        net_map_msgs.append("    --- " + signature + ":")
      net_map_msgs.append("        --- " + instance)

    net_map_msgs.append("")
  return "\n".join(net_map_msgs)


try:
  while True:
    sleep(10)

    # pipeline.P(generate_net_map(), color='m')
except KeyboardInterrupt:
  pipeline.P("CTRL+C detected. Closing example..", color='r')


sess.close(close_pipelines=True)
