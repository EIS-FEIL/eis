# -*- coding: utf-8 -*- 
"""Tõrkehaldus
"""
from eis.lib.base import *
_ = i18n._

def httpfound(exc, request):
    """
    Süsteemist visati HTTPFound teisele lehele suunamiseks
    """
    return exc

def notauthorized(exc, request):
    """
    Kasutaja proovis teha midagi, milleks tal polnud ligipääsuõigust.
    Nüüd näidatakse veateadet või avalehte või sisselogimisvormi või suunatakse kuhugi mujale.
    """
    model.Session.rollback()
    if exc.location == 'message':
        # vastus läheb dialoogiaknasse, kuvame ainult teate,
        # kujundust pole vaja
        return Response(exc.message)
    else:
        if exc.message:
            # teade kasutajale
            handler = ErrorController(request)
            handler.error(exc.message)
        if exc.location == 'avaleht':
            # kasutaja suunatakse avalehele
            handler = ErrorController(request)
            return HTTPFound(location=handler.url('avaleht'))            
        elif exc.location == 'login':
            # kasutaja suunatakse sisse logima
            handler = ErrorController(request)            
            # jätame meelde URLi, mida kasutaja tegelikult tahtis,
            # et peale autentimist ta sinna suunata saaks
            # eemaldame hosti nime, sest tegelik hostinimi erineb sõltuvalt sellest, 
            # kas autendib parooliga või id-kaardiga
            li = request.url.split('/')
            if len(li) > 3:
                handler.c.request_url = '/' + '/'.join(li[3:])
            else:
                handler.c.request_url = '/'
            handler.c.is_login_page = True
            # referer on vajalik siis, kui tullakse kohalikust eksamiserverist
            # see on kohaliku serveri aadress, kuhu kasutaja lõpuks tagasi suunatakse
            response = handler.render_to_response('minu/login.mako')
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        else:
            # kasutaja suunatakse sinna, kuhu vaja
            log.error('notauthorized, redirect to %s' % exc.location)
            return HTTPFound(location=exc.location)

def notfound(exc, request):
    """
    Pöördutakse vale URLi poole.
    """
    log.info(exc)
    model.Session.rollback()
    handler = ErrorController(request)
    response = handler.render_to_response('common/error404.mako')
    response.status = 404
    return response

def toomanyusers(exc, request):
    """
    Kasutajate arv on suurem kui kasutajale lubatud
    """
    log.info(exc)
    model.Session.rollback()
    handler = ErrorController(request)
    handler.error(_("Ressursid on hõivatud - palun pöördu hiljem tagasi"))
    log.error("Resources are busy (%s users, %s allowed)" % (exc.current, exc.allowed))
    return handler.render_to_response('toomanyusers.mako')

def error(exc, request):
    """
    Ilmnes ootamatu viga. Viga logitakse ja kasutajale näidatakse avalehte.
    Kasutatakse ainult siis, kui konfifailis ei ole debugimist määratud.
    """
    model.Session.rollback()
    #handler = ErrorController(request)
    handler = request.handler
    # repr(exc), exc.code, exc.detail
    if isinstance(exc, model.sa.exc.InternalError) and \
       'read-only transaction' in str(exc) and \
       request.session.get('kohteelvaade'):
        # eelvaates ei või andmebaasi salvestada
        error = _("Eelvaates ei saa andmeid muuta")
    else:
        msg = handler._error(exc)
        error = _("Tehniline probleem") + ' ' + msg
    return request.handler.response_on_error(error)

class ErrorController(BaseController):
    _authorize = False
    _is_error_controller = True    
