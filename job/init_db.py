import sqlite3

DB_PATH = 'job_queue.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create a table "jobs" with:
# - id: primary key
# - prompt: text prompt for the job
# - status: job status (queued, running, completed, failed)
# - created_at: timestamp when job was added
# - started_at: timestamp when job started processing
# - completed_at: timestamp when job finished processing
# - error_message: error message if the job failed
c.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
)
''')

conn.commit()
conn.close()

print("Database initialized successfully.")
