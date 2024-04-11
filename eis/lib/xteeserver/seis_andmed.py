"""
Seaduse tundmise eksami soorituste ja registreeringute andmete väljastamine riigiportaalis ametnikule.
Väljastatakse sooritatud eksamite tulemused, avaldatud või kehtetuks tunnistatud tunnistused, registreeringud ja registreeringu testiosade soorituskohad.
"""
from lxml import etree

from eis.lib.pyxadapterlib.xutils import *
import formencode
from datetime import date

from eis import model
import eiscore.const as const
from eis.forms import validators
from eis.lib.xtee.xroad import *
import eis.lib.helpers as h

import logging
log = logging.getLogger(__name__)

def serve(paring, header=None, attachments=[], context=None):
    error = None
    ik = get_text(paring, 'isikukood') or ''
    ik = ik.strip()
    # kontrollime isikukoodi
    try:
        validators.Isikukood().to_python(ik)
    except formencode.api.Invalid as ex:
        error = 'Vigane isikukood'
        res = E.response(E.teade(error))
        return res, []

    model.Paring_logi.log(header, paritav=ik)                
    return seis_andmed_x(ik)

def seis_andmed_x(ik):
    k = model.Kasutaja.get_by_ik(ik)
    if not k:
        error = 'Meil pole isiku kohta andmeid'
        res = E.response(E.teade(error))
    else:
        res = E.response(E.nimi(k.nimi))

        # eksamitulemused
        li = E.eksamitulemus_jada()
        q = model.Session.query(model.Test,
                                model.Sooritaja.algus,
                                model.Sooritaja.staatus,
                                model.Sooritaja.hindamine_staatus,
                                model.Sooritaja.pallid,
                                model.Testimiskord.tulemus_kinnitatud,
                                model.Testimiskord.koondtulemus_avaldet)
        q = q.filter(model.Test.testiliik_kood==const.TESTILIIK_SEADUS).\
            join(model.Test.sooritajad).\
            filter(model.Sooritaja.kasutaja_id==k.id).\
            filter(model.Sooritaja.staatus>=const.S_STAATUS_TEHTUD).\
            join(model.Sooritaja.testimiskord).\
            order_by(model.Sooritaja.algus)
        
        for r in q.all():
            test, algus, staatus, h_staatus, pallid, kinnitatud, avaldet = r

            tulemus = ''
            if staatus == const.S_STAATUS_TEHTUD:
                if kinnitatud and avaldet:
                    staatus = 'Tulemus on teada'
                    tulemus = h.fstr(pallid) or ''
                else:
                    staatus = 'Tulemus ei ole teada'
            else:
                staatus = const.S_STAATUS.get(staatus)
            
            li.append(E.item(E.aeg(h.str_from_date(algus) or ''),
                             E.staatus(staatus),
                             E.tulemus(tulemus)))
        res.append(li)

        # tunnistused
        li = E.tunnistus_jada()
        q = model.Session.query(model.Tunnistus.tunnistusenr,
                                model.Tunnistus.valjastamisaeg,
                                model.Tunnistus.staatus,
                                model.Tunnistus.id)
        q = q.filter(model.Tunnistus.kasutaja_id==k.id).\
            filter(model.Tunnistus.testiliik_kood==const.TESTILIIK_SEADUS).\
            filter(model.Tunnistus.staatus.in_((const.N_STAATUS_KEHTETU,
                                                const.N_STAATUS_AVALDATUD))).\
            order_by(model.Tunnistus.id)
        for r in q.all():
            tunnistusenr, valjastamisaeg, staatus, tunnistus_id = r
            if tunnistusenr:
                li.append(E.item(E.nbr(tunnistusenr),
                                 E.kpv(h.str_from_date(valjastamisaeg)),
                                 E.kehtiv(staatus and '1' or '0'),
                                 E.tunnistus_id(str(tunnistus_id))))
        res.append(li)

        # seaduse tundmise eksamile registreerimise staatused
        li = E.reg_staatus_jada()
        q = model.Session.query(model.Test, model.Sooritaja)
        q = q.filter(model.Test.testiliik_kood==const.TESTILIIK_SEADUS).\
            join(model.Test.sooritajad).\
            filter(model.Sooritaja.kasutaja_id==k.id).\
            filter(model.Sooritaja.staatus<=const.S_STAATUS_REGATUD).\
            order_by(model.Sooritaja.id)
        
        for r in q.all():
            test, sooritaja = r
            koht = '%s %s / %s' % (test.keeletase_nimi,
                                   sooritaja.piirkond and sooritaja.piirkond.nimi or '',
                                   sooritaja.testimiskord.millal or '')
            item = E.item(E.kpv(h.str_from_date(sooritaja.reg_aeg)),
                          E.koht(koht),
                          E.staatus(const.S_STAATUS.get(sooritaja.staatus)),
                          E.id(str(sooritaja.id)))
            if sooritaja.staatus != const.S_STAATUS_TYHISTATUD:
                tkord = sooritaja.testimiskord
                dt_today = date.today()
                if tkord.reg_xtee and \
                   tkord.reg_xtee_alates<=dt_today and \
                   tkord.reg_xtee_kuni>=dt_today:
                    # kui saab regada, siis saab ka tyhistada
                    item.append(E.dele(''))

            li.append(item)

        res.append(li)

        # eksamikoha teated
        li = E.kohateade_jada()
        for r in q.all():
            test, sooritaja = r
            for sooritus in sooritaja.sooritused:
                if sooritus.testikoht and sooritus.kavaaeg and sooritus.toimumisaeg.kohad_avalikud:
                    koht = sooritus.testikoht.koht
                    li.append(E.item(E.eksam('%s %s' % (test.nimi, sooritus.testiosa.nimi)),
                                     E.aeg(h.str_from_datetime(sooritus.kavaaeg) or ''),
                                     E.koht(koht and koht.nimi or '')))
        res.append(li)
        
    return res, []

if __name__ == '__main__':
    import sys
    from eis.scripts.scriptuser import *
    ik = sys.argv[1]
    res, atts = seis_andmed_x(ik)
    print(etree.tostring(res, encoding=str, xml_declaration=False, method='xml'))
