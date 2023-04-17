# PyE2 SDK

This Python package enables low-code development and deployment of end-to-end AI cooperative application pipelines within the AiXpand Execution Engine processing nodes ecosystem. For further information please see "AiXpand - Decentralized ubiquitous computing MLOps execution engine".

## Installation

## Quick start "Hello world!"

Below is a simple "Hello world!" style application that creates a session by connecting to a known communication broker, listens for processing nodes heartbeats and displays the basic compute capabilities of the discovered nodes such as CPU & RAM.

### Importing and configuration

```python
from PyE2 import Session
```

### Preparing callbacks

```python
def on_hb(session, data):
  print(data['EE_ID'], " has a ", data['CPU'])
  return
```

### Running a simple main loop

```python
if __name__ == '__main__':
  sess = Session(
    host="hostname",
    port=88888,
    user="username",
    pwd="password",
    on_heartbeat=on_hb
  )
  sess.run(wait=10)
```

## Advanced quick-start with decentralized distributed jobs

For a more advanced quick-start we are going to create a execution pipeline on a target processing node that will request a specific number of workers in the network (including itself) to run a brute prime number search job.
The initiator job itself will create the request for the required number of discovered worker peers then will listen for results. Finally after a given configurable amount of time will close its own execution pipeline as well as each worker pipeline.

### Worker code

The worker will randomly generate numbers and will check if they are prime. If it finds a prime number, it sets the `_result`
variable.

```python
_result=None
skip = False
for _ in range(plugin.cfg_max_tries):
  # generate up to `max_tries` numbers in this call
  num = plugin.np.random.randint(1, 10_000)
  for n in range(2,int(num**0.5)+1):
    if num % n == 0:
      # the generated number is not a prime
      skip=True
      break
    # endif
  # endfor
  if not skip:
    _result=num
    break
  # endif
# endfor
```

### Initiator node code

The initiator will search for available workers in the network and will send them the custom job, then will collect data for a time,
after which will close the worker nodes and itself

```python
result=None
if plugin.int_cache['run_first_time'] == 0:
  # this is the first run, consider this the setup

  plugin.int_cache['run_first_time'] = 1

  worker_code = plugin.cfg_worker_code
  n_workers = plugin.cfg_n_workers
  # we use DeAPI `plugin.deapi_get_wokers` call to get the needed workers
  plugin.obj_cache['lst_workers'] = plugin.deapi_get_wokers(n_workers)
  plugin.obj_cache['dct_workers'] = {}
  plugin.obj_cache['dct_worker_progress'] = {}
  plugin.P(plugin.obj_cache['lst_workers'])

  # for each worker we symetrically launch the same job
  for worker in plugin.obj_cache['lst_workers']:
    plugin.obj_cache['dct_worker_progress'][worker] = []
    pipeline_name = plugin.cmdapi_start_simple_custom_pipeline(
      base64code=worker_code,
      dest=worker,
      instance_config={
        'MAX_TRIES': plugin.cfg_max_tries,
      }
    )
    plugin.obj_cache['dct_workers'][worker] = pipeline_name
  # endfor

  plugin.obj_cache["start_time"] = plugin.datetime.now()
  # endfor
elif (plugin.datetime.now() - plugin.obj_cache["start_time"]).seconds > plugin.cfg_max_run_time:
  # if the configured time has elapsed we stop all the worker pipelines
  # as well as stop this pipeline itself

  for ee_id, pipeline_name in plugin.obj_cache['dct_workers'].items():
    plugin.cmdapi_archive_pipeline(dest=ee_id, name=pipeline_name)
  # now archive own pipeline
  plugin.cmdapi_archive_pipeline()
  result = {
    'STATUS'  : 'DONE',
    'RESULTS' : plugin.obj_cache['dct_worker_progress']
  }
else:
  # here are the operations we are running periodically
  payload = plugin.dataapi_struct_data() # we use the DataAPI to get upstream data
  if payload is not None:

    ee_id = payload.get('EE_ID', payload.get('SB_ID'))
    pipeline_name = payload.get('STREAM_NAME')

    if (ee_id, pipeline_name) in plugin.obj_cache['dct_workers'].items():
      # now we extract result from the result key of the payload JSON
      # this also can be configured to another name
      num = payload.get('EXEC_RESULT', payload.get('EXEC_INFO'))
      if num is not None:
        plugin.obj_cache['dct_worker_progress'][ee_id].append(num)
        result = {
          'STATUS'  : 'IN_PROGRESS',
          'RESULTS' : plugin.obj_cache['dct_worker_progress']
        }
  # endif
# endif
```

### The local code

```python

from PyE2 import Session, code_to_base64

SERVER_CONFIG = {
    'host': "****************",
    'port': 8888,
    'user': "****************",
    'pwd': "****************"
}


def instance_on_data(pipeline, data):
  print(data)
  return


def pipeline_on_data(pipeline, signature, instance, data):
  pass

if __name__ == '__main__':

  WORKER_CODE_PATH = 'xperimental/dedist_example_worker.py'
  INITIATOR_CODE_PATH = 'xperimental/dedist_example_initiator.py'

  with open(WORKER_CODE_PATH, 'rt') as fh:
    worker_code = fh.read()

  e2id = 'e2id' # provide a known EE id
  sess = Session(**SERVER_CONFIG, silent=True)
  sess.connect()

  listener_params = {k.upper(): v for k, v in SERVER_CONFIG.items()}
  listener_params["PASS"] = listener_params["PWD"]
  listener_params["TOPIC"] = "lummetry/payloads"

  pipeline = sess.create_pipeline(
      e2id=e2id,
      name='test_dist_jobs',
      # data_source='Void',
      # config={},
      data_source='IotQueueListener', # this DCT allows data acquisition from MQTT brokers
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
        'MAX_TRIES': 10, # this will be used within plugin as `plugin.cfg_max_tries`
        'MAX_RUN_TIME': 60, # this will be used within plugin as `plugin.cfg_max_run_time`
        'N_WORKERS': 2, # this will be used within plugin as `plugin.cfg_n_workers`

        # this will be used within plugin as `plugin.cfg_worker_code`
        'WORKER_CODE': code_to_base64(worker_code)
        },
      on_data=instance_on_data,
      process_delay=0.2
  )

  sess.wait_until_sigint(close_session=True, close_pipelines=True)

```
