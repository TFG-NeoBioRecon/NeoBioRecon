from datetime import datetime

def Logdate():
    now = datetime.now()
    return f'[{now.strftime("%d/%m/%y %H:%M:%S")}]'