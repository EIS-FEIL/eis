"Vahekiht pylonsi seansi ja andmemudeli vahel, et mudel ei sõltuks pylonsist"

import threading
from eiscore.i18n import tsf
import eiscore.const as const

data = threading.local()

def get_threading_data():
    return data

def set_user(user):
    "Seansi kasutaja meeldejätmine andmemudeli jaoks"
    data.user = user

def get_user():
    "Seansi kasutaja"
    try:
        return data.user
    except AttributeError:
        pass

def get_userid():
    "Väärtus väljadele creator ja modifier"
    user = get_user()
    return user and user.isikukood or const.USER_NOT_AUTHENTICATED

def get_opt():
    "Valikute objekt"
    return data.user.handler.c.opt

def get_request():
    "Päringu objekt"
    user = get_user()
    if user:
        return user.handler.request

def get_lang():
    "Kasutajaliidese keel"
    return get_request().locale_name

def _(msgid, **kw):
    "Tõlkefunktsioon"
    request = data.user.handler.request
    return request.translate(tsf(msgid, **kw))

