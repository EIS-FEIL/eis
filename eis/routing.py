"URLide ruutimine kontrolleriteni"
# teadetes kasutatud fikseeritud urlid on EISi koodist leitavad FIXURL kaudu
from .routingbase import *

import eiscore.const as const

def make_map(config, settings, app_name, is_live, is_test):
    """Ruutingu koostamine
    """
    if app_name == 'adapter':
        import eis.lib.xteeserver as xteeserver
        xteeserver.register_services(settings)
        add_handler(config, 'check', '/check', 'eis.handlers.adapter:AdapterHandler', action='check')
        add_handler(config, 'adapter', '/', 'eis.handlers.adapter:AdapterHandler', action='serve')
        add_handler(config,
                    'opirada_testisooritused',
                    '/opirada/testisooritused',
                    'eis.lib.xteeserver_json.opirada_testisooritused:testisooritused')
        add_handler(config,
                    'hsilm_tulemused',
                    '/hsilm/tulemused',
                    'eis.lib.xteeserver_json.hsilm_tulemused:tulemused')
        add_handler(config,
                    'hsilm_rvtunnistused',
                    '/hsilm/rvtunnistused',
                    'eis.lib.xteeserver_json.hsilm_rvtunnistused:rvtunnistused')
        config.add_view('eis.handlers.error:error', context=Exception)
        return

    # kõigi rakenduste yhine ruuting
    make_global_map(config, settings, app_name, is_live, is_test)

    # avaleht
    add_handler(config, 'avaleht', '/', 'eis.handlers.index:IndexController', action='index')
    add_handler(config, 'avalehepilt', '/avalehepilt/{id:\d+}.{format:[a-z]+}', 'eis.handlers.index:IndexController', action='avalehepilt')    

    # Ühised failid
    add_handler(config, 'shared', '/shared/{filename:.+}',
                       'eis.handlers.avalik.lahendamine.images:ImagesController', 
                       action='shared',
                       request_method='GET')
    add_handler(config, 'shareddummy', '{dummypath:.*}/shared/{filename:.+}',
                       'eis.handlers.avalik.lahendamine.images:ImagesController', 
                       action='shared',
                       request_method='GET')
    # testi tagasisides kasutatud pildid (avalikud)
    add_handler(config, 'testimages', '{dummypath:.*}/testimages/{test_id:\d+}/{filename}',
                       'eis.handlers.avalik.lahendamine.images:ImagesController', 
                       action='testimages',
                       request_method='GET')

    # vastuse failid ilma testita lahendamisel
    add_handler(config, 'lahendamine_vastusfail_format',
                '/lahendamine/vastusfail/{uuid}.{id}.{fileversion}.{format}',
                'eis.handlers.avalik.lahendamine.vastusfailid:VastusfailidController',
                action='download')

    if app_name == const.APP_EKK:
        return make_map_ekk(config, is_live, is_test)
    elif app_name == const.APP_EIS:
        return make_map_avalik(config, is_live, is_test)

def make_map_ekk(config, is_live, is_test):
    """Eksamikeskuse vaate ruuting
    """
    # js tõlkefailide genereerimiseks, mitte päriselt kasutamiseks
    add_handler(config, 'eis_textjs', '/eis_textjs.js', 'eis.handlers.pub.textjs:TextjsController', action='index')
    
    make_map_ekk_ylesanne(config)
    make_map_ekk_testid(config)
    make_map_ekk_regamine(config)
    make_map_ekk_korraldamine(config)
    make_map_ekk_hindamine(config)
    make_map_ekk_sisestamine(config)    
    make_map_ekk_muud(config)
    make_map_ekk_otsingud(config)

    # sooritusklastrite haldamine
    add_resource_handler(config,'klaster', 'klastrid', 
                 'eis.handlers.admin.klastrid:KlastridController', 
                 path_prefix='/admin', name_prefix='admin_')

    add_resource_handler(config,'testsessioon', 
                                'testsessioonid', 
                                'eis.handlers.admin.testsessioonid:TestsessioonidController',
                                path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'leping', 
                         'lepingud', 
                         'eis.handlers.admin.lepingud:LepingudController',
                         path_prefix='/admin', name_prefix='admin_')

    # paroolide muutmine
    add_resource_handler(config,'parool', 'paroolid', 'eis.handlers.admin.paroolid:ParoolidController', 
                 path_prefix='/admin', name_prefix='admin_')

    # EKK töötajad
    add_resource_handler(config,'ametnik', 'ametnikud', 'eis.handlers.admin.ametnikud:AmetnikudController', 
                 path_prefix='/admin', name_prefix='admin_')

    # EKK töötajate rollid
    add_resource_handler(config,'roll', 'rollid', 
                 'eis.handlers.admin.ametnikurollid:AmetnikurollidController',
                 path_prefix='admin/ametnikud/{kasutaja_id}',
                 name_prefix='admin_ametnik_')
    add_resource_handler(config,'ylesanne', 'ylesanded', 
                 'eis.handlers.admin.ametnikuylesanded:AmetnikuylesandedController',
                 path_prefix='admin/ametnikud/{kasutaja_id}',
                 name_prefix='admin_ametnik_')
    add_resource_handler(config,'test', 'testid', 
                 'eis.handlers.admin.ametnikutestid:AmetnikutestidController',
                 path_prefix='admin/ametnikud/{kasutaja_id}',
                 name_prefix='admin_ametnik_')

    # Testide läbiviimisega seotud isikud
    add_resource_handler(config,'kasutaja', 'kasutajad', 'eis.handlers.admin.kasutajad:KasutajadController', 
                 path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'labiviijalaadimine1', 'labiviijalaadimine',
                         'eis.handlers.admin.labiviijalaadimine:LabiviijalaadimineController', 
                         path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'ametnikulaadimine1', 'ametnikulaadimine',
                         'eis.handlers.admin.ametnikulaadimine:AmetnikulaadimineController', 
                         path_prefix='/admin', name_prefix='admin_')    
    add_resource_handler(config,'koolitus', 'koolitused', 'eis.handlers.admin.koolitused:KoolitusedController', 
                 path_prefix='/admin', name_prefix='admin_')    
    add_resource_handler(config,'kaskkiri', 'kaskkirjad', 'eis.handlers.admin.kaskkirjad:KaskkirjadController', 
                 path_prefix='/admin', name_prefix='admin_')    
    add_resource_handler(config,'amet', 'ametid', 'eis.handlers.admin.kasutajaametid:KasutajaametidController', 
                 path_prefix='/admin/kasutajad/{kasutaja_id}',
                 name_prefix='admin_kasutaja_')

    add_resource_handler(config,'veriffid1', 'veriffid',
                         'eis.handlers.admin.veriffid:VeriffidController', 
                         path_prefix='/admin', name_prefix='admin_')
    
    # Kasutaja: läbiviija profiil
    add_sub_handler(config, None, 'profiil',
                    'eis.handlers.admin.profiil:ProfiilController',
                    'admin/kasutajad', 'admin_kasutaja_')
                    
    # Kasutaja: nõusolekud
    add_resource_handler(config,'nousolek', 'nousolekud', 'eis.handlers.admin.nousolekud:NousolekudController', 
                 path_prefix='/admin/kasutajad/{kasutaja_id}',
                 name_prefix='admin_kasutaja_')
    # Kasutaja: läbiviija ajalugu
    add_resource_handler(config,'ajalugu1', 'ajalugu', 'eis.handlers.admin.ajalugu:AjaluguController', 
                 path_prefix='/admin/kasutajad/{kasutaja_id}',
                 name_prefix='admin_kasutaja_')
    # Kasutaja: soorituskohad
    add_resource_handler(config,'koht', 'kohad', 'eis.handlers.admin.kasutajakohad:KasutajakohadController', 
                 path_prefix='/admin/kasutajad/{kasutaja_id}',
                 name_prefix='admin_kasutaja_')

    # Testide sooritajate haldus
    add_resource_handler(config,'eksaminand', 'eksaminandid', 'eis.handlers.admin.eksaminandid:EksaminandidController', 
                 path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'yhendamine', 'yhendamised', 'eis.handlers.admin.yhendamised:YhendamisedController', 
                 path_prefix='/admin/eksaminandid/{yhendatav_id}', name_prefix='admin_eksaminand_')
    add_resource_handler(config,'caeeeltest', 'caeeeltestid',
                         'eis.handlers.admin.caeeeltest:CAEeeltestController', 
                         path_prefix='/admin', name_prefix='admin_')

    add_resource_handler(config,'ehisoppur', 'ehisoppurid', 'eis.handlers.admin.ehisoppurid:EhisoppuridController', 
                 path_prefix='/admin/eksaminandid', name_prefix='admin_eksaminandid_')
    add_resource_handler(config,'ehisopetaja', 'ehisopetajad', 'eis.handlers.admin.ehisopetajad:EhisopetajadController', 
                 path_prefix='/admin/kasutajad', name_prefix='admin_kasutajad_')

    add_resource_handler(config,'kasutajagrupp', 'kasutajagrupid', 'eis.handlers.admin.kasutajagrupid:KasutajagrupidController', 
                 path_prefix='/admin', name_prefix='admin_')

    # lk abiinfo (eksamistatistika)
    add_handler(config, 'admin_abiinfo',
                '/admin/abiinfo',
                'eis.handlers.admin.abiinfo:AbiinfoController',
                action='index',
                request_method='GET')
    add_handler(config, 'admin_create_abiinfo',
                '/admin/abiinfo',
                'eis.handlers.admin.abiinfo:AbiinfoController',
                action='create',
                request_method='POST')                

    # avalehe teated
    add_handler(config, 'admin_olulineinfo',
                '/admin/olulineinfo',
                'eis.handlers.admin.avaleheteated.AvaleheteatedController',
                action='landing')
    add_resource_handler(config, 'avaleheteade', 'avaleheteated',
                         'eis.handlers.admin.avaleheteated:AvaleheteatedController', 
                         path_prefix='/admin',
                         name_prefix='admin_')
    add_handler(config, 'admin_avaleheteatelogid',
                '/admin/avaleheteatelogid',
                'eis.handlers.admin.avaleheteatelogid.AvaleheteatelogidController',
                action='index')
    add_resource_handler(config, 'avalehepilt', 'avalehepildid',
                         'eis.handlers.admin.avalehepildid:AvalehepildidController', 
                         path_prefix='/admin',
                         name_prefix='admin_')

    
    # soorituskohtade logi
    add_resource_handler(config,'logi1', 'logi', 'eis.handlers.admin.kohalogid:KohalogidController', 
                 path_prefix='/admin/kohad', name_prefix='admin_kohad_')

    # Soorituskohtade andmed
    add_resource_handler(config,'koht', 'kohad', 'eis.handlers.admin.kohad:KohadController', 
                 path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'ruum', 'ruumid', 'eis.handlers.admin.ruumid:RuumidController', 
                 path_prefix='/admin/kohad/{koht_id}',
                 name_prefix='admin_koht_')
    add_resource_handler(config,'kasutaja', 'kasutajad', 'eis.handlers.admin.kohakasutajad:KohakasutajadController', 
                 path_prefix='/admin/kohad/{koht_id}',
                 name_prefix='admin_koht_')
    add_resource_handler(config,'oppekava', 'oppekavad', 'eis.handlers.admin.oppekavad:OppekavadController', 
                 path_prefix='/admin/kohad/{koht_id}',
                 name_prefix='admin_koht_')
    
    # isikute otsimine dialoogiaknas soorituskohaga seostamiseks
    add_resource_handler(config,'isik', 'isikud',
                 'eis.handlers.admin.isikud:IsikudController',
                 path_prefix='admin/kohad/{koht_id}',
                 name_prefix='admin_koht_')

    add_resource_handler(config,'logi1', 'logi', 'eis.handlers.admin.logi:LogiController', 
                 path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'logiadapter1', 'logiadapter', 'eis.handlers.admin.logiadapter:LogiadapterController', 
                 path_prefix='/admin', name_prefix='admin_')

    # klassifikaatorid
    add_resource_handler(config,'klassifikaator', 'klassifikaatorid', 
                 'eis.handlers.admin.klassifikaatorid:KlassifikaatoridController', 
                 path_prefix='/admin', name_prefix='admin_', id_re='')
    add_resource_handler(config,'klrida', 'klread', 
                 'eis.handlers.admin.klread:KlreadController', 
                 path_prefix='/admin', name_prefix='admin_', id_re='')
    add_resource_handler(config,'ainevastavus', 'ainevastavused', 
                 'eis.handlers.admin.ainevastavus:AinevastavusController', 
                 path_prefix='/admin/{kl2}', name_prefix='admin_', id_re='')
    
    # klassifikaatorite tõlked
    add_handler(config, 'admin_tklassifikaatorid',
                '/admin/tklassifikaatorid/{lang}',
                'eis.handlers.admin.tklassifikaatorid:TKlassifikaatoridController',
                action='index', request_method='GET')
    add_handler(config, 'admin_show_tklassifikaator',
                '/admin/tklassifikaatorid/{lang}/{id}',
                'eis.handlers.admin.tklassifikaatorid:TKlassifikaatoridController',               
                action='show', request_method='GET')
    add_handler(config, 'admin_update_tklassifikaator',
                '/admin/tklassifikaatorid/{lang}/{id}',
                'eis.handlers.admin.tklassifikaatorid:TKlassifikaatoridController',
                action='update', request_method='POST')        
    add_handler(config, 'admin_edit_tklassifikaator',
                '/admin/tklassifikaatorid/{lang}/{id}/edit',
                'eis.handlers.admin.tklassifikaatorid:TKlassifikaatoridController',
                action='edit', request_method='GET')
    add_handler(config, 'admin_tklread',  '/admin/tklread/{lang}',
                'eis.handlers.admin.tklread:TKlreadController', 
                action='index', request_method='GET')

    # abivahendid
    add_resource_handler(config,'abivahend', 'abivahendid', 
                 'eis.handlers.admin.abivahendid:AbivahendidController', 
                 path_prefix='/admin', name_prefix='admin_')
    
    add_resource_handler(config,'piirkond', 'piirkonnad', 'eis.handlers.admin.piirkonnad:PiirkonnadController', 
                 path_prefix='/admin', name_prefix='admin_')

    # digiallkirjastamise testimine
    add_resource_handler(config,'testallkiri', 'testallkirjad', 
                         'eis.handlers.admin.testallkiri:TestallkiriController',
                         id_re='')
    add_resource_handler(config,'potext_', 'potext', 
                         'eis.handlers.admin.potext:PotextController',
                         id_re='[a-z]{2}')

    add_resource_handler(config,
                         'ylesandekogu', 
                         'ylesandekogud', 
                         'eis.handlers.ekk.ylesandekogud.ylesandekogud:YlesandekogudController')
    add_handler(config, 'ylesandekogu_kogusisu',
                '/ylesandekogu/{kogu_id}/kogusisu',
                'eis.handlers.ekk.ylesandekogud.kogusisu:KogusisuController',
                action='index')    
    add_sub_handler(config, 'ylesandekogu', 'muutjad',
                    'eis.handlers.ekk.ylesandekogud.muutjad:MuutjadController')

    # add_resource_handler(config,'kiirvalik', 
    #              'kiirvalikud', 
    #              'eis.handlers.admin.kiirvalikud:KiirvalikudController',
    #              path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'rveksam', 
                 'rveksamid', 
                 'eis.handlers.admin.rveksamid:RveksamidController',
                 path_prefix='/admin', name_prefix='admin_')


    add_handler(config, 'admin_asukohamaarus',
                '/admin/asukohamaarus',
                'eis.handlers.admin.asukohamaarus:AsukohamaarusController',
                action='index',
                request_method='GET')
    add_handler(config, 'admin_create_asukohamaarus',
                '/admin/asukohamaarus',
                'eis.handlers.admin.asukohamaarus:AsukohamaarusController',
                action='create',
                request_method='POST')                

    # konsultatsioonid
    add_resource_handler(config,'konsultatsioon', 'konsultatsioonid',
                         'eis.handlers.ekk.konsultatsioonid.konsultatsioonid:KonsultatsioonidController')

    # Korraldus
    # konsultatsiooni testimiskord
    add_resource_handler(config,'kord', 
                         'korrad', 
                         'eis.handlers.ekk.konsultatsioonid.korrad:KorradController',
                         path_prefix='konsultatsioonid/{test_id:\d+}',
                         name_prefix='konsultatsioon_')

    # arvutusprotsessi faili laadimine
    add_handler(config, 'protsessifail', '/protsessifail/{id:\d+}.{format}', 'eis.handlers.minu.protsessifail:ProtsessifailController', action='download')
    return map

