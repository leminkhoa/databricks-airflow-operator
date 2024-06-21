import requests


class DatabricksCreateJobsApi:
    """API to create Databricks Jobs"""
    def __init__(self, hostname, token):
        # Pick relevant workspace
        self.hostname = hostname
        self.token = token
        self.endpoint = "api/2.1/jobs/create"

        self.header = {
            f"Authorization": "Bearer {token}".format(token=self.token)
        }

    def run_job(self, body):
        try:
            response = requests.post(
                url = self.hostname + "/" + self.endpoint,
                headers = self.header,
                json = body
            )
        except Exception as err:
            print(err)
            raise err

        if response.status_code == 200:
            print("Status code: 200 -> Successfully send request!")
            print("Response:\n", response.content)
        else:
            print(f"Status code: {response.status_code}")
            print("Response:\n", response.content)

        return response


def tasks_body_mapping(task_cfg):
    """
    Transform current task config to fit with supported databricks api for `tasks`
    """
    
    def _transform_depends_on(task):
        depends_on = []

        for upstream in list(task["upstream"]):
            # Check the type of task upstream
            depends_on.append({
                "task_key": upstream
            })
        return depends_on

    # Initialize empty task configuration
    updated_task_cfg = []

    for task in task_cfg:
        # ********************** NOTE: NOTEBOOK_TASK ***********************
        if task['task_type'] == "notebook_task":
            task_key        = task['task_key']
            run_if          = task.get("run_if", "ALL_SUCCESS")
            libraries       = task.get("libraries", [])
            notebook_task   = dict(
                notebook_path   = task["path"],
                source          = task["source"]
            )
            job_cluster_key = task["job_cluster_key"]


            # Add elements to depends_on list, based on task upstream
            depends_on = _transform_depends_on(task)


            updated_task_cfg.append({
                "task_key": task_key,
                "run_if": run_if,
                "notebook_task": notebook_task,
                "libraries": libraries,
                "job_cluster_key": job_cluster_key,
                "depends_on": depends_on
            })

        # ********************** NOTE: RUN_JOB_TASK ***********************
        elif task['task_type'] == "run_job_task":

            task_key         = task['task_key']
            run_if           = task.get("run_if", "ALL_SUCCESS")

            run_job_task = {
                "job_id": task["job_id"],
                "job_parameters": task["job_parameters"]
            }

            # Add elements to depends_on list, based on task upstream
            depends_on = _transform_depends_on(task)

            updated_task_cfg.append({
                "task_key": task_key,
                "run_if": run_if,
                "run_job_task": run_job_task,
                "depends_on": depends_on
            })

    return updated_task_cfg  # Returning the updated configuration



def cfg_to_body(cfg: dict):
  """
  Convert current config to body that matches with supported Databricks API
  Reference: https://docs.databricks.com/api/workspace/jobs/create

  Args:
      cfg (dict): The configuration dictionary

  Returns:
      dict: The converted body dictionary
  """

  # Standard config
  standard_cfg = {
      "name":                   cfg.get("name"),
      "description":            cfg.get("description",          ""),
      "email_notifications":    cfg.get("email_notifications",  {}),
      "parameters":             cfg.get("parameters",           []),
      "run_as":                 cfg.get("run_as",               {}),
      "tasks":                  tasks_body_mapping(cfg["tasks"]),
      "job_clusters":           cfg.get("job_clusters",         {}),
      "tags":                   cfg.get("tags",                 {}),
  }

  # Optional config
  optional_cfg = {}

  if cfg.get("schedule"):
      optional_cfg["schedule"] = cfg.get("schedule")

  if cfg.get("access_control_list"):
      optional_cfg["access_control_list"] = cfg.get("access_control_list")

  return {**standard_cfg, **optional_cfg}
