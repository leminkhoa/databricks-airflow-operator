import getpass
import argparse

from src.loader import load_config
from src.databricks_api import DatabricksCreateJobsApi, cfg_to_body


if __name__ == "__main__":

    # Load argument
    parser = argparse.ArgumentParser(description="Databricks workflows deployment")
    parser.add_argument('--file', type=str, help='a filename.yaml inside deployment folder')

    # Parse the arguments
    args = parser.parse_args()

    # Load deployment config
    cfg = load_config(args.file)
    body = cfg_to_body(cfg)


    # Hostname and token
    hostname    = getpass.getpass("Please provide Databricks hostname (Ex: https://adb-<some address>.azuredatabricks.net )  to deploy: ")
    token       = getpass.getpass("Please provide token used to call API:")
    
    # Send API
    api = DatabricksCreateJobsApi(hostname=hostname ,token=token)


    # Send api
    response = api.run_job(body=body)

    if response.status_code == 200:
        print(f""" Workflow has been deployed with following properties:
            Workspace url: {api.hostname}
            Workflow name: {body.get("name")}
        """)
