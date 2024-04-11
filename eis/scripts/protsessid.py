# -*- coding: utf-8 -*- 
# $Id: protsessid.py 9 2015-06-30 06:34:46Z ahti $
"""
Pooleliolevate arvutusprotsesside kuvamine
"""
from .scriptuser import *
import eis.lib.helpers as h

q = model.Arvutusprotsess.query.\
    filter(model.Arvutusprotsess.lopp==None).\
    order_by(model.Arvutusprotsess.id)
cnt = q.count()
if not cnt:
    print('Ei ole pooleli arvutusprotsesse.')
else:
    print('%s protsessi on pooleli.' % cnt)
    for r in q.all():
        k = model.Kasutaja.get_by_ik(r.creator)
        print('%s. %s pid=%s %s%% algus %s, muudetud %s %s %s (%s)' % \
              (r.id,
               r.hostname or '',
               r.pid,
               r.edenemisprotsent,
               h.str_from_datetime(r.algus),
               h.str_from_datetime(r.modified),
               r.kirjeldus,
               r.viga or '',
               k and k.nimi or r.creator
               ))
