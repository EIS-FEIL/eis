"""
Teenus väljastab antud õppeasutuses olevad antud seeriaga plankide numbrid,
mida koolil on võimalik lõpetajatele väljastada.
EHISel oleks võimalik selle teenuse abil tõsta kasutamismugavust ning vähendada vigaste andmete sisestamise riski, pakkudes kasutajaliideses kasutajale valiku vabadest plankidest selmet kasutaja peab planginumbri käsitsi sisestama.
Kooli ID on kohustuslik parameeter. Kui sisendis puudub õppetase, siis antakse välja koolis olevad vabad plangid kõigi õppetasemete kohta.
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
import eis.lib.helpers as h
from eis_plank import model
from eis_plank.model import const

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = None
    try:
        kool_id = int(paring.find('kool_id').text)
    except:
        error = 'Vigane sisend (kool_id)'
    else:
        kool = model.Koht.query.filter(model.Koht.kool_id==kool_id).first()
        if not kool:
            error = 'Kooli ei leitud'

    oppetase_kood = None
    oppetase_node = paring.find('oppetase')
    if oppetase_node is not None:
        oppetase_kood = oppetase_node.text

    pl_id = None
    pl_node = paring.find('liik_id')
    if pl_node is not None:
        pl_id = pl_node.text
        
    if not error:
        #model.Paring_logi.log(header, isikukood)
        res = _search(kool, oppetase_kood, pl_id)
    else:
        res = E.response(E.teade(error), E.kogus('0'))

    return res, []

def _search(kool, oppetase_kood, pl_id):
    q = model.Session.query(model.Plank.nr, model.Plangiseeria.id).\
        filter(model.Plank.koht_id==kool.id).\
        filter(model.Plank.staatus==const.P_STAATUS_VABA).\
        join(model.Plank.plangiseeria)
    if pl_id:
        q = q.filter(model.Plangiseeria.plangiliik_id==pl_id)
    elif oppetase_kood:
        q = q.join(model.Plangiseeria.plangiliik).\
            filter(model.Plangiliik.oppetase_kood==oppetase_kood)
    q = q.order_by(model.Plangiseeria.id, model.Plank.nr)

    ps = None # jooksev plangiseeria
    liigid = [] # siia kogume vastuse jada
    liik = None # vastus yhe liigi kohta
    vahemik = None # yhe liigi yks vahemik

    class Liik(object):
        ps = None
        
    class Vahemik(object):
        nr_alates = None
        nr_kuni = None
        kogus = 0
        ps = None
        current = 0
        
    for plank_nr, ps_id, in q.all():
        log.info('VAHEMIK: %s, %d' % (plank_nr, ps_id))
        if not ps or ps_id != ps.id:
            # algavad uue liigi vahemikud
            ps = model.Plangiseeria.get(ps_id)
            liik = Liik()
            liik.ps = ps
            liik.vahemikud = []
            liigid.append(liik)
            vahemik = None

        if plank_nr:
            n = ps.get_n(plank_nr)
        else:
            n = None

        if n and vahemik and vahemik.current == n-1:
            # jätkub vana liigi vana vahemik
            vahemik.kuni = plank_nr
            vahemik.kogus += 1
        elif not plank_nr and vahemik and not vahemik.alates:
            # jätkub numbrita vahemik
            vahemik.kogus += 1
        else:
            # algab uus vahemik
            vahemik = Vahemik()
            vahemik.alates = vahemik.kuni = plank_nr
            vahemik.kogus = 1
            liik.vahemikud.append(vahemik)

        vahemik.current = n

    kogus = 0
    li = E.plangijada()
    for liik in liigid:
         item = E.item()
         item.append(E.oppetase(liik.ps.plangiliik.oppetase_kood))
         item.append(E.liik_id(str(liik.ps.id)))
         item.append(E.nimetus(liik.ps.plangiliik.nimi))
         li_v = E.vahemikud()
         for vahemik in liik.vahemikud:
             item_v = E.item()
             if vahemik.alates:
                 item_v.append(E.alates(vahemik.alates))
                 item_v.append(E.kuni(vahemik.kuni))
             item_v.append(E.kogus(str(vahemik.kogus)))
             li_v.append(item_v)
             kogus += vahemik.kogus
         item.append(li_v)
         li.append(item)

    keha = E.response()
    keha.append(E.kogus(str(kogus)))
    keha.append(li)
    return keha
