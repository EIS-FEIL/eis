"Saatekiri"

from datetime import date
from eis.model import const
import eis.lib.helpers as h

from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, testipakett):
    # ainult p-testis
    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi

    story.append(Paragraph('Toimumisaja tähis: <font size="14"><b>%s</b></font>' % toimumisaeg.tahised, NR))
    story.append(Spacer(100*mm, 10*mm))
    story.append(Paragraph('Saatekiri', LC))
    story.append(Spacer(100*mm, 20*mm))
   
    testiruum = testipakett.testiruum
    ruum = testiruum and testiruum.ruum
    if ruum:
        # on_ruumiprotokoll
        if ruum.tahis:
            koht_nimi = '%s, ruum %s' % (koht_nimi, ruum.tahis)
        kpv = h.str_from_date(testiruum.algus)
    else:
        kpv = testikoht.millal

    data = [[[Paragraph('<u>%s</u>' % koht_nimi, NB),
              Paragraph('(kooli nimi)', S)],
             [Paragraph('<u>%s</u>' % kpv, NB),
              Paragraph('(kuupäev)', S)]],
            [[Paragraph('<u>%s</u>' % testikoht.tahis, NB),
              Paragraph('(kooli kood)', S)],
             ''],
            ]
    story.append(Table(data, colWidths=(125*mm, 30*mm)))

    story.append(Spacer(100*mm, 20*mm))

    # protokollirühmade arv
    tpr_cnt = len(testipakett.testiprotokollid)

    # hindamisprotokollide arv
    if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
        # hindamisprotokollide arv tuleb kuvada suulise p-testi korral
        # ja sellise kirjaliku p-testi korral, mille puhul ei toimu e-hindamist;
        # kui toimub e-hindamine, siis hindamisprotokolle ei ole ja saame siit 0
        hpr_cnt = sum([len(item.hindamisprotokollid) \
                           for item in testipakett.testiprotokollid])
    else:
        hpr_cnt = 0

    data = [[Paragraph('Eksam', N),
             Paragraph(test.nimi + ', ' + testiosa.nimi, NB)],
            [Paragraph('Eksami sooritamise keel', N),
             Paragraph(testipakett.lang_nimi, NB)],
            [Paragraph('Turvakotid materjalide tagastamiseks', N),
             Paragraph(str(testipakett.tagastuskottidearv or ''), N)],
            [Paragraph('Väikesed tagasisaatmise ümbrikud', N),
             Paragraph(str(testipakett.tagastusymbrikearv or ''), N)],
            ]
    if testiosa.vastvorm_kood == const.VASTVORM_KP:
        data.append([Paragraph('Eksamitööde arv', N),
                     Paragraph(str(testipakett.toodearv or ''), N)])

    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        data.extend([
            [Paragraph('Nimekirjade arv', N),
             Paragraph('2', N)],
            [Paragraph('Riigieksamitööde paketi avamisprotokollide arv', N),
             Paragraph('1', N)],
            [Paragraph('Riigieksami toimumisprotokollide arv', N),
             Paragraph('1', N)],
            [Paragraph('Riigieksamitöö üleandmisprotokollide arv', N),
             Paragraph(str(tpr_cnt), N)],
            [Paragraph('Hindamisprotokollide arv', N),
             Paragraph(str(hpr_cnt), N)],
            ])
    elif test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        data.extend([
            [Paragraph('Nimekirjade arv', N),
             Paragraph('2', N)],
            [Paragraph('Põhikooli lõpueksamitööde paketi avamisprotokollide arv', N),
             Paragraph('1', N)],
            [Paragraph('Põhikooli lõpueksami toimumisprotokollide arv', N),
             Paragraph('1', N)],
            [Paragraph('Põhikooli lõpueksamitöö üleandmisprotokollide arv', N),
             Paragraph(str(tpr_cnt), N)],
            [Paragraph('Hindamisprotokollide arv', N),
             Paragraph(str(hpr_cnt), N)],
            ])
    else:
        #if test.on_tseis:
        data.extend([
            [Paragraph('Nimekirjade arv', N),
             Paragraph('2', N)],
            [Paragraph('Eksamitööde paketi avamisprotokollide arv', N),
             Paragraph('1', N)],
            [Paragraph('Eksami toimumisprotokollide arv', N),
             Paragraph('1', N)],
            [Paragraph('Eksamitöö üleandmisprotokollide arv', N),
             Paragraph(str(tpr_cnt), N)],
            [Paragraph('Hindamisprotokollide arv', N),
             Paragraph(str(hpr_cnt), N)],
            ])

    TS = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),                         
                     ])        
    tbl = Table(data, 
                colWidths=(75*mm, 75*mm),
                style=TS)
    story.append(tbl)

    story.append(PageBreak())

