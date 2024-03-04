# PyE2 SDK

This is the Python SDK package that allows interactions, development and deployment of jobs in AiXpand network. The SDK enables low-code development and deployment of end-to-end AI (and not only) cooperative application pipelines within the AiXpand Execution Engine processing nodes ecosystem. For further information please see "AiXpand - Decentralized ubiquitous computing MLOps execution engine".

## Dependencies

This packet depends on the following packets: [`pika`, `paho-mqtt`, `numpy`, `cryptography`].

## Installation

```shell
python -m pip install PyE2
```

## Documentation

Minimal documentation will be presented here. The complete documentation is
Work in Progress.

Code examples are located in the `xperimental` folder in the project's repository.

## Quick start guides

Here you will find a selection of guides and documentation snippets to get
you started with the `PyE2` SDK. These are only the most important aspects,
selected from the documentation and from the code examples. For more
in-depth information, please consult the examples from the repository
and the documentation.

### Naming conventions & FAQs

The following are the same:

- `Pipeline == Stream` (The latter was used internally by the Hyperfy team, but now it is considered legacy)
- `Signature == Plugin's name`
- `Plugin ~ Instance` (Only in the context of talking about a running plugin (instance); people tend to omit the word `instance`)
- `Node == Worker` (The latter was used internally by the Hyperfy team. Unless it is in the context of a distributed job, the 2 words refer to the same thing)

### "Hello world!"

Below is a simple "Hello world!" style application that creates a session by connecting to a known communication broker, listens for processing nodes heartbeats and displays the basic compute capabilities of the discovered nodes such as CPU & RAM.

#### Importing and configuration

```python
from PyE2 import Session
```

#### Preparing callbacks

```python
def on_hb(session : Session, e2id : str, data : dict):
  print(e2id, " has a ", data['CPU'])
  return
```

#### Running a simple main loop

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

### Advanced quick-start with decentralized distributed jobs

For a more advanced quick-start we are going to create a execution pipeline on a target processing node that will request a specific number of workers in the network (including itself) to run a brute prime number search job.
The initiator job itself will create the request for the required number of discovered worker peers then will listen for results. Finally after a given configurable amount of time will close its own execution pipeline as well as each worker pipeline.

<details>
  <summary>Expand this tutorial</summary>

#### Worker code

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

#### Initiator node code

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

#### The local code

```python

from PyE2 import Session, Pipeline, code_to_base64

SERVER_CONFIG = {
    'host': "****************",
    'port': 8888,
    'user': "****************",
    'pwd': "****************"
}


def instance_on_data(pipeline : Pipeline, custom_code_result: dict, data: dict):
  """
  in `custom_code_result` we have the output of our custom code
  in `data` we have the entire payload
  """
  pipeline.P(custom_code_result)
  return


if __name__ == '__main__':

  WORKER_CODE_PATH = 'chain_dist_example_worker.py'
  INITIATOR_CODE_PATH = 'chain_dist_example_initiator.py'

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
      data_source='IotQueueListener', # this DCT allows data acquisition from MQTT brokers
      config={
          'STREAM_CONFIG_METADATA': listener_params,
          "RECONNECTABLE": True,
      },
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

  sess.run(wait=True, close_session=True, close_pipelines=True)

```

</details>

### Real-time person tracking in a video file

In this tutorial we will focus on creating a pipeline that consumes data
from a video file and starts a plugin that draws bounding boxes on all
the persons that are visible, and returns the images back to us.

<details>
  <summary>Expand this tutorial</summary>

#### Pre-requisites

For this application, we need to install the PIL (`pillow`) library to use some advanced functionalities involving image manipulation.

```shell
python -m pip install pillow
```

#### Importing and configuration

```python
from PyE2 import Session, Pipeline, Payload
```

Here we will use the `Payload` class, which is an extension of the
`dict` class in Python. What this means is that the `Payload` object can be
thought of as a `dict` object with some extra functionality.

One of such functionality is the method `get_image_as_PIL(key='IMG')`, which
searches in the dictionary for a given key (the default key being 'IMG'), extracts
the image stored at that key, and converts it from base64 to a PIL format.

#### Preparing callbacks

```python
val = 0

def on_instance_data(pipeline : Pipeline, payload: Payload):
  global val
  image = payload.get_image_as_PIL()
  if image is not None:
    # if we received an image, save it with at `./img_#.jpeg`
    image.save("img_{}.jpeg".format(val))
    val += 1
```

Here we can observe that unlike in the previous examples, the data/payload received is now
typed as `Payload`, and not as `dict`. This will allow us to use the functionalities
introduced by the `Payload` class, which greatly reduce the amount of code required to parse
the messages.

#### Running a the main loop

```python
if __name__ == '__main__':
  sess = Session(
    host="hostname",
    port=88888,
    user="username",
    pwd="password",
    on_heartbeat=on_hb
  )

  # Notice that we call `sess.connect()` before `sess.run()`. That is because in order
  # to create pipelines and to start plugin instances, we need to be connected to the session
  sess.connect()

  # Create a pipeline that will acquire data from a Video File located at the given URL
  # The URL can be a path to a local file or a link to a downloadable file
  pipeline = sess.create_pipeline(
    e2id="e2id",
    name="RealTimePersonTracking",
    data_source="VideoFile",
    config={
      "URL": "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    },
  )

  # Create an object_tracking plugin instance that will track only the persons in the video
  instance = pipeline.start_plugin_instance(
    signature="OBJECT_TRACKING_01",
    instance_id="EXAMPLE_OBJECT_TRACKING",
    params={
      "OBJECT_TYPE": ["person"]
    },
    on_data=instance_on_data,
  )

  sess.run(wait=60)
```

</details>

## Change log

### v0.4.5

- Feature(heartbeats): support compressed heartbeat
- Feature(Session): add optional callback for `on_payload` in Session

### v0.4.1

- Documentation(README): updated this README with examples
- Refactor(examples): updated all examples to match changes from `v0.3.6`

### v0.4.0

- Feature(Payload): created class `Payload` that extends `dict`;
  this class exposes useful methods when interacting with messages from nodes
- Documentation(examples): added an example of saving images generated by a plugin

### v0.3.8

- Hotfix(session): get_active_nodes was returning an empty list
- Hotfix(session): attach_to_pipeline now waits for a heartbeat,
  as it needs to know the configuration of the payload

### v0.3.6

- Feat(session): added `filter_workers` to Session, process only messages from specific workers
- Feat(session): track online nodes and keep a list of them;
  consider a node offline if it did not send any message for more than 60 seconds

BREAKING CHANGE:

- Refactor(on_heartbeat): added `e2id` as parameter, now the signature of the method looks like this

  ```python
  on_heartbeat(sess: Session, e2id: str, heartbeat: dict)
  ```

### v0.3.5

- Hotfix(session): changed self.e2id to e2id

### v0.3.4

- Added docstrings
- Included examples with credentials from environment variables

### v0.3.2

- Added base files
