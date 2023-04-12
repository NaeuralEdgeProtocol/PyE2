from threading import Thread
from time import sleep


class Runner():
  def __init__(self):
    self.done = False
    self.id = '#'
    return
  
  def worker(self):
    while not self.done:
      sleep(1)
      print(self.id)
    return
  
  def run(self):
    self.thr = Thread(target=self.worker, daemon=True)
    self.thr.start()
    return
    
if __name__ == '__main__':
  eng = Runner()
  
  eng.run()
  
  sleep(5)
  
  print("Post run")


  
