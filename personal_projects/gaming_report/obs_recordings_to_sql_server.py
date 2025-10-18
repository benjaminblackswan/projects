# duration is now in seconds
# datestr is now dateandtime in datetime data type

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

# --- Ensure schema exists ---
cursor.execute("""
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'gaming')
    EXEC('CREATE SCHEMA gaming')
""")
conn.commit()

# --- Ensure table exists ---
cursor.execute("""
IF OBJECT_ID(N'gaming.daily', N'U') IS NULL
BEGIN
    CREATE TABLE gaming.daily (
        dateandtime DATETIME,
        PlayID VARCHAR(5),
        Duration TINYINT
    )
END
""")
conn.commit()

# --- Video folder path ---
video_folder_path = Path(r"D:")

video_files = sorted([f for f in video_folder_path.rglob("*")
                      if f.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv']])

# Counters for logging
inserted_count = 0
skipped_count = 0

for video in video_files:
    cap = cv2.VideoCapture(str(video))
    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration_seconds = round(frame_count / fps, 3) if fps else 0

        # Extract date and time from filename (format: YYYY-MM-DD_HH.MM.SS GM)
        date_time_match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}\.\d{2}\.\d{2})', video.stem)
        if date_time_match:
            date_part, time_part = date_time_match.groups()
            time_part = time_part.replace(".", ":")
            datetime_str = f"{date_part} {time_part}"
            dateandtime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        else:
            # fallback if pattern not found
            dateandtime = datetime.now()

        # Use first 5 characters of parent folder as PlayID
        play_id = video.parent.name[:5]

        # Insert if not exists
        cursor.execute("""
        INSERT INTO gaming.daily (dateandtime, PlayID, Duration)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM gaming.daily
            WHERE dateandtime = ? AND PlayID = ? AND Duration = ?
        )
        """, dateandtime, play_id, duration_seconds, dateandtime, play_id, duration_seconds)

        if cursor.rowcount == 0:
            skipped_count += 1
            print(f"Skipped duplicate {play_id}/{video.name}")
        else:
            inserted_count += 1
            print(f"Inserted {play_id}/{video.name} -> {duration_seconds} sec")

    finally:
        cap.release()

conn.commit()
cursor.close()
conn.close()

print(f"✅ Processing complete: {inserted_count} rows inserted, {skipped_count} rows skipped.")
