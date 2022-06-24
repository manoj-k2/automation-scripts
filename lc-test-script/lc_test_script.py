import OperationLC
from threading import Thread
import time
import os


if __name__ == "__main__":
    OperationLC.set_config()
    # for getting application UUID
    OperationLC.get_app_uuid()
    OperationLC.get_lc_file()
    thread1 = Thread(target=OperationLC.get_json_info,args=('applicationinfo',))
    thread1.start() 
    thread2 = Thread(target=OperationLC.get_json_info,args=("http-connection-stat",))
    thread2.start()
    thread3 = Thread(target=OperationLC.get_json_info,args=("healthcheck",))
    thread3.start()
    thread4 = Thread(target=OperationLC.get_json_info,args=("getPolicy Response",))
    thread4.start()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    OperationLC.get_errors()