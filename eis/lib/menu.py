"Menüü moodustamine"

from .menuitem import *
from eis.model import const
import eiscore.i18n as i18n
_ = i18n._
import logging
log = logging.getLogger(__name__)

def get_menu(handler, user):
    """
    Tagastatakse vasak ja parem menüü täies mahus, ilma kasutajaõigusi arvestamata.
    """
    app_name = handler.c.app_name

    if user.testpw_id:
        # testiparooliga kasutaja
        MenuItem.initmenu()
        return get_menu_testpw(handler, user.testpw_home_url())

    url_prefix = handler.url('avaleht')
    MenuItem.initmenu(url_prefix)
    if app_name == const.APP_EKK:
        return get_menu_ekk(handler)
    elif app_name == const.APP_EIS:
        return get_menu_avalik(handler, user)
    else:
        log.error('Unknown app name: %s' % (app_name))
        return MenuItem()

def get_menu_testpw(handler, testpw_url):
    """Testiparooliga sisseloginud kasutaja menüü
    """
    request = handler.request
    menu_left = MenuItem(subitems=
        [
        MenuItem(_("Testi sooritamine"), testpw_url, permission='testpw')
        ])
    menu_left.set_level(0)
    return menu_left

def NoneMenuItem(*args, **kw):
    kw['fn_check'] = lambda x: False
    return MenuItem(*args, **kw)

