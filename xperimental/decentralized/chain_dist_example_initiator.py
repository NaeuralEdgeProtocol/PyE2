result = None
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

  for node_id, pipeline_name in plugin.obj_cache['dct_workers'].items():
    plugin.cmdapi_archive_pipeline(dest=node_id, name=pipeline_name)
  # now archive own pipeline
  plugin.cmdapi_archive_pipeline()
  result = {
    'STATUS': 'DONE',
    'RESULTS': plugin.obj_cache['dct_worker_progress']
  }
else:
  # here are the operations we are running periodically
  payload = plugin.dataapi_struct_data()  # we use the DataAPI to get upstream data
  if payload is not None:

    node_id = payload.get('EE_ID', payload.get('SB_ID'))
    pipeline_name = payload.get('STREAM_NAME')

    if (node_id, pipeline_name) in plugin.obj_cache['dct_workers'].items():
      # now we extract result from the result key of the payload JSON
      # this also can be configured to another name
      num = payload.get('EXEC_RESULT', payload.get('EXEC_INFO'))
      if num is not None:
        plugin.obj_cache['dct_worker_progress'][node_id].append(num)
        result = {
          'STATUS': 'IN_PROGRESS',
          'RESULTS': plugin.obj_cache['dct_worker_progress']
        }
  # endif
# endif
