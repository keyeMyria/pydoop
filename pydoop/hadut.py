# BEGIN_COPYRIGHT
# END_COPYRIGHT

"""
The hadut module provides access to some Hadoop functionalities
available via the Hadoop shell.
"""

import os, subprocess, uuid
import pydoop.hadoop_utils as hu


HADOOP = hu.get_hadoop_exec()
GENERIC_ARGS = frozenset([
  "-conf", "-D", "-fs", "-jt", "-files", "-libjars", "-archives"
  ])


def _construct_property_args(prop_dict):
  return sum((['-D', '%s=%s' % p] for p in prop_dict.iteritems()), [])


# generic args must go before command-specific args
def _pop_generic_args(args):
  generic_args = []
  i = len(args) - 1
  while i >= 0:
    if args[i] in GENERIC_ARGS:
      try:
        args[i+1]
      except IndexError:
        raise ValueError("option %s has no value" % args[i])
      generic_args.extend(args[i:i+2])
      del args[i:i+2]
      i -= 2
    i -= 1
  return generic_args


def run_cmd(cmd, args=None, properties=None):
  """
  Run a Hadoop command.

  If the command succeeds, return its output; if it fails, raise a
  ``RuntimeError`` with its output as the message.

  .. code-block:: python

    >>> properties = {'dfs.block.size': 32*2**20}
    >>> args = ['-put', 'hadut.py', uuid.uuid4().hex]
    >>> res = run_cmd('fs', args, properties)
    >>> res
    ''
    >>> print run_cmd('dfsadmin', ['-help', 'report'])
    -report: Reports basic filesystem information and statistics.
    >>> try:
    ...     run_cmd('foo')
    ... except RuntimeError as e:
    ...     print e
    ... 
    Exception in thread "main" java.lang.NoClassDefFoundError: foo
    ...
  """
  _args = [HADOOP, cmd]
  if properties:
    _args.extend(_construct_property_args(properties))
  if args:
    if isinstance(args, basestring):
      args = args.split()
    gargs = _pop_generic_args(args)
    for seq in gargs, args:
      _args.extend(map(str, seq))
  p = subprocess.Popen(_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  output, _ = p.communicate()
  if p.returncode:
    raise RuntimeError(output)
  return output


def get_task_trackers(properties=None):
  """
  Get the list of task trackers in the Hadoop cluster.

  Each element in the returned list is in the ``(host, port)`` format.
  ``properties`` is passed to :func:`run_cmd`.
  """
  stdout = run_cmd("job", ["-list-active-trackers"], properties)
  task_trackers = []
  for l in stdout.splitlines():
    if not l:
      continue
    l = l.split(":")
    task_trackers.append((l[0].split("_")[1], int(l[-1])))
  return task_trackers


def get_num_nodes(properties=None):
  """
  Get the number of task trackers in the Hadoop cluster.

  ``properties`` is passed to :func:`get_task_trackers`.
  """
  return len(get_task_trackers(properties))


def dfs(args=None, properties=None):
  """
  Run Hadoop dfs/fs.

  ``args`` and ``properties`` are passed to :func:`run_cmd`.
  """
  return run_cmd("dfs", args, properties)


def path_exists(path, properties=None):
  """
  Return ``True`` if ``path`` exists in the default HDFS, else ``False``.

  ``properties`` is passed to :func:`dfs`.

  This function does the same thing as :func:`hdfs.path.exists
  <pydoop.hdfs.path.exists>`, but it uses a wrapper for the Hadoop
  shell rather than the hdfs extension.
  """
  try:
    dfs(["-stat", path], properties)
  except RuntimeError:
    return False
  return True


def run_jar(jar_name, more_args=None, properties=None):
  """
  Run a jar on Hadoop (``hadoop jar`` command).
  
  ``more_args`` (after prepending ``jar_name``) and ``properties`` are
  passed to :func:`run_cmd`.

  .. code-block:: python

    >>> import pydoop
    >>> hadoop_home = pydoop.hadoop_home()
    >>> hadoop_ver = ".".join(map(str, hu.get_hadoop_version()))
    >>> jar_name = '%s/hadoop-%s-examples.jar' % (hadoop_home, hadoop_ver)    
    >>> more_args = ['wordcount']
    >>> try:
    ...     run_jar(jar_name, more_args=more_args)
    ... except RuntimeError as e:
    ...     print e
    ... 
    Usage: wordcount <in> <out>
  """
  if hu.is_readable(jar_name):
    args = [jar_name]
    if more_args is not None:
      args.extend(more_args)
    return run_cmd("jar", args, properties)
  else:
    raise ValueError("Can't read jar file %s" % jar_name)


def run_class(class_name, args=None, properties=None, classpath=None):
  """
  Run a class that needs the Hadoop jars in its class path.

  ``args`` and ``properties`` are passed to :func:`run_cmd`.

  .. code-block:: python

    >>> cls = 'org.apache.hadoop.hdfs.tools.DFSAdmin'
    >>> print run_class(cls, args=['-help', 'report'])
    -report: Reports basic filesystem information and statistics.
  """
  old_classpath = None
  if classpath:
    old_classpath = os.getenv('HADOOP_CLASSPATH', '')
    if isinstance(classpath, basestring):
      classpath = [classpath]
    for i, s in enumerate(classpath):
      classpath[i] = [cp.strip() for cp in s.split(":")]
    os.environ['HADOOP_CLASSPATH'] = ":".join(classpath)
  res = run_cmd(class_name, args, properties)
  if old_classpath is not None:
    os.environ['HADOOP_CLASSPATH'] = old_classpath
  return res


def run_pipes(executable, input_path, output_path, more_args=None,
              properties=None):
  """
  Run a pipes command.

  ``more_args`` (after setting input/output path) and ``properties``
  are passed to :func:`run_cmd`.
  """
  if path_exists(executable):
    hdfs_executable = executable
  elif os.path.isfile(executable):
    hdfs_executable = uuid.uuid4().hex
    dfs(["-put", executable, hdfs_executable], properties)
  else:
    raise ValueError("%s not found" % executable)
  args = ["-input", input_path, "-output", output_path]
  if more_args is not None:
    args.extend(more_args)
  properties = properties.copy() if properties is not None else {}
  properties['hadoop.pipes.executable'] = hdfs_executable
  return run_cmd("pipes", args, properties)


def find_jar(jar_name, root_path=None):
  """
  Look for the named jar in:

  #. ``root_path``, if specified
  #. working directory -- ``PWD``
  #. ``${PWD}/build``
  #. ``/usr/share/java``

  Return the full path of the jar if found; else return ``None``.
  """
  jar_name = os.path.basename(jar_name)
  root = root_path or os.getcwd()
  paths = (root, os.path.join(root, "build"), "/usr/share/java")
  for p in paths:
    p = os.path.join(p, jar_name)
    if os.path.exists(p):
      return p
  return None


if __name__ == "__main__":
  import doctest
  FLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
  doctest.testmod(optionflags=FLAGS)
