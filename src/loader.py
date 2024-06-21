import re

from .utils import *
from .tasks import *


def load_config(file_name, folder_name = "deployment"):

  # Load yaml config
  cfg = yaml_read(
    root        = folder_name,
    filename    = file_name
  )  

  #Task handler
  _cfg = dict()

  for task in cfg['tasks']:
    # ********************** NOTE: NOTEBOOK_TASK ***********************
    if task['type'] == 'notebook_task':
      task_key = task['task_key']
      _cfg[task_key] = NotebookTask(
          task_key        = task['task_key'],
          path            = os.path.join(cfg['base_directory'], task['notebook_task']['notebook_path']),
          source          = task['notebook_task']['source'],
          libraries       = cfg.get("libraries", []),
          run_if          = task.get("run_if", "ALL_SUCCESS"),
          job_cluster_key = task['job_cluster_key']
      )

    # ********************** NOTE: JOB_TASK ***********************
    elif task['type'] == 'run_job_task':
      task_key = task['task_key']
      _cfg[task_key] = JobTask(
          task_key        = task['task_key'],
          job_id          = task['run_job_task']['job_id'],
          job_parameters  = task['run_job_task'].get("job_parameters", [])
      )

  #Load lineage
  _cfg = lineage_reader(_cfg, cfg['lineage'])  # Assuming lineage_reader is a defined function

  # Merge it back to cfg
  cfg['tasks'] = []

  for _, task in _cfg.items():
    cfg['tasks'].append(task.__dict__)

  return cfg


def lineage_reader(_cfg, lineages: list):
  for lineage in lineages:
    
    def _node_cleaning(node):
      return re.split(",\s+", node.strip().replace("[", "").replace("]", ""))

    nodes = [_node_cleaning(node) for node in lineage.split(">>")]

    if nodes:
      # First node
      current_node = nodes[0]
      current_node = [_cfg[child_node] for child_node in current_node]

    # Iterates
    for node in nodes[1:]:
      next_node = [_cfg[child_node] for child_node in node]

      for current_child_node in current_node:
        for next_child_node in next_node:
          current_child_node >> next_child_node

      # Move on
      current_node = next_node
  return _cfg
