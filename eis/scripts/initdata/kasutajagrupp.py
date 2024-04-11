# -*- coding: utf-8 -*-
"""Püsiandmete laadimine installimisel
"""
import logging
import datetime
from pyramid.request import Request
from eiscore.i18n import add_localizer
from eis.model import *

def get_opt():
    request = Request.blank('/', base_url='http://localhost:6543')
    request._LOCALE_ = 'en'
    from pyramid.paster import bootstrap
    info = bootstrap('tmp/development.dbg.ini')
    request.registry = info['registry']

    class DummyHandler(object):
        pass
    handler = DummyHandler()
    handler.request = request
    add_localizer(handler)
    return Opt(handler)
    
def insert_kasutajagrupp():
    grupid = get_opt().grupp_dict()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_ADMIN], 
                      id=const.GRUPP_ADMIN,
                      tyyp=const.USER_TYPE_EKK)
    from .oigus import txt_permissions
    for line in txt_permissions.split('\n'):
        permission = line.split('#')[0]
        if permission:
            g.lisaoigused([(permission, const.BT_ALL)])
            g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_SYSADMIN],
                      id=const.GRUPP_SYSADMIN,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('sysinfo', const.BT_ALL),
                   ])
    g.flush()
            
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_AINESPETS],
                      id=const.GRUPP_AINESPETS,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('ylesanded', const.BT_ALL),
                   ('ylesandekogud', const.BT_ALL),
                   ('ylesanderoll', const.BT_ALL),
                   ('ylkvaliteet', const.BT_ALL),                   
                   ('testiroll', const.BT_ALL),                                                         
                   ('yhisfailid', const.BT_ALL),
                   ('ekk-testid', const.BT_ALL),
                   ('konsultatsioonid', const.BT_ALL),
                   ('hindamisanalyys', const.BT_ALL),
                   ('vastusteanalyys', const.BT_ALL),
                   ('ekk-hindamine', const.BT_INDEX|const.BT_SHOW),
                   ('kasutajad', const.BT_INDEX|const.BT_SHOW),
                   ('profiil', const.BT_ALL),
                   ('testid', const.BT_INDEX|const.BT_SHOW),
                   ('omanimekirjad', const.BT_ALL),
                   ('klassifikaatorid', const.BT_INDEX|const.BT_SHOW),
                   ('aruanded-labiviijad', const.BT_ALL),
                   ('aruanded-labiviijakaskkirjad', const.BT_ALL),
                   ('aruanded-nousolekud3', const.BT_ALL),                                      
                   ('aruanded-erinevused', const.BT_ALL),
                   ('aruanded-tulemused', const.BT_ALL),
                   ('aruanded-osalemine', const.BT_ALL),
                   ('aruanded-vaided', const.BT_ALL),
                   ('aruanded-osaoskused', const.BT_ALL),
                   ('aruanded-testitulemused', const.BT_ALL),
                   ])
    g.flush()
    
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_AINETOORYHM],
                      id=const.GRUPP_AINETOORYHM,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('yhisfailid', const.BT_ALL),
                   ('ylesanded', const.BT_ALL),
                   ('ylesanded-markused', const.BT_ALL),
                   ('ylesandetahemargid', const.BT_ALL),                   
                   ])
    g.flush()
    
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_OSASPETS],
                      id=const.GRUPP_OSASPETS,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('ylesanded', const.BT_ALL),
                   ('ylesanderoll', const.BT_ALL),
                   ('yhisfailid', const.BT_ALL),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_VALJAVOTE],
                      id=const.GRUPP_VALJAVOTE,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('vastustevaljavote', const.BT_SHOW),
                   ])
    g.flush()
    
    # Ülesannete grupid
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_Y_KOOSTAJA],
                      id=const.GRUPP_Y_KOOSTAJA,
                      tyyp=const.USER_TYPE_Y)
    g.lisaoigused([('ylesanded', const.BT_ALL),
                   ('avylesanded', const.BT_ALL),                   
                   ])
    g.flush()
    
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_Y_VAATAJA],
                      id=const.GRUPP_Y_VAATAJA,
                      tyyp=const.USER_TYPE_Y)
    g.lisaoigused([('ylesanded', const.BT_INDEX|const.BT_SHOW),
                   ('ylesanded-markused', const.BT_ALL),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_Y_TOIMETAJA],
                      id=const.GRUPP_Y_TOIMETAJA,
                      tyyp=const.USER_TYPE_Y)
     # toimetaja on nagu tõlkija, aga põhikeeles
    g.lisaoigused([('ylesanded', const.BT_INDEX|const.BT_SHOW),
                   ('ylesanded-markused', const.BT_ALL),
                   ('ylesanded-toimetamine', const.BT_ALL),
                   ('ylesandetahemargid', const.BT_ALL),                                      
                   ])
    g.flush()
    
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_Y_TOLKIJA],
                      id=const.GRUPP_Y_TOLKIJA,
                      tyyp=const.USER_TYPE_Y)
    g.lisaoigused([('ylesanded', const.BT_INDEX|const.BT_SHOW),
                   ('ylesanded-markused', const.BT_ALL),
                   ('ylesanded-tolkimine', const.BT_ALL),
                   ('ylesandetahemargid', const.BT_ALL),                                      
                   ])
    g.flush()
    
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_Y_KUJUNDAJA],
                      id=const.GRUPP_Y_KUJUNDAJA,
                      tyyp=const.USER_TYPE_Y)
    g.lisaoigused([('ylesanded', const.BT_INDEX|const.BT_SHOW),
                   ('ylesanded-markused', const.BT_ALL),
                   ('ylesanded-failid', const.BT_ALL),
                   ])
    g.flush()
    
    # Testide grupid
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_KOOSTAJA],
                      id=const.GRUPP_T_KOOSTAJA,
                      tyyp=const.USER_TYPE_T)
    g.lisaoigused([('ylesanded', const.BT_ALL),
                   ('ekk-testid', const.BT_ALL),
                   ('testid', const.BT_ALL),
                   ('konsultatsioonid', const.BT_ALL),
                   ('vastusteanalyys', const.BT_INDEX|const.BT_SHOW),
                   ])
    g.flush()
   
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_VAATAJA],
                      id=const.GRUPP_T_VAATAJA,
                      tyyp=const.USER_TYPE_T)
    g.lisaoigused([('ylesanded', const.BT_INDEX|const.BT_SHOW),
                   ('ekk-testid', const.BT_INDEX|const.BT_SHOW),
                   ('vastusteanalyys', const.BT_INDEX|const.BT_SHOW),
                   ])
    g.flush()
    
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_TOIMETAJA],
                      id=const.GRUPP_T_TOIMETAJA,
                      tyyp=const.USER_TYPE_T)
    g.lisaoigused([('ylesanded', const.BT_INDEX|const.BT_SHOW),
                   ('ylesanded-toimetamine', const.BT_ALL),
                   ('ylesanded-markused', const.BT_ALL),
                   ('ekk-testid', const.BT_INDEX|const.BT_SHOW),
                   ('ekk-testid-toimetamine', const.BT_ALL),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_TOLKIJA],
                      id=const.GRUPP_T_TOLKIJA,
                      tyyp=const.USER_TYPE_T)
    g.lisaoigused([('ylesanded', const.BT_INDEX|const.BT_SHOW),
                   ('ylesanded-tolkimine', const.BT_ALL),
                   ('ylesanded-markused', const.BT_ALL),
                   ('ekk-testid', const.BT_INDEX|const.BT_SHOW),
                   ('ekk-testid-tolkimine', const.BT_ALL),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_KUJUNDAJA],
                      id=const.GRUPP_T_KUJUNDAJA,
                      tyyp=const.USER_TYPE_T)
    g.lisaoigused([('ylesanded', const.BT_INDEX|const.BT_SHOW),
                   ('ylesanded-failid', const.BT_ALL),
                   ('ylesanded-markused', const.BT_ALL),
                   ('ekk-testid', const.BT_INDEX|const.BT_SHOW),
                   ('ekk-testid-failid', const.BT_ALL),
                   ])
    g.flush()

    # avalikus vaates testiga seotud isik omanikuna
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_OMANIK],
                      id=const.GRUPP_T_OMANIK,
                      tyyp=const.USER_TYPE_T)
    g.lisaoigused([('testid', const.BT_ALL),
                   ('ekk-testid', const.BT_ALL),                   
                   ('omanimekirjad', const.BT_ALL),
                   ('thindamine', const.BT_ALL),
                   ('avylesanded', const.BT_INDEX|const.BT_SHOW)])
    # õigus lahendada teise õpetaja loodud ylesannet, kui see on minu testis
    g.flush()

    # avalikus vaates testiga seotud isik vaatajana
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_TOOVAATAJA],
                      id=const.GRUPP_T_TOOVAATAJA,
                      tyyp=const.USER_TYPE_KOOL)
    g.lisaoigused([('testid', const.BT_INDEX|const.BT_SHOW),
                   ])
    g.flush()
    
    # õpetaja, kellele on eeltest antud korraldada
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_KORRALDAJA],
                      id=const.GRUPP_T_KORRALDAJA,
                      tyyp=const.USER_TYPE_T)
    g.lisaoigused([('testid', const.BT_ALL),
                   ('thindamine', const.BT_ALL),                   
                   ('omanimekirjad', const.BT_ALL)])
    g.flush()
    
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_KORRALDUS],
                      id=const.GRUPP_KORRALDUS,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('korraldamine', const.BT_ALL),
                   ('regamine', const.BT_ALL),
                   ('erivajadused', const.BT_ALL),
                   ('testimiskorrad', const.BT_ALL),
                   ('ekk-hindamine', const.BT_ALL),
                   ('hindamisanalyys', const.BT_ALL),
                   ('vastusteanalyys', const.BT_ALL),                   
                   ('eksperthindamine', const.BT_INDEX|const.BT_SHOW),
                   ('ekspertryhmad', const.BT_INDEX|const.BT_SHOW),
                   ('hindajamaaramine', const.BT_ALL),
                   ('juhendamine', const.BT_ALL),
                   ('sisestamine', const.BT_ALL),
                   ('parandamine', const.BT_ALL),
                   ('aruanded-tunnistused', const.BT_ALL),
                   ('aruanded-testisooritused', const.BT_ALL),
                   ('aruanded-kohateated', const.BT_ALL),
                   ('aruanded-vaatlejateated', const.BT_ALL),
                   ('aruanded-labiviijateated', const.BT_ALL),
                   ('aruanded-tulemusteteavitused', const.BT_ALL),
                   ('aruanded-teated', const.BT_ALL),
                   ('aruanded-prktulemused', const.BT_ALL),
                   ('aruanded-labiviijad', const.BT_ALL),
                   ('aruanded-labiviijakaskkirjad', const.BT_ALL),
                   ('aruanded-nousolekud3', const.BT_ALL),                                      
                   ('aruanded-erinevused', const.BT_ALL),
                   ('aruanded-soorituskohad', const.BT_ALL),
                   ('aruanded-tulemused', const.BT_ALL),
                   ('aruanded-osalemine', const.BT_ALL),
                   ('aruanded-vaided', const.BT_ALL),
                   ('aruanded-osaoskused', const.BT_ALL),
                   ('aruanded-testitulemused', const.BT_ALL),
                   ('aruanded-tugiisikud', const.BT_ALL),
                   ('aruanded-sooritajatearv', const.BT_ALL),
                   ('vaided', const.BT_INDEX|const.BT_SHOW),
                   ('tunnistused', const.BT_SHOW),
                   ('tulemusteavaldamine', const.BT_ALL),                   
                   ('statistikaraportid', const.BT_ALL),                   
                   ('lopetamised', const.BT_ALL),
                   ('regkontroll', const.BT_ALL),                                      
                   ('ekk-testid', const.BT_INDEX|const.BT_SHOW),
                   ('konsultatsioonid', const.BT_ALL),
                   ('piirkonnad', const.BT_ALL),
                   ('kohad', const.BT_ALL),
                   ('kiirvalikud', const.BT_ALL),
                   ('sessioonid', const.BT_ALL),
                   ('kasutajad', const.BT_ALL),
                   ('eksaminandid', const.BT_ALL),
                   ('eksaminandid-ik', const.BT_ALL),
                   ('kparoolid', const.BT_ALL),
                   ('profiil', const.BT_ALL),
                   ('kohteelvaade', const.BT_SHOW),
                   ('ylesanderoll', const.BT_ALL),
                   ('testiroll', const.BT_ALL),                                      
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_P_KORRALDUS],
                      id=const.GRUPP_P_KORRALDUS,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('korraldamine', const.BT_ALL),
                   ('piirkonnad', const.BT_ALL),
                   ('kohad', const.BT_ALL),
                   ('kiirvalikud', const.BT_INDEX|const.BT_SHOW),
                   ('sessioonid', const.BT_INDEX|const.BT_SHOW),
                   ('kasutajad', const.BT_ALL),
                   ('profiil', const.BT_INDEX|const.BT_SHOW),
                   ('profiil-vaatleja', const.BT_ALL),
                   ('erivajadused', const.BT_INDEX|const.BT_SHOW),
                   ('aruanded-vaatlejateated', const.BT_ALL),
                   ('aruanded-prktulemused', const.BT_ALL),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_E_KORRALDUS],
                      id=const.GRUPP_E_KORRALDUS,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('korraldamine', const.BT_ALL),
                   ('regamine', const.BT_ALL),
                   ('testimiskorrad', const.BT_ALL),
                   ('ekk-testid', const.BT_INDEX|const.BT_SHOW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_REGAJA],
                      id=const.GRUPP_REGAJA,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('regamine', const.BT_ALL),
                   ('erivajadused', const.BT_INDEX|const.BT_SHOW),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_HINDAMISJUHT],
                      id=const.GRUPP_HINDAMISJUHT,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('ekk-hindamine', const.BT_ALL),
                   ('eksperthindamine', const.BT_INDEX|const.BT_SHOW),
                   ('ekspertryhmad', const.BT_ALL),
                   ('hindajamaaramine', const.BT_ALL),
                   ('juhendamine', const.BT_ALL),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_HINDAMISJUHT],
                      id=const.GRUPP_T_HINDAMISJUHT,
                      tyyp=const.USER_TYPE_T)    
    g.lisaoigused([('ekk-hindamine', const.BT_ALL),
                   ('eksperthindamine', const.BT_INDEX|const.BT_SHOW),
                   ('ekspertryhmad', const.BT_ALL),
                   ('hindajamaaramine', const.BT_ALL),
                   ('juhendamine', const.BT_ALL),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_HINDAMISEKSPERT],
                      id=const.GRUPP_HINDAMISEKSPERT,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('hindamisanalyys', const.BT_ALL),
                   ('vastusteanalyys', const.BT_ALL),                                      
                   ('ekk-hindamine', const.BT_INDEX|const.BT_SHOW),
                   ('eksperthindamine', const.BT_ALL),
                   ('ekspertryhmad', const.BT_INDEX|const.BT_SHOW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_SISESTAJA],
                      id=const.GRUPP_SISESTAJA,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('sisestamine', const.BT_ALL),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_PARANDAJA],
                      id=const.GRUPP_PARANDAJA,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('sisestamine', const.BT_ALL),
                   ('parandamine', const.BT_ALL),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_VAIDEKOM],
                      id=const.GRUPP_VAIDEKOM,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('vaided', const.BT_ALL),
                   ])
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_VAIDEKOM_SEKRETAR],
                      id=const.GRUPP_VAIDEKOM_SEKRETAR,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('vaided', const.BT_ALL),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_VAIDEKOM_ESIMEES],
                      id=const.GRUPP_VAIDEKOM_ESIMEES,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('vaided', const.BT_ALL),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_ERIVAJADUS],
                      id=const.GRUPP_ERIVAJADUS,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('erivajadused', const.BT_ALL),
                   ('regamine', const.BT_INDEX|const.BT_SHOW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_AMETNIK],
                      id=const.GRUPP_AMETNIK,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('ylesanded', const.BT_INDEX),
                   ('ekk-testid', const.BT_INDEX),
                   ('ekk-hindamine', const.BT_INDEX),                   
                   #('konsultatsioonid', const.BT_INDEX),
                   #('piirkonnad', const.BT_INDEX|const.BT_SHOW),
                   #('kohad', const.BT_INDEX|const.BT_SHOW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_FAILID],
                      id=const.GRUPP_FAILID,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('failid', const.BT_ALL),
                   ])
    g.flush()

    # EKK vaate avalike kasutajate rollid
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_OMATEST],
                      id=const.GRUPP_OMATEST,
                      tyyp=const.USER_TYPE_AV)
    g.lisaoigused([('ylesanded', const.BT_ALL),
                   ('ylesanderoll', const.BT_ALL),
                   ('testiroll', const.BT_ALL),
                   ('ekk-testid', const.BT_ALL),
                   ('testimiskorrad', const.BT_ALL),
                   ('korraldamine', const.BT_ALL),
                   ('ekk-hindamine', const.BT_ALL),
                   ('hindajamaaramine', const.BT_ALL),
                   ('eksperthindamine', const.BT_ALL),
                   ('hindamisanalyys', const.BT_ALL),
                   ('vastusteanalyys', const.BT_ALL),
                   ])
    g.flush()
    

    # Avaliku vaate rollid
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_OPETAJA],
                      id=const.GRUPP_OPETAJA,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('ylesanded', const.BT_ALL),
                   ('testid', const.BT_ALL),
                   ('omanimekirjad', const.BT_ALL),
                   ('nimekirjad', const.BT_ALL),
                   ('tookogumikud', const.BT_ALL),
                   ('klass', const.BT_ALL),
                   ('avylesanded', const.BT_CREATE),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_K_ADMIN],
                      id=const.GRUPP_K_ADMIN,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('testid', const.BT_ALL),
                   ('omanimekirjad', const.BT_ALL),
                   ('nimekirjad', const.BT_ALL),
                   ('paroolid', const.BT_ALL),
                   ('profiil', const.BT_ALL),
                   ('klass', const.BT_ALL),
                   ('avylesanded', const.BT_CREATE),                   
                   ('avalikadmin', const.BT_ALL),
                   ('testiadmin', const.BT_ALL),
                   ('toimumisprotokoll', const.BT_ALL),
                   ('abimaterjalid', const.BT_VIEW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_K_JUHT],
                      id=const.GRUPP_K_JUHT,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('failid', const.BT_ALL),
                   ('plangid', const.BT_ALL),
                   ('testid', const.BT_ALL),
                   ('omanimekirjad', const.BT_ALL),
                   ('nimekirjad', const.BT_ALL),
                   ('paroolid', const.BT_ALL),
                   ('kasutajad', const.BT_ALL),
                   ('profiil', const.BT_ALL),
                   ('klass', const.BT_ALL),
                   ('tookogumikud', const.BT_ALL),
                   ('avylesanded', const.BT_CREATE),
                   ('avalikadmin', const.BT_ALL),
                   ('testiadmin', const.BT_ALL),
                   ('toimumisprotokoll', const.BT_ALL),
                   ('abimaterjalid', const.BT_VIEW),                                      
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_K_PLANK],
                      id=const.GRUPP_K_PLANK,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('plangid', const.BT_ALL),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_K_PROTOKOLL],
                      id=const.GRUPP_K_PROTOKOLL,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('toimumisprotokoll', const.BT_VIEW),
                   ('tprotsisestus', const.BT_ALL),                   
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_K_FAILID],
                      id=const.GRUPP_K_FAILID,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('failid', const.BT_VIEW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_OPILANE],
                      id=const.GRUPP_OPILANE,
                      tyyp=const.USER_TYPE_KOOL)
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_LOPETANU],
                      id=const.GRUPP_LOPETANU,
                      tyyp=const.USER_TYPE_KOOL)
    g.flush()
    
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_T_ADMIN],
                      id=const.GRUPP_T_ADMIN,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('testiadmin', const.BT_ALL),
                   ('toimumisprotokoll', const.BT_VIEW),
                   ('omanimekirjad', const.BT_VIEW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_VAATLEJA],
                      id=const.GRUPP_VAATLEJA,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('nousolekud', const.BT_ALL),
                   ('testiadmin', const.BT_VIEW),
                   ('toimumisprotokoll', const.BT_VIEW),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_HINDAJA_S],
                      id=const.GRUPP_HINDAJA_S,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('nousolekud', const.BT_ALL),
                   ('shindamine', const.BT_ALL),
                   ('testiadmin', const.BT_VIEW),
                   ('toimumisprotokoll', const.BT_VIEW),
                   ])
    g.flush()
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_HINDAJA_K],
                      id=const.GRUPP_HINDAJA_K,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('nousolekud', const.BT_ALL),
                   ('khindamine', const.BT_ALL),
                   ('thindamine', const.BT_ALL),                   
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_HINDAJA_S2],
                      id=const.GRUPP_HINDAJA_S2,
                      tyyp=const.USER_TYPE_KOOL)
    g.lisaoigused([('nousolekud', const.BT_ALL),
                   ('shindamine', const.BT_ALL),
                   ('testiadmin', const.BT_VIEW),
                   ('toimumisprotokoll', const.BT_VIEW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_INTERVJUU],
                      id=const.GRUPP_INTERVJUU,
                      tyyp=const.USER_TYPE_KOOL)
    g.lisaoigused([('nousolekud', const.BT_ALL),
                   ('testiadmin', const.BT_VIEW),
                   ('intervjuu', const.BT_ALL),
                   ('toimumisprotokoll', const.BT_VIEW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_HIND_INT],
                      id=const.GRUPP_HIND_INT,
                      tyyp=const.USER_TYPE_KOOL)
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_KOMISJON],
                      id=const.GRUPP_KOMISJON,
                      tyyp=const.USER_TYPE_KOOL)
    g.lisaoigused([('testiadmin', const.BT_VIEW),
                   ('toimumisprotokoll', const.BT_VIEW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_KOMISJON_ESIMEES],
                      id=const.GRUPP_KOMISJON_ESIMEES,
                      tyyp=const.USER_TYPE_KOOL)
    g.lisaoigused([('testiadmin', const.BT_ALL),
                   ('toimumisprotokoll', const.BT_ALL),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_KONSULTANT],
                      id=const.GRUPP_KONSULTANT,
                      tyyp=const.USER_TYPE_KOOL)
    g.lisaoigused([('testiadmin', const.BT_VIEW),
                   ('toimumisprotokoll', const.BT_ALL),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_LABIVIIJA],
                      id=const.GRUPP_LABIVIIJA,
                      tyyp=const.USER_TYPE_KOOL)
    g.lisaoigused([('nousolekud', const.BT_ALL),
                   ('shindamine', const.BT_VIEW),
                   ('khindamine', const.BT_VIEW),
                   ('intervjuu', const.BT_ALL),
                   ('testiadmin', const.BT_VIEW),
                   ('toimumisprotokoll', const.BT_VIEW),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_A_PSYH],
                      id=const.GRUPP_A_PSYH,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('ylesanded', const.BT_ALL),
                   ('testid', const.BT_ALL),
                   ('tookogumikud', const.BT_ALL),
                   ('omanimekirjad', const.BT_ALL),                   
                   ('koolipsyh', const.BT_ALL),                   
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_A_PSYHADMIN],
                      id=const.GRUPP_A_PSYHADMIN,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('pslitsentsid', const.BT_ALL),
                   ])
    g.flush()


    g = Kasutajagrupp(nimi=grupid[const.GRUPP_A_LOGOPEED],
                      id=const.GRUPP_A_LOGOPEED,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('ylesanded', const.BT_ALL),
                   ('testid', const.BT_ALL),
                   ('tookogumikud', const.BT_ALL),                   
                   ('omanimekirjad', const.BT_ALL),
                   ('logopeed', const.BT_ALL),                   
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_A_LOGOPEEDADMIN],
                      id=const.GRUPP_A_LOGOPEEDADMIN,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('lglitsentsid', const.BT_ALL),
                   ])
    g.flush()


    g = Kasutajagrupp(nimi=grupid[const.GRUPP_AINEOPETAJA],
                      id=const.GRUPP_AINEOPETAJA,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('aineopetaja', const.BT_ALL),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_TOOVAATAJA],
                      id=const.GRUPP_TOOVAATAJA,
                      tyyp=const.USER_TYPE_KOOL)    
    g.lisaoigused([('toovaatamine', const.BT_INDEX),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_HTMLEDIT],
                      id=const.GRUPP_HTMLEDIT,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('srcedit', const.BT_ALL),
                   ])
    g.flush()
   
    g = Kasutajagrupp(nimi=grupid[const.GRUPP_STATISTIK],
                      id=const.GRUPP_STATISTIK,
                      tyyp=const.USER_TYPE_EKK)    
    g.lisaoigused([('statistikaraportid', const.BT_ALL),
                   ('aruanded-erinevused', const.BT_VIEW),
                   ('aruanded-kohateated', const.BT_VIEW),
                   ('aruanded-labiviijad', const.BT_VIEW),
                   ('aruanded-labiviijakaskkirjad', const.BT_VIEW),
                   ('aruanded-osalemine', const.BT_VIEW),
                   ('aruanded-rvtunnistused', const.BT_VIEW),
                   ('aruanded-soorituskohad', const.BT_VIEW),
                   ('aruanded-testisooritused', const.BT_VIEW),
                   ('aruanded-tulemused', const.BT_VIEW),
                   ('aruanded-tunnistused', const.BT_VIEW),
                   ('aruanded-vaatlejateated', const.BT_VIEW),
                   ('aruanded-vaided', const.BT_VIEW),
                   ('hindamisanalyys', const.BT_VIEW),
                   ('vastusteanalyys', const.BT_VIEW),
                   ('vastustevaljavote', const.BT_SHOW),
                   ('tunnistused', const.BT_SHOW),
                   ('tulemusteavaldamine', const.BT_ALL),
                   ])

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_AVALDET],
                      id=const.GRUPP_AVALDET,
                      tyyp=const.USER_TYPE_EKK)

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_UI_TOLKIJA],
                      id=const.GRUPP_UI_TOLKIJA,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('ui-tolkimine', const.BT_ALL),
                   ])
    g.flush()

    g = Kasutajagrupp(nimi=grupid[const.GRUPP_SISUAVALDAJA],
                      id=const.GRUPP_SISUAVALDAJA,
                      tyyp=const.USER_TYPE_EKK)
    g.lisaoigused([('sisuavaldamine', const.BT_ALL),
                   ])
    g.flush()
    

def insert_kasutaja():
    Kasutaja(isikukood='ADMIN',
             eesnimi='ADMIN',
             perenimi='ADMIN',
             on_ametnik=True).\
        lisagrupid([const.GRUPP_ADMIN,
                    const.GRUPP_AMETNIK,
                    ]).\
        set_password('admin', True)

def insert_testkasutaja():
    k = Kasutaja(isikukood='30809010002',
                 eesnimi='Ivan',
                 perenimi='Orav',
                 on_ametnik=True,
                 on_labiviija=True)
    k.set_password('admin', True)
    k.lisagrupid([const.GRUPP_ADMIN,
                  const.GRUPP_AMETNIK])
    k.lisaroll(const.GRUPP_AINESPETS, aine_kood='f')
    k.lisaroll(const.GRUPP_AINESPETS, aine_kood='m')
    k.lisaroll(const.GRUPP_AINESPETS, aine_kood='b')
    k.lisaroll(const.GRUPP_AINESPETS, aine_kood='e')
    k.lisaroll(const.GRUPP_OPETAJA)
             
    Kasutaja(isikukood='33003300303',
             eesnimi='Katariina',
             perenimi='Jee',
             on_labiviija=True)\
        .set_password('admin', True)

                  
