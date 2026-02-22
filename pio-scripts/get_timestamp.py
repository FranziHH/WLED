import datetime
import os

# Holt das aktuelle Datum und die Uhrzeit
now = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

# Setzt die Umgebungsvariable für den aktuellen Prozess
os.environ["WLED_BUILD_TS"] = now

print(f"--- Build Timestamp gesetzt: {now} ---")