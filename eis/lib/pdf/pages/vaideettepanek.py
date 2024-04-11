# -*- coding: utf-8 -*- 
# $Id: vaideettepanek.py 9 2015-06-30 06:34:46Z ahti $
"Vaideotsuse ettepanek"

from .pdfutils import *
from .stylesheet import *
from datetime import date
import sqlalchemy as sa
from eis.model import const
import eis.model as model
import eis.lib.helpers as h

def generate(story, vaie, diff):

    sooritaja = vaie.sooritaja
    k = sooritaja.kasutaja
    test = sooritaja.test
    story.append(Paragraph('Ettepanek nr %s' % (vaie.vaide_nr), NBC))
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        story.append(Paragraph('riigieksamite apellatsioonikomisjonile', NR))
    elif test.testiliik_kood == const.TESTILIIK_TASE:
        story.append(Paragraph('eesti keele tasemeeksamite tulemuste vaidekomisjonile', NR))
    else:
        story.append(Paragraph('vaidekomisjonile', NR))
    story.append(Spacer(6*mm, 6*mm))
    buf = 'Arutanud eksaminandi %s' % (sooritaja.nimi)
    if k.isikukood:
        buf += ' (isikukood %s)' % k.isikukood
    else:
        buf += ' (sünniaeg %s)' % k.synnikpv.strftime('%d.%m.%Y')
    buf += ' vaiet eksami <b>%s</b> tulemuseks saadud %s hindepalli kohta,' % (sooritaja.test.nimi, h.fstr(vaie.pallid_enne))
    buf += ' teeb ekspertrühm ettepaneku:'
    story.append(Paragraph(buf, N))
    story.append(Spacer(6*mm, 6*mm))
    story.append(Paragraph(gen_diff_txt(vaie, diff), NBC))

    if vaie.ettepanek_pohjendus:
        story.append(Spacer(3*mm, 3*mm))
        pohjendus = vaie.ettepanek_pohjendus
        if pohjendus[-1] not in '.!?':
            pohjendus += '.'
        #story.append(Paragraph(pohjendus, N))
        for line in pohjendus.split('\n'):
            story.append(Paragraph(line, N))
    
    story.append(Spacer(10*mm, 10*mm))

    # ekspertide nimed
    q = model.SessionR.query(model.Kasutaja.nimi).\
        filter(model.Kasutaja.labiviijad.any(
        sa.and_(
            model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT,
            model.Labiviija.id==model.Labivaatus.ekspert_labiviija_id,
            model.Labivaatus.hindamine_id==model.Hindamine.id,
            model.Hindamine.hindamisolek_id==model.Hindamisolek.id,
            model.Hindamisolek.sooritus_id==model.Sooritus.id,
            model.Sooritus.sooritaja_id==sooritaja.id))).\
        order_by(model.Kasutaja.nimi)
    li = [nimi for nimi, in q.all()]
    eksperdid = ', '.join(li)
    story.append(Paragraph('Eksperdid: %s' % eksperdid, N))

def gen_diff_txt(vaie, diff):
    if vaie.pallid_enne == vaie.pallid_parast: 
        buf = 'jätta eksami tulemus (%s p) muutmata' % (h.fstr(vaie.pallid_enne))
    else:
        d = vaie.pallid_parast - vaie.pallid_enne
        buf = '%s eksami tulemust (%s p) %s hindepalli võrra %s hindepallile' % \
                      (d > 0 and 'tõsta' or 'langetada',
                       h.fstr(vaie.pallid_enne),
                       h.fstr(abs(d)),
                       h.fstr(vaie.pallid_parast))
    return buf
    
