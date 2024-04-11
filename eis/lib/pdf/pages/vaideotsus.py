"Riigieksami või põhikooli lõpueksami vaideotsus"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h
import eis.lib.utils as utils
from .aadress import aadressikast

def generate(story, vaie, allkirjastajad):
    sooritaja = vaie.sooritaja
    test = sooritaja.test

    muutus = vaie.pallid_parast - vaie.pallid_enne    
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        eksamiliigi = 'riigi'
    elif test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        eksamiliigi = 'ühtse põhikooli lõpu'
    else:
        eksamiliigi = ''
 
    k = sooritaja.kasutaja

    # HTM korporatiivne font on arial narrow
    N = ParagraphStyle(name='TimesRoman',
                       fontName='Times-Roman',
                       fontSize=12,
                       leading=16,
                       spaceBefore=3,
                       spaceAfter=3)
    NB = ParagraphStyle(name='TimesRomanBold',
                        parent=N,
                        fontName='Times-Bold')
    NR12 = ParagraphStyle(name='TimesRomanRight',
                          parent=N,
                          fontSize=12,
                          spaceBefore=12,
                          spaceAfter=14)

    story.append(Spacer(1*mm, 25*mm))
    if allkirjastajad:
        story.append(Paragraph('<b>RIIGIEKSAMI JA ÜHTSE PÕHIKOOLI LÕPUEKSAMI TULEMUSTE APELLATSIOONIKOMISJONI OTSUS NR %s</b>' % (vaie.vaide_nr), NB))
    else:
        story.append(Paragraph('<b>RIIGIEKSAMI JA ÜHTSE PÕHIKOOLI LÕPUEKSAMI TULEMUSTE APELLATSIOONIKOMISJONI OTSUSE EELNÕU</b>', NB))

    story.append(Spacer(6*mm,4*mm))
    story.append(Paragraph('Riigieksami ja ühtse põhikooli lõpueksami tulemuste apellatsioonikomisjon vaatas läbi', N))

    story.append(Spacer(3*mm, 3*mm))
    omastav = sooritaja.nimi.upper()
    #if not omastav[-1] in u'AEIOUÕÄÖÜY':
    #    omastav += "'i"
    story.append(Paragraph('%s (%s)' % (omastav, k.isikukood or k.synnikpv.strftime('%d.%m.%Y')), NB))
    story.append(Paragraph('<b>%s</b>' % (test.aine_nimi.upper()), NB))
    story.append(Spacer(3*mm, 3*mm))

    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:    
        buf = 'riigieksamitöö'
    elif test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        buf = 'ühtse põhikooli lõpueksami töö'
    else:
        buf = 'eksamitöö'

    story.append(Paragraph(buf + ' ja kontrollis selle hindamise vastavust hindamisjuhendile.', N))
    story.append(Spacer(3*mm, 3*mm))

    if muutus < 0 - 1e-12:
        # langetati
        buf = 'Põhikooli- ja gümnaasiumiseaduse § 33 lõike 1 ja lõike 2 punkti 3 alusel'
    elif muutus > 1e-12:
        # tõsteti
        buf = 'Põhikooli- ja gümnaasiumiseaduse § 33 lõike 1 ja lõike 2 punkti 2 alusel'
    else:
        # jäeti samaks
        buf = 'Põhikooli- ja gümnaasiumiseaduse § 33 lõike 1 ja lõike 2 punkti 1 alusel'
    buf += ' ja võttes arvesse apellatsioonikomisjoni töösse kaasatud ekspertide ettepanekut apellatsioonikomisjon'
    story.append(Paragraph(buf, N))

    story.append(Spacer(3*mm, 3*mm))

    story.append(Paragraph('o t s u s t a s', NB))
    story.append(Paragraph(vaie.gen_ettepanek_txt(), NB))
    story.append(Spacer(3*mm, 3*mm))
    if allkirjastajad:
        # otsus
        pohjendus = vaie.otsus_pohjendus
    else:
        # eelnõu
        pohjendus = vaie.eelnou_pohjendus

    if pohjendus:
        pohjendus = pohjendus.strip()
        if pohjendus and pohjendus[-1] not in '.!?':
            pohjendus += '.'
        for line in pohjendus.split('\n'):
            story.append(Paragraph(line, N))
        #story.append(Paragraph(pohjendus, N))
    story.append(Spacer(3*mm, 3*mm))        

    story.append(Paragraph('Seega on %seksami lõplik tulemus %s hindepalli.' % (eksamiliigi, h.fstr(vaie.pallid_parast)), NB))

    if allkirjastajad:
        story.append(Spacer(3*mm, 3*mm))    
        story.append(Paragraph('Apellatsioonikomisjoni otsuse võib vaidlustada 30 päeva jooksul, arvates otsuse teatavaks tegemise päevast, esitades Tartu Halduskohtule kaebuse halduskohtumenetluse seadustikus ettenähtud korras.', N))

        story.append(Spacer(9*mm, 5*mm))
        story.append(vaide_allkirjad(allkirjastajad))

def vaide_allkirjad(allkirjastajad):
    row = []
    # allkirjastajate nimed ja tiitlid kõrvuti vasakult paremale,
    # järjestatult vastupidi allkirjastamise järjekorrale,
    # et esimesena oleks vaidekomisjoni esimees
    for nimi, tiitel1, tiitel2 in reversed(allkirjastajad):
        buf = '(allkirjastatud digitaalselt)<br/>' + nimi
        if tiitel1:
            buf += '<br/>' + tiitel1
        if tiitel2:
            buf += '<br/>' + tiitel2            
        row.append(Paragraph(buf, N))
    if row:
        rows = len(row)
        width = 164 * mm / rows
        ts = [('VALIGN', (0,0), (-1,-1), 'TOP')]
        tbl = Table([row],
                    colWidths=(width,) * rows,
                    style=TableStyle(ts))
        return tbl
        
def first_page(canvas, doc, pdoc):
    "Esimene lehekülg on plangil"
    canvas.saveState()

    image = os.path.join(IMAGES_DIR,  'HTM_logo_plangil.jpg')
    canvas.drawImage(image, 8*mm, 258*mm, 85*mm, 28*mm)

    # juurdepääsupiirang 75 aastat
    if pdoc.allkirjastajad:
        dt = pdoc.vaie.otsus_kp
    else:
        # eelnõu
        dt = date.today()

    dt_end = utils.add_months(dt, 75*12)
    canvas.setFont('Times-Bold', 10)    
    x = 136*mm
    y = 278*mm
    lines = ('ASUTUSESISESEKS',
             'KASUTAMISEKS',
             'Märge tehtud: %s' % utils.str_date(dt),
             'Kehtib kuni: %s' % utils.str_date(dt_end),
             'Alus: 75 aastat - AvTS § 35 lg 1 p 12',
             'Teabevaldaja: Haridus- ja',
             'Teadusministeerium')
    for ind, text in enumerate(lines):
        if ind < 2:
            canvas.setFont('Times-Bold', 10)
        else:
            canvas.setFont('Times-Roman', 10)
        canvas.drawString(x, y, text)
        y -= 4*mm

    # kontaktandmed
    canvas.setFont('Times-Roman', 10)
    buf = 'Munga 18/ 50088 Tartu / Tel 735 0222 / Faks 730 1080 / hm@hm.ee / www.hm.ee'
    canvas.drawString(30*mm, 17*mm, buf)

    buf = 'Registrikood 70000740'
    canvas.drawString(30*mm, 13*mm, buf)   

    canvas.restoreState()

