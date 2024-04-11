"""Vigadega tegelemine
"""
import logging
from webob.response import SCHEME_RE, url_quote, urlparse, bytes_
from pyramid.httpexceptions import HTTPFound as _HTTPFound

class HTTPFound(_HTTPFound):
    "Et HTTP suunamisel pandaks URLile alati ette https, mitte http"
    @staticmethod
    def _make_location_absolute(environ, value):
        # vt webob/response.py
        if SCHEME_RE.search(value):
            return value
        new_location = urlparse.urljoin(_request_uri(environ), value)
        return new_location
        
class NotAuthorizedException(Exception):
    def __init__(self, location, message=None):
        self.location = location
        self.message = message
    
class TooManyUsersException(Exception):
    def __init__(self, allowed, current):
        self.allowed = allowed
        self.current = current

class ProcessCanceled(Exception):
    "Arvutusprotsess katkestatud"
    def __init__(self):
        pass

class APIIntegrationError(Exception):
    "Ei saanud teha päringut API poole (võrguviga vms)"
    def __init__(self, exc, method, url, message, statuscode, inp_data, try_cnt=None):
        self.message = f'{str(exc)}\n{method} {url}'
        if message:
            self.message += '\n{message}'
        self.statuscode = statuscode
        self.inp_data = inp_data
        self.orig_exc = exc
        self.try_cnt = try_cnt
        
def real_host(environ):
    "Leiab URLis tegelikult esineva hosti"
    scheme = environ.get('HTTP_X_HTM_FORWARDED_PROTO') or \
        environ.get('HTTP_X_FORWARDED_PROTO') or \
        environ['wsgi.url_scheme']
    host = environ.get('HTTP_X_HTM_FORWARDED_HOST') or \
        environ.get('HTTP_X_FORWARDED_HOST') or \
        environ['HTTP_HOST']
    url = scheme + '://' + host
    return url

def real_uri(request):
    "Leiab kasutaja poolt kasutatud URLi"
    # request.url sisaldab konteineri ingressi nime, see asendatakse EISi domeeniga
    return real_host(request.environ) + '/' + request.url.split('/', 3)[-1]

def _request_uri(environ):
    """webob.response originaali muudetud, et arvestaks HTTP_X_FORWARDED_PROTO
    ega määraks proxy taga olles protokolliks http
    """
    url = real_host(environ)
    script_name = bytes_(environ.get('SCRIPT_NAME', '/'), 'latin-1')
    path_info = bytes_(environ.get('PATH_INFO', ''), 'latin-1')

    url += url_quote(script_name)
    qpath_info = url_quote(path_info)
    if 'SCRIPT_NAME' not in environ:
        url += qpath_info[1:]
    else:
        url += qpath_info
    return url
    
