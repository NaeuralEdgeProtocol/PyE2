_result=None
skip = False
for _ in range(plugin.cfg_max_tries):
  num = plugin.np.random.randint(1, 10_000)
  for n in range(2,int(num**0.5)+1):
    if num % n == 0:
      skip=True
      break
    # endif
  # endfor
  if not skip:
    _result=num
    break
  # endif
# endfor