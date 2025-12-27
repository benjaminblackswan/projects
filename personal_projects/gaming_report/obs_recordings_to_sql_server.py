import pyodbc
import cv2
from pathlib import Path
import re
from datetime import datetime

# --- SQL Server connection (on-prem) using Windows Authentication ---
server = 'localhost'
database = 'Ben'
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
)
cursor = conn.cursor()

# --- Define source folder, schema, and table ---
video_folder_path = Path(r"D:\2025")   # Updated folder path
schema_name = "gaming"        # Change if needed
table_name = "daily"         # Change if needed

# --- Ensure schema exists ---
cursor.execute(f"""
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{schema_name}')
    EXEC('CREATE SCHEMA {schema_name}')
""")
conn.commit()

# --- Ensure table exists (create if not exists) ---
cursor.execute(f"""
IF OBJECT_ID(N'{schema_name}.{table_name}', N'U') IS NULL
BEGIN
    CREATE TABLE {schema_name}.{table_name} (
        PlayDate DATE,
        PlayTime TIME(0),
        PlayID VARCHAR(5),
        DurationSecond INT
    )
END
""")
conn.commit()

# --- Gather video files ---
video_files = sorted([f for f in video_folder_path.rglob("*")
                      if f.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv']])

# --- Counters ---
inserted_count = 0
skipped_count = 0

for video in video_files:
    cap = cv2.VideoCapture(str(video))
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration_seconds = int(round(frame_count / fps)) if fps else 0

        # --- Extract date and time from filename ---
        date_time_match = re.search(r'(\d{4}-\d{2}-\d{2})[_-](\d{2}[\.:]\d{2}[\.:]\d{2})', video.stem)
        if date_time_match:
            date_part, time_part = date_time_match.groups()
            time_part = time_part.replace(".", ":")
            datetime_str = f"{date_part} {time_part}"
            dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.now()

        play_date = dt.date()
        play_time = dt.time()

        # --- PlayID from first 5 characters of parent folder ---
        play_id = video.parent.name[:5]

        # --- Insert if not exists (based on PlayDate + PlayTime) ---
        cursor.execute(f"""
        INSERT INTO {schema_name}.{table_name} (PlayDate, PlayTime, PlayID, DurationSecond)
        SELECT ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM {schema_name}.{table_name}
            WHERE PlayDate = ? AND PlayTime = ?
        )
        """, play_date, play_time, play_id, duration_seconds, play_date, play_time)

        if cursor.rowcount == 0:
            skipped_count += 1
            print(f"Skipped duplicate {play_id}/{video.name}")
        else:
            inserted_count += 1
            print(f"Inserted {play_id}/{video.name} -> {duration_seconds} sec")

    finally:
        cap.release()

# --- Commit and close ---
conn.commit()
cursor.close()
conn.close()

print(f"✅ Processing complete: {inserted_count} rows inserted, {skipped_count} rows skipped.")
