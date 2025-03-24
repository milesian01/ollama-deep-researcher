import sys
import sqlite3

def main():
    """Main function to submit a new job"""
    if len(sys.argv) < 2:
        print("Usage: python3 job_submit.py \"Your job prompt here\"")
        sys.exit(1)
    
    prompt = sys.argv[1]
    
    conn = sqlite3.connect('/app/job/job_queue.db')
        job_id = db_handler.submit_job(prompt)
        
    if job_id:
        print(f"Job added with ID {job_id} and prompt: {prompt}")
    else:
        print("Failed to submit job")

if __name__ == "__main__":
    main()
