"URLide ruutimine kontrolleriteni"

import re
from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPFound
from eis.lib.exceptions import NotAuthorizedException, TooManyUsersException

route_args_by_name = {}
routes_by_handler = {}

def find_route_by_action(handler, action, namepart=None):
    """Ruutingu nime leidmine actioni järgi (kasulik sama kontrolleri teise tegevuse URLi leidmisel)"""
    routes = routes_by_handler.get(handler)
    if routes:
        found = None
        for name, route_action in routes.items():
            if route_action == action:
                if not namepart or namepart in name:
                    return name
                elif not found:
                    # eelistatakse nime, milles sisaldub namepart,
                    # aga selles nimes ei sisaldu
                    found = name
        return found

def find_action_by_name(handler, name):
    routes = routes_by_handler.get(handler)
    if routes:
        return routes.get(name)

def find_route_args(name):
    """URLis olevate argumentide loetelu leidmine (kasulik URLi moodustamisel)"""
    return route_args_by_name.get(name)
        
def save_route(name, path, handler, action):
    """Ruutingu loomisel jäetakse info meelde, et kontrollerites seda kasutada saaks."""
    
    # leiame parameetrid, mis URLi sisse käivad
    route_args = re.findall('{([^}]+)}',path)
    # eemaldame koolonijärgsed ('filename:.+')
    route_args2 = [arg.split(':')[0] for arg in route_args]

    # jätame ruutingu meelde
    route_args_by_name[name] = route_args2
    if handler not in routes_by_handler:
        routes_by_handler[handler] = {}
    routes_by_handler[handler][name] = action

def add_sub_handler(config, parent, subpage, handler, path_prefix=None, name_prefix=None, id2=None):
    """Ressursid, mille URLis on ID kontrollerist eespool
    ning mida see kontroller ise ei loo.
    """
    path_prefix = r'/%s/{id:\d+}' % (path_prefix or parent)
    if id2:
        path_prefix += '/{%s}' % (id2) 
    
    name_prefix = name_prefix or parent + '_'

    add_handler(config, '%s%s_format' % (name_prefix, subpage),
                 '%s/%s.{format}' % (path_prefix, subpage),
                 handler,
                 action='download',
                 request_method='GET')

    add_handler(config, '%s%s' % (name_prefix, subpage), 
                 '%s/%s' % (path_prefix, subpage), 
                 handler,
                 action='show',  
                 request_method='GET')
    
    # kuva sisu
    add_handler(config, '%sedit_%s' % (name_prefix, subpage), 
                 '%s/%s/edit' % (path_prefix, subpage), 
                 handler,
                 action='edit',  
                 request_method='GET')

    # salvesta muudatused
    add_handler(config, '%supdate_%s' % (name_prefix, subpage), 
                 '%s/%s' % (path_prefix, subpage), 
                 handler,
                 action='update',  
                 request_method='POST') # PUT
    
    # kustuta midagi
    add_handler(config, '%sdelete_%s' % (name_prefix, subpage),
                 '%s/%s/delete' % (path_prefix, subpage),
                 handler,
                 action='delete',  
                 request_method='POST') # DELETE
   
def add_resource_handler(config, item, items, handler, path_prefix='', name_prefix='', slash=False, slash2=False, id_re=r'-?\d+', post_path_prefix=None, format_re='', path_id=None):
    handler = config.maybe_dotted(handler)

    if path_prefix:
        path_prefix += '/'
    if post_path_prefix:
        post_path_prefix += '/'
    else:
        post_path_prefix = path_prefix
    if id_re:
        id_temp = 'id:%s' % id_re
    else:
        id_temp = 'id'

    if path_id:
        post_path_id = path_id
        download_path_id = path_id
    else:
        path_id = path_prefix + '%s/{%s}' % (items, id_temp)
        post_path_id = post_path_prefix + '%s/{%s}' % (items, id_temp)
        download_path_id = path_prefix + '%s/{id}' % (items)
        
    try:
        actions = handler._actions.split(',')
    except:
        actions = 'index,create,new,download,show,update,delete,edit'.split(',')

    if 'index' in actions:
        add_handler(config, '%s%s' % (name_prefix, items),
                    '%s%s' % (path_prefix, items),
                    handler,
                    action='index',
                    request_method='GET')
    if 'create' in actions:
        add_handler(config, '%screate_%s' % (name_prefix, items), # nimi pole RESTful!
                    '%s%s' % (post_path_prefix, items),
                    handler,
                    action='create',
                    request_method='POST')
    if 'new' in actions:
        add_handler(config, '%snew_%s' % (name_prefix, item),
                    '%s%s/new' % (path_prefix, items),
                    handler,
                    action='new',
                    request_method='GET')
        
    if format_re:
        format_temp = 'format:%s' % (format_re)
    else:
        format_temp = 'format'
    if 'download' in actions:
        add_handler(config, '%s%s_format' % (name_prefix, item),
                    '%s.{%s}' % (download_path_id, format_temp),
                    handler,
                    action='download',
                    request_method='GET')
        
    if 'downloadfile' in actions:
        # alamelemendi allalaadimine, millel on oma file_id
        add_handler(config, '%s%s_downloadfile' % (name_prefix, item),
                    '%s/{file_id}.{%s}' % (path_id, format_temp),
                    handler,
                    action='downloadfile',
                    request_method='GET')

    # osadel lehtedel on vaja, et show URLis oleks kaldkriips lõpus,
    # et saaks lehel suhtelisi URLe kasutada

    if 'show' in actions:
        route_name = '%s%s' % (name_prefix, item)
        add_handler(config, route_name,
                    path_id + (slash and '/' or ''),
                    handler,
                    action='show',
                    request_method='GET')
        # kaldkriipsuta lehed suuname ümber
        add_handler(config, '%sredirect_%s' % (name_prefix, item),
                    path_id + (not slash and '/' or ''),
                    handler,
                    action='show_redirect',
                    request_method='GET')
    if 'update' in actions:
        add_handler(config, '%supdate_%s' % (name_prefix, item),
                    post_path_id + ((slash or slash2) and '/' or ''),
                    handler,
                    action='update',
                    request_method='POST')
    if 'delete' in actions:
        add_handler(config, '%sdelete_%s' % (name_prefix, item), 
                    post_path_id + '/delete',
                    handler,
                    action='delete',
                    request_method='POST')
    if 'edit' in actions:
        add_handler(config, '%sedit_%s' % (name_prefix, item),
                    path_id + '/edit',
                    handler,
                    action='edit',
                    request_method='GET')

