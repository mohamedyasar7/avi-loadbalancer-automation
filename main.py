import threading
from utils import load_config
from framework import AviFramework

def main():
    config = load_config()
    if not config:
        return

    # We run 2 test cases in parallel using Threading
    threads = []
    num_tests = config['test_settings']['parallel_instances']

    print(f"=== Starting Automation Framework (Parallelism: {num_tests}) ===")

    for i in range(num_tests):
        runner = AviFramework(config)
        t = threading.Thread(target=runner.execute_workflow, args=(f"Thread-{i+1}",))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n=== ALL TEST CASES FINISHED ===")

if __name__ == "__main__":
    main()
