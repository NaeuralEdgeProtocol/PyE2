
import os

from dotenv import load_dotenv

from PyE2 import Session, code_to_base64

load_dotenv()

SERVER_CONFIG = {
    'host': os.getenv('PYE2_HOSTNAME'),
    'port': int(os.getenv('PYE2_PORT')),
    'user': os.getenv('PYE2_USERNAME'),
    'pwd': os.getenv('PYE2_PASSWORD')
}


def instance_on_data(pipeline, data):
  print(data)
  return


def pipeline_on_data(pipeline, signature, instance, data):
  pass


if __name__ == '__main__':
  folder = os.path.split(__file__)[0]
  WORKER_CODE_PATH = os.path.join(folder, 'dedist_example_worker.py')
  INITIATOR_CODE_PATH = os.path.join(folder, 'dedist_example_initiator.py')

  with open(WORKER_CODE_PATH, 'rt') as fh:
    worker_code = fh.read()

  e2id = 'e2id'  # provide a known EE id
  sess = Session(**SERVER_CONFIG, silent=False)
  sess.connect()

  listener_params = {
      **SERVER_CONFIG
  }
  listener_params["PASS"] = listener_params["pwd"]
  listener_params["TOPIC"] = "lummetry/payloads"

  pipeline = sess.create_pipeline(
      e2id=e2id,
      name='test_dist_jobs',
      # data_source='Void',
      # config={},
      data_source='IotQueueListener',  # this DCT allows data acquisition from MQTT brokers
      config={
          'STREAM_CONFIG_METADATA': listener_params,
          "RECONNECTABLE": True,
      },
      plugins=None,
      on_data=pipeline_on_data,
  )

  pipeline.start_custom_plugin(
      instance_id='inst02',
      plain_code_path=INITIATOR_CODE_PATH,
      params={
          'MAX_TRIES': 10,  # this will be used within plugin as `plugin.cfg_max_tries`
          'MAX_RUN_TIME': 60,  # this will be used within plugin as `plugin.cfg_max_run_time`
          'N_WORKERS': 3,  # this will be used within plugin as `plugin.cfg_n_workers`

          # this will be used within plugin as `plugin.cfg_worker_code`
          'WORKER_CODE': code_to_base64(worker_code)
      },
      on_data=instance_on_data,
      process_delay=0.2
  )

  sess.run(wait=True, close_session=True, close_pipelines=True)