def add_task_handler(config, name, handler, path=None, editpath=None, updatepath=None):
    "Ülesannete sooritamise ja vaatamise kontroller"
    try:
        actions = handler._actionstask.split(',')
    except:
        actions = 'edittask,showtask,updatetask,correct,showtool,images,moredata'

    if not editpath:
        editpath = path + r'/ty/{ty_id:\d+}'
    if not updatepath:
        updatepath = editpath + r'/{vy_id:\d+}/{ylesanne_id:\d+}'

    if 'edittask' in actions:
        add_handler(config,
                    name + 'edittask',
                    editpath + '/edittask',
                    handler,
                    action='edittask',
                    request_method='GET')
    if 'showtask' in actions:
        add_handler(config,
                    name + 'showtask',
                    editpath + '/showtask',
                    handler,
                    action='showtask',
                    request_method='GET')
    if 'updatetask' in actions:
        add_handler(config,
                    name + 'updatetask',
                    updatepath + '/updatetask',
                    handler,
                    action='updatetask',
                    request_method='POST')
    if 'showtool' in actions:
        add_handler(config,
                    name + 'showtool',
                    editpath + '/showtool-{task_id}/{vahend}',
                    handler,
                    action='showtool',
                    request_method='GET')
    if 'correct' in actions:
        add_handler(config,
                    name + 'correct',
                    editpath + '/correct-{task_id}',
                    handler,
                    action='correct',
                    request_method='GET')
    add_handler(config,
                name + 'datafile',
                editpath + '/showtask/{task_id}/datafile/{filename:.+}',
                handler,
                action='datafile',
                request_method='GET')
    add_handler(config,
                name + 'images',
                editpath + '/showtask/{task_id}/images{args:[^/]*}/{filename:.+}',                    
                handler,
                action='images',
                request_method='GET')

def add_handler( config, name, path, handler, action=None, request_method=None, **kw):
    handler = config.maybe_dotted(handler)   
    save_route(name, path, handler, action)
    config.add_handler(name, path, handler, action=action, request_method=request_method, **kw)

