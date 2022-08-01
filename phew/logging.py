import machine, os, time, network

def datetime_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d} {4:02d}:{5:02d}:{6:02d}".format(*dt)

def log(level, text):
  datetime = datetime_string()
  log_entry = "{0} [{1:8}] {2}".format(datetime, level, text)
  print(log_entry)
  with open("log.txt", "a") as logfile:
    logfile.write(log_entry + '\n')

def info(*items):
  log("info", " ".join(map(str, items)))

def warn(*items):
  log("warning", " ".join(map(str, items)))
  
def error(*items):
  log("error", " ".join(map(str, items)))

def debug(*items):
  log("debug", " ".join(map(str, items)))