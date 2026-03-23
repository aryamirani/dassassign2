import os
import subprocess
import random
from datetime import datetime, timedelta

# Configuration
COMMITS_FILE = "commits.txt"
START_TIME = datetime(2026, 3, 23, 10, 0, 0) # March 23, 2026, 10:00 AM

def run_command(cmd, env=None):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f"Error running: {cmd}")
        print(stderr.decode())
    return stdout.decode()

def main():
    if not os.path.exists(COMMITS_FILE):
        print(f"Error: {COMMITS_FILE} not found.")
        return

    with open(COMMITS_FILE, "r") as f:
        lines = f.readlines()

    current_time = START_TIME
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        commit_hash, commit_msg = line.split("|", 1)
        
        # Stagger time by 15-30 mins
        interval = random.randint(15, 30)
        current_time += timedelta(minutes=interval)
        
        # Format date for Git
        git_date = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Replaying: {commit_msg} at {git_date}")
        
        # 1. Checkout file contents from original commit
        run_command(f"git checkout {commit_hash} -- .")
        
        # 2. Stage changes
        run_command("git add .")
        
        # 3. Commit with forged date (SYNC AUTHOR and COMMITTER)
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = git_date
        env["GIT_COMMITTER_DATE"] = git_date
        
        # Use a temporary file for the commit message
        with open("temp_msg.txt", "w") as msg_f:
            msg_f.write(commit_msg)
            
        run_command("git commit -F temp_msg.txt", env=env)
        
        if os.path.exists("temp_msg.txt"):
            os.remove("temp_msg.txt")

    print("\nSuccessfully replayed all commits with synchronized dates.")

if __name__ == "__main__":
    main()
