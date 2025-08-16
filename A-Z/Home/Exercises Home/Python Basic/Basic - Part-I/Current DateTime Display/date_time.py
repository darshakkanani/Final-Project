from datetime import datetime

current = datetime.now()
print("Date:",current.strftime("%d/%m/%Y"))
print("Time:",current.strftime("%H:%M:%S"))