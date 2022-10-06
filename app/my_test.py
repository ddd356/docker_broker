import requests
import time

def test():
    requests.get('http://127.0.0.1:5000/1/1000.0/put')
    time.sleep(1.0)


    requests.get('http://127.0.0.1:5000/2/1000.0/put')
    time.sleep(1.0)
