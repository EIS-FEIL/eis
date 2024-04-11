from datetime import datetime, date
import logging
log = logging.getLogger(__name__)
from eis.lib.apiclient import APIClient

class EstnltkClient(APIClient):
    apikey = 'eisestnltk'
    
    def analyze(self, txt, is_rtf):
        url = '/analyze'
        params = {'txt': txt,
                  'is_rtf': is_rtf,
                  }
        res = self.apicall(url, params, post=True)
        return res['items']

if __name__ == '__main__':
    from eis.scripts.scriptuser import *
    cl = EstnltkClient(handler)
    res = cl.analyze('Eila liikusid pilved kuidaki', False)
    print(res)
