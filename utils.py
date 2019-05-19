import calendar
import os

from datetime import datetime

def create_dir_if_not_exist(path):
    try:
        os.makedirs(path)
    except:
        pass

def get_expiry_date(year=None, month=None):
    if not year or not month:
        today = datetime.today()
        month, year = today.month, today.year
    cal_month = calendar.month(year, month).split("\n")
    try:
        last_thursday = cal_month[-2].strip().split(' ')[3]
    except:
        last_thursday = cal_month[-3].strip().split(' ')[3]
    month_name = cal_month[0].strip().split(" ")[0][:3].upper()
    expiry_date = "{}{}{}".format(last_thursday, month_name, year)
    return expiry_date

def is_weekend():
    today = datetime.today()
    if calendar.weekday(today.year, today.month, today.day) >= 5:
        # 5 and 6 are Saturday and Sunday.
        return True
    return False

def get_home_directory():
    return os.path.expanduser("~")

if __name__ == "__main__":
    main()
