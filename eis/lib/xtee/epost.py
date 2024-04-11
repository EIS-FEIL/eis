# # ei ole kasutusel, ei ole testitud
# import re
# from datetime import datetime
# from eis.lib.xtee.xroad import *

# class Epost(XroadClientEIS):
#     producer = 'epost'
        
#     def activeaccounts(self, isikukood):
#         param = E.request(E.isikukood(isikukood),
#                           E.eesnimi(),
#                           E.perenimi(),
#                           E.postiaadress())
#         list_path = ['/response/item']
#         response = self.call('activeaccounts', E.Request(param), list_path)
#         return response

# def get_eestiaadress(ik, **kw):
#     error = None
#     reg = Epost(**kw)
#     try:
#         res = reg.activeaccounts(ik)
#     except SoapFault as e:
#         error = e.faultstring
#     else:
#         res = res.get('response')
#         li = res.get('item')
#         if li:
#             for item in li:
#                 # vastuseks tulevad:
#                 # perenimi, muudetud (date), loodud (date), 
#                 # postiaadress (eesti.ee ja riik.ee aadressid), 
#                 # eesnimi, isikukood, suunatuid (int)
#                 postiaadress = item.get('postiaadress')
#                 suunatuid = int(item.get('suunatuid'))
#                 if re.match('[^0-9].*@eesti.ee', postiaadress) and suunatuid > 0:
#                     # valime nimega algava eesti.ee aadressi,
#                     # sest isikukood@eesti.ee aadressile ei saa kirju saata
#                     return postiaadress, error
                
#     return None, error

# if __name__=='__main__':
#     import logging
#     logging.basicConfig(level=logging.DEBUG)
#     log = logging.getLogger()
    
#     ik = '30101010007'
#     userId = 'EE%s' % ik
#     r = get_eestiaadress(ik, userId=userId)
#     print(r)
