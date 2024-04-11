import logging
log = logging.getLogger(__name__)
from eis.lib.apiclient import APIClient

class DigitempelClient(APIClient):
    apikey = 'digitempel'
    
    def start(self):
        url = '/start'
        res = self.apicall(url, None)
        return res

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    cl = DigitempelClient(handler)
    res = cl.start()
    print(res)
