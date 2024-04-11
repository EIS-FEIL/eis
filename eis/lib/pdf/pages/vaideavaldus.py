"Vaideotsus"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, vaie):

    sooritaja = vaie.sooritaja
    k = sooritaja.kasutaja
    tais_aadress = k.tais_aadress
    test = sooritaja.test

    story.append(Paragraph('VAIE', NBC))
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        story.append(Paragraph('RIIGIEKSAMITE VAIDEKOMISJONILE', NBC))
    elif test.testiliik_kood == const.TESTILIIK_TASE:
        story.append(Paragraph('TASEMEEKSAMITE VAIDEKOMISJONILE', NBC))
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:
        story.append(Paragraph('PÕHISEADUSE JA KODAKONDSUSE SEADUSE TUNDMISE EKSAMITE VAIDEKOMISJONILE', NBC))
    else:
        story.append(Paragraph('VAIDEKOMISJONILE', NBC))
    story.append(Spacer(10*mm,10*mm))

    story.append(Paragraph('TÄIDAB VAIDE ESITAJA', NB))
    story.append(Paragraph('Vaide esitaja nimi: <b>%s</b>' % sooritaja.nimi, N))
    if k.isikukood:
        story.append(Paragraph('Isikukood: <b>%s</b>' % k.isikukood, N))
    else:
        story.append(Paragraph('Sünniaeg: <b>%s</b>' % k.synnikpv.strftime('%d.%m.%Y'), N))

    if tais_aadress:
        story.append(Paragraph('Elukoht (koos postiindeksiga): <b>%s %s</b>' % \
                               (tais_aadress or '', k.postiindeks or ''), N))
    story.append(Paragraph('Telefon: <b>%s</b>' % (k.telefon or ''), N))
    story.append(Paragraph('e-mail: <b>%s</b>' % (k.epost or ''), N))

    # leiame mõne kirjaliku osa kuupäeva ja koha
    # või kui pole kirjalikku osa, siis varaseima kuupäeva ja suvalise testiosa koha
    millal = sooritaja.algus 
    koht = None
    for tos in sooritaja.sooritused:
        if tos.staatus == const.S_STAATUS_TEHTUD:
            # ei arvesta vabastatud testiosi
            if not koht and tos.testikoht:
                koht = tos.testikoht.koht
            if tos.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
                millal = tos.algus or tos.kavaaeg
                koht = tos.testikoht.koht
                break

    if koht:
        story.append(Paragraph('Eksami sooritamise koht: <b>%s</b>' % (koht.nimi), N))

    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        #kool = sooritaja.kool_koht and sooritaja.kool_koht.nimi or k.kool_nimi or ''
        #story.append(Paragraph(u'kool: <b>%s</b>' % (kool), N))
        story.append(Paragraph('Riigieksam, mille tulemust soovitakse vaidlustada: <b>%s</b>' % (test.aine_nimi), N))
    elif test.testiliik_kood == const.TESTILIIK_TASE:
        story.append(Paragraph('Eksam, mille tulemust soovitakse vaidlustada: <b>eesti keele %s-taseme eksam</b>' % (test.keeletase_nimi), N))
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:
        story.append(Paragraph('Eksam, mille tulemust soovitakse vaidlustada: <b>Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksam</b>', N))

    story.append(Paragraph('Eksami toimumise kuupäev: <b>%s</b>' % (h.str_from_date(millal)), N))
    if vaie.markus:
        story.append(Paragraph('Vaide põhjendus: <b>%s</b>' % (vaie.markus), N))
    story.append(Paragraph('Vaide esitamise kuupäev: <b>%s</b>' % (h.str_from_date(vaie.esitamisaeg)), N))


    story.append(Paragraph('Otsus väljastatakse %s teel avaldusel märgitud aadressil.' % \
                               (vaie.otsus_epostiga and 'e-posti' or 'posti'), N))


    story.append(Table([['']],
                       colWidths=(160*mm),
                       style=TableStyle([('LINEABOVE', (0,0),(-1,-1), 0.5,colors.black),
                                         ])
                       ))

    # if vaie.vaide_nr:
    #     story.append(Paragraph(u'TÄIDAB APELLATSIOONIKOMISJON', NB))
    #     story.append(Paragraph(u'avalduse registreerimise number apellatsiooniregistris: <b>%s</b>' % (vaie.vaide_nr or ''), N))
    #     story.append(Paragraph(u'eksamitöö läbivaatamise tulemus:', N))

