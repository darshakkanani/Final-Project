from datetime import date

first_date = date(2014,7,2)
last_date = date(2014,7,11)

day = last_date - first_date
print(day.days)