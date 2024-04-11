import sys
import fcntl
import os
import webob
from pyramid.i18n import make_localizer
import eiscore

class NewItem(object):
    """
    Uus objekt.
    Kasutatakse mako failis uue kirje loomise vormi moodustamisel
    uue kirje asemel (suvalise nimega atribuudi väärtus on tühi string)
    """
    def __init__(self, **attrs):
        for key in attrs:
            self.__setattr__(key, attrs[key])

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return ''

    def tran(self, lang, original_if_missing=True, versioon_id=None):
        if original_if_missing:
            return self

class MockRequest(object):
    def __init__(self, registry, settings):
        self.registry = registry
        self.url = 'http://localhost:6543/eis'
        self.params = webob.multidict.MultiDict()
        self.locale_name = 'et'
        self.remote_addr = '127.0.0.1'
        self.environ = {}
        self.is_ext = lambda: True
        path = os.path.dirname(os.path.realpath(eiscore.__file__))
        self.localizer = make_localizer(self.locale_name, [path + '/locale/'])

    def translate(self, tstring):
        return str(tstring)

class MockHandler(object):
    "Pseudo-kontroller"
    user = None
    form = None
    def __init__(self, registry, settings, model):
        #TmplContext = eis.lib.basehandler.TmplContext
        self.c = c = NewItem()
        #settings = registry.settings
        # vormil kasutatavad helper-funktsioonid
        #self.h = h = eis.lib.helpers.RequestHelpers(None, c, registry)
        # meetodite tyypvastus on dict, mis antakse mako mallile ette
        #self.resp_dict = dict(c=c, h=h, user=self.user)
        self.request = MockRequest(registry, settings)
        c.opt = model.Opt(self)
        
    def error(self, txt):
        print(txt)