def make_map_ekk_ylesanne(config):
    """Ülesandepank eksamikeskuse vaates
    """
    add_handler(config, 'ylesanne_image_tran',
                 '/ylesanded/{ylesanne_id:\d+}/{dummypath:.+}/lang/{lang:..}/images{args:[^/]*}/{filename:.+}',
                'eis.handlers.ekk.ylesanded.images:ImagesController',
                action='images')        
    add_handler(config, 'ylesanne_image_p',
                 '/ylesanded/{ylesanne_id:\d+}/{dummypath:.+}/images{args:[^/]*}/{filename:.+}',
                'eis.handlers.ekk.ylesanded.images:ImagesController',
                action='images')        
    add_handler(config, 'ylesanne_image',
                '/ylesanded/{ylesanne_id:\d+}/images{args:[^/]*}/{filename:.+}',
                'eis.handlers.ekk.ylesanded.images:ImagesController',
                action='images')        

    add_resource_handler(config,'hulga', 
                 'hulgi', 
                 'eis.handlers.ekk.ylesanded.hulgi:HulgiController',
                 path_prefix='ylesanded',
                 name_prefix='ylesanded_',
                 id_re='')
    add_resource_handler(config,'isik',
                         'isikud',
                         'eis.handlers.ekk.ylesanded.hulgiisikud:HulgiisikudController',
                         path_prefix='ylesanded/hulgi/{ylesanded_id}',
                         name_prefix='ylesanded_hulgi_',
                         id_re='')
    
    add_resource_handler(config,'sisuplokk', 
                 'sisuplokid', 
                 'eis.handlers.ekk.ylesanded.sisuplokk:SisuplokkController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}/sisu',
                 name_prefix='ylesanne_')
    add_handler(config,
                'ylesanne_sisuplokk_showtool',
                'ylesanded/{ylesanne_id:\d+}/sisu/{id}/showtool-{task_id}/{vahend}',
                'eis.handlers.ekk.ylesanded.sisuplokk:SisuplokkController',
                action='showtool',
                request_method='GET')

    add_resource_handler(config, 'cwchar', 
                         'cwchars', 
                         'eis.handlers.ekk.ylesanded.cwchar:CwcharController',
                         path_prefix='ylesanded/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}',
                         name_prefix='ylesanne_sisuplokk_',
                         id_re='')
    add_resource_handler(config, 'kysimus', 
                         'kysimused', 
                         'eis.handlers.ekk.ylesanded.kysimus:KysimusController',
                         path_prefix='ylesanded/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}',
                         name_prefix='ylesanne_sisuplokk_',
                         id_re='')
    add_resource_handler(config, 'maatriks', 'maatriksid',
                'eis.handlers.ekk.ylesanded.hindamismaatriksid:HindamismaatriksidController', 
                path_prefix='ylesanne/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id:\d+}/kysimus/{kysimus_id}',
                name_prefix='ylesanne_sisuplokk_kysimus_')

    add_resource_handler(config,'sisufail', 
                 'sisufailid', 
                 'eis.handlers.ekk.ylesanded.sisufail:SisufailController',
                 path_prefix='ylesanded',
                 name_prefix='ylesanne_')

    add_resource_handler(config,'taustobjekt', 
                 'taustobjektid', 
                 'eis.handlers.ekk.ylesanded.taustobjekt:TaustobjektController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}',
                 name_prefix='ylesanne_')
    add_resource_handler(config,'piltobjekt', 
                 'piltobjektid', 
                 'eis.handlers.ekk.ylesanded.piltobjekt:PiltobjektController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}',
                 name_prefix='ylesanne_')

    add_resource_handler(config,'yhisfail',
                 'yhisfailid',
                 'eis.handlers.ekk.ylesanded.yhisfailid:YhisfailidController',
                 path_prefix='ylesanded',
                 name_prefix='ylesanne_')

    add_handler(config, 'ylesanded_create_import', '/ylesanded/import',
                       'eis.handlers.ekk.ylesanded.import:ImportController',
                       action='create',
                       request_method='POST')
    add_handler(config, 'ylesanded_import', '/ylesanded/import',
                       'eis.handlers.ekk.ylesanded.import:ImportController',
                       action='index')
    add_handler(config, 'ylesanded_formatted_export',
                       '/ylesanded/{id}/export.{format}',
                       'eis.handlers.ekk.ylesanded.export:ExportController',
                       action='show',  
                       request_method='GET')

    add_handler(config, 'ylesanded_new_ylesandeaine',
                       '/ylesanded/ylesandeaine/new',
                       'eis.handlers.ekk.ylesanded.ylesandeained:YlesandeainedController',
                       action='new',  
                       request_method='GET')

    add_resource_handler(config, 'psisu', 'psisud',
                         'eis.handlers.ekk.ylesanded.psisu:PsisuController',
                         path_prefix='ylesanded',
                         name_prefix='ylesanne_')                         
    add_resource_handler(config,'lisatesti1', 'lisatesti',
                 'eis.handlers.ekk.ylesanded.lisatesti:LisatestiController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}',
                 name_prefix='ylesanne_')
    
    add_resource_handler(config, 'ylesanne', 'ylesanded',
                         'eis.handlers.ekk.ylesanded.ylesanded:YlesandedController') 
    add_sub_handler(config, 'ylesanded', 'sisu',
                    'eis.handlers.ekk.ylesanded.sisu:SisuController')
    add_sub_handler(config, 'ylesanded', 'editorsettings', 
                    'eis.handlers.ekk.ylesanded.editorsettings:EditorsettingsController')
    add_sub_handler(config, 'ylesanded', 'mathsettings', 
                    'eis.handlers.ekk.ylesanded.mathsettings:MathsettingsController')
    add_sub_handler(config, 'ylesanded', 'wmathsettings', 
                    'eis.handlers.ekk.ylesanded.wmathsettings:WmathsettingsController')    

    add_handler(config, 'ylesanded_edit_lahendamine2',
                       '/ylesanded/{id:\d+}/lahendamine/',
                       'eis.handlers.ekk.ylesanded.lahendamine:LahendamineController',
                       action='edit')
    add_sub_handler(config, 'ylesanded', 'lahendamine',
                    'eis.handlers.ekk.ylesanded.lahendamine:LahendamineController')
    add_task_handler(config,
                     'ylesanded_lahendamine_',
                     'eis.handlers.ekk.ylesanded.lahendamine:LahendamineController',
                     editpath='ylesanded/{id:\d+}/lahendamine',
                     updatepath='ylesanded/{id:\d+}/lahendamine/{yv_id:\d+}') # temp

    add_resource_handler(config,'isik',
                         'isikud',
                         'eis.handlers.ekk.ylesanded.isikud:IsikudController',
                         path_prefix='ylesanded/{ylesanne_id:\d+}',
                         name_prefix='ylesanne_koostamine_')

    add_handler(config, 'ylesanded_koostamine_download', '/ylesanded/{id}/koostamine/ylesanne.cdoc',
                      'eis.handlers.ekk.ylesanded.koostamine:KoostamineController',
                      action='download')

    add_sub_handler(config, 'ylesanded', 'koostamine',
                    'eis.handlers.ekk.ylesanded.koostamine:KoostamineController')
    add_resource_handler(config,'tagasiside1', 'tagasiside', 
                         'eis.handlers.ekk.ylesanded.tagasisided:TagasisidedController',
                         path_prefix='ylesanded/{ylesanne_id:\d+}',
                         name_prefix='ylesanded_')
    add_resource_handler(config,'versioon', 'versioonid', 
                         'eis.handlers.ekk.ylesanded.versioonid:VersioonidController',
                         path_prefix='ylesanded/{ylesanne_id:\d+}',
                         name_prefix='ylesanded_')
    add_sub_handler(config, 'ylesanded', 'muutjad',
                    'eis.handlers.ekk.ylesanded.muutjad:MuutjadController')
    add_resource_handler(config,'test', 'testid', 
                 'eis.handlers.ekk.ylesanded.testid:TestidController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}',
                 name_prefix='ylesanded_')
    add_sub_handler(config, 'ylesanded', 'juhised',
                    'eis.handlers.ekk.ylesanded.juhised:JuhisedController')
    add_handler(config, 'ylesanded_fail', '/ylesanded/{id:\d+}/fail/{ylesandefail_id}.{format}',
                       'eis.handlers.ekk.ylesanded.juhised:JuhisedController',
                       action='download')        

