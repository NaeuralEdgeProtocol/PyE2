
import os

from pye2 import Session, Payload, code_to_base64


def instance_on_data(pipeline, custom_code_data: dict, data: Payload):
  print(custom_code_data)
  return


if __name__ == '__main__':
  folder = os.path.split(__file__)[0]
  WORKER_CODE_PATH = os.path.join(folder, 'chain_dist_example_worker.py')
  INITIATOR_CODE_PATH = os.path.join(folder, 'chain_dist_example_initiator.py')

  with open(WORKER_CODE_PATH, 'rt') as fh:
    worker_code = fh.read()

  e2id = 'stefan-box'  # provide a known EE id
  sess = Session(filter_workers=[e2id])

  listener_params = {
    'HOST': os.getenv('AIXP_HOSTNAME'),
    'PORT': int(os.getenv('AIXP_PORT')),
    'USER': os.getenv('AIXP_USERNAME'),
    'PASS': os.getenv('AIXP_PASSWORD'),
    'TOPIC': 'lummetry/ctrl',
  }

  pipeline = sess.create_pipeline(
      e2id=e2id,
      name='test_dist_jobs',
      data_source='IotQueueListener',  # this DCT allows data acquisition from MQTT brokers
      config={
          'STREAM_CONFIG_METADATA': listener_params,
          "RECONNECTABLE": True,
      },
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