def make_global_map(config, settings, app_name, is_live, is_test):
    """Kõigi rakenduste ühine ruuting
    """
    config.add_view('eis.handlers.error:httpfound', context=HTTPFound)
    config.add_view('eis.handlers.error:notfound', context=NotFound)    
    config.add_view('eis.handlers.error:notauthorized', context=NotAuthorizedException)
    config.add_view('eis.handlers.error:toomanyusers', context=TooManyUsersException)    

    if is_live:
        config.add_view('eis.handlers.error:error', context=Exception)

    add_handler(config, 'check', '/check', 'eis.handlers.index:IndexController', action='check')
    add_handler(config, 'locale', '/locale', 'eis.handlers.index:IndexController', action='locale')
    add_handler(config, 'locale2', '/locale/{locale}', 'eis.handlers.index:IndexController', action='locale')
    add_handler(config, 'dbgtest', '/sysinfo', 'eis.handlers.sysinfo:SysinfoController', action='index')
    #add_handler(config, 'dbgtest2', '/index/test2', 'eis.handlers.indextest:IndextestController', action='test2')
    add_handler(config, 'login_role', '/login/role/{role:[^/]*}', 'eis.handlers.login:LoginController', action='role')
    add_handler(config, 'login', '/login/{action}', 'eis.handlers.login:LoginController')    

    # abiinfo
    add_handler(config, 'update_abi', '/abi/{page_id}/{id}', 'eis.handlers.abi:AbiController', action='update',
                request_method='POST')
    add_handler(config, 'abi', '/abi/{page_id}/{id}', 'eis.handlers.abi:AbiController', action='index')
    add_handler(config, 'abi_title', '/abi/{page_id}', 'eis.handlers.abi:AbiController', action='index') # id=TITLE
    add_handler(config, 'edit_abi', '/abi_edit/{page_id}/{id}', 'eis.handlers.abi:AbiController', action='edit')
    add_handler(config, 'edit_abi_title', '/abi_edit/{page_id}', 'eis.handlers.abi:AbiController', action='edit')

    # klassifikaatorid
    add_handler(config, 'pub_formatted_valikud', '/pub/valikud/{kood}', 'eis.handlers.pub.valikud:ValikudController', action='index')
    add_handler(config, 'pub_piirkonnad', '/pub/piirkonnad', 'eis.handlers.pub.piirkonnad:PiirkonnadController', action='index')

    # toimumisaja testikohtade valik piirkonna järgi
    add_handler(config, 'pub_testikohad', '/pub/testikohad/{toimumisaeg_id}', 'eis.handlers.pub.testikohad:TestikohadController', action='index')

    # klassifikaatorirea kirjelduse küsimine AJAXiga
    add_handler(config, 'pub_valikud_kirjeldus',
                       '/pub/valikud/{klassifikaator_kood}/kirjeldus',
                       'eis.handlers.pub.valikud:ValikudController',
                       action='kirjeldus')

    # oma parooli muutmine
    add_handler(config,
                 'minu_parool',
                 '/minu/parool',
                 'eis.handlers.minu.parool:ParoolController',
                 action='index',
                 request_method='GET')
    add_handler(config,
                 'minu_parool_create',
                 '/minu/parool',
                 'eis.handlers.minu.parool:ParoolController',
                 action='create',
                 request_method='POST')                       

    # Minu andmed
    add_resource_handler(config,'anne', 'andmed', 
                         'eis.handlers.minu.minuandmed:MinuandmedController',
                         path_prefix='minu',
                         name_prefix='minu_',
                         id_re='')
    add_resource_handler(config,'teade', 'teated', 
                         'eis.handlers.minu.minuteated:MinuteatedController',
                         path_prefix='minu',
                         name_prefix='minu_',
                         id_re='')
    add_handler(config,
                'minu_kontaktuuendamine_index',
                '/minu/kontaktuuendamine',
                'eis.handlers.minu.kontaktuuendamine:KontaktuuendamineController',
                action='index',
                request_method='GET')
    add_handler(config,
                'minu_kontaktuuendamine',
                '/minu/kontaktuuendamine',
                'eis.handlers.minu.kontaktuuendamine:KontaktuuendamineController',
                action='create',
                request_method='POST')
    # add_resource_handler(config, 'kontaktuuendamine1', 'kontaktuuendamine',
    #             'eis.handlers.minu.kontaktuuendamine:KontaktuuendamineController',
    #             path_prefix='minu',
    #             name_prefix='minu_')
    
    # kysimused ja ettepanekud kasutajatoele
    add_resource_handler(config, 'ettepanek', 'ettepanekud',
                         'eis.handlers.avalik.ettepanekud:EttepanekudController')

    add_handler(config, 'kasutustingimused', '/kasutustingimused', 'eis.handlers.index:IndexController', action='kasutustingimused')        
    add_handler(config, 'cookieconsent', '/cookieconsent', 'eis.handlers.index:IndexController', action='cookieconsent')        
    add_handler(config, 'showcookieconsent', '/rmcconsent', 'eis.handlers.index:IndexController', action='showcookieconsent', request_method='GET')        
    add_handler(config, 'deletecookieconsent', '/rmcconsent', 'eis.handlers.index:IndexController', action='deletecookieconsent', request_method='POST')
    add_handler(config, 'emergency_close', '/emergency/{modified:[0-9\.]+}', 'eis.handlers.index:IndexController', action='emergency', request_method='POST')            

    add_resource_handler(config, 'seade', 'seaded', 'eis.handlers.seaded:SeadedController')

    if app_name == 'eis' or settings.get('devel') == 'true':
        # TARA autentimine
        config.add_route('tara_login', '/tara/login')        
        config.add_view('eis.handlers.logintara:LogintaraController', attr='login', route_name='tara_login')
        config.add_route('tara_tagasi', '/tara/tagasi')        
        config.add_view('eis.handlers.logintara:LogintaraController', attr='tagasi', route_name='tara_tagasi')        
        config.add_route('tara_katkes', '/tara/katkes')        
        config.add_view('eis.handlers.logintara:LogintaraController', attr='katkes', route_name='tara_katkes')

    # HarID autentimine
    config.add_route('harid_login', '/harid/login')        
    config.add_view('eis.handlers.loginharid:LoginharidController', attr='login', route_name='harid_login')
    config.add_route('harid_returned', '/harid/returned')        
    config.add_view('eis.handlers.loginharid:LoginharidController', attr='returned', route_name='harid_returned')        
    config.add_route('harid_canceled', '/harid/canceled')        
    config.add_view('eis.handlers.loginharid:LoginharidController', attr='canceled', route_name='harid_canceled')
