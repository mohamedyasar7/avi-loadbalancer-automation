# Avi Load Balancer Automation Framework

## How to Run
1. Ensure Python is installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Update `config.yaml` with our credentials.
4. Run the framework: `python main.py`

## Project Logic
The framework uses a 4-stage workflow (Pre-fetch, Pre-validate, Task, Post-validate) 
to disable a Virtual Service. It uses Python's `threading` module to execute 
tasks in parallel and reads configuration from YAML.