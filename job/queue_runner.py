import sqlite3
import subprocess
import time
from datetime import datetime

DB_PATH = '/app/job/job_queue.db'
POLL_INTERVAL = 5  # seconds between polling for new jobs

def get_next_job(conn):
    c = conn.cursor()
    c.execute("SELECT id, prompt FROM jobs WHERE status='queued' ORDER BY created_at LIMIT 1")
    return c.fetchone()

def mark_job_running(conn, job_id):
    c = conn.cursor()
    c.execute("UPDATE jobs SET status='running', started_at=? WHERE id=?",
              (datetime.now(), job_id))
    conn.commit()

def mark_job_completed(conn, job_id):
    c = conn.cursor()
    c.execute("UPDATE jobs SET status='completed', completed_at=? WHERE id=?",
              (datetime.now(), job_id))
    conn.commit()

def mark_job_failed(conn, job_id, error_message):
    c = conn.cursor()
    c.execute("UPDATE jobs SET status='failed', completed_at=?, error_message=? WHERE id=?",
              (datetime.now(), error_message, job_id))
    conn.commit()

def run_job(prompt):
    # Call run.py with the prompt as a CLI argument
    cmd = ['python3', 'run.py', prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def main():
    print("Worker started, polling for jobs...")
    while True:
        conn = sqlite3.connect(DB_PATH)
        job = get_next_job(conn)
        if job is None:
            conn.close()
            time.sleep(POLL_INTERVAL)
            continue

        job_id, prompt = job
        print(f"Processing job {job_id} with prompt: {prompt}")
        mark_job_running(conn, job_id)
        conn.close()

        try:
            result = run_job(prompt)
            if result.returncode == 0:
                conn = sqlite3.connect(DB_PATH)
                mark_job_completed(conn, job_id)
                conn.close()
                print(f"Job {job_id} completed successfully.")
            else:
                error_message = result.stderr.strip() if result.stderr else "Unknown error"
                conn = sqlite3.connect(DB_PATH)
                mark_job_failed(conn, job_id, error_message)
                conn.close()
                print(f"Job {job_id} failed. Error: {error_message}")
        except Exception as e:
            conn = sqlite3.connect(DB_PATH)
            mark_job_failed(conn, job_id, str(e))
            conn.close()
            print(f"Job {job_id} encountered an exception: {e}")

        # Short delay before next polling iteration
        time.sleep(1)

if __name__ == "__main__":
    main()
