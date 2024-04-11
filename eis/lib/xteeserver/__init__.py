# -*- coding: utf-8 -*-
"""
X-tee adapterserveri teenused

Turvaserver pöördub URLile http://server/adapter ,
mida teenindab failis handlers/adapter.py AdapterHandler.serve(),
mis kutsub välja siit lib.xteeserver.srv.dispatch()

Iga teenuse jaoks on kataloogis xteeserver oma fail funktsiooniga serve().
Funktsiooni serve() parameetriteks antakse:
- päringu keha XML objekt
- päringu päis dictina
- sisendis olevate manuste list
Funktsioon serve() peab tagastama:
- vastuse keha XML objekt
- vastuse manuste list

Teenuste registreerimine toimub allolevas funktsioonis register().
Teenuste kirjeldus asub eis/static/util/eis_v4.wsdl.
"""

from eis.lib.pyxadapterlib.xroadserver import XroadServer
from eis.model_log import Logi_adapter
from eis.model import const

from . import testSystem
from . import saisEksamid
from . import saisApellatsioonid
from . import e_tunnistus_am
from . import e_tunnistus_am_notar
from . import e_tunnistus_kehtivus
from . import e_tunnistus_list_notar
from . import pohikoolieksamid_ehis
from . import riigieksamid_ehis
from . import tulemused_riigiportaali
from . import testsessioonid_kod
from . import testid_kod
from . import e_tunnistus_kod
from . import load_cl_aine
from . import load_cl
from . import load_cl_rveksam
from . import teis_andmed
from . import seis_andmed
from . import teis_andmed_kod
from . import seis_andmed_kod
from . import teis_del_kod
from . import seis_del_kod
from . import riigikeeletase
from . import riigikeeletase_ehis
from . import legacyX
from . import legacyTE
from . import legacySE

try:
    from . import plank_vabad
    from . import plank_valjasta
except ImportError:
    # plankide moodulit ei ole
    plank_vabad = plank_valjasta = None
    
srv = None

class XroadServerEIS(XroadServer):
    is_trace = False
    
    def _log_msg(self, xrheader, input_xml, output_xml, input_data, output_data, started, request):
        client_str = userid = name = None
        if xrheader:
            try:
                client = xrheader.client
                li = [client.xRoadInstance,
                      client.memberClass,
                      client.memberCode,
                      client.subsystemCode,
                      ]
                client_str = '/'.join(li)
            except:
                pass

            try:
                userid = xrheader.userId
            except:
                pass

            try:
                service = xrheader.service
                name = service.serviceCode
                version = service.serviceVersion
                if version:
                    name = name + '.' + version
            except:
                pass

        if name == 'testSystem.v1':
            # kui ei taha monitooringut logida
            return
        Logi_adapter.add(client_str, userid, name, input_xml or input_data, output_xml, started, request)

def register_services(settings):
    global srv
    producer = settings.get('xroad.producer') or 'eis'   
    namespace = "http://eis.x-road.eu/v4"
    srv = XroadServerEIS(settings, producer, namespace)
    srv.namespace3 = "http://%s.x-road.ee/producer/" % (producer)
    srv.namespace2 = "http://producers.%s.xtee.riik.ee/producer/%s" % (producer, producer)

    srv.register(testSystem)
    srv.register(saisEksamid)
    srv.register(saisApellatsioonid)
    srv.register(saisEksamid, version='v2')
    srv.register(saisApellatsioonid, version='v2')    
    srv.register(saisEksamid, version='v3')
    srv.register(e_tunnistus_am)
    srv.register(e_tunnistus_am_notar)
    srv.register(e_tunnistus_kehtivus)
    srv.register(e_tunnistus_list_notar)
    srv.register(riigieksamid_ehis)
    srv.register(tulemused_riigiportaali)
    srv.register(testsessioonid_kod)
    srv.register(testid_kod)
    srv.register(e_tunnistus_kod)
    srv.register(load_cl_aine)
    srv.register(load_cl_aine, version='v2')
    srv.register(load_cl)
    srv.register(load_cl_rveksam)    
    srv.register(teis_andmed)
    srv.register(seis_andmed)    
    srv.register(teis_andmed_kod)
    srv.register(seis_andmed_kod)
    srv.register(teis_del_kod)
    srv.register(seis_del_kod)
    srv.register(pohikoolieksamid_ehis, version='v2')
    srv.register(pohikoolieksamid_ehis, version='v1')
    srv.register(riigikeeletase)
    srv.register(riigikeeletase_ehis)
    
    if plank_vabad:
        srv.register(plank_vabad)
        srv.register(plank_valjasta)

    srv.register(legacyX)
    srv.register(legacyTE)
    srv.register(legacySE)
