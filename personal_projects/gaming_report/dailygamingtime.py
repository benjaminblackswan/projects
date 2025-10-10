import pyodbc
import cv2
from pathlib import Path
import re  # import regex module

server = 'myfirstserverben.database.windows.net'
database = 'Free_Tier_01'
username = ''
password = ''
driver = '{ODBC Driver 17 for SQL Server}'

conn = pyodbc.connect(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
cursor = conn.cursor()

# Ensure table exists
cursor.execute("""
IF OBJECT_ID('dbo.Playthrough', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Playthrough (
        DateStr NVARCHAR(20),
        Game NVARCHAR(255),
        Duration DECIMAL(10,3)
    )
END
""")
conn.commit()

video_folder_path = Path(r"S:\OBS recordings\Gaming")

video_files = sorted([f for f in video_folder_path.rglob("*")
                      if f.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv']])

for video in video_files:
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        print(f"Cannot open {video}")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration_seconds = frame_count / fps if fps else 0
    duration_minutes = round(duration_seconds / 60, 3)

    # Extract date from filename, splitting on _ or space
    date_str = re.split(r'[_ ]', video.stem)[0]
    folder_name = video.parent.name[3:]

    # INSERT with WHERE NOT EXISTS to avoid duplicates
    cursor.execute("""
    INSERT INTO dbo.Playthrough (DateStr, Game, Duration)
    SELECT ?, ?, ?
    WHERE NOT EXISTS (
        SELECT 1 FROM dbo.Playthrough
        WHERE DateStr = ? AND Game = ? AND Duration = ?
    )
    """, date_str, folder_name, duration_minutes, date_str, folder_name, duration_minutes)

    cap.release()
    print(f"Inserted {folder_name}/{video.name} -> {duration_minutes} min")

conn.commit()
cursor.close()
conn.close()

print("✅ All videos loaded into Azure SQL (duplicates skipped)")
