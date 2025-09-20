from datetime import datetime
import time

while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")   # 24hr format
    current_date = now.strftime("%A, %d %B %Y")  # Day, Date Month Year
    print("Date:", current_date)
    print("Time:", current_time)
    time.sleep(1)  # updates every second