def make_map_ekk_testid(config):
    #################################### Testid

    add_resource_handler(config,'test', 'testid',
                         'eis.handlers.ekk.testid.testid:TestidController')
    add_resource_handler(config,'hulga', 
                 'hulgi', 
                 'eis.handlers.ekk.testid.hulgi:HulgiController',
                 path_prefix='testid',
                 name_prefix='testid_',
                 id_re='')
    add_resource_handler(config,'isik',
                         'isikud',
                         'eis.handlers.ekk.testid.hulgiisikud:HulgiisikudController',
                         path_prefix='testid/hulgi/{testid_id}',
                         name_prefix='testid_hulgi_',
                         id_re='')

    add_resource_handler(config,'struktuur1', 
                         'struktuur', 
                         'eis.handlers.ekk.testid.struktuur:StruktuurController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
    add_resource_handler(config,'testiosa', 
                         'testiosad', 
                         'eis.handlers.ekk.testid.testiosad:TestiosadController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
    add_resource_handler(config,'viis1','viis', 
                         'eis.handlers.ekk.testid.tagasisideviis:TagasisideviisController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id}/tagasiside',
                         name_prefix='test_tagasiside_')    
    add_resource_handler(config,'tunnus','tunnused', 
                         'eis.handlers.ekk.testid.tagasisidetunnused:TagasisidetunnusedController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id}/tagasiside',
                         name_prefix='test_tagasiside_')
    add_resource_handler(config,'atgrupp','atgrupid', 
                         'eis.handlers.ekk.testid.tagasisideatgrupid:TagasisideatgrupidController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id}/tagasiside',
                         name_prefix='test_tagasiside_')
    add_resource_handler(config,'nsgrupp','nsgrupid', 
                         'eis.handlers.ekk.testid.tagasisidensgrupid:TagasisidensgrupidController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id}/tagasiside',
                         name_prefix='test_tagasiside_')
    add_resource_handler(config,'ylgrupp','ylgrupid', 
                         'eis.handlers.ekk.testid.tagasisideylgrupid:TagasisideylgrupidController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id}/tagasiside',
                         name_prefix='test_tagasiside_')
    add_resource_handler(config,'vorm','vormid', 
                         'eis.handlers.ekk.testid.tagasisidevormid:TagasisidevormidController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id}/tagasiside',
                         name_prefix='test_tagasiside_', id_re='F?\d+')    
    # tagasiside pildi kuvamine koostajale, kui URLis on testimages/filename
    add_handler(config, 'test_tagasiside_testimages', 'testid/{test_id:\d+}/{dummypath:.*}/testimages/{filename}',
                       'eis.handlers.avalik.lahendamine.images:ImagesController', 
                       action='testimages',
                       request_method='GET')

    add_resource_handler(config,'fail','failid',
                         'eis.handlers.ekk.testid.tagasisidefailid:TagasisidefailidController',
                         path_prefix='testid/{test_id:\d+}/tagasiside',
                         name_prefix='test_tagasiside_')

    add_resource_handler(config,'fbvar','fbvars', 
                         'eis.handlers.ekk.testid.tagasisidevar:TagasisidevarController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id:\d+}/tagasiside',
                         name_prefix='test_tagasiside_', id_re='F?\d+')
    add_handler(config, 'test_tagasiside_new_diagramm',
                'testid/{test_id:\d+}/{testiosa_id:\d+}/tagasiside/diagramm/new',
                'eis.handlers.ekk.testid.tagasisidediagramm:TagasisidediagrammController',
                action='new',
                request_method='GET')
    add_handler(config, 'test_tagasiside_edit_diagramm',
                'testid/{test_id:\d+}/{testiosa_id:\d+}/tagasiside/diagramm/edit',
                'eis.handlers.ekk.testid.tagasisidediagramm:TagasisidediagrammController',
                action='edit',
                request_method='POST')
    add_handler(config, 'test_tagasiside_create_diagramm',
                'testid/{test_id:\d+}/{testiosa_id:\d+}/tagasiside/diagramm/create',
                'eis.handlers.ekk.testid.tagasisidediagramm:TagasisidediagrammController',
                action='create',
                request_method='POST')
    add_handler(config, 'test_tagasiside_diagramm',
                'testid/{test_id:\d+}/{testiosa_id:\d+}/tagasiside/vormid{dummy:.*}/diagramm/{fn}.png',
                'eis.handlers.ekk.testid.tagasisidediagramm:TagasisidediagrammController',
                action='show',
                request_method='GET')

    # tagasiside testimine
    add_handler(config,
                'test_tagasiside_eelvaade_diagrammtunnus',
                '/testid/{test_id:\d+}/{testiosa_id}/tagasiside/eelvaade/tunnused.png',
                'eis.handlers.ekk.testid.diagrammtunnus:DiagrammtunnusController',
                action='index')
    add_handler(config,
                'test_tagasiside_eelvaade_diagrammhinnang',                
                '/testid/{test_id:\d+}/{testiosa_id}/tagasiside/eelvaade/hinnang.png',
                'eis.handlers.ekk.testid.diagrammhinnang:DiagrammhinnangController',
                action='index')

    add_resource_handler(config,'eelvaade1','eelvaade', 
                         'eis.handlers.ekk.testid.tagasisideeelvaade:TagasisideeelvaadeController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id}/tagasiside',
                         name_prefix='test_tagasiside_', id_re='F?\d+')    

    add_resource_handler(config,'alatest', 
                         'alatestid', 
                         'eis.handlers.ekk.testid.alatestid:AlatestidController',
                         path_prefix='testid/{test_id:\d+}/testiosad/{testiosa_id}',
                         name_prefix='test_testiosa_')
    add_resource_handler(config,'testiplokk', 
                         'testiplokid', 
                         'eis.handlers.ekk.testid.testiplokid:TestiplokidController',
                         path_prefix='testid/{test_id:\d+}/testiosad/{testiosa_id}',
                         name_prefix='test_testiosa_')
    add_resource_handler(config,'testiylesanne', 
                         'testiylesanded', 
                         'eis.handlers.ekk.testid.testiylesanded:TestiylesandedController',
                         path_prefix='testid/{test_id:\d+}/testiosad/{testiosa_id}',
                         name_prefix='test_testiosa_')
    add_resource_handler(config,'otsiylesanne', 
                         'otsiylesanded', 
                         'eis.handlers.ekk.testid.struktuurotsiylesanded:StruktuurOtsiylesandedController',
                         path_prefix='testid/{test_id:\d+}/testiosad/{testiosa_id}',
                         name_prefix='test_testiosa_')

    add_resource_handler(config,'ylesandegrupp', 
                         'ylesandegrupid', 
                         'eis.handlers.ekk.testid.ylesandegrupid:YlesandegrupidController',
                         path_prefix='testid/{test_id:\d+}/testiosad/{testiosa_id}',
                         name_prefix='test_testiosa_')
    
    # Ülesanded
    add_resource_handler(config,'valitudylesanne', 
                         'valitudylesanded', 
                         'eis.handlers.ekk.testid.valitudylesanded:ValitudylesandedController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
    add_resource_handler(config,'komplektivalik', 
                         'komplektivalikud', 
                         'eis.handlers.ekk.testid.komplektivalikud:KomplektivalikudController',
                         path_prefix='testid/{test_id:\d+}/testiosad/{testiosa_id}',
                         name_prefix='test_testiosa_')
    add_resource_handler(config,'komplekt', 
                         'komplektid', 
                         'eis.handlers.ekk.testid.komplektid:KomplektidController',
                         path_prefix='testid/{test_id:\d+}/testiosad/{testiosa_id}',
                         name_prefix='test_testiosa_')
    add_resource_handler(config,'valimitu1', 
                         'valimitu', 
                         'eis.handlers.ekk.testid.valimitu:ValimituController',
                         path_prefix='testid/{test_id:\d+}/testiosad/{testiosa_id}/komplekt/{komplekt_id}',
                         name_prefix='test_komplekt_')
    add_resource_handler(config,'fail', 
                         'failid', 
                         'eis.handlers.ekk.testid.failid:FailidController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
    add_resource_handler(config,'erialatest', 
                         'erialatestid', 
                         'eis.handlers.ekk.testid.erialatestid:ErialatestidController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
                 #path_prefix='testid/{test_id}/komplekt/{komplekt_id}',
                 #name_prefix='test_komplekt_')
    # Erivajadustega soorituste otsing erivajaduste vormil
    add_resource_handler(config,'erisooritus', 
                         'erisooritused', 
                         'eis.handlers.ekk.testid.erisooritused:ErisooritusedController',
                         path_prefix='testid/{test_id:\d+}/komplekt/{komplekt_id}',
                         name_prefix='test_komplekt_')
    # Soorituse erivajadused
    add_resource_handler(config,'erivajadus', 'erivajadused',
                 'eis.handlers.ekk.testid.erivajadused:ErivajadusedController',
                 path_prefix='testid/{test_id:\d+}/erialatestid/{komplekt_id}',
                 name_prefix='test_komplekt_')

    # valitudylesandesse ylesande valimine
    add_resource_handler(config,'otsiylesanne', 
                         'otsiylesanded', 
                         'eis.handlers.ekk.testid.komplektotsiylesanded:KomplektOtsiylesandedController',
                         path_prefix='testid/{test_id:\d+}/komplekt/{komplekt_id}/testiylesanne/{testiylesanne_id}',
                         name_prefix='test_komplekt_')
    add_handler(config, 'test_komplekt_export',
                 '/testid/{test_id:\d+}/komplektid/{komplekt_id}/export.{format}',
                 'eis.handlers.ekk.testid.export:ExportController',
                 action='show',  
                 request_method='GET')

    # testi eelvaade
    add_resource_handler(config, 'eelvaade', 'eelvaated',
                         'eis.handlers.ekk.testid.eelvaade:EelvaadeController',
                         path_prefix='testid/{test_id:\d+}/{testiosa_id:\d+}-{e_komplekt_id:[L\d]*}-{alatest_id:\d*}',
                         path_id='testid/{test_id:\d+}/{testiosa_id:\d+}-{e_komplekt_id:[L\d]*}-{alatest_id:\d*}/eelvaade/{id:-?\d+}',                         
                         name_prefix='test_')
                         
    add_task_handler(config,
                     'test_eelvaade_',
                     'eis.handlers.ekk.testid.eelvaade:EelvaadeController',
                     'testid/{test_id:\d+}/{testiosa_id:\d+}-{e_komplekt_id:[L\d]*}-{alatest_id:\d*}/eelvaade/{id:-?\d+}')

    # Korraldus
    add_resource_handler(config,
                         'kord', 
                         'korrad', 
                         'eis.handlers.ekk.testid.kutsekorrad:KutsekorradController',
                         path_prefix='testid/{test_id:\d+}/kutse',
                         name_prefix='test_kutse_')
    add_resource_handler(config,'kord', 
                         'korrad', 
                         'eis.handlers.ekk.testid.korrad:KorradController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
    add_resource_handler(config,'toimumisaeg', 
                         'toimumisajad', 
                         'eis.handlers.ekk.testid.toimumisajad:ToimumisajadController',
                         path_prefix='testid/{test_id:\d+}/korrad/{kord_id}',
                         name_prefix='test_kord_')
    add_resource_handler(config,'kogum', 
                         'kogumid', 
                         'eis.handlers.ekk.testid.kogumid:KogumidController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
    add_resource_handler(config,'hindamiskriteerium', 
                         'hindamiskriteeriumid', 
                         'eis.handlers.ekk.testid.hindamiskriteeriumid:HindamiskriteeriumidController',
                         path_prefix='testid/{test_id:\d+}/hk/{hindamiskogum_id}',
                         name_prefix='test_')
    add_resource_handler(config,'hindamiskogum', 
                         'hindamiskogumid', 
                         'eis.handlers.ekk.testid.hindamiskogumid:HindamiskogumidController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
    add_resource_handler(config,'sisestuskogum', 
                         'sisestuskogumid', 
                         'eis.handlers.ekk.testid.sisestuskogumid:SisestuskogumidController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')

    add_sub_handler(config, 'testid', 'koostamine',
                    'eis.handlers.ekk.testid.koostamine:KoostamineController',
                    'testid', 'test_')
    add_resource_handler(config,'isik',
                         'isikud',
                         'eis.handlers.ekk.testid.isikud:IsikudController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_koostamine_')
    add_handler(config, 'testid_koostamine_download', '/testid/{id}/koostamine/test.cdoc',
                      'eis.handlers.ekk.testid.koostamine:KoostamineController',
                      action='download')

    add_resource_handler(config,'eeltest', 
                         'eeltestid', 
                         'eis.handlers.ekk.testid.eeltestid:EeltestidController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')
    add_resource_handler(config,'korraldaja', 
                         'korraldajad', 
                         'eis.handlers.ekk.testid.korraldajad:KorraldajadController',
                         path_prefix='testid/{test_id:\d+}',
                         name_prefix='test_')

    # testimiskorrata testi statistika
    add_resource_handler(config,'analyys1', 'analyys', 
                 'eis.handlers.ekk.testid.analyys:AnalyysController',
                 path_prefix='testid/{test_id:\d+}',                 
                 name_prefix='test_')        
    add_handler(config, 
                 'test_analyys_image_p',
                 '/testid/{test_id:\d+}/analyys/{vy_id}/{path:.*}images{args:[^/]*}/{filename:.+}',
                 'eis.handlers.ekk.testid.images:ImagesController',
                 action='images')            

    add_resource_handler(config, 'maatriks', 'maatriksid',
                'eis.handlers.ekk.testid.analyysmaatriksid:AnalyysmaatriksidController', 
                path_prefix='testid/{test_id}/analyys/vastused/kysimus/{kysimus_id}',
                name_prefix='test_analyys_vastused_kysimus_')

    add_sub_handler(config, 'testid', 'muutjad',
                    'eis.handlers.ekk.testid.muutjad:MuutjadController',
                    'testid', 'test_')

def make_map_ekk_regamine(config):
    #################################
    
    # Registreerimine - otsing ja registreeringu vaatamine/muutmine
    add_resource_handler(config,'regamine', 'regamised', 
                 'eis.handlers.ekk.regamine.sooritajad:SooritajadController')

    # tugiisiku määramine registreeringu vormilt
    add_resource_handler(config, 'tugiisik', 'tugiisikud',
                         'eis.handlers.ekk.regamine.tugiisik:TugiisikController',
                         path_prefix='regamine/{sooritus_id}',
                         name_prefix='regamine_')

    # Soorituse erivajadused
    add_resource_handler(config,'erivajadus', 'erivajadused',
                 'eis.handlers.ekk.regamine.erivajadused:ErivajadusedController',
                 path_prefix='regamine',
                 name_prefix='regamine_')
    # Meeldetuletuskirjade saatmine
    add_resource_handler(config,'meeldetuletus', 'meeldetuletused',
                 'eis.handlers.ekk.regamine.meeldetuletus:MeeldetuletusController',
                 path_prefix='regamine',
                 name_prefix='regamine_')

    # Registreerimisavalduse sisestamine
    add_handler(config, 'regamine_new_avaldus', 
                '/regamine/avaldus',
                'eis.handlers.ekk.regamine.avaldus.isikuvalik:IsikuvalikController',
                action='new',
                 request_method='GET')
    add_handler(config, 'regamine_create_avaldus', 
                 '/regamine/avaldus',
                 'eis.handlers.ekk.regamine.avaldus.isikuvalik:IsikuvalikController',
                 action='create',
                 request_method='POST')

    add_handler(config, 'regamine_edit_avaldus', 
                 '/regamine/avaldus/{id}',
                 'eis.handlers.ekk.regamine.avaldus.isikuvalik:IsikuvalikController',
                 action='edit',
                 request_method='GET')
    add_handler(config, 'regamine_update_avaldus', 
                 '/regamine/avaldus/{id}',
                 'eis.handlers.ekk.regamine.avaldus.isikuvalik:IsikuvalikController',
                 action='update',
                 request_method='POST') # PUT

    add_handler(config, 'regamine_avaldus_edit_isikuandmed', 
                 '/regamine/avaldus/{id}/isikuandmed',
                 'eis.handlers.ekk.regamine.avaldus.isikuandmed:IsikuandmedController',
                 action='edit',
                 request_method='GET')
    add_handler(config, 'regamine_avaldus_isikuandmed', 
                 '/regamine/avaldus/{id}/isikuandmed',
                 'eis.handlers.ekk.regamine.avaldus.isikuandmed:IsikuandmedController',
                 action='update',
                 request_method='POST') # PUT
    
    # valitud testide vaatamine
    add_handler(config, 'regamine_avaldus_testid', 
                 '/regamine/avaldus/{id}/testid',
                 'eis.handlers.ekk.regamine.avaldus.testid:TestidController',
                 action='index',
                 request_method='GET')
    # dialoogiaknas leitud testide lisamine nimekirja
    add_handler(config, 'regamine_avaldus_lisatestid', 
                '/regamine/avaldus/{id}/lisatestid',
                'eis.handlers.ekk.regamine.avaldus.testid:TestidController',
                action='create',
                 request_method='POST')

    # dialoogiaknas testi keele ja piirkonna muutmine
    add_handler(config, 'regamine_avaldus_edit_test', 
                       '/regamine/avaldus/{id}/testid/{sooritaja_id}',
                       'eis.handlers.ekk.regamine.avaldus.testid:TestidController',
                       action='edit',
                       request_method='GET') 
    add_handler(config, 'regamine_avaldus_update_test', 
                       '/regamine/avaldus/{id}/testid/{sooritaja_id}',
                       'eis.handlers.ekk.regamine.avaldus.testid:TestidController',
                       action='update',
                       request_method='POST') # PUT

    # testi eemaldamine
    add_handler(config, 'regamine_avaldus_delete_test', 
                '/regamine/avaldus/{id}/testid/{sooritaja_id}/delete',
                'eis.handlers.ekk.regamine.avaldus.testid:TestidController',
                 action='delete',
                 request_method='POST') # DELETE

    # avaldusel tugiisiku muutmine
    add_resource_handler(config, 'tugiisik', 'tugiisikud',
                         'eis.handlers.ekk.regamine.avaldus.tugiisik:TugiisikController',
                         path_prefix='regamine/avaldus/{kasutaja_id}/testid/{sooritaja_id}',
                         name_prefix='regamine_avaldus_')
    
    # testide otsimine dialoogiaknas
    add_resource_handler(config,'otsitest', 'otsitestid',
                 'eis.handlers.ekk.regamine.avaldus.otsitestid:OtsitestidController',
                 path_prefix='regamine/avaldus/{kasutaja_id}',
                 name_prefix='regamine_avaldus_')

    add_handler(config, 'regamine_avaldus_edit_kinnitamine', 
                '/regamine/avaldus/{id}/kinnitamine',
                'eis.handlers.ekk.regamine.avaldus.kinnitamine:KinnitamineController',
                action='edit',
                 request_method='GET')
    add_handler(config, 'regamine_avaldus_kinnitamine', 
                 '/regamine/avaldus/{id}/kinnitamine',
                 'eis.handlers.ekk.regamine.avaldus.kinnitamine:KinnitamineController',
                 action='update',
                 request_method='POST') # PUT
    
# GET regamine/avaldus
# GET regamine/avaldus/1499/isikuvalik
# PUT regamine/avaldus/1499/isikuvalik
# GET regamine/avaldus/1499/isikuandmed
# PUT regamine/avaldus/1499/isikuandmed
# GET regamine/avaldus/1499/testid
# PUT regamine/avaldus/1499/testid
# GET regamine/avaldus/1499/kinnitamine
# PUT regamine/avaldus/1499/kinnitamine

    # Registreerimisavalduse sisestamine sooritajate failist
    # testimiskorra valik
    add_resource_handler(config,'testivalik1', 'testivalik',
                 'eis.handlers.ekk.regamine.nimistu.testivalik:TestivalikController',
                 path_prefix='regamine/nimistu',
                 name_prefix='regamine_nimistu_')
    ## valitud testi yksikasjade kuvamine
    add_handler(config, 'regamine_nimistu_edit_yksikasjad', 
                '/regamine/nimistu/{korrad_id}/yksikasjad',
                'eis.handlers.ekk.regamine.nimistu.yksikasjad:YksikasjadController',
                action='edit',
                 request_method='GET')
    # sooritajate faili laadimise lehekülg
    add_handler(config, 'regamine_nimistu_edit_sooritajad', 
                '/regamine/nimistu/{korrad_id}/sooritajad',
                'eis.handlers.ekk.regamine.nimistu.sooritajad:SooritajadController',
                action='edit',
                 request_method='GET')
    add_handler(config, 'regamine_nimistu_create_sooritajad', 
                '/regamine/nimistu/{korrad_id}/sooritajad',
                'eis.handlers.ekk.regamine.nimistu.sooritajad:SooritajadController',
                action='create',
                 request_method='POST')
    # sooritajate faili laadimise lehekülg
    add_handler(config, 'regamine_nimistu_sooritajad_protsessid', 
                '/regamine/nimistu/{korrad_id}/sooritajad/protsessid',
                'eis.handlers.ekk.regamine.nimistu.sooritajad:SooritajadController',
                action='index',
                request_method='GET')
    ## keele valik
    add_handler(config, 'regamine_nimistu_create_lisavalikud', 
                '/regamine/nimistu/{korrad_id}/lisavalikud/{protsess_id:\d+}',
                'eis.handlers.ekk.regamine.nimistu.lisavalikud:LisavalikudController',
                action='create',
                 request_method='POST')
    add_handler(config, 'regamine_nimistu_edit_lisavalikud', 
                 '/regamine/nimistu/{korrad_id}/lisavalikud/{protsess_id:\d+}',
                 'eis.handlers.ekk.regamine.nimistu.lisavalikud:LisavalikudController',
                 action='edit',
                 request_method='GET')

# GET regamine/nimistu (new)
# GET regamine/nimistu/{kord_id}/testivalik (tagasi)
# GET regamine/nimistu/{kord_id}/lisavalikud/{protsess_id} (kuva)
# GET regamine/nimistu/{kord_id}/sooritajad?lang={lang} (kuva)
# POST regamine/nimistu/{kord_id}/sooritajad (create, salvesta fail)

def make_map_ekk_korraldamine(config):
    ################################ korraldamine
    add_resource_handler(config,'korraldamine', 
                 'korraldamised', 
                 'eis.handlers.ekk.korraldamine.toimumisajad:ToimumisajadController')
    add_resource_handler(config,'soorituskoht', 'soorituskohad', 
                 'eis.handlers.ekk.korraldamine.soorituskohad:SoorituskohadController',
                 path_prefix='korraldamine/{toimumisaeg_id}',                 
                 name_prefix='korraldamine_')

    # valimi laadimine
    add_resource_handler(config,'valim1','valim', 
                 'eis.handlers.ekk.korraldamine.valim:ValimController',
                 path_prefix='korraldamine/{toimumisaeg_id}',
                 name_prefix='korraldamine_')

    # yhe või mitme soorituskoha kõigi sooritajate ümbersuunamine dialoogiaknas
    add_resource_handler(config,'otsikoht', 'otsikohad',
                 'eis.handlers.ekk.korraldamine.otsikohad:OtsikohadController',
                 path_prefix='korraldamine/{toimumisaeg_id}',
                 name_prefix='korraldamine_')

    # soorituskoha sooritajate loetelu
    add_resource_handler(config,'sooritaja','sooritajad', 
                 'eis.handlers.ekk.korraldamine.koht.sooritajad:SooritajadController',
                 path_prefix='korraldamine/{toimumisaeg_id}/koht/{testikoht_id}',
                 name_prefix='korraldamine_koht_')
    # sooritajate otsimine dialoogiaknas
    add_resource_handler(config,'otsisooritaja', 'otsisooritajad',
                 'eis.handlers.ekk.korraldamine.koht.otsisooritajad:OtsisooritajadController',
                 path_prefix='korraldamine/{toimumisaeg_id}/koht/{testikoht_id}',
                 name_prefix='korraldamine_koht_')
    # testiruumi protokollide haldamine
    add_resource_handler(config,'protokollruum', 'protokollruumid',
                 'eis.handlers.ekk.korraldamine.koht.protokollruum:ProtokollruumController',
                 path_prefix='korraldamine/{toimumisaeg_id}/koht/{testikoht_id}/pakett/{pakett_id}',
                 name_prefix='korraldamine_koht_')
    # sooritajate ümbersuunamine dialoogiaknas
    # index POST, et kannataks väga suurt hulka parameetreid edastada
    add_handler(config, 'korraldamine_koht_otsikohad',
                'korraldamine/{toimumisaeg_id}/koht/{testikoht_id}/otsikohad',
                'eis.handlers.ekk.korraldamine.koht.otsikohad:OtsikohadController',
                action='index',
                request_method='POST')

    # soorituskoha läbiviijate loetelu
    add_resource_handler(config,'labiviija', 'labiviijad', 
                 'eis.handlers.ekk.korraldamine.koht.labiviijad:LabiviijadController',
                 path_prefix='korraldamine/{toimumisaeg_id}/koht/{testikoht_id}',
                 name_prefix='korraldamine_koht_')
    # läbiviijate otsimine dialoogiaknas
    add_resource_handler(config,'otsilabiviija', 'otsilabiviijad',
                 'eis.handlers.ekk.korraldamine.koht.otsilabiviijad:OtsilabiviijadController',
                 path_prefix='korraldamine/{toimumisaeg_id}/koht/{testikoht_id}',
                 name_prefix='korraldamine_koht_')
    # läbiviijate ümbersuunamine dialoogiaknas
    add_resource_handler(config,'otsilabikoht', 'otsilabikohad',
                 'eis.handlers.ekk.korraldamine.koht.otsilabikohad:OtsilabikohadController',
                 path_prefix='korraldamine/{toimumisaeg_id}/koht/{testikoht_id}',
                 name_prefix='korraldamine_koht_')

    add_resource_handler(config,'logistika1','logistika', 
                 'eis.handlers.ekk.korraldamine.koht.logistika:LogistikaController',
                 path_prefix='korraldamine/{toimumisaeg_id}/koht/{testikoht_id}',
                 name_prefix='korraldamine_koht_')
    add_resource_handler(config,'yldanne','yldandmed', 
                 'eis.handlers.ekk.korraldamine.koht.yldandmed:YldandmedController',
                 path_prefix='korraldamine/{toimumisaeg_id}/koht/{testikoht_id}',
                 name_prefix='korraldamine_koht_')
    add_resource_handler(config,'labiviija', 'labiviijad', 
                 'eis.handlers.ekk.korraldamine.labiviijad:LabiviijadController',
                 path_prefix='korraldamine/{toimumisaeg_id}',                 
                 name_prefix='korraldamine_')
    add_resource_handler(config,'valjastus1', 'valjastus', 
                 'eis.handlers.ekk.korraldamine.valjastus:ValjastusController',
                 path_prefix='korraldamine/{toimumisaeg_id}',                 
                 name_prefix='korraldamine_')
    add_handler(config,
                'korraldamine_valjastus_valjastusymbrikud',
                '/korraldamine/{toimumisaeg_id}/valjastus/valjastusymbrikud',
                'eis.handlers.ekk.korraldamine.valjastus:ValjastusController',
                action='valjastusymbrikud',
                request_method='GET')
    add_handler(config,
                'korraldamine_valjastus_tagastusymbrikud',
                '/korraldamine/{toimumisaeg_id}/valjastus/tagastusymbrikud',
                'eis.handlers.ekk.korraldamine.valjastus:ValjastusController',
                action='tagastusymbrikud',
                request_method='GET')
    add_handler(config,
                'korraldamine_valjastus_protokollid',
                '/korraldamine/{toimumisaeg_id}/valjastus/protokollid',
                'eis.handlers.ekk.korraldamine.valjastus:ValjastusController',
                action='protokollid',
                request_method='GET')
    add_handler(config,
                'korraldamine_valjastus_turvakotikleebised',
                '/korraldamine/{toimumisaeg_id}/valjastus/turvakotikleebised',
                'eis.handlers.ekk.korraldamine.valjastus:ValjastusController',
                action='turvakotikleebised',
                request_method='GET')
    add_handler(config,
                'korraldamine_valjastus_turvakotiaktid',
                '/korraldamine/{toimumisaeg_id}/valjastus/turvakotiaktid',
                'eis.handlers.ekk.korraldamine.valjastus:ValjastusController',
                action='turvakotiaktid',
                request_method='GET')
    add_handler(config,
                'korraldamine_valjastus_lisatingimused',
                '/korraldamine/{toimumisaeg_id}/valjastus/lisatingimused',
                'eis.handlers.ekk.korraldamine.valjastus:ValjastusController',
                action='lisatingimused',
                request_method='GET')

    add_resource_handler(config,'tagastuskott','tagastuskotid', 
                 'eis.handlers.ekk.korraldamine.tagastuskotid:TagastuskotidController',
                 path_prefix='korraldamine/{toimumisaeg_id}',                 
                 name_prefix='korraldamine_')
    add_resource_handler(config,'tagastusymbrik','tagastusymbrikud', 
                 'eis.handlers.ekk.korraldamine.tagastusymbrikud:TagastusymbrikudController',
                 path_prefix='korraldamine/{toimumisaeg_id}',                 
                 name_prefix='korraldamine_')
    add_resource_handler(config,'tagastustoimumine','tagastustoimumised', 
                 'eis.handlers.ekk.korraldamine.tagastustoimumised:TagastustoimumisedController',
                 path_prefix='korraldamine/{toimumisaeg_id}',                 
                 name_prefix='korraldamine_')

    add_resource_handler(config, 'eksamilogi1','eksamilogi',
                 'eis.handlers.ekk.korraldamine.eksamilogi:EksamilogiController',
                 path_prefix='korraldamine/{toimumisaeg_id}',                 
                 name_prefix='korraldamine_')
    add_handler(config, 'korraldamine_markused', 
                 '/korraldamine/{toimumisaeg_id}/markused',
                 'eis.handlers.ekk.korraldamine.markused:MarkusedController',
                 action='index',
                 request_method='GET')
    add_handler(config, 'korraldamine_aadressid', 
                 '/korraldamine/{toimumisaeg_id}/aadressid',
                 'eis.handlers.ekk.korraldamine.aadressid:AadressidController',
                 action='index',
                 request_method='GET')
    add_handler(config, 'korraldamine_kandideerimine', 
                 '/korraldamine/{toimumisaeg_id}/kandideerimine',
                 'eis.handlers.ekk.korraldamine.kandideerimine:KandideerimineController',
                 action='index',
                 request_method='GET')
    add_handler(config, 'korraldamine_eritingimused', 
                 '/korraldamine/{toimumisaeg_id}/eritingimused',
                 'eis.handlers.ekk.korraldamine.eritingimused:EritingimusedController',
                 action='index',
                 request_method='GET')
    add_handler(config, 'korraldamine_helifailid', 
                 '/korraldamine/{toimumisaeg_id}/helifailid',
                 'eis.handlers.ekk.korraldamine.helifailid:HelifailidController',
                 action='index',
                 request_method='GET')

    # konsultatsiooni korral sooritajate konsultatsiooninimekirjad
    add_resource_handler(config,'konsultatsiooninimekiri', 'konsultatsiooninimekirjad', 
                 'eis.handlers.ekk.korraldamine.konsultatsiooninimekirjad:KonsultatsiooninimekirjadController',
                 path_prefix='korraldamine/{toimumisaeg_id}',                 
                 name_prefix='korraldamine_')


def make_map_ekk_hindamine(config):
    # hindamine
    add_resource_handler(config,'hindamine', 
                 'hindamised', 
                 'eis.handlers.ekk.hindamine.toimumisajad:ToimumisajadController')
    add_resource_handler(config,'hindaja', 'hindajad', 
                 'eis.handlers.ekk.hindamine.hindajad:HindajadController',
                 path_prefix='hindamine/{toimumisaeg_id}',                 
                 name_prefix='hindamine_')
    add_resource_handler(config,'sooritus', 'sooritused', 
                 'eis.handlers.ekk.hindamine.sooritused:SooritusedController',
                 path_prefix='hindamine/{toimumisaeg_id}/hindaja/{hindaja_id}',                 
                 name_prefix='hindamine_')
    add_resource_handler(config,'kolmandaks', 'kolmandaks2', 
                 'eis.handlers.ekk.hindamine.kolmandaks:KolmandaksController',
                 path_prefix='hindamine/{toimumisaeg_id}',                 
                 name_prefix='hindamine_')
    add_resource_handler(config,'hindaja3', 'hindajad3', 
                 'eis.handlers.ekk.hindamine.hindajad3:Hindajad3Controller',
                 path_prefix='hindamine/{toimumisaeg_id}',                 
                 name_prefix='hindamine_')
    add_resource_handler(config,'suunamine', 'suunamised', 
                 'eis.handlers.ekk.hindamine.suunamised:SuunamisedController',
                 path_prefix='hindamine/{toimumisaeg_id}',                 
                 name_prefix='hindamine_')

    add_resource_handler(config,'vastaja', 'vastajad',
                 'eis.handlers.ekk.hindamine.hindajavaade_vastajad:HindajavaadeVastajadController',
                 path_prefix='hindamine/{toimumisaeg_id}/hindajavaade/{hindaja_id}',
                 name_prefix='hindamine_hindajavaade_')
    add_resource_handler(config,'hkhindamine', 'hkhindamised',
                 'eis.handlers.ekk.hindamine.hindajavaade_hkhindamine:HindajavaadeHkhindamineController',
                 path_prefix='hindamine/{toimumisaeg_id}/hindajavaade/{hindaja_id}/{sooritus_id}',
                 name_prefix='hindamine_hindajavaade_')
    add_task_handler(config,
                     'hindamine_hindajavaade_',
                     'eis.handlers.ekk.hindamine.hindajavaade_hkhindamine:HindajavaadeHkhindamineController',
                     path='hindamine/{toimumisaeg_id}/hindajavaade/{hindaja_id}/{sooritus_id:\d+}')

    add_resource_handler(config,'shindamine', 'shindamised',
                          'eis.handlers.ekk.hindamine.hindajavaade_shindamised:HindajavaadeShindamisedController',
                          path_prefix='hindamine/{toimumisaeg_id}/hindajavaade/{hindaja_id}',
                          name_prefix='hindamine_hindajavaade_')
    
    add_resource_handler(config,'lahendamine', 'lahendamised',
                 'eis.handlers.ekk.hindamine.hindajavaade_lahendamine:HindajavaadeLahendamineController',
                 path_prefix='hindamine/{toimumisaeg_id:\d+}/{vy_id}',
                 name_prefix='hindamine_hindajavaade_')
    add_task_handler(config,
                     'hindamine_hindajavaade_lahendamine_',
                     'eis.handlers.ekk.hindamine.hindajavaade_lahendamine:HindajavaadeLahendamineController',
                     editpath='hindamine/{toimumisaeg_id:\d+}/{vy_id:\d+}/lahendamine/{id:\d+}',
                     updatepath='hindamine/{toimumisaeg_id:\d+}/{vy_id:\d+}/lahendamine/{id:\d+}/{yv_id:\d+}') # temp
    
    # hindamisjuhendid
    add_resource_handler(config, 'juhend', 'juhendid',
                 'eis.handlers.ekk.hindamine.hindajavaade_juhend:HindajavaadeJuhendController',
                 path_prefix='hindamine/{toimumisaeg_id}/{vy_id}',
                 name_prefix='hindamine_hindajavaade_')
    add_resource_handler(config, 'hindamiskysimus', 'hindamiskysimused',
                 'eis.handlers.ekk.hindamine.hindajavaade_hindamiskysimused:HindajavaadeHindamiskysimusedController',
                 path_prefix='hindamine/{toimumisaeg_id}/{vy_id}',
                 name_prefix='hindamine_hindajavaade_')

    add_resource_handler(config, 'tekstianalyys1', 'tekstianalyys',
                 'eis.handlers.ekk.hindamine.hindajavaade_tekstianalyys:HindajavaadeTekstianalyysController',
                 path_prefix='hindamine/{toimumisaeg_id}/{vy_id}',
                 name_prefix='hindamine_hindajavaade_')

    
    # tulemuste arvutus
    add_resource_handler(config,'arvutus', 'arvutused', 
                 'eis.handlers.ekk.hindamine.arvutused:ArvutusedController',
                 path_prefix='hindamine/{toimumisaeg_id}',                 
                 name_prefix='hindamine_')        
    # tulemuste arvutus superserveris
    add_resource_handler(config,'arvutus', 'arvutused', 
                 'eis.handlers.ekk.hindamine.arvutused:ArvutusedController',
                 path_prefix='clu6/hindamine/{toimumisaeg_id}',                 
                 name_prefix='clu6_hindamine_')        
    # hindamise analüüs
    add_resource_handler(config,'ymbrik', 'ymbrikud', 
                 'eis.handlers.ekk.hindamine.ymbrikud:YmbrikudController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',                 
                 name_prefix='hindamine_analyys_')        
    add_resource_handler(config,'protokoll', 'protokollid', 
                 'eis.handlers.ekk.hindamine.protokollid:ProtokollidController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',                 
                 name_prefix='hindamine_analyys_')        
    add_resource_handler(config,'probleem', 'probleemid', 
                 'eis.handlers.ekk.hindamine.probleemid:ProbleemidController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',                 
                 name_prefix='hindamine_analyys_')        
    add_resource_handler(config,'hindamine3', 'hindamised3', 
                 'eis.handlers.ekk.hindamine.hindamised3:Hindamised3Controller',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',                 
                 name_prefix='hindamine_analyys_')        
    add_resource_handler(config,'hindaja', 'hindajad', 
                 'eis.handlers.ekk.hindamine.analyyshindajad:AnalyyshindajadController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',                 
                 name_prefix='hindamine_analyys_')        
    add_resource_handler(config,'vastus', 'vastused', 
                 'eis.handlers.ekk.hindamine.analyysvastused:AnalyysvastusedController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',                 
                 name_prefix='hindamine_analyys_',
                 slash=True) # slash vajalik, et show korral ylesannetes link images ette jääks ylesanne_id        
    add_resource_handler(config,'kvstatistika', 'kvstatistikad', 
                 'eis.handlers.ekk.hindamine.analyyskvstatistikad:AnalyyskvstatistikadController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys/{kst_id}',                 
                 name_prefix='hindamine_analyys_')        
    add_handler(config, 
                 'test_analyys_vastused_image',
                 'hindamine/{toimumisaeg_id}/analyys/vastused/{vy_id}/images{args:[^/]*}/{filename:.+}',
                 'eis.handlers.ekk.testid.images:ImagesController',
                 action='images')            
    add_resource_handler(config, 'maatriks', 'maatriksid',
                'eis.handlers.ekk.hindamine.analyysmaatriksid:AnalyysmaatriksidController', 
                path_prefix='hindamine/{toimumisaeg_id}/analyys/vastused/kysimus/{kysimus_id}',
                name_prefix='hindamine_analyys_vastused_kysimus_')
    # vastuste analyysis antud vastuste paginaatori lingid
    add_resource_handler(config,'kvstatistika', 'kvstatistikad', 
                 'eis.handlers.ekk.testid.analyyskvstatistikad:AnalyyskvstatistikadController',
                 path_prefix='test/{test_id}/analyys/{kst_id}',                 
                 name_prefix='test_analyys_')        

    add_resource_handler(config,'kool', 'koolid', 
                 'eis.handlers.ekk.hindamine.analyyskoolid:AnalyyskoolidController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',                 
                 name_prefix='hindamine_analyys_')        
    add_resource_handler(config,'mootmisviga', 'mootmisvead', 
                 'eis.handlers.ekk.hindamine.mootmisvead:MootmisveadController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',                 
                 name_prefix='hindamine_analyys_')        
    add_handler(config, 'hindamine_analyys_sarnasedvastused', 
                'hindamine/{toimumisaeg_id}/analyys/sarnasedvastused', 
                'eis.handlers.ekk.hindamine.sarnasedvastused:SarnasedvastusedController', 
                action='index')
    # soorituse hindamiste vaatamine
    add_resource_handler(config,'testitoo', 'testitood',
                 'eis.handlers.ekk.hindamine.testitood:TestitoodController',
                 path_prefix='hindamine/{toimumisaeg_id}/analyys',
                 name_prefix='hindamine_analyys_')

    # hindajate juhendamine
    add_resource_handler(config,'juhendamine', 'juhendamised', 
                 'eis.handlers.ekk.hindamine.juhendamine:JuhendamineController',
                 path_prefix='hindamine/{toimumisaeg_id}',                 
                 name_prefix='hindamine_')        
    # eksperthindamise soorituste loetelu ja otsing
    add_resource_handler(config,'eksperttoo', 'eksperttood', 
                 'eis.handlers.ekk.hindamine.eksperttood:EksperttoodController',
                 path_prefix='hindamine/{toimumisaeg_id}',                 
                 name_prefix='hindamine_')        

    # eksperthindamise all soorituse hindamisolekute loetelu vaatamine
    add_resource_handler(config,'kogum', 'kogumid',
                 'eis.handlers.ekk.hindamine.ekspertkogumid:EkspertkogumidController',
                 path_prefix='hindamine/{toimumisaeg_id}/ekspert',
                 name_prefix='hindamine_ekspert_')
    # eksperthindamise all soorituse vaatamine hindamiskogumite kaupa
    add_resource_handler(config,'vaatamine', 'vaatamised',
                         'eis.handlers.ekk.hindamine.ekspertvaatamised:EkspertvaatamisedController',
                 path_prefix='hindamine/{toimumisaeg_id}/sooritus/{sooritus_id}/hk/{hindamiskogum_id}/ekspert',
                 name_prefix='hindamine_ekspert_')
    add_task_handler(config,
                     'hindamine_ekspert_vaatamine_',
                     'eis.handlers.ekk.hindamine.ekspertvaatamised:EkspertvaatamisedController',
                     path='hindamine/{toimumisaeg_id}/sooritus/{sooritus_id}/hk/{hindamiskogum_id}/ekspert/vaatamine')
    
    # soorituse hindamine eksperdi poolt
    add_resource_handler(config,'hindamine', 'hindamised',
                 'eis.handlers.ekk.hindamine.eksperthindamised:EksperthindamisedController',
                 path_prefix='hindamine/{toimumisaeg_id}/sooritus/{sooritus_id}/hk/{hindamiskogum_id}/ekspert',
                 name_prefix='hindamine_ekspert_')
    add_task_handler(config,
                     'hindamine_ekspert_hindamine_',
                     'eis.handlers.ekk.hindamine.eksperthindamised:EksperthindamisedController',
                     path='hindamine/{toimumisaeg_id}/sooritus/{sooritus_id}/hk/{hindamiskogum_id}/ekspert/hindamine')


    # soorituse VI hindamise põhjuse sisestamine enne hindamiskogumi VI hindamist
    add_resource_handler(config,'hindamispohjus', 'hindamispohjused',
                 'eis.handlers.ekk.hindamine.hindamispohjus:HindamispohjusController',
                 path_prefix='hindamine/{toimumisaeg_id}/hk/{hindamiskogum_id}',
                 name_prefix='hindamine_')
    add_resource_handler(config,'rikkumisotsus', 'rikkumisotsused',
                 'eis.handlers.ekk.hindamine.rikkumisotsus:RikkumisotsusController',
                 path_prefix='hindamine/{toimumisaeg_id}',
                 name_prefix='hindamine_')

    # soorituse ühe ülesande hindamine juhteksperdi poolt vaide ettepaneku tegemisel
    add_resource_handler(config,'hindamine', 'hindamised',
                 'eis.handlers.ekk.hindamine.ettepanekhindamised:EttepanekhindamisedController',
                 path_prefix='hindamine/{toimumisaeg_id}/sooritus/{sooritus_id}/ettepanek',
                 name_prefix='hindamine_ettepanek_')
    add_task_handler(config,
                     'hindamine_ettepanek_hindamine_',
                     'eis.handlers.ekk.hindamine.ettepanekhindamised:EttepanekhindamisedController',
                     path='hindamine/{toimumisaeg_id}/sooritus/{sooritus_id}/ettepanek/hindamine')

    # soorituse ühe sisestuskogumi vastuste sisestamine juhteksperdi poolt vaide ettepaneku tegemisel
    add_resource_handler(config,'vastus', 'vastused',
                 'eis.handlers.ekk.hindamine.ettepanekvastused:EttepanekvastusedController',
                 path_prefix='hindamine/{toimumisaeg_id}/ettepanek/{sooritus_id}',
                 name_prefix='hindamine_ettepanek_')
    # soorituse ekspertide määramine vaidehindamisel
    add_resource_handler(config,'ekspert', 'eksperdid',
                 'eis.handlers.ekk.hindamine.ettepanekeksperdid:EttepanekeksperdidController',
                 path_prefix='hindamine/{toimumisaeg_id}/ettepanek/{sooritus_id}',
                 name_prefix='hindamine_ettepanek_')
    
    # vaide korral juhtekspert koostab otsuse ettepaneku vaidekomisjoni jaoks
    add_resource_handler(config,'ettepanek', 'ettepanekud',
                 'eis.handlers.ekk.hindamine.ettepanekud:EttepanekudController',
                 path_prefix='hindamine/{toimumisaeg_id}',
                 name_prefix='hindamine_')
    
    # toimumisaja ekspertrühmade haldamine
    add_resource_handler(config,'ekspertryhm', 'ekspertryhmad', 
                 'eis.handlers.ekk.hindamine.ekspertryhmad:EkspertryhmadController',
                 path_prefix='hindamine/{toimumisaeg_id}',                 
                 name_prefix='hindamine_')        

def make_map_ekk_sisestamine(config):
    # testi toimumise protokollide otsimine sisestamiseks
    add_resource_handler(config,'protokoll', 
                 'protokollid', 
                 'eis.handlers.ekk.sisestamine.protokollid:ProtokollidController',
                 path_prefix='sisestamine',
                 name_prefix='sisestamine_')
    # testi toimumise protokolli sisestamine
    add_resource_handler(config,'osaleja', 
                 'osalejad', 
                 'eis.handlers.ekk.sisestamine.protokollilosalejad:ProtokollilosalejadController',
                 path_prefix='sisestamine/{toimumisprotokoll_id}',
                 name_prefix='sisestamine_protokoll_')

    # toimumisaja otsing turvakottide numbrite sisestamiseks
    add_handler(config, 'sisestamine_turvakotid', '/sisestamine/turvakotid', 
                'eis.handlers.ekk.sisestamine.turvakotid:TurvakotidController', 
                action='index')
    # toimumisaja turvakottide numbrite sisestamine
    add_resource_handler(config,'turvakotinumber', 
                 'turvakotinumbrid', 
                 'eis.handlers.ekk.sisestamine.turvakotinumbrid:TurvakotinumbridController',
                 path_prefix='sisestamine/{toimumisaeg_id}',
                 name_prefix='sisestamine_')

    # turvakottide ja testitööde ümbrike saabumise registreerimine
    add_handler(config, 'sisestamine_saabumised', '/sisestamine/saabumised', 
                'eis.handlers.ekk.sisestamine.saabumised:SaabumisedController', 
                action='index',
                 request_method='GET')
    add_handler(config, 'sisestamine_create_saabumised', '/sisestamine/saabumised', 
                'eis.handlers.ekk.sisestamine.saabumised:SaabumisedController', 
                action='create',
                 request_method='POST')

    # testi toimumise protokolli helifailid
    add_resource_handler(config,'helifail', 'helifailid',
                 'eis.handlers.ekk.sisestamine.helifailid:HelifailidController',
                 path_prefix='sisestamine/{toimumisprotokoll_id}',
                 name_prefix='sisestamine_protokoll_')
    
    # suulise testi hindamise protokolli sisestamine
    add_resource_handler(config,'suuline', 
                 'suulised', 
                 'eis.handlers.ekk.sisestamine.suulised:SuulisedController',
                 path_prefix='sisestamine',
                 name_prefix='sisestamine_')
    add_resource_handler(config,'hindamine', 
                 'hindamised', 
                 'eis.handlers.ekk.sisestamine.suulisedhindamised:SuulisedhindamisedController',
                 path_prefix='sisestamine/suulised/{hindamisprotokoll_id}/{sisestus}',
                 name_prefix='sisestamine_suulised_')
    add_handler(config, 'sisestamine_hindamine_logi',
                '/sisestamine/hindamine/{hindamine_id}/logi',
                'eis.handlers.ekk.sisestamine.sisestuslogi:SisestuslogiController',
                action='index')
    # kirjaliku testi hindamise protokolli sisestamine
    add_resource_handler(config,'kirjalik', 
                 'kirjalikud', 
                 'eis.handlers.ekk.sisestamine.kirjalikud:KirjalikudController',
                 path_prefix='sisestamine',
                 name_prefix='sisestamine_')
    add_resource_handler(config,'hindamine', 
                 'hindamised', 
                 'eis.handlers.ekk.sisestamine.kirjalikudhindamised:KirjalikudhindamisedController',
                 path_prefix='sisestamine/kirjalikud/{hindamisprotokoll_id}/{sisestus}',
                 name_prefix='sisestamine_kirjalikud_')
    # toimumisaja otsing kirjalike paberil testitööde ümbrike hindajatele väljastamiseks
    add_handler(config, 'sisestamine_valjastamine', '/sisestamine/valjastamine', 
                'eis.handlers.ekk.sisestamine.valjastamine:ValjastamineController', 
                action='index')
    # kirjalike paberil testitööde ümbrike hindajatele väljastamine
    add_resource_handler(config,'hindamispakett', 
                 'hindamispaketid', 
                 'eis.handlers.ekk.sisestamine.hindamispaketid:HindamispaketidController',
                 path_prefix='sisestamine/valjastamine/{toimumisaeg_id}',
                 name_prefix='sisestamine_valjastamine_')
    # ühele hindajale (või hindajate paarile) väljastatud ümbrikud
    add_resource_handler(config,'hindajaymbrik', 
                 'hindajaymbrikud', 
                 'eis.handlers.ekk.sisestamine.hindajaymbrikud:HindajaymbrikudController',
                 path_prefix='sisestamine/valjastamine/{toimumisaeg_id}/{hindaja_id}',
                 name_prefix='sisestamine_valjastamine_')

    # kirjaliku testitöö vastuste sisestamine
    add_resource_handler(config,'vastus', 
                 'vastused', 
                 'eis.handlers.ekk.sisestamine.vastused:VastusedController',
                 path_prefix='sisestamine/testitoo/{sooritus_id}/sk/{sisestuskogum_id}/{sisestus}',
                 name_prefix='sisestamine_')    
    # kirjaliku testitöö otsing vastuste sisestamiseks
    add_resource_handler(config,'testitoo', 
                 'testitood', 
                 'eis.handlers.ekk.sisestamine.testitood:TestitoodController',
                 path_prefix='sisestamine',
                 name_prefix='sisestamine_')    

    # kirjaliku testitöö otsing skannimise laadimiseks
    add_resource_handler(config,'skannimine', 
                 'skannimised', 
                 'eis.handlers.ekk.sisestamine.skannimised:SkannimisedController',
                 path_prefix='sisestamine',
                 name_prefix='sisestamine_')    

    # rahvusvaheliste eksamite tunnistuste sisestamine
    add_resource_handler(config,'rvtunnistus', 
                 'rvtunnistused', 
                 'eis.handlers.ekk.sisestamine.rvtunnistused:RvtunnistusedController',
                 path_prefix='sisestamine',
                 name_prefix='sisestamine_')    
    add_resource_handler(config,'fail', 'failid', 
                 'eis.handlers.ekk.sisestamine.rvtunnistusedfail:RvtunnistusedfailController',
                 path_prefix='sisestamine/rvtunnistused/{rveksam_id}',
                 name_prefix='sisestamine_rvtunnistused_')    


def make_map_ekk_otsingud(config):

    add_resource_handler(config,'profiilileht', 'profiililehed',
                 'eis.handlers.ekk.otsingud.profiilileht:ProfiililehtController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    
    add_resource_handler(config,'testisooritus', 'testisooritused',
                 'eis.handlers.ekk.otsingud.testisooritused:TestisooritusedController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_handler(config, 'tulemus_osa', '/otsing/testisooritus/{test_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/sooritus/{id}',
                 'eis.handlers.ekk.otsingud.sooritus:SooritusController',
                 action='show')
    add_task_handler(config,
                     'tulemus_osa_',
                     'eis.handlers.ekk.otsingud.sooritus:SooritusController',                     
                     'otsing/testisooritus/{test_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/s/{id:\d+}')
    # kõigi failina antud vastuste allalaadimine
    add_handler(config, 
                 'sooritamine_vastusfail',
                 '/otsing/testisooritus/sooritus/{sooritus_id}/{id}',
                 'eis.handlers.ekk.otsingud.vastusfailid:VastusfailidController',
                 action='download')
    add_handler(config, 
                 'sooritamine_vastusfail_format',
                 '/otsing/testisooritus/{test_id:\d+}/{testiosa_id:\d+}/sooritus/{sooritus_id}/{id:\d+}.{fileversion}.{format}',
                 'eis.handlers.ekk.otsingud.vastusfailid:VastusfailidController',
                 action='download')

    add_handler(config, 
                 'tulemus_skskann',
                 '/otsing/testisooritus/sooritus/{sooritus_id}/skskann/{id}.pdf',
                 'eis.handlers.ekk.otsingud.skannid:SkannidController',
                 action='skskann')
    add_handler(config, 
                 'tulemus_yvskann',
                 '/otsing/testisooritus/sooritus/{sooritus_id}/yvskann/{id}.jpg',
                 'eis.handlers.ekk.otsingud.skannid:SkannidController',
                 action='yvskann')
    add_handler(config, 
                 'tulemus_kvskann',
                 '/otsing/testisooritus/sooritus/{sooritus_id}/kvskann/{id}.jpg',
                 'eis.handlers.ekk.otsingud.skannid:SkannidController',
                 action='kvskann')

    # Töövaataja õiguse andmise dialoog
    add_resource_handler(config,'toovaataja', 'toovaatajad',
                 'eis.handlers.ekk.otsingud.toovaataja:ToovaatajaController',
                 path_prefix='otsing/testisooritus/{sooritaja_id}',
                 name_prefix='otsing_testisooritus_')

    # Läbiviijate aruanded
    add_resource_handler(config,'sisestaja', 'sisestajad',
                 'eis.handlers.ekk.otsingud.sisestajad:SisestajadController',
                 path_prefix='otsing/labiviijad',
                 name_prefix='otsing_labiviijad_')
    # läbiviijate aruande algne otsinguvorm
    add_resource_handler(config,'labiviija', 'labiviijad',
                 'eis.handlers.ekk.otsingud.labiviijad:LabiviijadController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    # läbiviijate käskkirja andmed
    add_resource_handler(config,'labiviijakaskkiri', 'labiviijakaskkirjad',
                 'eis.handlers.ekk.otsingud.labiviijakaskkirjad:LabiviijakaskkirjadController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_resource_handler(config,'nousolek3', 'nousolekud3',
                 'eis.handlers.ekk.otsingud.nousolekud3:Nousolekud3Controller',
                 path_prefix='otsing',
                 name_prefix='otsing_')

    # hindamiserinevustega tööd
    add_handler(config,
                'otsing_hindamiserinevused',
                '/otsing/hindamiserinevused',
                'eis.handlers.ekk.otsingud.hindamiserinevused:HindamiserinevusedController',
                action='index')


    add_resource_handler(config,'tunnistus', 'tunnistused',
                 'eis.handlers.ekk.otsingud.tunnistused:TunnistusedController',
                 path_prefix='otsing',
                 name_prefix='otsing_')

    add_resource_handler(config,'kohateade', 'kohateated',
                 'eis.handlers.ekk.otsingud.kohateated:KohateatedController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_resource_handler(config,'vaatlejateade', 'vaatlejateated',
                 'eis.handlers.ekk.otsingud.vaatlejateated:VaatlejateatedController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_resource_handler(config,'labiviijateade', 'labiviijateated',
                 'eis.handlers.ekk.otsingud.labiviijateated:LabiviijateatedController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_resource_handler(config,'tulemusteteavitus', 'tulemusteteavitused',
                 'eis.handlers.ekk.otsingud.tulemusteteavitused:TulemusteteavitusedController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_resource_handler(config,'teade', 'teated',
                 'eis.handlers.ekk.otsingud.teated:TeatedController',
                 path_prefix='otsing',
                 name_prefix='otsing_')

    # rahvusvaheliste eksamite tunnistused
    add_resource_handler(config,'rvtunnistus', 
                 'rvtunnistused', 
                 'eis.handlers.ekk.otsingud.rvtunnistused:RvtunnistusedController',
                 path_prefix='otsing',
                 name_prefix='otsing_')    


    ## Statistika

    add_handler(config, 'statistika_soorituskohad', '/statistika/soorituskohad', 'eis.handlers.ekk.statistika.soorituskohad:SoorituskohadController', action='index')
    add_handler(config, 'statistika_vaided', '/statistika/vaided', 'eis.handlers.ekk.statistika.vaided:VaidedController', action='index')

    add_handler(config, 'statistika_osaoskused', '/statistika/osaoskused', 'eis.handlers.ekk.statistika.osaoskused:OsaoskusedController', action='index')
    add_handler(config, 'statistika_testitulemused', '/statistika/testitulemused', 'eis.handlers.ekk.statistika.testitulemused:TestitulemusedController', action='index')

    add_handler(config, 'statistika_tulemused', '/statistika/tulemused', 'eis.handlers.ekk.statistika.tulemused:TulemusedController', action='index')    

    add_handler(config, 'statistika_osalemine', '/statistika/osalemine', 'eis.handlers.ekk.statistika.osalemine:OsalemineController', action='index')

    # testitulemuste vaatamine piirkonnas testide kaupa
    add_resource_handler(config, 'piirkonnatulemus', 'piirkonnatulemused', 
                         'eis.handlers.ekk.statistika.piirkonnatulemused:PiirkonnatulemusedController',
                         path_prefix='statistika',
                         name_prefix='statistika_')
    # piirkonna statistika ühe testi kohta
    add_handler(config,
                'statistika_piirkonnas',
                '/statistika/piirkonnas/{test_id:\d+}/k{kursus:\w*}/{testimiskord_id}',
                'eis.handlers.ekk.statistika.piirkonnas:PiirkonnasController',
                action='show')

    # Eksamite tulemuste statistika
    add_resource_handler(config,'eksamistatistik', 'eksamistatistika', 
                 'eis.handlers.ekk.statistika.eksamistatistika:EksamistatistikaController')
    add_handler(config,
                'eksamistatistika_riikliktagasiside',
                '/eksamistatistika/riikliktagasiside/{test_id:\d+}/k{kursus:\w*}/{aasta:\d+}',
                'eis.handlers.ekk.statistika.riikliktagasiside:RiikliktagasisideController',
                action='show')

    add_resource_handler(config,'tugiisik', 'tugiisikud',
                 'eis.handlers.ekk.otsingud.tugiisikud:TugiisikudController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_resource_handler(config,'sooritajatearv', 'sooritajatearvud',
                 'eis.handlers.ekk.otsingud.sooritajatearv:SooritajatearvController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_resource_handler(config,'sooritajatearv2', 'sooritajatearvud2',
                 'eis.handlers.ekk.otsingud.sooritajatearv2:Sooritajatearv2Controller',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_resource_handler(config,'sooritajateolek', 'sooritajateolekud',
                 'eis.handlers.ekk.otsingud.sooritajateolek:SooritajateolekController',
                 path_prefix='otsing',
                 name_prefix='otsing_')
    add_handler(config, 'otsing_kasutajatearvud', '/otsing/kasutajatearvud',
                'eis.handlers.ekk.otsingud.kasutajatearv:KasutajatearvController',
                action='index')

def make_map_ekk_muud(config):
    # vaided
    add_resource_handler(config,'vaie', 'vaided',
                 'eis.handlers.ekk.muud.vaided:VaidedController',
                 path_prefix='muud',
                 name_prefix='muud_')

    add_resource_handler(config,'ettepanek', 'ettepanekud',
                 'eis.handlers.ekk.muud.ettepanekud:EttepanekudController',
                 path_prefix='muud',
                 name_prefix='muud_')

    # erivajadused
    add_resource_handler(config,'erivajadus', 'erivajadused',
                 'eis.handlers.ekk.muud.erivajadused:ErivajadusedController',
                 path_prefix='muud',
                 name_prefix='muud_')
    # tugiisiku määramine registreeringu vormilt
    add_resource_handler(config, 'tugiisik', 'tugiisikud',
                         'eis.handlers.ekk.regamine.tugiisik:TugiisikController',
                         path_prefix='muud/erivajadused/{sooritus_id}',
                         name_prefix='muud_erivajadused_')

    # eksamitunnistused
    add_resource_handler(config,'valjastamine', 'valjastamised',
                         'eis.handlers.ekk.muud.tunnistused.valjastamine:ValjastamineController',
                         path_prefix='muud/tunnistused',
                         post_path_prefix='muud/clufs/tunnistused',
                         name_prefix='muud_tunnistused_')
    add_resource_handler(config,'salvestamine', 'salvestamised',
                         'eis.handlers.ekk.muud.tunnistused.salvestamine:SalvestamineController',
                         path_prefix='muud/clufs/tunnistused',
                         post_path_prefix='muud/clufs/tunnistused',
                         name_prefix='muud_tunnistused_')
    add_resource_handler(config,'avaldamine', 'avaldamised',
                         'eis.handlers.ekk.muud.tunnistused.avaldamine:AvaldamineController',
                         path_prefix='muud/tunnistused',
                         name_prefix='muud_tunnistused_')
    add_resource_handler(config,'tyhistamine', 'tyhistamised',
                         'eis.handlers.ekk.muud.tunnistused.tyhistamine:TyhistamineController',
                         path_prefix='muud/tunnistused',
                         name_prefix='muud_tunnistused_')    
    
    # skannitud eksamitööga tutvumise korraldamine
    add_resource_handler(config,'taotlemine', 'taotlemised',
                         'eis.handlers.ekk.muud.skannid.taotlemine.TaotlemineController',
                         path_prefix='muud/skannid',
                         name_prefix='muud_skannid_')
    add_resource_handler(config,'tellimine', 'tellimised',
                         'eis.handlers.ekk.muud.skannid.tellimised:TellimisedController',
                         path_prefix='muud/skannid',
                         name_prefix='muud_skannid_')
    add_resource_handler(config,'toolaadimine', 'toolaadimised',
                         'eis.handlers.ekk.muud.skannid.toolaadimine:ToolaadimineController',
                         path_prefix='muud/skannid',
                         post_path_prefix='muud/skannid',
                         name_prefix='muud_skannid_')
    add_resource_handler(config,'laadimine', 'laadimised',
                         'eis.handlers.ekk.muud.skannid.laadimine:LaadimineController',
                         path_prefix='muud/skannid',
                         post_path_prefix='muud/skannid',
                         name_prefix='muud_skannid_')

    # tulemuste avaldamine
    add_resource_handler(config,'tulemus', 'tulemused',
                 'eis.handlers.ekk.muud.tulemused:TulemusedController',
                 path_prefix='muud',
                 name_prefix='muud_')

    # statistikaraportite avaldamine
    add_resource_handler(config,'statistikaraport', 'statistikaraportid',
                         'eis.handlers.ekk.muud.statistikaraportid:StatistikaraportidController',
                         path_prefix='muud',
                         name_prefix='muud_',
                         id_re='')

    # registreerimise kontroll
    add_resource_handler(config,'regkontroll', 'regkontrollid',
                 'eis.handlers.ekk.muud.regkontroll:RegkontrollController',
                 path_prefix='muud',
                 name_prefix='muud_')
    # lõpetamiste kontroll
    add_resource_handler(config,'lopetamine', 'lopetamised',
                 'eis.handlers.ekk.muud.lopetamised:LopetamisedController',
                 path_prefix='muud',
                 name_prefix='muud_')

    add_resource_handler(config,'toofail', 'toofailid',
                 'eis.handlers.ekk.muud.toofailid:ToofailidController',
                 path_prefix='muud',
                 name_prefix='muud_')

    add_resource_handler(config,'pstulemus', 'pstulemused', 
                         'eis.handlers.ekk.muud.pstulemus:PstulemusController',
                         path_prefix='muud',
                         name_prefix='muud_')

def make_map_avalik_eksam(config, is_live, is_test):
    """Avaliku vaate ruuting
    """
    # arvuti registreerimine testiruumis
    add_handler(config, 'arvuti', '/arvuti', 'eis.handlers.login:LoginController', action='signin_arvuti')
    # seansi hoidmise päringud ajaks, kui kasutaja on SEBis
    add_handler(config, 'keepsess', '/keepsess', 'eis.handlers.index:IndexController', action='keepsess')    

    # ylesande lahendamine
    add_handler(config,
                'edit_lahendamine2',
                '/lahendamine/{id:\d+}/edit',
                'eis.handlers.avalik.lahendamine.lahendamine:LahendamineController', 
                action='edit')
    add_resource_handler(config,
                         'lahendamine1', 
                         'lahendamine', 
                         'eis.handlers.avalik.lahendamine.lahendamine:LahendamineController',
                         slash=False)
    add_task_handler(config,
                     'lahendamine_',
                     'eis.handlers.avalik.lahendamine.lahendamine:LahendamineController',
                     editpath='/lahendamine/{id:\d+}',
                     updatepath='/lahendamine/{id:\d+}/{yv_id:\d+}') # temp

    add_handler(config, 'lahendamine_lisa', '/lahendamine/{sisuplokk_id}/lisa',
                       'eis.handlers.avalik.lahendamine.lisad:LisadController',
                       action='create',
                       request_method='POST')

    make_map_avalik_testid(config, is_live, is_test)

    make_map_avalik_regamine(config)


    # Sooritajate määramine
    # EKK testi sooritajate määramine, otsitakse testimiskordi
    add_resource_handler(config,'testimiskord', 'testimiskorrad',
                 'eis.handlers.avalik.nimekirjad.testimiskorrad:TestimiskorradController',
                 path_prefix='nimekirjad',
                 name_prefix='nimekirjad_')
    add_resource_handler(config, 'korrasooritaja', 'korrasooritajad',
                         'eis.handlers.avalik.nimekirjad.korrasooritajad:KorrasooritajadController',
                         path_prefix='nimekirjad/testimiskorrad/{testimiskord_id}',
                         name_prefix='nimekirjad_testimiskord_')
    
    # registreerimise kontroll
    add_resource_handler(config,'kontroll', 'kontrollid',
                 'eis.handlers.avalik.nimekirjad.kontroll:KontrollController',
                 path_prefix='nimekirjad',
                 name_prefix='nimekirjad_')
    # sooritaja tulemuse vaatamine
    add_resource_handler(config,'tulemus', 'tulemused', 
                          'eis.handlers.avalik.nimekirjad.tulemused:TulemusedController',
                          path_prefix='nimekirjad/kontroll',
                          name_prefix='nimekirjad_kontroll_')
    # sooritaja testiosa soorituse vaatamise lehe avamine
    add_resource_handler(config, 'osa', 'osad', 
                          'eis.handlers.avalik.nimekirjad.sooritus:SooritusController',
                          path_prefix='nimekirjad/kontroll/tulemus/{test_id}/{testiosa_id}',
                          name_prefix='nimekirjad_kontroll_tulemus_',
                          slash=True, id_re='T?\d+')
    # alatesti sooritamise lehe avamine
    add_resource_handler(config,'osa', 'osad', 
                          'eis.handlers.avalik.nimekirjad.sooritus:SooritusController',
                          path_prefix='nimekirjad/kontroll/tulemus/{test_id}/{testiosa_id}/{alatest_id}',
                          name_prefix='nimekirjad_kontroll_tulemus_alatest_',
                          slash=True, id_re='T?\d+')

    add_resource_handler(config,'sooritaja', 'sooritajad', 
                 'eis.handlers.avalik.nimekirjad.sooritajad:SooritajadController',
                 path_prefix='nimekiri/{testimiskord_id}',
                 name_prefix='nimekiri_')
    add_resource_handler(config,'isik', 'isikud', 
                 'eis.handlers.avalik.nimekirjad.isikud:IsikudController',
                 path_prefix='nimekiri/{testimiskord_id}',
                 name_prefix='nimekiri_')
    add_resource_handler(config,'kanne', 'kanded',
                 'eis.handlers.avalik.nimekirjad.kanne:KanneController',
                 path_prefix='nimekiri/{testimiskord_id}',
                 name_prefix='nimekiri_')
    add_resource_handler(config, 'tugiisik', 'tugiisikud',
                         'eis.handlers.avalik.nimekirjad.tugiisik:TugiisikController',
                         path_prefix='nimekiri/kanne/{sooritus_id}',
                         name_prefix='nimekiri_kanne_')

    # Soorituse erivajadused
    add_resource_handler(config,'erivajadus', 'erivajadused',
                 'eis.handlers.avalik.nimekirjad.erivajadused:ErivajadusedController',
                 path_prefix='nimekiri',
                 name_prefix='nimekiri_')

    # kool registreerib õpilase avalduse mitmele testile
    add_handler(config, 'nimekirjad_new_avaldus', 
                '/nimekirjad/avaldus',
                'eis.handlers.avalik.nimekirjad.avaldus.isikuvalik:IsikuvalikController',
                action='new',
                 request_method='GET')
    add_handler(config, 'nimekirjad_create_avaldus', 
                 '/nimekirjad/avaldus',
                 'eis.handlers.avalik.nimekirjad.avaldus.isikuvalik:IsikuvalikController',
                 action='create',
                 request_method='POST')

    add_handler(config, 'nimekirjad_edit_avaldus', 
                 '/nimekirjad/avaldus/{id}',
                 'eis.handlers.avalik.nimekirjad.avaldus.isikuvalik:IsikuvalikController',
                 action='edit',
                 request_method='GET')
    add_handler(config, 'nimekirjad_update_avaldus', 
                 '/nimekirjad/avaldus/{id}',
                 'eis.handlers.avalik.nimekirjad.avaldus.isikuvalik:IsikuvalikController',
                 action='update',
                 request_method='POST') # PUT

    add_handler(config, 'nimekirjad_avaldus_isikuandmed', 
                 '/nimekirjad/avaldus/{id}/isikuandmed',
                 'eis.handlers.avalik.nimekirjad.avaldus.isikuandmed:IsikuandmedController',
                 action='edit',
                 request_method='GET')
    add_handler(config, 'nimekirjad_avaldus_update_isikuandmed', 
                 '/nimekirjad/avaldus/{id}/isikuandmed',
                 'eis.handlers.avalik.nimekirjad.avaldus.isikuandmed:IsikuandmedController',
                 action='update',
                 request_method='POST')
    
    # valitud testide vaatamine
    add_handler(config, 'nimekirjad_avaldus_testid', 
                 '/nimekirjad/avaldus/{id}/testid',
                 'eis.handlers.avalik.nimekirjad.avaldus.testid:TestidController',
                 action='index',
                 request_method='GET')
    # dialoogiaknas leitud testide lisamine nimekirja
    add_handler(config, 'nimekirjad_avaldus_lisatestid', 
                '/nimekirjad/avaldus/{id}/lisatestid',
                'eis.handlers.avalik.nimekirjad.avaldus.testid:TestidController',
                action='create',
                 request_method='POST')

    # dialoogiaknas testi keele ja piirkonna muutmine
    add_handler(config, 'nimekirjad_avaldus_edit_test', 
                       '/nimekirjad/avaldus/{id}/testid/{sooritaja_id}',
                       'eis.handlers.avalik.nimekirjad.avaldus.testid:TestidController',
                       action='edit',
                       request_method='GET') 
    add_handler(config, 'nimekirjad_avaldus_update_test', 
                       '/nimekirjad/avaldus/{id}/testid/{sooritaja_id}',
                       'eis.handlers.avalik.nimekirjad.avaldus.testid:TestidController',
                       action='update',
                       request_method='POST') # PUT

    # avaldusel tugiisiku muutmine
    add_resource_handler(config, 'tugiisik', 'tugiisikud',
                         'eis.handlers.avalik.nimekirjad.avaldus.tugiisik:TugiisikController',
                         path_prefix='nimekirjad/avaldus/{kasutaja_id}/sooritaja/{sooritaja_id}',
                         name_prefix='nimekirjad_avaldus_')

    # testi eemaldamine
    add_handler(config, 'nimekirjad_avaldus_delete_test', 
                '/nimekirjad/avaldus/{id}/testid/{sooritaja_id}/delete',
                'eis.handlers.avalik.nimekirjad.avaldus.testid:TestidController',
                 action='delete',
                 request_method='POST') # DELETE
    # testide otsimine dialoogiaknas
    add_resource_handler(config,'otsitest', 'otsitestid',
                 'eis.handlers.avalik.nimekirjad.avaldus.otsitestid:OtsitestidController',
                 path_prefix='nimekirjad/avaldus/{kasutaja_id}',
                 name_prefix='nimekirjad_avaldus_')

    add_handler(config, 'nimekirjad_avaldus_edit_kinnitamine', 
                '/nimekirjad/avaldus/{id}/kinnitamine',
                'eis.handlers.avalik.nimekirjad.avaldus.kinnitamine:KinnitamineController',
                action='edit',
                 request_method='GET')
    add_handler(config, 'nimekirjad_avaldus_kinnitamine', 
                 '/nimekirjad/avaldus/{id}/kinnitamine',
                 'eis.handlers.avalik.nimekirjad.avaldus.kinnitamine:KinnitamineController',
                 action='update',
                 request_method='POST') # PUT  
    add_handler(config, 'nimekirjad_avaldus_delete_kinnitamine', 
                 '/nimekirjad/avaldus/{id}/kinnitamine/delete',
                 'eis.handlers.avalik.nimekirjad.avaldus.kinnitamine:KinnitamineController',
                 action='delete',
                 request_method='POST')


    ################################### Testide sooritamine

    # sooritamiste otsimise lehekülg
    add_resource_handler(config,'sooritamine', 'sooritamised', 
                 'eis.handlers.avalik.sooritamine.testid:TestidController')

    # testi sooritamise alustamise lehekülg
    add_handler(config, 'sooritamine_test', 
                '/sooritamine/{test_id}', 
                 'eis.handlers.avalik.sooritamine.alustamine:AlustamineController',
                 action='index')
    # testi sooritamise alustamise ja lõpetamiselehekülg
    add_handler(config, 'sooritamine_alustamine', 
                '/sooritamine/{test_id}/sooritaja/{sooritaja_id}/alustamine', 
                 'eis.handlers.avalik.sooritamine.alustamine:AlustamineController',
                 action='index')
    # testi sooritamise alustamise lehelt tagasiside PDFi alla laadimine
    add_handler(config, 'sooritamine_alustamine_format', 
                '/sooritamine/{test_id}/{sooritaja_id}/alustamine/fail.pdf', 
                 'eis.handlers.avalik.sooritamine.alustamine:AlustamineController',
                 action='download')
    
    # sooritaja isiku kontroll (Veriff)
    # sooritaja suunamine verifitseerimisele
    add_handler(config, 'veriff_start', 
                '/veriff/start/{sooritus_id}', 
                 'eis.handlers.avalik.sooritamine.veriff:VeriffController',
                 action='start')
    # sooritaja tagasitulek verifitseerimiselt
    add_handler(config, 'veriff_returned', 
                '/veriff/returned/{id}', 
                 'eis.handlers.avalik.sooritamine.veriff:VeriffController',
                 action='returned')
    # webhookid veriffilt tulevate teavituste jaoks
    add_handler(config, 'veriff_eventhook', 
                '/veriff/eventhook/{int_id}', 
                'eis.handlers.avalik.sooritamine.veriff:VeriffController',
                action='eventhook',
                request_method='POST')
    add_handler(config, 'veriff_decision', 
                '/veriff/decision/{int_id}', 
                'eis.handlers.avalik.sooritamine.veriff:VeriffController',
                action='decision',
                request_method='POST')

    # kypsiste muutmine enne Proctoriosse suunamist
    add_handler(config, 'proctorio_start', 
                '/proctorio/{test_id}/{testiosa_id}/{sooritus_id}/start', 
                 'eis.handlers.avalik.sooritamine.proctorio:ProctorioController',
                 action='start')
    # sooritaja suunamine Proctorio teenusesse
    add_handler(config, 'proctorio_start1', 
                '/proctorio/{test_id}/{testiosa_id}/{sooritus_id}/start1', 
                 'eis.handlers.avalik.sooritamine.proctorio:ProctorioController',
                 action='start1')
    # korraldaja vaade Proctorios
    add_handler(config, 'proctorio_review', 
                '/proctorio/{test_id}/{toimumisaeg_id}/{testiruum_id}/review', 
                 'eis.handlers.avalik.sooritamine.proctorio:ProctorioController',
                 action='review')

    # SEB konfi allalaadimine
    add_handler(config, 'seb_start', 
                '/seb/{test_id}/{testiosa_id}/{sooritus_id}/start.seb', 
                 'eis.handlers.avalik.sooritamine.seb:SebController',
                 action='start')
    # SEB maandumine
    add_handler(config, 'seb_start1', 
                '/seb/{test_id}/{testiosa_id}/{sooritaja_id}/{sooritus_id}/start1/{klaster_id}/{url_key}', 
                 'eis.handlers.avalik.sooritamine.seb:SebController',
                 action='start1')
    # SEB kasutaja vales kohas
    add_handler(config, 'seb_notauthorized', 
                '/seb/notauthorized', 
                 'eis.handlers.avalik.sooritamine.seb:SebController',
                 action='notauthorized')
    
    make_map_avalik_sooritamine(config)
    make_map_avalik_tooylesanne(config)


    ###################### Minu tulemused

    # Skannitud vastuste pildid
    add_handler(config, 
                 'tulemus_skskann',
                 '/tulemus/{sooritus_id}/skskann/{id}.pdf',
                 'eis.handlers.avalik.tulemused.skannid:SkannidController',
                 action='skskann')
    add_handler(config, 
                 'tulemus_yvskann',
                 '/tulemus/{sooritus_id}/yvskann/{id}.jpg',
                 'eis.handlers.avalik.tulemused.skannid:SkannidController',
                 action='yvskann')
    add_handler(config, 
                 'tulemus_kvskann',
                 '/tulemus/{sooritus_id}/kvskann/{id}.jpg',
                 'eis.handlers.avalik.tulemused.skannid:SkannidController',
                 action='kvskann')

    # volituste lisamine
    add_resource_handler(config,'volitus', 'volitused', 
                 'eis.handlers.avalik.tulemused.volitused:VolitusedController',
                 path_prefix='tulemused',
                 name_prefix='tulemused_')

    # Vaide esitamine
    add_resource_handler(config,'vaie', 'vaided',
                 'eis.handlers.avalik.tulemused.vaided:VaidedController')
    # skannitud eksamitööga tutvumise taotluse esitamine
    add_resource_handler(config,'tellimine', 'tellimised',
                         'eis.handlers.avalik.tulemused.tellimine:TellimineController',
                         path_prefix='tulemus',
                         name_prefix='tulemus_')
    add_handler(config,
                'tulemus_skannfail',
                '/tulemus/skannfail/{id}.pdf',
                'eis.handlers.avalik.tulemused.skannfail:SkannfailController',
                action='download')

    # Tulemuste loetelu
    add_resource_handler(config,'tulemus', 'tulemused', 
                 'eis.handlers.avalik.tulemused.tulemused:TulemusedController')

    # tehtud testiosa vaatamise lehe avamine
    add_resource_handler(config, 'osa', 'osad',
                         'eis.handlers.avalik.tulemused.sooritus:SooritusController',
                         path_prefix='tulemus/{test_id:\d+}/{testiosa_id:\d+}',
                         path_id='tulemus/{test_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/s/{id:\d+}',
                         name_prefix='tulemus_')
    add_task_handler(config,
                     'tulemus_osa_',
                     'eis.handlers.avalik.tulemused.sooritus:SooritusController',                     
                     'tulemus/{test_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/s/{id:\d+}')
    add_handler(config,
               'tulemus_osa1',
               'tulemus/{test_id:\d+}/{testiosa_id:\d+}/s/{id:\d+}',
               'eis.handlers.avalik.tulemused.sooritus:SooritusController',
               action='show')

    add_resource_handler(config,'profiilileht', 'profiililehed',
                 'eis.handlers.avalik.tulemused.profiilileht:ProfiililehtController',
                 path_prefix='tulemus_',
                 name_prefix='tulemus_')


    ################################# Testide läbiviimine

    # testi eelvaade testi administraatorile
    # testi lahendamise eelvaade: testiosa sooritamise lehe avamine
    add_resource_handler(config,'eelvaade', 'eelvaated', 
                         'eis.handlers.avalik.klabiviimine.eelvaade:EelvaadeController',
                         path_prefix='klabiviimine/{test_id:\d+}/{testiruum_id:\d+}-{alatest_id:\d*}',
                         name_prefix='klabiviimine_')
    add_task_handler(config,
                     'klabiviimine_eelvaade_',
                     'eis.handlers.avalik.klabiviimine.eelvaade:EelvaadeController',
                     'klabiviimine/{test_id:\d+}/{testiruum_id:\d+}-{alatest_id:\d*}/eelvaade/{id:-?\d+}')

    # testimiskorraga testi läbiviimine
    add_resource_handler(config,'toimumisaeg', 'toimumisajad', 
                 'eis.handlers.avalik.klabiviimine.toimumisajad:ToimumisajadController',
                 path_prefix='klabiviimine', 
                 name_prefix='klabiviimine_')
    # # avaliku vaate testi läbiviimine
    add_handler(config, 'labiviimine_alatestisooritus', '/labiviimine/sooritus/{id}/{alatest_id}',
                 'eis.handlers.avalik.klabiviimine.sooritus:SooritusController',
                 action='show')
    
    add_resource_handler(config,'parool', 'paroolid', 'eis.handlers.avalik.admin.paroolid:ParoolidController', 
                 path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'volitus', 'volitused', 'eis.handlers.avalik.admin.volitused:VolitusedController', 
                 path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'klassiparool', 'klassiparoolid', 'eis.handlers.avalik.admin.klassiparoolid:KlassiparoolidController', 
                 path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'klassiopilane', 'klassiopilased', 'eis.handlers.avalik.admin.klassiopilased:KlassiopilasedController', 
                 path_prefix='/admin', name_prefix='admin_')        

    # Testide korraldamine soorituskohas
    add_resource_handler(config,'korraldamine', 'korraldamised', 
                 'eis.handlers.avalik.korraldamine.testikohad:TestikohadController')
    add_resource_handler(config,'sooritaja','sooritajad', 
                 'eis.handlers.avalik.korraldamine.sooritajad:SooritajadController',
                 path_prefix='korraldamine/{testikoht_id}',
                 name_prefix='korraldamine_')
    # testiprotokollirühmade lisamine ja kustutamine
    add_resource_handler(config,'testiprotokoll','testiprotokollid', 
                 'eis.handlers.avalik.korraldamine.testiprotokollid:TestiprotokollidController',
                 path_prefix='korraldamine/{testikoht_id}/{testipakett_id}/{testiruum_id}',
                 name_prefix='korraldamine_')    
    add_resource_handler(config,'labiviija','labiviijad', 
                 'eis.handlers.avalik.korraldamine.labiviijad:LabiviijadController',
                 path_prefix='korraldamine/{testikoht_id}',
                 name_prefix='korraldamine_')
    # läbiviijate otsimine dialoogiaknas
    add_resource_handler(config,'otsilabiviija', 'otsilabiviijad',
                 'eis.handlers.avalik.korraldamine.otsilabiviijad:OtsilabiviijadController',
                 path_prefix='korraldamine/{testikoht_id}',
                 name_prefix='korraldamine_')
    add_resource_handler(config,'materjal','materjalid', 
                 'eis.handlers.avalik.korraldamine.materjalid:MaterjalidController',
                 path_prefix='korraldamine/{testikoht_id}',
                 name_prefix='korraldamine_')
    add_resource_handler(config,'hindaja','hindajad', 
                 'eis.handlers.avalik.korraldamine.hindajad:HindajadController',
                 path_prefix='korraldamine/{testikoht_id}',
                 name_prefix='korraldamine_')
    # add_resource_handler(config,'otsihindaja', 'otsihindajad',
    #              'eis.handlers.avalik.korraldamine.otsihindajad:OtsihindajadController',
    #              path_prefix='korraldamine/{testikoht_id}',
    #              name_prefix='korraldamine_')

    # korraldamise sooritajate loetelu lehel uue aineõpetaja lisamine koolile
    add_resource_handler(config,'aineopetaja', 'aineopetajad', 'eis.handlers.avalik.korraldamine.aineopetajad:AineopetajadController', 
                 path_prefix='korraldamine/{testikoht_id}',
                 name_prefix='korraldamine_')
    # isikute otsimine dialoogiaknas soorituskohaga seostamiseks
    add_resource_handler(config,'aineopetajaisik', 'aineopetajaisikud',
                 'eis.handlers.avalik.korraldamine.aineopetajaisikud:AineopetajaisikudController',
                 path_prefix='korraldamine/{testikoht_id}',
                 name_prefix='korraldamine_')


    # Testi protokolli koostamine
    add_resource_handler(config,'protokoll', 'protokollid',
                 'eis.handlers.avalik.protokollid.protokollid:ProtokollidController')
    add_resource_handler(config,'osaleja', 'osalejad',
                 'eis.handlers.avalik.protokollid.osalejad:OsalejadController',
                 path_prefix='protokoll/{toimumisprotokoll_id}',
                 name_prefix='protokoll_')

    # Suulise vastamise vastuvõtt (intervjueerimine)
    add_resource_handler(config,'svastamine', 'svastamised',
                 'eis.handlers.avalik.svastamine.suulised:SuulisedController')
    # vastuste sisestamine
    add_resource_handler(config,'vastaja', 'vastajad',
                 'eis.handlers.avalik.svastamine.vastajad:VastajadController',
                 path_prefix='svastamine/{testiruum_id}',
                 name_prefix='svastamine_')
    # vastuste salvestamine helifailidena
    add_resource_handler(config,'intervjuu', 'intervjuud',
                 'eis.handlers.avalik.svastamine.intervjuu:IntervjuuController',
                 path_prefix='svastamine/{test_id}/{testiruum_id}',
                 name_prefix='svastamine_')

    # Suulise vastamise hindamine
    add_resource_handler(config,'vastaja', 'vastajad',
                 'eis.handlers.avalik.shindamine.vastajad:VastajadController',
                 path_prefix='shindamine/{testiruum_id}',
                 name_prefix='shindamine_')
    add_resource_handler(config,'hindamine', 'hindamised',
                          'eis.handlers.avalik.shindamine.hindamised:HindamisedController',
                          path_prefix='shindamine/{hindaja_id}',
                          name_prefix='shindamine_')

    # testimiskorrata testide (õpetaja testide) hindamine
    add_resource_handler(config, 'rhindamine', 'rhindamised',
                'eis.handlers.avalik.khindamine.rhindamised:RhindamisedController')
    add_resource_handler(config, 'muuhindamine', 'muudhindamised',
                'eis.handlers.avalik.khindamine.muudhindamised:MuudhindamisedController')


    # Kirjaliku vastamise hindamine
    # hindamiskogumite ja toimumisaegade otsing
    add_resource_handler(config, 'khindamine', 'khindamised',
                'eis.handlers.avalik.khindamine.hindamiskogumid:HindamiskogumidController')

    # hindamiskogumis olevate ülesannete loetelu kuvamine
    add_handler(config, 'khindamine_hindamiskogum', 
                '/khindamine/{toimumisaeg_id}/hindaja/{id}',
                'eis.handlers.avalik.khindamine.hindamiskogumid:HindamiskogumidController',
                action='show')
    add_resource_handler(config,'vastaja', 'vastajad',
                 'eis.handlers.avalik.khindamine.vastajad:VastajadController',
                 path_prefix='khindamine/{toimumisaeg_id}/hindaja/{hindaja_id}',
                 name_prefix='khindamine_')
    add_resource_handler(config,'hkhindamine', 'hkhindamised',
                 'eis.handlers.avalik.khindamine.hkhindamine:HkhindamineController',
                 path_prefix='khindamine/{toimumisaeg_id}/hindaja/{hindaja_id}/{sooritus_id}',
                 name_prefix='khindamine_')
    add_task_handler(config,
                     'khindamine_hkhindamine_',
                     'eis.handlers.avalik.khindamine.hkhindamine:HkhindamineController',
                     path='khindamine/{toimumisaeg_id}/hindaja/{hindaja_id}/{sooritus_id:\d+}')

    # hindaja parempoolse ekraaniosa sakid:
    add_resource_handler(config, 'tekstianalyys1', 'tekstianalyys',
                 'eis.handlers.avalik.khindamine.tekstianalyys:TekstianalyysController',
                 path_prefix='khindamine/{toimumisaeg_id}/{vy_id}',
                 name_prefix='khindamine_')

    # ülesande lahendamine
    add_resource_handler(config,'lahendamine', 'lahendamised',
                 'eis.handlers.avalik.khindamine.lahendamine:LahendamineController',
                 path_prefix='khindamine/{toimumisaeg_id}/{vy_id}',
                 name_prefix='khindamine_')
    add_task_handler(config,
                     'khindamine_lahendamine_',
                     'eis.handlers.avalik.khindamine.lahendamine:LahendamineController',
                     editpath='khindamine/{toimumisaeg_id:\d+}/{vy_id:\d+}/lahendamine/{id:\d+}',
                     updatepath='khindamine/{toimumisaeg_id:\d+}/{vy_id:\d+}/lahendamine/{id:\d+}/{yv_id:\d+}') # temp
    
    # hindamisjuhendid
    add_resource_handler(config, 'juhend', 'juhendid',
                 'eis.handlers.avalik.khindamine.juhend:JuhendController',
                 path_prefix='khindamine/{toimumisaeg_id}/{vy_id}',
                 name_prefix='khindamine_')
    add_resource_handler(config, 'hindamiskysimus', 'hindamiskysimused',
                 'eis.handlers.avalik.khindamine.hindamiskysimused:HindamiskysimusedController',
                 path_prefix='khindamine/{toimumisaeg_id}/{vy_id}',
                 name_prefix='khindamine_')

    make_map_avalik_ktulemused(config, is_live, is_test)

    ###################### Minu tulemused

    # Eksamitunnistused
    add_resource_handler(config,'tunnistus', 'tunnistused', 
                 'eis.handlers.avalik.tunnistused.tunnistused:TunnistusedController')

    # rahvusvaheliste eksamite tunnistused - õpilase päring
    add_resource_handler(config,'rvtunnistus', 'rvtunnistused', 
                         'eis.handlers.avalik.tunnistused.rvtunnistused:RvtunnistusedController',
                         path_prefix='tunnistused',
                         name_prefix='tunnistused_')

    # koolipsyhholoogi litsentside haldamine
    add_resource_handler(config,'litsents', 'litsentsid', 
                         'eis.handlers.avalik.koolipsyhholoogid.litsentsid:LitsentsidController',
                         path_prefix='koolipsyhholoogid',
                         name_prefix='koolipsyhholoogid_')
    add_resource_handler(config,'koolipsyhholoog', 'koolipsyhholoogid', 
                         'eis.handlers.avalik.koolipsyhholoogid.koolipsyhholoogid:KoolipsyhholoogidController')

    # logopeedide litsentside haldamine
    add_resource_handler(config,'litsents', 'litsentsid', 
                         'eis.handlers.avalik.logopeedid.litsentsid:LitsentsidController',
                         path_prefix='logopeedid',
                         name_prefix='logopeedid_')
    add_resource_handler(config,'logopeed', 'logopeedid', 
                         'eis.handlers.avalik.logopeedid.logopeedid:LogopeedidController')

    
    ################################
    # Testi läbiviimise nõusolekud avalikus vaates
    # Nõusolekud: määramised
    add_resource_handler(config,'maaramine', 'maaramised',
                 'eis.handlers.avalik.nousolekud.maaramised:MaaramisedController', 
                 path_prefix='nousolekud',
                 name_prefix='nousolekud_')
    # Nõusolekud: minu läbiviija profiil     
    add_resource_handler(config,'profiil1', 'profiil',
                 'eis.handlers.avalik.nousolekud.profiil:ProfiilController', 
                 path_prefix='nousolekud',
                 name_prefix='nousolekud_')
    ## Nõusolekud: minu isikuandmed
    add_resource_handler(config,'isikuanne', 'isikuandmed',
                 'eis.handlers.avalik.nousolekud.isikuandmed:IsikuandmedController', 
                 path_prefix='nousolekud',
                 name_prefix='nousolekud_')
    # Testi läbiviimise nõusolekud avalikus vaates
    add_resource_handler(config,'nousolek', 'nousolekud',
                 'eis.handlers.avalik.nousolekud.nousolekud:NousolekudController')
    

    # Testi protokolli koostamine
    add_resource_handler(config,'helifail', 'helifailid',
                 'eis.handlers.avalik.protokollid.helifailid:HelifailidController',
                 path_prefix='protokoll/{toimumisprotokoll_id}',
                 name_prefix='protokoll_')
    add_resource_handler(config,'turvakott', 'turvakotid',
                 'eis.handlers.avalik.protokollid.turvakotid:TurvakotidController',
                 path_prefix='protokoll/{toimumisprotokoll_id}',
                 name_prefix='protokoll_')
    add_resource_handler(config,'ruumifail', 'ruumifailid',
                 'eis.handlers.avalik.protokollid.ruumifailid:RuumifailidController',
                 path_prefix='protokoll/{toimumisprotokoll_id}',
                 name_prefix='protokoll_')
    add_resource_handler(config,'kinnitamine1', 'kinnitamine',
                 'eis.handlers.avalik.protokollid.kinnitamine:KinnitamineController',
                 path_prefix='protokoll/{toimumisprotokoll_id}',
                 name_prefix='protokoll_')

    # erivajadused
    add_resource_handler(config,'erivajadus', 'erivajadused', 
                 'eis.handlers.avalik.erivajadused.erivajadused:ErivajadusedController')


    # rahvusvaheliste eksamite tunnistused - kooli päring
    add_resource_handler(config,'rvtunnistus', 'rvtunnistused', 
                         'eis.handlers.avalik.rvtunnistused.rvtunnistused:RvtunnistusedController',
                         name_prefix='otsing_')

    # testitööde vaatamine (individuaalse õiguse olemasolul)
    add_resource_handler(config,'toovaatamine', 'toovaatamised',
                         'eis.handlers.avalik.toovaatamised.toovaatamised:ToovaatamisedController')
    add_handler(config, 'toovaatamine_osa', '/toovaatamine/{test_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/sooritus/{id}',
                 'eis.handlers.avalik.toovaatamised.sooritus:SooritusController',
                 action='show')
    add_task_handler(config,
                     'toovaatamine_osa_',
                     'eis.handlers.avalik.toovaatamised.sooritus:SooritusController',
                     'toovaatamine/{test_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/s/{id:\d+}')
        
    add_resource_handler(config,'toofail', 'toofailid', 
                         'eis.handlers.avalik.toofailid.toofailid:ToofailidController')

    # EKK toe ligipääs avaliku vaate kasutajate testinimekirjadele
    add_handler(config, 'testinimekirjad', '/testinimekirjad',
                'eis.handlers.avalik.testinimekirjad.testinimekirjad:TestinimekirjadController',
                action='index',
                request_method='GET')

    
def make_map_avalik_ktulemused(config, is_live, is_test):
    "Avalikus vaates tulemuste vaatamine koolile"
    # testide loetelu
    add_resource_handler(config,'ktulemus', 'ktulemused', 
                         'eis.handlers.avalik.ktulemused.testid:TestidController')
    add_resource_handler(config,'kirjeldus1', 'kirjeldus', 
                         'eis.handlers.avalik.ktulemused.kirjeldus:KirjeldusController',
                         path_prefix='ktulemused/{test_id}/k{kursus:\w*}/{testimiskord_id}',
                         name_prefix='ktulemused_')
    add_resource_handler(config,'osaleja', 'osalejad', 
                         'eis.handlers.avalik.ktulemused.osalejad:OsalejadController',
                         path_prefix='ktulemused/{test_id}/k{kursus:\w*}/{testimiskord_id}',
                         name_prefix='ktulemused_')
    add_resource_handler(config,'gruppidetulemus', 'gruppidetulemused', 
                         'eis.handlers.avalik.ktulemused.gruppidetulemused:GruppidetulemusedController',
                         path_prefix='ktulemused/{test_id}/k{kursus:\w*}/{testimiskord_id}',
                         name_prefix='ktulemused_')
    add_resource_handler(config,'osalejatetulemus', 'osalejatetulemused', 
                         'eis.handlers.avalik.ktulemused.osalejatetulemused:OsalejatetulemusedController',
                         path_prefix='ktulemused/{test_id}/k{kursus:\w*}/{testimiskord_id}',
                         name_prefix='ktulemused_')
    add_resource_handler(config,'valimitulemus', 'valimitulemused', 
                         'eis.handlers.avalik.ktulemused.valimitulemused:ValimitulemusedController',
                         path_prefix='ktulemused/{test_id}/k{kursus:\w*}/{testimiskord_id}',
                         name_prefix='ktulemused_')

    # tulemuste saatmine õpilastele (dialoogiaknas)
    add_resource_handler(config,'saatmine', 'saatmised', 
                         'eis.handlers.avalik.ktulemused.saatmine:SaatmineController',
                         path_prefix='ktulemused/{test_id}/k{kursus:\w*}/{testimiskord_id}/osalejad',
                         name_prefix='ktulemused_osalejad_')

    add_handler(config,
                'ktulemused_diagrammtunnus',
                '/ktulemused/{dummypath:.*}/tunnused.png',
                'eis.handlers.ekk.testid.diagrammtunnus:DiagrammtunnusController',
                action='index')
    add_handler(config,
                'ktulemused_diagrammhinnang',
                '/ktulemused/{dummypath:.*}/hinnang.png',
                'eis.handlers.ekk.testid.diagrammhinnang:DiagrammhinnangController',
                action='index')

    # tehtud testiosa vaatamise lehe avamine
    add_resource_handler(config, 'osa', 'osad', 
                          'eis.handlers.avalik.ktulemused.sooritus:SooritusController',
                          path_prefix='ktulemused/{test_id:\d+}/k{kursus:\w*}/{testimiskord_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}',
                          name_prefix='ktulemused_')
    add_task_handler(config,
                     'ktulemused_osa_',
                     'eis.handlers.avalik.ktulemused.sooritus:SooritusController',
                     'ktulemused/{test_id:\d+}/k{kursus:\w*}/{testimiskord_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/s/{id:\d+}')
    
    # õpetaja vaatab õpilase tagasisidevormi
    add_resource_handler(config, 'opetajatulemus', 'opetajatulemused', 
                          'eis.handlers.avalik.ktulemused.opetajatulemus:OpetajatulemusController',
                          path_prefix='ktulemused/{test_id:\d+}/k{kursus:\w*}/{testimiskord_id:\d+}',
                          name_prefix='ktulemused_',
                          slash=True)
    add_resource_handler(config, 'opilasetulemus', 'opilasetulemused', 
                          'eis.handlers.avalik.ktulemused.opilasetulemus:OpilasetulemusController',
                          path_prefix='ktulemused/{test_id:\d+}/k{kursus:\w*}/{testimiskord_id:\d+}',
                          name_prefix='ktulemused_',
                          slash=True)

def make_map_avalik_sooritamine(config):

    # testi sooritamiseks testiosa avamine - POST (GET suunatakse alustamise lehele)
    add_handler(config,
               'sooritamine_alusta_osa',
               'sooritamine/{test_id}/{testiosa_id}/s/{id}/alusta',
               'eis.handlers.avalik.sooritamine.sooritus:SooritusController',
               action='alusta')
    add_handler(config,
               'sooritamine_jatka_osa',
               'sooritamine/{test_id}/{testiosa_id}/s/{id}/jatka',
               'eis.handlers.avalik.sooritamine.sooritus:SooritusController',
               action='jatka')

    add_resource_handler(config, 'osa', 'osad',
                         'eis.handlers.avalik.sooritamine.sooritus:SooritusController',
                         path_prefix='sooritamine/{test_id:\d+}/{testiosa_id:\d+}',
                         path_id='sooritamine/{test_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/s/{id}',
                         name_prefix='sooritamine_')
    add_task_handler(config,
                     'sooritamine_osa_',
                     'eis.handlers.avalik.sooritamine.sooritus:SooritusController',
                     'sooritamine/{test_id:\d+}/{testiosa_id:\d+}-{alatest_id:\d*}/s/{id}')

    # helisalvestamise sisuplokis helifaili üleslaadimine,
    # kõigi failina antud vastuste allalaadimine
    add_resource_handler(config,'vastusfail', 'vastusfailid', 
                 'eis.handlers.avalik.sooritamine.vastusfailid:VastusfailidController',
                 path_prefix='sooritamine/{test_id}/{testiosa_id}/s/{sooritus_id}',
                 name_prefix='sooritamine_')    

def make_map_avalik_tooylesanne(config):

    add_resource_handler(config, 'tooylesanne', 'tooylesanded',
                         'eis.handlers.avalik.sooritamine.tooylesanded:TooylesandedController',
                         path_prefix='sooritamine/{test_id:\d+}/t/{sooritus_id:\d+}',
                         name_prefix='sooritamine_')
    add_task_handler(config,
                     'sooritamine_tooylesanded_',
                     'eis.handlers.avalik.sooritamine.tooylesanded:TooylesandedController',
                     editpath='sooritamine/{test_id:\d+}/t/{sooritus_id}/tooylesanne/{id}',
                     updatepath='sooritamine/{test_id:\d+}/t/{sooritus_id}/tooylesanne/{id}/{yv_id:\d+}')

def make_map_avalik_regamine(config):
   
    # Registreerimine - otsing ja registreeringu vaatamine/muutmine
    add_resource_handler(config,'regamine', 'regamised', 
                 'eis.handlers.avalik.regamine.regamised:RegamisedController')

    # avalduse sisestamiselt pangalingis käimine
    add_handler(config, 'regamine_avaldus_pangalink',
                       '/regamised/avaldus/pangalink/{pank_id}',
                       'eis.handlers.avalik.regamine.pangalink:PangalinkController',
                       action='new',
                       request_method='GET')
    add_handler(config, 'regamine_avaldus_return_pangalink_post',
                '/regamised/avaldus/pangalink/{pank_id}/return',
                'eis.handlers.avalik.regamine.pangalink:PangalinkController',
                action='returned_post',
                request_method='POST')
    add_handler(config, 'regamine_avaldus_return_pangalink',
                '/regamised/avaldus/pangalink/{pank_id}/return',
                'eis.handlers.avalik.regamine.pangalink:PangalinkController',
                action='returned',
                request_method='GET')

    # sooritaja kirjelt pangalingis käimine
    add_handler(config, 'regamine_pangalink',
                       '/regamised/{sooritaja_id}/pangalink/{pank_id}',
                       'eis.handlers.avalik.regamine.pangalink:PangalinkController',
                       action='new',
                       request_method='GET')
    add_handler(config, 'regamine_return_pangalink_post',
                '/regamised/{sooritaja_id}/pangalink/{pank_id}/return',
                'eis.handlers.avalik.regamine.pangalink:PangalinkController',
                action='returned',
                request_method='POST')
    add_handler(config, 'regamine_return_pangalink',
                '/regamised/{sooritaja_id}/pangalink/{pank_id}/return',
                'eis.handlers.avalik.regamine.pangalink:PangalinkController',
                action='returned',
                request_method='GET')

    # Registreerimisavalduse sisestamine
    add_handler(config, 'regamine_avaldus_isikuandmed', 
                       '/regamine/avaldus/isikuandmed/{testiliik:[a-zA-Z]+}',
                       'eis.handlers.avalik.regamine.avaldus.isikuandmed:IsikuandmedController',
                       action='index',
                       request_method='GET')
    add_handler(config, 'regamine_create_avaldus', 
                       '/regamine/avaldus/{testiliik:[a-zA-Z]+}',
                       'eis.handlers.avalik.regamine.avaldus.isikuandmed:IsikuandmedController',
                       action='create',
                       request_method='POST')

    # testide valimise vorm enne testiliigi valimist
    add_handler(config, 'regamine_avaldus_testid', 
                       '/regamine/avaldus/testid',
                       'eis.handlers.avalik.regamine.avaldus.testid:TestidController',
                       action='index',
                       request_method='GET')
    # kindla testiliigi ja testiga regama suunamise URL
    add_handler(config, 'regamine_avaldus_testid_test', 
                       '/regamine/avaldus/test/{test_id:\d+}',
                       'eis.handlers.avalik.regamine.avaldus.testid:TestidController',
                       action='index',
                       request_method='GET')
    # kindla testiliigiga regama suunamise URL
    add_handler(config, 'regamine_avaldus_testid_testiliik', 
                       '/regamine/avaldus/testid/{testiliik:[a-zA-Z]+}',
                       'eis.handlers.avalik.regamine.avaldus.testid:TestidController',
                       action='index',
                       request_method='GET')

    # tyhistamise nupuga testide valikusse saabumine
    add_handler(config, 'regamine_avaldus_tyhista', 
                       '/regamine/avaldus/tyhista/{testiliik:[a-zA-Z]+}',
                       'eis.handlers.avalik.regamine.avaldus.testid:TestidController',
                       action='tyhista',
                       request_method='GET')
    
    # testide valiku salvestamine
    add_handler(config, 'regamine_avaldus_create_testid', 
                       '/regamine/avaldus/testid/{testiliik:[a-zA-Z]+}',
                       'eis.handlers.avalik.regamine.avaldus.testid:TestidController',
                       action='create',
                       request_method='POST')
    # testi eemaldamine
    add_handler(config, 'regamine_avaldus_delete_test', 
                       '/regamine/avaldus/testid/{testiliik:[a-zA-Z]+}/{id:\d+}/delete/{sooritaja_id:\d+}',
                       'eis.handlers.avalik.regamine.avaldus.testid:TestidController',
                       action='delete',
                       request_method='POST') # DELETE

    # avalduse kinnitamisvorm
    add_handler(config, 'regamine_avaldus_kinnitamine', 
                       '/regamine/avaldus/kinnitamine/{testiliik:[a-zA-Z]+}',
                       'eis.handlers.avalik.regamine.avaldus.kinnitamine:KinnitamineController',
                       action='index',
                       request_method='GET')
    # avalduse kinnitamine
    add_handler(config, 'regamine_avaldus_create_kinnitamine', 
                       '/regamine/avaldus/kinnitamine/{testiliik:[a-zA-Z]+}',
                       'eis.handlers.avalik.regamine.avaldus.kinnitamine:KinnitamineController',
                       action='create',
                       request_method='POST')
    add_handler(config, 'regamine_avaldus_kinnitatud', 
                       '/regamine/avaldus/kinnitatud/{testiliik:[a-zA-Z]+}',
                       'eis.handlers.avalik.regamine.avaldus.kinnitamine:KinnitamineController',
                       action='kinnitatud',
                       request_method='GET')

    # regamise katkestamine
    add_handler(config, 'regamine_avaldus_delete_kinnitamine', 
                 '/regamine/avaldus/kinnitamine/{testiliik:[a-zA-Z]+}/delete',
                 'eis.handlers.avalik.regamine.avaldus.kinnitamine:KinnitamineController',
                 action='delete',
                 request_method='POST')

def make_map_avalik_testid(config, is_live, is_test):
    "Avaliku vaate testid"
    # avalikus vaates testide koostamine

    # testi yldandmed
    add_sub_handler(config, 'testid', 'yldandmed', 'eis.handlers.avalik.testid.yldandmed:YldandmedController', id2='testiruum_id')
    add_resource_handler(config,'test', 'testid', 'eis.handlers.avalik.testid.testid:TestidController')

    # testi struktuuri lehekülg
    add_sub_handler(config, 'testid', 'struktuur', 'eis.handlers.avalik.testid.struktuur:StruktuurController', id2='testiruum_id')
    # töökogumikust valitud ylesannete/testi jagamine sooritamiseks
    add_handler(config, 'test_tknimekiri',
                '/testid/tknimekiri',
                'eis.handlers.avalik.testid.tknimekiri:TknimekiriController',
                action='create',
                request_method='POST')
    
    # testiga seotud isikud (omanikud)
    add_resource_handler(config,'isik',
                 'isikud',
                 'eis.handlers.avalik.testid.isikud:IsikudController',
                 path_prefix='testid/{test_id}/{testiruum_id}',
                 name_prefix='test_')
    # testile ülesannete lisamine
    add_resource_handler(config, 'ylesanne', 'ylesanded',
                         'eis.handlers.avalik.testid.ylesanded:YlesandedController',
                         path_prefix='testid/{test_id}/{testiruum_id}',
                         name_prefix='test_')
    add_resource_handler(config, 'otsiylesanne', 'otsiylesanded',
                         'eis.handlers.avalik.testid.otsiylesanded:OtsiylesandedController',
                         path_prefix='testid/{test_id}/{testiruum_id}',
                         name_prefix='test_')
    add_resource_handler(config, 'otsiylesandekogu', 'otsiylesandekogud',
                         'eis.handlers.avalik.testid.otsiylesandekogud:OtsiylesandekogudController',
                         path_prefix='testid/{test_id}/{testiruum_id}',
                         name_prefix='test_')        
    add_resource_handler(config, 'otsitookogumik', 'otsitookogumikud',
                         'eis.handlers.avalik.testid.otsitookogumikud:OtsitookogumikudController',
                         path_prefix='testid/{test_id}/{testiruum_id}',
                         name_prefix='test_')        
    
    # testi lahendamise eelvaade: testiosa sooritamise lehe avamine
    add_resource_handler(config,'eelvaade', 'eelvaated', 
                 'eis.handlers.avalik.testid.eelvaade:EelvaadeController',
                 path_prefix='testid/{test_id}/{testiruum_id}/{testiosa_id:\d*}-{e_komplekt_id:[L\d]*}-{alatest_id:\d*}',
                 name_prefix='test_')    
    add_task_handler(config,
                     'test_eelvaade',
                     'eis.handlers.avalik.testid.eelvaade:EelvaadeController',
                     'testid/{test_id}/{testiruum_id}/{testiosa_id:\d+}-{e_komplekt_id:[L\d]*}-{alatest_id:\d*}/eelvaade/{id:-?\d+}')
    
    # testimiskorrata testi statistika avalikus vaates
    add_resource_handler(config,'avanalyys1', 'avanalyys', 
                 'eis.handlers.avalik.testid.avanalyys:AvanalyysController',
                 path_prefix='testid/{test_id}/{testiruum_id}',                 
                 name_prefix='test_',
                 slash=True)        
    add_handler(config, 
                 'test_avanalyys_image_p',
                 '/testid/{test_id}/{testiruum_id}/avanalyys/{vy_id}/{path:.*}images{args:[^/]*}/{filename:.+}',
                 'eis.handlers.avalik.testid.images:ImagesController',
                 action='images')            
    add_handler(config, 
                 'test_avanalyys_image_pp',
                 '/testid/{test_id}/{testiruum_id}/avanalyys/images{args:[^/]*}/{filename:.+}',
                 'eis.handlers.avalik.testid.images:ImagesController',
                 action='images')            
    add_resource_handler(config,'kvstatistika', 'kvstatistikad', 
                 'eis.handlers.avalik.testid.analyyskvstatistikad:AnalyyskvstatistikadController',
                 path_prefix='testid/{test_id}/{testiruum_id}/analyys/{kst_id}',                 
                 name_prefix='test_analyys_')        
    add_resource_handler(config, 'maatriks', 'maatriksid',
                'eis.handlers.avalik.testid.analyysmaatriksid:AnalyysmaatriksidController', 
                path_prefix='testid/{test_id}/{testiruum_id}/avanalyys/vastused/kysimus/{kysimus_id}',
                name_prefix='test_analyys_vastused_kysimus_')


    
    add_resource_handler(config,'nimekiri', 'nimekirjad', 
                 'eis.handlers.avalik.testid.testinimekirjad:TestinimekirjadController',
                 path_prefix='testid/{test_id}/{testiruum_id}',
                 name_prefix='test_')
    add_resource_handler(config,'sooritaja', 'sooritajad', 
                 'eis.handlers.avalik.testid.sooritajad:SooritajadController',
                 path_prefix='testid/{test_id}/nimekiri/{nimekiri_id}',
                 name_prefix='test_nimekiri_')
    add_resource_handler(config,'otsisooritaja', 'otsisooritajad', 
                 'eis.handlers.avalik.testid.otsisooritajad:OtsisooritajadController',
                 path_prefix='testid/{test_id}/nimekiri/{nimekiri_id}',
                 name_prefix='test_nimekiri_')
    add_resource_handler(config,'otsiadmin', 'otsiadminid', 
                 'eis.handlers.avalik.testid.otsiadminid:OtsiadminidController',
                 path_prefix='testid/{test_id}/nimekiri/{nimekiri_id}/testiruum/{testiruum_id}',
                 name_prefix='test_nimekiri_')
    add_resource_handler(config,'otsihindaja', 'otsihindajad', 
                 'eis.handlers.avalik.testid.otsihindajad:OtsihindajadController',
                 path_prefix='testid/{test_id}/nimekiri/{nimekiri_id}/testiruum/{testiruum_id}',
                 name_prefix='test_nimekiri_')
    add_resource_handler(config,'kanne', 'kanded',
                 'eis.handlers.avalik.testid.kanne:KanneController',
                 path_prefix='testid/{test_id}/{testiruum_id}/nimekiri/{nimekiri_id}',
                 name_prefix='test_nimekiri_')
    add_resource_handler(config,'tugiisik', 'tugiisikud',
                 'eis.handlers.avalik.testid.tugiisik:TugiisikController',
                 path_prefix='testid/{test_id}/{testiruum_id}/nimekiri/{nimekiri_id}/sooritaja/{sooritaja_id}',
                 name_prefix='test_nimekiri_kanne_')

    # avaliku vaate testi läbiviimine
    #add_sub_handler(config, 'testid', 'labiviimine', 'eis.handlers.avalik.testid.labiviimine:LabiviimineController', id2='testiruum_id')    
    add_resource_handler(config,'labiviimine', 'labiviimised', 
                         'eis.handlers.avalik.testid.labiviimine:LabiviimineController',
                         path_prefix='testid/{test_id}',
                         name_prefix='testid_')
    
    # kutseeksami protokoll
    add_resource_handler(config,'protokoll1', 'protokoll',
                 'eis.handlers.avalik.testid.protokoll.ProtokollController',
                 path_prefix='/testid/{test_id}/{testiruum_id}',
                 name_prefix='test_')
    
    # avalikus vaates koostatud testi tulemused
    add_resource_handler(config,'avtulemus', 'avtulemused',
                 'eis.handlers.avalik.testid.avtulemused:AvtulemusedController',
                 path_prefix='testid/{test_id}/{testiruum_id}',
                 name_prefix='test_')
    add_resource_handler(config,'avylesanne', 'avylesanded',
                 'eis.handlers.avalik.testid.avylesanded:AvylesandedController',
                 path_prefix='testid/{test_id}/{testiruum_id}',
                 name_prefix='test_')


    # ylesannete kaupa hindamine
    add_resource_handler(config,'ylesandehindamine', 'ylesandehindamised',
                 'eis.handlers.avalik.thindamine.ylesandehindamised:YlesandehindamisedController',
                 path_prefix='testid/{test_id}/{testiruum_id}',
                 name_prefix='test_')
    add_resource_handler(config,'hindamine', 'hindamised',
                 'eis.handlers.avalik.thindamine.ylesandehindamine:YlesandehindamineController',
                 path_prefix='testid/{test_id}/{testiruum_id}/vy/{vy_id}',
                 name_prefix='test_ylesanne_')
    add_task_handler(config,
                     'test_ylesanne_hindamine_',
                     'eis.handlers.avalik.thindamine.ylesandehindamine:YlesandehindamineController',
                     editpath='testid/{test_id}/{testiruum_id}/{id:\d+}/ty/{ty_id:\d+}/{vy_id:\d+}',
                     updatepath='testid/{test_id}/{testiruum_id}/{id:\d+}/ty/{ty_id:\d+}/{vy_id:\d+}/{ylesanne_id:\d+}')

    # tööde kaupa hindamine
    add_resource_handler(config,'toohindamine', 'toohindamised',
                 'eis.handlers.avalik.thindamine.toohindamised:ToohindamisedController',
                 path_prefix='testid/{test_id}/{testiruum_id}',
                 name_prefix='test_')
    add_resource_handler(config,'hindamine', 'hindamised',
                 'eis.handlers.avalik.thindamine.toohindamine:ToohindamineController',
                 path_prefix='testid/{test_id}/{testiruum_id}/toohindamine/{sooritus_id}',
                 name_prefix='test_sooritus_')
    add_task_handler(config,
                     'test_sooritus_hindamine_',
                     'eis.handlers.avalik.thindamine.toohindamine:ToohindamineController',
                     path='testid/{test_id}/{testiruum_id}/toohindamine/{sooritus_id:\d+}')
    

    # hindaja parempoolse ekraaniosa sakid:
    # ülesande lahendamine
    add_resource_handler(config,'lahendamine', 'lahendamised',
                 'eis.handlers.avalik.thindamine.lahendamine:LahendamineController',
                 path_prefix='testid/{test_id}/{testiruum_id}/{vy_id}',
                 name_prefix='test_hindamine_')
    add_task_handler(config,
                     'test_hindamine_lahendamine_',
                     'eis.handlers.avalik.thindamine.lahendamine:LahendamineController',
                     editpath='testid/{test_id}/{testiruum_id}/{vy_id:\d+}/lahendamine/{id:\d+}',
                     updatepath='testid/{test_id}/{testiruum_id}/{vy_id:\d+}/lahendamine/{id:\d+}')
    
    # hindamisjuhendid
    add_resource_handler(config, 'juhend', 'juhendid',
                 'eis.handlers.avalik.thindamine.juhend:JuhendController',
                 path_prefix='testid/{test_id}/{testiruum_id}/{vy_id}',
                 name_prefix='test_hindamine_')


    # lahendaja lahenduse vaatamine
    add_handler(config, 'test_labiviimine_sooritus',
                '/testid/{test_id}/{testiruum_id}/sooritus/{id:\d+}',
                 'eis.handlers.avalik.testid.sooritus:SooritusController',
                 action='show')
    add_handler(config, 'test_labiviimine_sooritus_format',
                '/testid/{test_id}/{testiruum_id}/sooritus/{id:\d+}.{format}',
                 'eis.handlers.avalik.testid.sooritus:SooritusController',
                 action='download')
    add_handler(config, 'test_labiviimine_alatestisooritus',
                '/testid/{test_id}/{testiruum_id}/sooritus/{id}/{alatest_id}',
                 'eis.handlers.avalik.testid.sooritus:SooritusController',
                 action='show')
    add_task_handler(config,
                     'test_labiviimine_sooritus_',
                     'eis.handlers.avalik.testid.sooritus:SooritusController',
                     path='testid/{test_id:\d+}/{testiruum_id:\d+}-{alatest_id:\d*}/sooritus/{id:\d+}')

    # lahendaja lahenduse vaatamine dialoogiaknas
    add_handler(config, 'test_labiviimine_sooritusaknas', '/testid/{test_id}/{testiruum_id}/sooritusaknas/{id:\d+}',
                 'eis.handlers.avalik.testid.sooritusaknas:SooritusaknasController',
                 action='show')
    add_handler(config, 'test_labiviimine_sooritusaknas_format', '/testid/{test_id}/{testiruum_id}/sooritusaknas/{id:\d+}.{format}',
                 'eis.handlers.avalik.testid.sooritusaknas:SooritusaknasController',
                 action='download')
    add_handler(config, 'test_labiviimine_alatestisooritusaknas', '/testid/{test_id}/{testiruum_id}/sooritusaknas/{id}/{alatest_id}',
                 'eis.handlers.avalik.testid.sooritusaknas:SooritusaknasController',
                 action='show')
    add_task_handler(config,
                     'test_labiviimine_sooritusaknas_',
                     'eis.handlers.avalik.testid.sooritusaknas:SooritusaknasController',
                     path='testid/{test_id:\d+}/{testiruum_id:\d+}-{alatest_id:\d*}/sooritusaknas/{id:\d+}')

    # koolispyhholoogi õpilaste tulemused
    add_resource_handler(config,'psyhtulemus', 'psyhtulemused', 
                         'eis.handlers.avalik.testid.psyhtulemus:PsyhtulemusController',
                         path_prefix='testid/{test_id}/{testiruum_id}',
                         name_prefix='test_')

    # koolispyhholoogi õpilaste tulemused
    add_resource_handler(config,'psyhtulemus', 'psyhtulemused', 
                         'eis.handlers.avalik.psyhtulemused.psyhtulemused:PsyhtulemusedController')

    # koolipsyhholoogi testide otsimine ja lisamine
    add_handler(config,'psyhtestid', '/psyhtestid',
                'eis.handlers.avalik.psyhtulemused.psyhtestid:PsyhtestidController',
                action='index')
    
    # indeks, mis viitab õigele vormile
    add_handler(config, 'test_tulemused', '/testid/{test_id}/{testiruum_id}/tulemused', 
                'eis.handlers.avalik.testid.tulemused:TulemusedController', 
                action='index')
    
    # diagnoosiva testi tyyp 2 tulemused
    add_resource_handler(config,'tagasiside1', 'tagasiside', 
                         'eis.handlers.avalik.testid.tagasiside:TagasisideController',
                         path_prefix='testid/{test_id}/{testiruum_id}',
                         name_prefix='test_')
    # jagatud töö tulemused
    add_resource_handler(config,'tootulemus', 'tootulemused', 
                         'eis.handlers.avalik.testid.tootulemused:TootulemusedController',
                         path_prefix='testid/{test_id}/{testiruum_id}',
                         name_prefix='test_')

    # töökogumikud
    add_resource_handler(config, 'tookogumik', 'tookogumikud',
                         'eis.handlers.avalik.tookogumikud.tookogumikud:TookogumikudController')
    # ylesandekogude otsing
    add_resource_handler(config, 'ylesandekogu', 'ylesandekogud',
                         'eis.handlers.avalik.tookogumikud.ylesandekogud:YlesandekogudController',
                         path_prefix='tookogumik',
                         name_prefix='tookogumik_')        
    # testide otsing
    add_resource_handler(config, 'testiotsing1', 'testiotsing',
                         'eis.handlers.avalik.tookogumikud.testiotsing:TestiotsingController',
                         path_prefix='tookogumik',
                         name_prefix='tookogumik_')        
    # ylesannete detailotsing
    add_resource_handler(config, 'ylesandeotsing1', 'ylesandeotsing',
                         'eis.handlers.avalik.tookogumikud.ylesandeotsing:YlesandeotsingController',
                         path_prefix='tookogumik',
                         name_prefix='tookogumik_')        
    # jagamiste otsing otsing
    add_resource_handler(config, 'jagamine', 'jagamised',
                         'eis.handlers.avalik.tookogumikud.jagamised:JagamisedController',
                         path_prefix='tookogumik',
                         name_prefix='tookogumik_')        

    add_resource_handler(config, 'otsivaataja', 'otsivaatajad',
                         'eis.handlers.avalik.tookogumikud.otsivaatajad:OtsivaatajadController',
                         path_prefix='tookogumik/{tookogumik_id}',
                         name_prefix='tookogumik_')        

    add_resource_handler(config, 'opperyhm', 'opperyhmad',
                         'eis.handlers.avalik.opperyhmad.opperyhmad:OpperyhmadController')
    add_resource_handler(config,'otsiopilane', 'otsiopilased', 
                         'eis.handlers.avalik.opperyhmad.otsiopilased:OtsiopilasedController',
                         path_prefix='opperyhm/{opperyhm_id}',
                         name_prefix='opperyhm_')

def make_map_pangalink_test(config):
    # pangalingi testimine
    add_handler(config, 'admin_pangalinktestid',
                       '/admin/pangalinktestid',
                       'eis.handlers.avalik.regamine.pangalinktest:PangalinkTestController',
                       action='index',
                       request_method='GET')
    add_handler(config, 'admin_pangalinktest',
                       '/admin/pangalinktest/{pank_id}',
                       'eis.handlers.avalik.regamine.pangalinktest:PangalinkTestController',
                       action='new',
                       request_method='GET')
    # pangast vahetult POST-päringuga tulnud vastus, ilma seansi kypsisteta
    add_handler(config, 'admin_return_pangalinktest_post',
                       '/admin/pangalinktest/{pank_id}/return',
                       'eis.handlers.avalik.regamine.pangalinktest:PangalinkTestController',
                       action='returned_post',
                       request_method='POST')
    # panga vastus koos seansi kyspsistega
    add_handler(config, 'admin_return_pangalinktest',
                       '/admin/pangalinktest/{pank_id}/return',
                       'eis.handlers.avalik.regamine.pangalinktest:PangalinkTestController',
                       action='returned',
                        request_method='GET')
    
def make_map_avalik(config, is_live, is_test):
    make_map_avalik_eksam(config, is_live, is_test)
    make_map_avalik_ylesanne(config)
    make_map_pangalink_test(config)
    
    # Soorituskoha andmed
    add_resource_handler(config,'koht', 'kohad', 'eis.handlers.avalik.admin.kohad:KohadController', 
                 path_prefix='/admin', name_prefix='admin_')
    add_resource_handler(config,'ruum', 'ruumid', 'eis.handlers.avalik.admin.ruumid:RuumidController', 
                 path_prefix='/admin/kohad/{koht_id}',
                 name_prefix='admin_koht_')
    add_resource_handler(config,'kasutaja', 'kasutajad', 'eis.handlers.avalik.admin.kohakasutajad:KohakasutajadController', 
                 path_prefix='/admin/kohad/{koht_id}',
                 name_prefix='admin_koht_')
    add_resource_handler(config,'oppekava', 'oppekavad', 'eis.handlers.avalik.admin.oppekavad:OppekavadController', 
                 path_prefix='/admin/kohad/{koht_id}',
                 name_prefix='admin_koht_')
    add_handler(config, 'kohteelvaade', '/kohteelvaade/{id}',
                'eis.handlers.avalik.kohteelvaade:KohteelvaadeController', action='show')
    
    # isikute otsimine dialoogiaknas soorituskohaga seostamiseks
    add_resource_handler(config,'isik', 'isikud',
                 'eis.handlers.avalik.admin.isikud:IsikudController',
                 path_prefix='admin/kohad/{koht_id}',
                 name_prefix='admin_koht_')

    # Testide läbiviimisega seotud isikud
    add_resource_handler(config,'kasutaja', 'kasutajad', 'eis.handlers.avalik.admin.kasutajad:KasutajadController', 
                          path_prefix='/admin', name_prefix='admin_')


    # Eksamite tulemuste statistika
    add_resource_handler(config,'eksamistatistik', 'eksamistatistika', 
                 'eis.handlers.avalik.eksamistatistika.eksamistatistika:EksamistatistikaController')
    add_handler(config,
                'eksamistatistika_riikliktagasiside',
                '/eksamistatistika/riikliktagasiside/{test_id:\d+}/k{kursus:\w*}/{aasta:\d+}',
                'eis.handlers.avalik.eksamistatistika.riikliktagasiside:RiikliktagasisideController',
                action='show')

    # tagasisidevormi tasemete kirjeldused (viidatakse tagasisidevormilt)
    add_handler(config, 'htunnused', '/htunnused/{aine}/klass/{klass}',
                'eis.handlers.avalik.htunnused:HtunnusedController',
                action='show')

    # legacy-teenusega sisenemise URL
    add_handler(config, 'legacy', '/legacy', 'eis.handlers.avalik.legacy:LegacyController', action='index')

    make_map_metadata(config)

def make_map_metadata(config):
    # metaandmed võrguliikluse analyysimiseks
    add_handler(config,
                'metadata_ylesanded',
                '/metadata/ylesanded.csv',
                'eis.handlers.avalik.metadata:MetadataHandler',
                action='ylesanded')
    add_handler(config,
                'metadata_ylesandeteemad',
                '/metadata/ylesandeteemad.csv',
                'eis.handlers.avalik.metadata:MetadataHandler',
                action='ylesandeteemad')
    add_handler(config,
                'metadata_testid',
                '/metadata/testid.csv',
                'eis.handlers.avalik.metadata:MetadataHandler',
                action='testid')
    add_handler(config,
                'metadata_testiylesanded',
                '/metadata/testiylesanded.csv',
                'eis.handlers.avalik.metadata:MetadataHandler',
                action='testiylesanded')
    add_handler(config,
                'metadata_klassifikaator',
                '/metadata/klassifikaator/{kood}.csv',
                'eis.handlers.avalik.metadata:MetadataHandler',
                action='klassifikaator')
        
def make_map_avalik_ylesanne(config):
    """Oma ylesannete koostamine avalikus vaates
    """
    add_handler(config, 'ylesanne_image_tran',
                 '/ylesanded/{ylesanne_id:\d+}/{dummypath:.+}/lang/{lang:..}/images{args:[^/]*}/{filename:.+}',
                'eis.handlers.avalik.ylesanded.images:ImagesController',
                action='images')        
    add_handler(config, 'ylesanne_image_p',
                 '/ylesanded/{ylesanne_id:\d+}/{dummypath:.+}/images{args:[^/]*}/{filename:.+}',
                'eis.handlers.avalik.ylesanded.images:ImagesController',
                action='images')        
    add_handler(config, 'ylesanne_image',
                '/ylesanded/{ylesanne_id:\d+}/images{args:[^/]*}/{filename:.+}',
                'eis.handlers.avalik.ylesanded.images:ImagesController',
                action='images')        
    
    add_resource_handler(config,'sisuplokk', 
                 'sisuplokid', 
                 'eis.handlers.avalik.ylesanded.sisuplokk:SisuplokkController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}/sisu',
                 name_prefix='ylesanne_')
    add_handler(config,
                'ylesanne_sisuplokk_showtool',
                'ylesanded/{ylesanne_id:\d+}/sisu/{id}/showtool-{task_id}/{vahend}',
                'eis.handlers.avalik.ylesanded.sisuplokk:SisuplokkController',
                action='showtool',
                request_method='GET')

    add_resource_handler(config, 'cwchar', 
                         'cwchars', 
                         'eis.handlers.avalik.ylesanded.cwchar:CwcharController',
                         path_prefix='ylesanded/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}',
                         name_prefix='ylesanne_sisuplokk_',
                         id_re='')
    add_resource_handler(config, 'kysimus', 
                         'kysimused', 
                         'eis.handlers.avalik.ylesanded.kysimus:KysimusController',
                         path_prefix='ylesanded/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}',
                         name_prefix='ylesanne_sisuplokk_',
                         id_re='')
    add_resource_handler(config, 'maatriks', 'maatriksid',
                'eis.handlers.avalik.ylesanded.hindamismaatriksid:HindamismaatriksidController', 
                path_prefix='ylesanne/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}/kysimus/{kysimus_id}',
                name_prefix='ylesanne_sisuplokk_kysimus_')

    add_resource_handler(config,'sisufail', 
                 'sisufailid', 
                 'eis.handlers.avalik.ylesanded.sisufail:SisufailController',
                 path_prefix='ylesanded',
                 name_prefix='ylesanne_')

    add_resource_handler(config,'taustobjekt', 
                 'taustobjektid', 
                 'eis.handlers.avalik.ylesanded.taustobjekt:TaustobjektController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}',
                 name_prefix='ylesanne_')
    add_resource_handler(config,'piltobjekt', 
                 'piltobjektid', 
                 'eis.handlers.avalik.ylesanded.piltobjekt:PiltobjektController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}/sisuplokid/{sisuplokk_id}',
                 name_prefix='ylesanne_')
    
    add_resource_handler(config, 'ylesanne', 'ylesanded',
                         'eis.handlers.avalik.ylesanded.ylesanded:YlesandedController') 
    add_sub_handler(config, 'ylesanded', 'sisu',
                    'eis.handlers.avalik.ylesanded.sisu:SisuController')
    add_sub_handler(config, 'ylesanded', 'editorsettings', 
                    'eis.handlers.avalik.ylesanded.editorsettings:EditorsettingsController')
    add_sub_handler(config, 'ylesanded', 'mathsettings', 
                    'eis.handlers.avalik.ylesanded.mathsettings:MathsettingsController')
    add_sub_handler(config, 'ylesanded', 'wmathsettings', 
                    'eis.handlers.avalik.ylesanded.wmathsettings:WmathsettingsController')

    add_handler(config, 'ylesanded_edit_lahendamine2',
                       '/ylesanded/{id:\d+}/lahendamine/',
                       'eis.handlers.avalik.ylesanded.lahendamine:LahendamineController',
                       action='edit')
    add_sub_handler(config, 'ylesanded', 'lahendamine',
                    'eis.handlers.avalik.ylesanded.lahendamine:LahendamineController')
    add_task_handler(config,
                     'ylesanded_lahendamine_',
                     'eis.handlers.avalik.ylesanded.lahendamine:LahendamineController',
                     editpath='ylesanded/{id:\d+}/lahendamine',
                     updatepath='ylesanded/{id:\d+}/lahendamine/{yv_id:\d+}') # temp

    add_handler(config, 'ylesanded_formatted_export',
                       '/ylesanded/{id:\d+}/export.{format}',
                       'eis.handlers.avalik.ylesanded.export:ExportController',
                       action='show',  
                       request_method='GET')

    add_resource_handler(config,'isik',
                          'isikud',
                          'eis.handlers.avalik.ylesanded.isikud:IsikudController',
                          path_prefix='ylesanded/{ylesanne_id}',
                          name_prefix='ylesanne_')

    add_resource_handler(config,'test', 'testid', 
                 'eis.handlers.avalik.ylesanded.testid:TestidController',
                 path_prefix='ylesanded/{ylesanne_id:\d+}',
                 name_prefix='ylesanded_')
