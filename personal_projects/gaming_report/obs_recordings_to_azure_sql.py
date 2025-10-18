import pyodbc
import cv2
from pathlib import Path
import re

# --- Azure SQL connection ---
server = 'myfirstserverben.database.windows.net'
database = 'Free_Tier_01'
username = 'benjamin_blackswan'
password = ''
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
cursor = conn.cursor()

# --- Ensure table exists ---
cursor.execute("""
IF OBJECT_ID(N'dbo.Playthrough', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Playthrough (
        DateStr NVARCHAR(20),
        PlayID NVARCHAR(5),  -- Only first 5 chars
        Duration DECIMAL(10,3)
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
        duration_minutes = round(frame_count / fps / 60, 3) if fps else 0

        # Extract date and folder/play ID
        date_str = re.split(r'[_ ]', video.stem)[0]
        play_id = video.parent.name[:5]  # Only first 5 characters

        # Insert if not exists
        cursor.execute("""
        INSERT INTO dbo.Playthrough (DateStr, PlayID, Duration)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.Playthrough
            WHERE DateStr = ? AND PlayID = ? AND Duration = ?
        )
        """, date_str, play_id, duration_minutes, date_str, play_id, duration_minutes)

        if cursor.rowcount == 0:
            skipped_count += 1
            print(f"Skipped duplicate {play_id}/{video.name}")
        else:
            inserted_count += 1
            print(f"Inserted {play_id}/{video.name} -> {duration_minutes} min")

    finally:
        cap.release()

conn.commit()
cursor.close()
conn.close()

print(f"✅ Processing complete: {inserted_count} rows inserted, {skipped_count} rows skipped.")
