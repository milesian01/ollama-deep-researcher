import os
import sys
import sqlite3

def main():
    """Main function to submit a new job"""
    if len(sys.argv) < 2:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            print("Usage: python3 job_submit.py \"Your job prompt here\" or provide a file path")
            sys.exit(1)
    else:
        arg = sys.argv[1]
        # If the argument is a file, read its contents; otherwise, treat it as the prompt.
        if os.path.exists(arg) and os.path.isfile(arg):
            with open(arg, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()
        else:
            prompt = arg
    
    conn = sqlite3.connect('/app/job/job_queue.db')
    c = conn.cursor()
    c.execute("INSERT INTO jobs (prompt, status) VALUES (?, 'queued')", (prompt,))
    conn.commit()
    job_id = c.lastrowid
    conn.close()
        
    if job_id:
        print(f"Job added with ID {job_id} and prompt: {prompt}")
    else:
        print("Failed to submit job")

if __name__ == "__main__":
    main()
