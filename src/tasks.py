class Task:
  def __init__(self, task_key):
    self.task_key = task_key
    self.upstream = set()
  
  def __rshift__(self, other):
    if isinstance(other, Task):
      if not hasattr(self, 'upstream'):
        other.upstream = set()
      other.upstream.add(self.task_key)
    
    return other


class NotebookTask(Task):
  def __init__(self, task_key, path, source, libraries, run_if, job_cluster_key):
    super().__init__(task_key)
    self.task_type        = "notebook_task"

    self.path             = path
    self.source           = source
    self.libraries        = libraries
    self.run_if           = run_if
    self.job_cluster_key  = job_cluster_key


class JobTask(Task):
  def __init__(self, task_key, job_id, job_parameters):
    super().__init__(task_key)

    self.task_type        = "run_job_task"

    self.job_id           = job_id
    self.job_parameters   = job_parameters
