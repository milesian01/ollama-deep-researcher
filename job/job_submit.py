import sqlite3
import sys

def submit_new_job(prompt):
    """Submit a new job to the queue"""
    try:
        conn = sqlite3.connect('job_queue.db')
        c = conn.cursor()
        c.execute("INSERT INTO jobs (prompt, status) VALUES (?, 'queued')", (prompt,))
        conn.commit()
        job_id = c.lastrowid
        conn.close()
        return job_id
    except Exception as e:
        print(f"Error submitting job: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 job_submit.py \"Your job prompt here\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    job_id = submit_new_job(prompt)
    if job_id:
        print(f"Job added with ID {job_id} and prompt: {prompt}")
