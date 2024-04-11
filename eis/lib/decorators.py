# -*- coding: utf-8 -*-
# $Id: decorators.py 9 2015-06-30 06:34:46Z ahti $

#import pylons
#from pylons import session
#from pylons.controllers.util import abort, redirect
from decorator import decorator

import logging
log = logging.getLogger(__name__)

def authorize(permission):
    """Dekoraator meetodite individuaalseks autoriseerimiseks
    """
    def wrapper(func, self, *args, **kw):
        # if not c.user.has_permission(permission):
        #     #session['redirect'] = \
        #     #    pylons.request.environ['pylons.routes_dict']
        #     session['flash'] = 'Kasutajal pole niisuguseks tegevuseks õigust'
        #     session.save()
        #     if c.partial:
        #         redirect(url('error', partial=True))
        #     elif c.user.is_authenticated:
        #         redirect(url('avaleht'))
        #     else:
        #         redirect(url('login'))

        return func(self, *args, **kw)

    return decorator(wrapper)

def validate(schema, form):
    def wrapper(func, self, *args, **kw):
        # if not c.user.has_permission(permission):
        #     #session['redirect'] = \
        #     #    pylons.request.environ['pylons.routes_dict']
        #     session['flash'] = 'Kasutajal pole niisuguseks tegevuseks õigust'
        #     session.save()
        #     if c.partial:
        #         redirect(url('error', partial=True))
        #     elif c.user.is_authenticated:
        #         redirect(url('avaleht'))
        #     else:
        #         redirect(url('login'))

        return func(self, *args, **kw)

    return decorator(wrapper)


