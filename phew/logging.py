import machine, os, time, network, gc

def datetime_string():
  dt = machine.RTC().datetime()
  return "{0:04d}-{1:02d}-{2:02d} {4:02d}:{5:02d}:{6:02d}".format(*dt)

_log_file = "log.txt"
def log_file(file):
  global _log_file
  _log_file = file

# truncates the log file down to a target size while maintaining
# clean line breaks
def truncate(target):
  # get the current size of the log file
  size = 0
  try:
    size = os.stat(_log_file)[6]
  except OSError:
    return
  # calculate how many bytes we're aiming to discard
  discard = size - target

  if discard <= 0:
    return

  with open(_log_file, "rb") as infile:
    # skip a bunch of the input file until we've discarded
    # at least enough
    while discard > 0:
      chunk = infile.read(1024)
      discard -= len(chunk)

    with open(_log_file + ".tmp", "wb") as outfile:
      # we have a partial chunk to write, try to find a line
      # break nearby to split it on
      break_position = chunk.find(b"\n", -discard)
      if break_position == -1:
        break_position = chunk.rfind(b"\n", -discard)
      if break_position == -1:
        break_position = 0
      outfile.write(chunk[break_position + 1:])

      # now copy the rest of the file
      while True:
        chunk = infile.read(1024)
        if not chunk:
          break
        outfile.write(chunk)

  # delete the old file and replace with the new
  os.remove(_log_file)
  os.rename(_log_file + ".tmp", _log_file)


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
