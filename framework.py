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
        try:
            response = requests.post(url, auth=(self.username, self.password), timeout=10)
            if response.status_code == 200:
                self.token = response.json().get("token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                return True
        except Exception as e:
            print(f"Login Error: {e}")
        return False

    def stage_1_pre_fetcher(self):
        print("\n--- STAGE 1: PRE-FETCHER ---")
        for resource in ["tenant", "virtualservice", "serviceengine"]:
            res = requests.get(f"{self.base_url}/api/{resource}", headers=self.headers)
            if res.status_code == 200:
                data = res.json()
                # Handle if data is a list or a dict
                count = len(data) if isinstance(data, list) else len(data.get('results', []))
                print(f"Total {resource}s found: {count}")
        mock_ssh()

    def stage_2_pre_validation(self):
        print("\n--- STAGE 2: PRE-VALIDATION ---")
        res = requests.get(f"{self.base_url}/api/virtualservice", headers=self.headers)
        if res.status_code == 200:
            vss = res.json()
            
            # FIX: If API returns a dictionary, get the list from 'results'
            if isinstance(vss, dict):
                vss = vss.get('results', [])
            
            for vs in vss:
                # Extra check to ensure 'vs' is a dictionary
                if isinstance(vs, dict) and vs.get('name') == self.target_name:
                    self.target_uuid = vs.get('uuid')
                    print(f"Target VS '{self.target_name}' found. Enabled: {vs.get('enabled')}")
                    return vs.get('enabled') == True
        print(f"Target VS '{self.target_name}' not found or already disabled.")
        return False

    def stage_3_task_trigger(self):
        print("\n--- STAGE 3: TASK / TRIGGER (Disabling VS) ---")
        if not self.target_uuid: return
        url = f"{self.base_url}/api/virtualservice/{self.target_uuid}"
        payload = {"enabled": False}
        res = requests.put(url, headers=self.headers, json=payload)
        if res.status_code == 200:
            print(f"Successfully disabled {self.target_name}")

    def stage_4_post_validation(self):
        print("\n--- STAGE 4: POST-VALIDATION ---")
        mock_rdp()
        url = f"{self.base_url}/api/virtualservice/{self.target_uuid}"
        res = requests.get(url, headers=self.headers)
        if res.status_code == 200:
            status = res.json().get('enabled')
            if status is False:
                print("Verification Success: Virtual Service is now DISABLED.")
            else:
                print(f"Verification Failed: Status is {status}")

    def execute_workflow(self, thread_id):
        print(f"\n>>> Starting Test Workflow for {thread_id}")
        if self.login():
            self.stage_1_pre_fetcher()
            if self.stage_2_pre_validation():
                self.stage_3_task_trigger()
                time.sleep(1) 
                self.stage_4_post_validation()
        print(f"\n<<< Finished Test Workflow for {thread_id}")
