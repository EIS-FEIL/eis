# -*- coding: utf-8 -*- 
# $Id: vaideettepanek_hindajatega.py 598 2016-04-14 10:50:57Z ahti $
"Printimiseks mõeldud vaideotsuse ettepanek koos vaidlustatud tulemustega"

from .pdfutils import *
from .stylesheet import *
from datetime import date
import sqlalchemy as sa
from eis.model import const, Alatest
import eis.model as model
import eis.lib.helpers as h
import eis.lib.utils as utils

def generate(story, vaie, diff):

    sooritaja = vaie.sooritaja
    k = sooritaja.kasutaja
    test = sooritaja.test
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        buf = 'Riigieksami'
    elif test.testiliik_kood == const.TESTILIIK_TASE:
        buf = 'Eesti keele tasemeeksami'
    else:
        buf = 'Eksami'
    buf = buf + ' tulemuse kohta esitatud vaiete läbivaatamise ekspertiisikomisjoni ettepanek'
    story.append(Paragraph(buf, LBC))

    dd = date.today()
    story.append(Paragraph('%d. %s %d. a' % (dd.day, utils.str_month(dd), dd.year), NC))
    story.append(Spacer(3*mm,3*mm))

    story.append(Paragraph('<b>Vaide esitaja:</b> %s' % k.nimi, N))
    if k.isikukood:
        story.append(Paragraph('<b>Isikukood:</b> %s' % k.isikukood, N))
    else:
        story.append(Paragraph('<b>Sünniaeg:</b> %s' % h.str_from_date(k.synnikpv), N))
    if test.testiliik_kood == const.TESTILIIK_TASE:
        story.append(Paragraph('<b>Eksami tase:</b> eesti keele %s-tase' % test.keeletase_nimi, N))
    else:
        story.append(Paragraph('<b>Õppeaine:</b> %s' % test.aine_nimi, N))
    story.append(Paragraph('<b>Eksamitulemus:</b> %s punkti' % (h.fstr(vaie.pallid_enne)), N))

    data = []
    len1 = 0
    for s, osa, ylemsooritus in sooritaja.get_osasooritused():    
        osatulemus = None
        if s and s.staatus == const.S_STAATUS_TEHTUD:
            osatulemus = '%s: %s punkti' % (osa.nimi, h.fstr(s.pallid))
            if isinstance(osa, Alatest):
                hindajad = _get_alatestihindajad(s.sooritus, osa)
            else:
                hindajad = _get_hindajad(s)
        else:
            osatulemus = '%s: %s' % (osa.nimi, s and s.staatus_nimi or ylemsooritus.staatus_nimi)
            hindajad = ''

        # leiame esimese veeru laiuse nii, et mahuks yhele reale
        len1 = max(len1, Paragraph(osatulemus.replace(' ','_'), N).minWidth() + 2 * mm)
        data.append([Paragraph(osatulemus, N), Paragraph(hindajad, N)])

    TS = TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'),
                     ('LEFTPADDING', (0,0), (0,-1), 0),
                     ])
    len2 = 190*mm - len1
    story.append(Table(data, 
                       colWidths=(len1, len2),
                       style=TS,
                       hAlign='LEFT')
                 )
    li_kood = ['%s osa %s' % (s.testiosa.vastvorm_nimi.lower(), s.tahised) for s in sooritaja.sooritused]
    story.append(Paragraph('<b>Töö kood:</b> %s' % ('; '.join(li_kood)), N))

    story.append(Spacer(6*mm, 6*mm))
    story.append(Paragraph('Komisjoni arvamus (sh ettepanek vaidekomisjoni otsuseks):', NB))
    for n in range(11):
        story.append(Paragraph('.'*174, DOT))
    story.append(Spacer(3*mm, 3*mm))

    story.append(Paragraph('Ekspertiisikomisjoni liikmed:', NB))
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
    liikmed = [nimi for nimi, in q.all()]
    for nimi in liikmed:
        story.append(Paragraph(nimi, N))

def _get_hindajad(sooritus, hindamiskogumid_id=None):
    li_h = []
    for holek in sooritus.hindamisolekud:
        if hindamiskogumid_id is not None and holek.hindamiskogum_id not in hindamiskogumid_id:
            # kui on antud alatesti hindamiskogumid, siis 
            # jätame välja need hindamiskogumid, mis ei sisalda yhtki ylesannet antud alatestist
            continue

        for hindamine in holek.hindamised:
            if hindamine.liik <= const.HINDAJA4 and hindamine.sisestus == 1:
                if not hindamine.tyhistatud and hindamine.staatus == const.H_STAATUS_HINNATUD:
                    li_yl = []
                    toorpunktid = 0
                    for yh in hindamine.ylesandehinded:
                        vy = yh.valitudylesanne
                        ty = vy.testiylesanne
                        li_yl.append((ty.seq, '%s. ül %s' % (ty.seq, h.fstr(yh.toorpunktid) or '-')))
                        toorpunktid += yh.toorpunktid or 0
                    #buf = u'%s %s punkti ' % (hindamine.liik_nimi, h.fstr(hindamine.pallid) or '-')
                    buf = '%s %s punkti ' % (hindamine.liik_nimi, h.fstr(toorpunktid) or '-') +\
                          '(%s)' % (', '.join([r[1] for r in sorted(li_yl, key=lambda x: x[0])]))
                    li_h.append(buf)
    return '<br/>'.join(li_h)

def _get_alatestihindajad(sooritus, alatest):
    hindamiskogumid_id = [ty.hindamiskogum_id for ty in alatest.testiylesanded \
                              if not ty.hindamiskogum.arvutihinnatav]
    return _get_hindajad(sooritus, hindamiskogumid_id)
