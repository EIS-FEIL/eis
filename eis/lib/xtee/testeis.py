import pprint
from datetime import datetime
from eis.lib.xtee.xroad import *
from eis.lib.pyxadapterlib import attachment
import logging
log = logging.getLogger(__name__)

import eiscore.const as const

class TestEis(XroadClientEIS):
    "EISi teenuste testimine X-tee kaudu"
    #service_memberCode = '90008287'
    producer = 'eis'
    namespace = 'http://eis.x-road.eu/v4'

    def testSystem(self):
        result = err = None
        request = E.request()
        try:
            result = self.call('testSystem.v1', E.Request(request), [])
        except SoapFault as e:
            err = e.faultstring
        return err, result
    
    def load_cl_aine(self):
        result = err = None
        request = E.request()
        try:
            list_path = ['/response/cl_aine/item']
            result = self.call('load_cl_aine.v2', E.Request(request), list_path)
        except SoapFault as e:
            err = e.faultstring
        return err, result

    def load_cl(self):
        result = err = None
        request = E.request()
        try:
            list_path = ['/response/cl_tookoht/item',
                         '/response/cl_amet/item',
                         '/response/cl_haridus/item',
                         ]
            result = self.call('load_cl', E.Request(request), list_path)
        except SoapFault as e:
            err = e.faultstring
        return err, result

    def e_tunnistus_am(self, tunnistus_id):
        result = err = None
        request = E.request(E.tunnistus_id(tunnistus_id))
        try:
            result = self.call('e_tunnistus_am', E.Request(request), [])
        except SoapFault as e:
            err = e.faultstring
        return err, result

    def saisEksamid(self, isikukood):
        result = err = None
        request = E.request(E.isikukood(isikukood))
        try:
            list_path = ['/response/sais_eksam_jada/item']
            result = self.call('saisEksamid.v2', E.Request(request), list_path)
        except SoapFault as e:
            err = e.faultstring
        return err, result

    def riigikeeletase_ehis(self, alates, kuni, isikukoodid):
        request = E.request()
        if alates:
            request.append(E.alates(alates)) # alates.strftime('%Y-%m-%dT%H:%M:%S')
        if kuni:
            request.append(E.kuni(kuni)) # kuni.strftime('%Y-%m-%dT%H:%M:%S')
        attachments = []
        if isinstance(isikukoodid, bytes):
            att = attachment.Attachment(isikukoodid, use_gzip=False)
            att.filename = 'isikukoodid.zip'
            content_id = att.gen_content_id()
            attachments.append(att)
            isikukoodid = E.isikukoodid('',
                                        href='cid:%s' % content_id,
                                        filename=att.filename)
            request.append(isikukoodid)
        else:
            request.append(E.isikukoodid(isikukoodid))

        err = result = None
        try:
            result = self.call('riigikeeletase_ehis', E.Request(request), [], attachments=attachments)
        except SoapFault as e:
            err = e.faultstring
        return err, result

    def pohikoolieksamid_ehis(self, isikukoodid):
        li = E.isikukoodid()
        for ik in isikukoodid:
            li.append(E.isikukood(ik))
        request = E.request(li)
        err = result = None
        try:
            list_path = ['/response/oppurid/oppur',
                         '/response/oppurid/oppur/oppeained/oppeaine']            
            result = self.call('pohikoolieksamid_ehis.v2', E.Request(request), list_path)
        except SoapFault as e:
            err = e.faultstring
        return err, result

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    from eis.scripts.scriptuser import *
    admin = named_args.get('admin')
    if admin:
        admin = 'EE%s' % admin

    reg = TestEis(handler,
                  settings=registry.settings,
                  userId=admin)

    #reg.security_server = '192.168.116.128:5200'
    #reg.security_server_uri = '/adapter/'

    if 0:
        err, res = reg.testSystem()
        if err: print(err)
        pprint.pprint(res)        
    
    if 0:
        try:
            li = reg.allowedMethods()
        except SoapFault as e:
            print(e.faultstring)
            sys.exit(1)
        else:
            for item in li:
                print(item)
    if 0:
        res = reg.e_tunnistus_am(42)
        print(res)
        
    if 0:
        err, res = reg.load_cl_aine()
        if err: print(err)
        pprint.pprint(res)
    if 1:
        isikukoodid = '30101010007 33003300303'
        alates = datetime(2001,2,5)
        kuni = datetime(2025,9,2)
        err, res = reg.riigikeeletase_ehis(alates, kuni, isikukoodid)
        if err:
            print(err)
        else:
            pprint.pprint(res)
            for att in reg.response_attachments:
                print(('attachment: %s %sb' % (att.filename, len(att.data))))
    if 0:
        err, res = reg.saisEksamid('33602079941')
        if err: print(err)
        pprint.pprint(res)    

    if False:
        try:
            li = reg.listProducers()
        except SoapFault as e:
            print(e.faultstring)
            sys.exit(1)
        else:
            for item in li:
                print(item)

    if False:
        err, res = reg.load_cl()
        if err: print(err)
        pprint.pprint(res)

    if 0:
        err, res = reg.saisEksamid('33602079941')
        if err: print(err)
        pprint.pprint(res)    
    if 0:
        err, res = reg.pohikoolieksamid_ehis(['33602079941','30101010007'])
        if err: print(err)
        pprint.pprint(res)    