def get_menu_ekk(handler):
    """Eksamikeskuse vaate menüü
    """
    is_ext = handler.request.is_ext()
    ExtMenuItem = is_ext and MenuItem or NoneMenuItem
    #DbgMenuItem = handler.is_devel and MenuItem or NoneMenuItem
    request = handler.request
    menu_left = MenuItem(subitems=
        [
        MenuItem(_("Ülesandepank"), 'ylesanded', permission='ylesanded'), 
        MenuItem(_("Testid"), 'testid', permission='ekk-testid'), 
        ExtMenuItem(_("Konsultatsioonid"), 'konsultatsioonid', permission='konsultatsioonid'), 
        MenuItem(_("Registreerimine"), 'regamised', permission='regamine'), 
        MenuItem(_("Korraldamine"), 'korraldamised', permission='korraldamine'),
        MenuItem(_("Hindamine"), 'hindamised', permission='ekk-hindamine'),
        MenuItem(_("Sisestamine"), 'sisestamine', subitems=
                  [ExtMenuItem(_("Turvakottide numbrite sisestus"), 'sisestamine/turvakotid', permission='sisestamine'),
                   ExtMenuItem(_("Turvakoti/ümbriku saabumise registreerimine"), 'sisestamine/saabumised', permission='sisestamine'),
                   ExtMenuItem(_("Kirjalike testitööde ümbrike hindajatele väljastamine"), 'sisestamine/valjastamine', permission='sisestamine'),
                   MenuItem(_("Testi toimumise protokolli sisestamine"), 'sisestamine/protokollid', permission='sisestamine'),
                   ExtMenuItem(_("Suulise testi hindamise protokolli sisestamine"), 'sisestamine/suulised', permission='sisestamine'),
                   ExtMenuItem(_("Kirjaliku testi hindamise protokolli sisestamine"), 'sisestamine/kirjalikud', permission='sisestamine'),
                   ExtMenuItem(_("Kirjaliku testitöö sisestamine"), 'sisestamine/testitood', permission='sisestamine'),
                   ExtMenuItem(_("Skannitud vastuste laadimine"), 'sisestamine/skannimised', permission='sisestamine'),
                   ExtMenuItem(_("Rahvusvaheliste eksamite tunnistused"), 'sisestamine/rvtunnistused', permission='sisestamine'),                   
                   ]
                 ),
        MenuItem(_("Muud toimingud"), 'muud', subitems=
                  [ExtMenuItem(_("Vaided"), 'muud/vaided', permission='vaided'),
                   MenuItem(_("Eritingimused"), 'muud/erivajadused', permission='erivajadused'),
                   ExtMenuItem(_("Skannitud eksamitööd"), 'muud/skannid/taotlemised', permission='skannid'),
                   ExtMenuItem(_("Eksamitunnistused"), 'muud/tunnistused/valjastamised', permission='tunnistused'),
                   MenuItem(_("Tulemuste avaldamine"), 'muud/tulemused', permission='tulemusteavaldamine'),
                   MenuItem(_("Statistikaraportite avaldamine"), 'muud/statistikaraportid', permission='statistikaraportid'),                   
                   ExtMenuItem(_("Registreerimise kontroll"), 'muud/regkontrollid', permission='regkontroll'),                   
                   ExtMenuItem(_("Lõpetamise kontroll"), 'muud/lopetamised', permission='lopetamised'),
                   MenuItem(_("Küsimused ja ettepanekud"), 'muud/ettepanekud', permission='ettepanekud'),
                   MenuItem(_("Failide laadimine"), 'muud/toofailid', permission='failid'),
                   ]
                 ),
        MenuItem(_("Haldus"), 'admin', subitems=
                 [MenuItem(_("Kasutajate paroolid"), 'admin/paroolid', permission='kparoolid'),
                  MenuItem(_("Eksamikeskuse kasutajad"), 'admin/ametnikud', permission='ametnikud'), # BF
                  MenuItem(_("Testide läbiviimisega seotud isikud"), 'admin/kasutajad', permission='kasutajad'), # BF
                  MenuItem(_("Sooritajad"), 'admin/eksaminandid', permission='eksaminandid'), # BF
                  #MenuItem(_("CAE eeltesti sooritanud"), 'admin/caeeeltestid', permission='caeeeltest'),
                  MenuItem(_("Kasutajagrupid"), 'admin/kasutajagrupid', permission='admin'), # BF
                  MenuItem(_("Soorituspiirkonnad"), 'admin/piirkonnad', permission='piirkonnad'), # KM
                  MenuItem(_("Soorituskohad"), 'admin/kohad', permission='kasutajad'), # KM
                  ExtMenuItem(_("Asukohamäärus"), 'admin/asukohamaarus', permission='admin'),
                  MenuItem(_("Oluline info"), 'admin/olulineinfo', permission='olulineinfo'),
                  MenuItem(_("Lehekülje abiinfo"), 'admin/abiinfo', permission='olulineinfo'),                    
                  MenuItem(_("Testsessioonid"), 'admin/testsessioonid', permission='sessioonid'), # KM
                  MenuItem(_("Eksamiserverid"), 'admin/klastrid', permission='admin'),
                  #ExtMenuItem(_("Testide kiirvalikud"), 'admin/kiirvalikud', permission='kiirvalikud'), # KM
                  MenuItem(_("Klassifikaatorid"), 'admin/klassifikaatorid', permission='klassifikaatorid'),
                  MenuItem(_("Abivahendid"), 'admin/abivahendid', permission='klassifikaatorid'),
                  ExtMenuItem(_("Rahvusvaheliste eksamite tunnistused"), 'admin/rveksamid', permission='rveksamid'), # KM                  
                  MenuItem(_("Lepingud"), 'admin/lepingud', permission='lepingud'),
                  MenuItem(_("E-kogud"), 'ylesandekogud', permission='ylesandekogud'),                  
                  MenuItem(_("Logi"), 'admin/logi', permission='logi'), 
                  MenuItem(_("X-tee adapteri logi"), 'admin/logiadapter', permission='admin'),
                  #MenuItem(_("Allkirjastamise testimine"), 'testallkirjad', permission='admin'),
                  MenuItem(_("Kasutajaliidese tõlkimine"), 'potext', permission='ui-tolkimine'),
                  MenuItem(_("Süsteemi info"), 'sysinfo', permission='sysinfo'),
                  ]
                 ),
        MenuItem(_("Päringud"), 'otsing', subitems=
                 [ExtMenuItem(_("Eksamitunnistused"), 'otsing/tunnistused', permission='aruanded-tunnistused'),
                  MenuItem(_("Testisooritused"), 'otsing/testisooritused', permission='aruanded-testisooritused'),
                  ExtMenuItem(_("Testisoorituskoha teated"), 'otsing/kohateated', permission='aruanded-kohateated'),
                  ExtMenuItem(_("Vaatlejate teated"), 'otsing/vaatlejateated', permission='aruanded-vaatlejateated'),
                  ExtMenuItem(_("Läbiviijate teated"), 'otsing/labiviijateated', permission='aruanded-labiviijateated'),
                  ExtMenuItem(_("Tulemuste teavitused"), 'otsing/tulemusteteavitused', permission='aruanded-tulemusteteavitused'),
                  ExtMenuItem(_("Teadete ülevaade"), 'otsing/teated', permission='aruanded-teated'),
                  ExtMenuItem(_("Läbiviijate käskkirjad"), 'otsing/labiviijakaskkirjad', permission='aruanded-labiviijakaskkirjad'),
                  ExtMenuItem(_("III hindamise nõusolekud"), 'otsing/nousolekud3', permission='aruanded-nousolekud3'),                  
                  ExtMenuItem(_("Läbiviijate aruanded"), 'otsing/labiviijad', permission='aruanded-labiviijad'),
                  ExtMenuItem(_("Hindamiserinevused"), 'otsing/hindamiserinevused', permission='aruanded-erinevused'),
                  ExtMenuItem(_("Soorituskohad"), 'statistika/soorituskohad', permission='aruanded-soorituskohad'),
                  ExtMenuItem(_("Piirkondade tulemused"), 'statistika/piirkonnatulemused', permission='aruanded-prktulemused'),
                  MenuItem(_("Tulemuste statistika"), 'statistika/tulemused', permission='aruanded-tulemused'),
                  MenuItem(_("Osalemise statistika"), 'statistika/osalemine', permission='aruanded-osalemine'),
                  ExtMenuItem(_("Testide tulemuste statistika"), 'eksamistatistika', permission='aruanded-tulemused'),                             
                  ExtMenuItem(_("Vaiete statistika"), 'statistika/vaided', permission='aruanded-vaided'),
                  ExtMenuItem(_("Osaoskuste võrdlus"), 'statistika/osaoskused', permission='aruanded-osaoskused'),
                  ExtMenuItem(_("Testitulemuste võrdlus"), 'statistika/testitulemused', permission='aruanded-testitulemused'),
                  ExtMenuItem(_("Rahvusvahelised eksamid"), 'otsing/rvtunnistused', permission='aruanded-rvtunnistused'),
                  MenuItem(_("Tugiisikud"), 'otsing/tugiisikud', permission='aruanded-tugiisikud'),
                  MenuItem(_("Sooritajate arv"), 'otsing/sooritajatearvud', permission='aruanded-sooritajatearv'),
                  MenuItem(_("Kasutamise statistika"), 'otsing/kasutajatearvud', permission='admin'),                                    
                  ]
                 ),
        ])

    menu_left.set_level(0)
    return menu_left

