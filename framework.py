import requests
import time
from utils import mock_ssh, mock_rdp

class AviFramework:
    def __init__(self, config):
        self.config = config
        self.base_url = config['api']['base_url']
        self.username = config['api']['username']
        self.password = config['api']['password']
        self.target_name = config['test_settings']['target_vs_name']
        self.token = None
        self.target_uuid = None
        self.headers = {}

    def login(self):
        """Authenticates and sets the Bearer Token."""
        url = f"{self.base_url}/login"
        response = requests.post(url, auth=(self.username, self.password))
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            return True
        return False

    def stage_1_pre_fetcher(self):
        print("\n--- STAGE 1: PRE-FETCHER ---")
        # Fetching data to log counts
        for resource in ["tenant", "virtualservice", "serviceengine"]:
            res = requests.get(f"{self.base_url}/api/{resource}", headers=self.headers)
            if res.status_code == 200:
                print(f"Total {resource}s found: {len(res.json())}")
        mock_ssh() # Required mock call

    def stage_2_pre_validation(self):
        print("\n--- STAGE 2: PRE-VALIDATION ---")
        res = requests.get(f"{self.base_url}/api/virtualservice", headers=self.headers)
        if res.status_code == 200:
            vss = res.json()
            for vs in vss:
                if vs['name'] == self.target_name:
                    self.target_uuid = vs['uuid']
                    print(f"Target VS '{self.target_name}' found. Enabled status: {vs['enabled']}")
                    return vs['enabled'] == True
        return False

    def stage_3_task_trigger(self):
        print("\n--- STAGE 3: TASK / TRIGGER (Disabling VS) ---")
        if not self.target_uuid: return
        url = f"{self.base_url}/api/virtualservice/{self.target_uuid}"
        payload = {"enabled": False}
        res = requests.put(url, headers=self.headers, json=payload)
        if res.status_code == 200:
            print(f"Successfully sent PUT request to disable {self.target_name}")

    def stage_4_post_validation(self):
        print("\n--- STAGE 4: POST-VALIDATION ---")
        mock_rdp() # Required mock call
        url = f"{self.base_url}/api/virtualservice/{self.target_uuid}"
        res = requests.get(url, headers=self.headers)
        if res.status_code == 200 and res.json().get('enabled') == False:
            print("Verification Success: Virtual Service is now DISABLED.")
        else:
            print("Verification Failed: Virtual Service is still enabled.")

    def execute_workflow(self, thread_id):
        print(f"\n>>> Starting Test Workflow for {thread_id}")
        if self.login():
            self.stage_1_pre_fetcher()
            if self.stage_2_pre_validation():
                self.stage_3_task_trigger()
                time.sleep(1) # Wait for API to update
                self.stage_4_post_validation()
            else:
                print("Skipping Trigger: VS is already disabled or not found.")
        else:
            print("Login failed. Check credentials in config.yaml")
