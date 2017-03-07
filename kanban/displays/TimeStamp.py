
import datetime

def timestamp():
    right_now = datetime.datetime.now()
    return right_now.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
    print timestamp()