def get_menu_avalik(handler, user):
    """Avaliku vaate menüü
    """
    is_ext = handler.request.is_ext()
    request = handler.request
    
    def saab_kohta_valida(handler):
        if user:
            kasutaja = user.get_kasutaja()
            if kasutaja:
                return len(kasutaja.get_kohad()) > 1
        return False

    #log.debug('get_menu_avalik au=%s koht=%s roll=%s' % (user.is_authenticated, user.koht_id, user.uiroll))
    if not user or not user.is_authenticated:
        menu_left = MenuItem(subitems=
                [MenuItem(_("Avalikud ülesanded"), 'lahendamine', permission='lahendamine', koht=False), 
                 MenuItem(_("Eksamitunnistused"), 'tunnistused', permission='lahendamine'),
                 MenuItem(_("Testide tulemuste statistika"), 'eksamistatistika', permission='lahendamine'),
                 ])
    elif user.uiroll == const.UIROLL_S:
        # testisooritaja, avalik vaade
        menu_left = MenuItem(subitems=
                [MenuItem(_("Avalikud ülesanded"), 'lahendamine', permission='lahendamine', koht=False), 
                 MenuItem(_("Registreerimine"), 'regamised', permission='sooritamine', koht=False),
                 MenuItem(_("Sooritamine"), 'sooritamised', permission='sooritamine', koht=False),
                 MenuItem(_("Minu tulemused"), 'tulemused', permission='minu', koht=False),
                 MenuItem(_("Minu töölaud"), 'tookogumikud', permission='koolipsyh,logopeed'),
                 MenuItem(_("Hindamine"), 'hindamine', subitems=
                          [MenuItem(_("Tsentraalsed testid"), 'khindamised', permission='khindamine', kohatu=True),
                           ]),
                 MenuItem(_("Koolipsühholoogid"), 'kpsyh', subitems=
                          [MenuItem(_("Testide loetelu"), 'psyhtestid', permission='koolipsyh'),
                           MenuItem(_("Tulemused"), 'psyhtulemused', permission='koolipsyh'),
                           MenuItem(_("Koolipsühholoogid"), 'koolipsyhholoogid', permission='pslitsentsid'),
                           ]),
                 MenuItem(_("Logopeedid"), 'logopeedid', permission='lglitsentsid'),
                 MenuItem(_("Muud"), 'muud', subitems=
                          [MenuItem(_("Eksamitunnistused"), 'tunnistused', permission='lahendamine'),
                           MenuItem(_("Testide tulemuste statistika"), 'eksamistatistika', permission='lahendamine'),
                           MenuItem(_("Testinimekirjad"), 'testinimekirjad', permission='avtugi'),
                           ]),
                 ])
    else:
        # õpetaja, koolijuht
        menu_left = MenuItem(subitems=
                [MenuItem(_("Minu töölaud"), 'tookogumikud', permission='tookogumikud', koht=True),                              
                 MenuItem(_("Tsentraalsed testid"), 'ekktestid', subitems= # (prototyybis: EKK testide läbiviimine)
                          [MenuItem(_("Testi sooritajate määramine"), 'nimekirjad/testimiskorrad', permission='nimekirjad', koht=True),
                           MenuItem(_("Testi läbiviimise korraldamine"), 'korraldamised', permission='avalikadmin', koht=True),
                           MenuItem(_("E-testi läbiviimine"), 'klabiviimine/toimumisajad', permission='testiadmin', koht=True),
                           MenuItem(_("Intervjuu läbiviimine"), 'svastamised', permission='intervjuu'),                           
                           MenuItem(_("Testi toimumise protokolli koostamine"), 'protokollid', permission='toimumisprotokoll,tprotsisestus,aineopetaja', koht=True),
                           MenuItem(_("Eritingimused"), 'erivajadused', permission='avalikadmin'),
                           MenuItem(_("Tulemused"), 'ktulemused', permission='avalikadmin,testiadmin,aineopetaja', koht=True),
                           MenuItem(_("Rahvusvaheliste eksamite tunnistused"), 'rvtunnistused', permission='avalikadmin'),
                           MenuItem(_("Testitööde vaatamine"), 'toovaatamised', permission='toovaatamine'),
                           MenuItem(_("Failide laadimine"), 'toofailid', permission='failid', koht=True),                                     
                           ]),
                 MenuItem(_("Hindamine"), 'hindamine', subitems=
                          [MenuItem(_("Tsentraalsed testid"), 'khindamised', permission='khindamine'),
                           MenuItem(_("Minu korraldatud testid"), 'rhindamised', permission='omanimekirjad'),
                           MenuItem(_("Muud testid"), 'muudhindamised', permission='omanimekirjad'),
                           ]),
                 MenuItem(_("Haldus"), 'admin', subitems=
                          [MenuItem(_("Kasutajate paroolid"), 'admin/paroolid', permission='paroolid', koht=True),
                           MenuItem(_("Klassi paroolid"), 'admin/klassiparoolid', permission='paroolid', koht=True),  
                           MenuItem(_("Kasutajate volitused"), 'admin/volitused', permission='avalikadmin', koht=True),
                           MenuItem(_("Soorituskoha andmed"), 'admin/kohad', permission='avalikadmin', koht=True),
                           MenuItem(_("Testide läbiviimisega seotud isikud"), 'admin/kasutajad', permission='avalikadmin', koht=True),
                           ]),
                 MenuItem(_("Koolipsühholoogid"), 'kpsyh', subitems=
                          [MenuItem(_("Testide loetelu"), 'psyhtestid', permission='koolipsyh'),
                           MenuItem(_("Tulemused"), 'psyhtulemused', permission='koolipsyh'),
                           MenuItem(_("Koolipsühholoogid"), 'koolipsyhholoogid', permission='pslitsentsid'),
                           ]),
                 MenuItem(_("Logopeedid"), 'logopeedid', permission='lglitsentsid'),                 
                 MenuItem(_("Muud"), 'muud', subitems=
                          [MenuItem(_("Eksamitunnistused"), 'tunnistused', permission='lahendamine'),
                           MenuItem(_("Testide tulemuste statistika"), 'eksamistatistika', permission='lahendamine'),                                            MenuItem(_("Testinimekirjad"), 'testinimekirjad', permission='avtugi'),
                           ]),
                 ])

    menu_left.set_level(0)
    return menu_left

def get_permissions_notauthenticated(handler):
    "Sisselogimata kasutaja õigused"
    is_ext = handler.request.is_ext()
    return {'lahendamine': const.BT_ALL,
            'abi': const.BT_VIEW,
            'eksamitunnistused': const.BT_ALL,
            'login/index': const.BT_ALL,
            }

def get_permissions_student(handler):
    "Testisooritaja õigused"
    is_ext = handler.request.is_ext()
    return {'lahendamine': const.BT_ALL,
            'abi': const.BT_VIEW,
            'minu': const.BT_ALL,
            'sooritamine': const.BT_ALL,
            'ettepanemine': const.BT_ALL,
            }

def get_permissions_public(handler):
    "Iga tuvastatud kasutaja õigused"
    is_ext = handler.request.is_ext()
    return {'lahendamine': const.BT_ALL,
            'abi': const.BT_VIEW,
            'minu': const.BT_ALL,
            'sooritamine': const.BT_ALL,
            'ettepanemine': const.BT_ALL,
            }

def get_permissions_testpw(handler):
    "Testiparooliga sisenenud kasutaja õigused"
    return {'abi': const.BT_VIEW,
            'testpw': const.BT_ALL,
            }
