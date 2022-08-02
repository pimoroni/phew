import machine, os, time, network, gc

def datetime_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d} {4:02d}:{5:02d}:{6:02d}".format(*dt)

_log_file = "log.txt"
def log_file(file):
  global _log_file
  _log_file = file

def log(level, text):
  datetime = datetime_string()
  log_entry = "{0} [{1:8} /{2:>8}] {3}".format(datetime, level, gc.mem_free(), text)
  print(log_entry)
  with open(_log_file, "a") as logfile:
    logfile.write(log_entry + '\n')

def info(*items):
  log("info", " ".join(map(str, items)))

def warn(*items):
  log("warning", " ".join(map(str, items)))
  
def error(*items):
  log("error", " ".join(map(str, items)))

def debug(*items):
  log("debug", " ".join(map(str, items)))