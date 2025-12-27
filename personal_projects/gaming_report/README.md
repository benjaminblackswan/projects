# Gaming Report Project (Quarterly)

### Step 1. Consolidate video recordings

Moving all gaming OBS recordings to *S:\OBS recordings\Gaming*, each game in its own folder, starting video Playthrough ID.

<img width="388" height="120" alt="image" src="https://github.com/user-attachments/assets/4b2505e2-9748-4f57-ad93-8761aba12cd6" />

### Step 2. Combine video for Youtube 

Determine for each game, if the total recording is longer than 12 hours, as the maximum video length for youtube is 12 hours. If total gameplay is longer than 12 hours, then divide the video records into partitions, with the last of each partition with ################ in the file name. Eg, PL082 Psychonauts 2 is 15 hours, mark the last video of partition 1 with ##############, so that there will be two partitions, each partition is shorter than 12 hours.

<img width="806" height="1027" alt="image" src="https://github.com/user-attachments/assets/a09f0e71-ce7c-4a0d-a7ed-fde125e9e16e" />

Open **Da Vinci Resolve**, combine each partition and save to *S:\OBS recordings*, with game name and part number (only if the total game playthrough is longer than 12 hours)

### Step 3. Upload to Youtube

Upload all combined videos to Youtube channel [@ben_game](https://www.youtube.com/ben_game)

Once all uploaded, create playlist for games longer than 12 hours.

Delete combined videos from *S:\OBS recordings*

### Step 4. Extract information from OBS recordings and upload to SQL Server DB.

Update the data source and destination variables in the code and Run.

```
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
```












































### Step 5....


## Step 1. Data generation

Everytime I play a game, I record the gaming session using OBS, the recorded file contains date and time information in the file name and other information are contained in the file metadata.

<img width="743" height="300" alt="image" src="https://github.com/user-attachments/assets/60855595-6e80-44ee-b37c-c9ed85c25a2a" />

After the completion of each game, the recordings are then organised into folders for each game, each folder starts with a five character play ID which acts as the primary key.

<img width="536" height="401" alt="image" src="https://github.com/user-attachments/assets/67fde0fe-21ba-44dd-9e03-6c0afb7e4baf" />

Python is used to 



# Final product

https://app.powerbi.com/view?r=eyJrIjoiZWYyZGYyOTgtMmE1ZC00MmZlLTkxODUtZTEzMGM3YmM0ZmQ3IiwidCI6IjM4Zjk1YWI4LWJkYTYtNDg4MC1iMjg0LWMzYWMwMzAyMzgzYSJ9

<img width="2054" height="1220" alt="image" src="https://github.com/user-attachments/assets/db6c88c2-be31-43d2-b617-b8781eb48ecf" />
