"Üleandmisprotokoll kahe allkirjaga"

from datetime import date
import eis.model as model
from eis.model.usersession import _
from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, testipakett, tpr):
    testiosa = toimumisaeg.testiosa
    test = testiosa.test

    story.append(Paragraph(_('Protokolli kood') + ': <font size="12"><b>%s</b></font>' % tpr.tahised, NR))
    story.append(Spacer(100*mm, 6*mm))

    pealdis(story, toimumisaeg, testikoht, testipakett, tpr, False)
    
    # sooritajate loetelu tabel
    header = [Paragraph(_('Nr'), NC),
              Paragraph(_('Nimi'), NC),
              Paragraph(_('Isikukood'), NC),
              Paragraph(_('Eksamitöö kood'), NC),
              ]
    if test.on_tseis:
        header.append(Paragraph(_('Esitatud dok.nr'), NC))
        header.append(Paragraph(_('Kirjutamisosa (allkiri)'), NC))
        header.append(Paragraph(_('Lugemisosa (allkiri)'), NC))
    else:
        header.append(Paragraph(_('Kirjutamisosa (allkiri)'), NC))
        header.append(Paragraph(_('Lugemisosa (allkiri)'), NC))        

    data = [header]
    nimi_width = 50*mm
    n = 0
    q = (model.SessionR.query(model.Sooritus)
         .filter(model.Sooritus.testiprotokoll_id==tpr.id)
         .join(model.Sooritus.sooritaja)
         .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
         .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD))
    if toimumisaeg.nimi_jrk:
        q = q.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
    else:
        q = q.order_by(model.Sooritus.tahis)

    for tos in q.all():
        n += 1
        sooritaja = tos.sooritaja
        kasutaja = tos.sooritaja.kasutaja

        t = Paragraph('%s_%s' % (sooritaja.eesnimi, sooritaja.perenimi), N)
        nimi_width = max(nimi_width, t.minWidth())
        
        row = [Paragraph(str(n), N),
               Paragraph(sooritaja.nimi, N),
               Paragraph(kasutaja.isikukood or kasutaja.synnikpv.strftime('%d.%m.%Y'), N),
               Paragraph('%s %s' % (testikoht.tahis, tos.tahis), N),
               ]
        if test.on_tseis:
            row.append(Paragraph('', N))
        row.append(Table([['']], rowHeights=(7*mm,))) # allkirja koht, teeme rea kõrgemaks
        data.append(row)

    TS = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                     ('LEFTPADDING',(0,0),(-1,-1), 3),
                     ('RIGHTPADDING',(0,0),(-1,-1), 3),
                     ])
    colWidths = [7*mm, nimi_width, 23*mm, 18*mm]
    allkirjade_arv = 2
    allkiri_width = 75*mm/allkirjade_arv
    for i in range(allkirjade_arv):
        colWidths.append(allkiri_width)

    story.append(Table(data, 
                       colWidths=colWidths,
                       style=TS))

    story.append(Spacer(100*mm, 10*mm))

    allkirjad(story, test, testiosa, toimumisaeg)
    
    story.append(PageBreak())

def pealdis(story, toimumisaeg, testikoht, testipakett, tpr, kaksvihikut):
    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        story.append(Paragraph(_('Riigieksamitöö üleandmisprotokoll'), LC))
        if kaksvihikut:
            story.append(Paragraph(_('I ja II vihik'), LC))
        story.append(Spacer(4*mm, 4*mm))

    elif test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        story.append(Paragraph(_('Põhikooli eksamitöö üleandmisprotokoll'), LC))
        if kaksvihikut:
            story.append(Paragraph(_('I ja II vihik'), LC))
        story.append(Spacer(4*mm, 4*mm))
        
    elif test.on_tseis:
        if test.testiliik_kood == const.TESTILIIK_TASE:
            if testiosa.vastvorm_kood in (const.VASTVORM_SE, const.VASTVORM_SH, const.VASTVORM_I, const.VASTVORM_SP):
                buf = _('Eesti keele {s}-taseme eksamitöö suulise osa üleandmisprotokoll').format(s=test.keeletase_nimi)
            else:
                buf = _('Eesti keele {s}-taseme eksamitöö kirjaliku osa üleandmisprotokoll').format(s=test.keeletase_nimi)                

        elif test.testiliik_kood == const.TESTILIIK_SEADUS:
            buf = _('Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksamitöö üleandmisprotokoll')
        story.append(Paragraph(buf, LC))
        story.append(Spacer(4*mm, 4*mm))

    ruum = tpr.testiruum.ruum
    if ruum and ruum.tahis:
        p_ruum = [Paragraph('<u>%s %s</u>' % (_("ruum"), ruum.tahis), NBR),
                  Paragraph('(%s)' % _("ruum"), SR)]
    else:
        p_ruum = ''

    test_nimi = '%s, %s' % (test.nimi, testiosa.nimi)
    kursus_nimi = tpr.kursus_nimi
    if kursus_nimi:
        test_nimi += ' (%s)' % (kursus_nimi.lower())

    data = [[[Paragraph(test_nimi, NB),
              Paragraph('(%s)' % _("eksam"), S)],
             [Paragraph('<u>%s</u>' % tpr.testiruum.algus.strftime('%d.%m.%Y'), NBR),
              Paragraph('(%s)' % _("kuupäev"), SR)]],
            ]
    if testipakett and testipakett.lang:
        lang_nimi = testipakett.lang_nimi.capitalize()
        keel = [Paragraph('<u>%s</u>' % lang_nimi, NB),
                Paragraph('(%s)' % _("eksami sooritamise keel"), S)]
    else:
        keel = Paragraph('', S)
    data.append([keel, p_ruum])
    story.append(Table(data, colWidths=(125*mm, 30*mm)))

def allkirjad(story, test, testiosa, toimumisaeg):
    if test.on_tseis and testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP):
        data = [[Paragraph(_('Esimees'), NR),
                 Paragraph('.'*68, DOT),
                 Paragraph(_('Liige'), NR),
                 Paragraph('.'*68, DOT)],
                [Paragraph(_('Allkiri:'), NR),
                 Paragraph('.'*68, DOT),
                 Paragraph(_('Allkiri:'), NR),
                 Paragraph('.'*68, DOT)]                
                ]

        story.append(Table(data, 
                           colWidths=(20*mm, 53*mm, 30*mm, 53*mm),
                           rowHeights=(5*mm, 10*mm)))
    else:
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
            tegija = _('Intervjueerija')
        elif toimumisaeg.vaatleja_maaraja:
            tegija = _('Välisvaatleja')
        else:
            tegija = _('Esimees')
        data = [[Paragraph(tegija, NR),
                 Paragraph('.'*68, DOT)],
                [Paragraph(_('Allkiri:'), NR),
                 Paragraph('.'*68, DOT)]
                ]

        TS = TableStyle([('ALIGN',(0,0),(0,-1), 'RIGHT'),
                         ('ALIGN',(1,0),(1,-1), 'LEFT'),
                         ])
        story.append(Table(data, 
                           colWidths=(30*mm, 73*mm),
                           rowHeights=(5*mm, 10*mm),
                           style=TS))
    
