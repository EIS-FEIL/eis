"Eksami toimumise protokoll"

from datetime import date
from eis.model.usersession import _
from .pdfutils import *
from .stylesheet import *

def generate(story, testikoht, toimumisprotokoll):
    toimumisaeg = testikoht.toimumisaeg
    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi
    testiruum = toimumisprotokoll.testiruum
    if testiruum:
        ruum = testiruum.ruum
        if ruum and ruum.tahis:
            koht_nimi += ', %s %s' % (_("ruum"), ruum.tahis)

    if test.on_tseis:
        for tpr in testiruum.testiprotokollid:
            story.append(Paragraph(_('protokoll') + ': <font size="14"><b>%s</b></font>' % tpr.tahised, NR))
    else:
        story.append(Paragraph(_('Toimumisaja tähis') + ': <font size="14"><b>%s</b></font>' % toimumisaeg.tahised, NR))

    story.append(Spacer(5*mm, 5*mm))
    if test.testiliik_kood == const.TESTILIIK_TASE:
        buf = _('Protokoll eesti keele {a}-taseme eksami toimumise kohta').format(a=test.keeletase_nimi)
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:
        buf = _('Protokoll Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami toimumise kohta')
    elif test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        buf = _('Protokoll riigieksami toimumise kohta')
    elif test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        buf = _('Protokoll põhikooli lõpueksami toimumise kohta')
    else:
        buf = _('Protokoll eksami toimumise kohta')
    story.append(Paragraph(buf, LC))
    story.append(Spacer(100*mm, 12*mm))

    data = [[[Paragraph('<u>%s</u>' % testikoht.millal, NB),
              Paragraph('(%s)' % _("kuupäev"), S)],
             [Paragraph('<u>%s</u>' % testikoht.tahis, NBR),
              Paragraph('(%s)' % (test.on_tseis and _('koha kood') or _('kooli kood')), SR)]],
            [[Paragraph('<u>%s, %s</u>' % (test.nimi, testiosa.nimi), NB),
              Paragraph('(%s)' % _("eksam"), S)],
             [Paragraph('<u>%s</u>' % koht_nimi, NBR),
              Paragraph('(%s)' % (test.on_tseis and _('koht') or _('kooli nimi')), SR)]],
            ]
    if toimumisprotokoll.lang:
        lang_nimi = toimumisprotokoll.lang_nimi.capitalize()
        data.append([[Paragraph('<u>%s</u>' % lang_nimi, NB),
                      Paragraph('(%s)' % _("eksami sooritamise keel"), S)],
                     ''])

    TS = TableStyle([('ALIGN',(0,0),(0,-1), 'LEFT'),
                     ('ALIGN',(1,0),(1,-1), 'RIGHT'),
                     ('LEFTPADDING', (0,0),(-1,-1), 0),
                     ])        
    story.append(Table(data, 
                       colWidths=(83*mm, 83*mm),
                       style=TS,
                       hAlign='LEFT'))
        
    if test.on_tseis:
        story.append(Paragraph(_('Eksamil osales .................... eksaminandi.'), DOT))
        story.append(Paragraph(_('Eksamile registreerunutest puudus .................... eksaminandi (tuua ära nende eksamitööde koodid):'), DOT))
    else:
        story.append(Paragraph(_('Eksamil osales .................... õpilast.'), DOT))
        story.append(Paragraph(_('Eksamile registreerunutest puudus .................... õpilast (tuua ära nende eksamitööde koodid):'), DOT))    

    for n in range(4):
        story.append(Paragraph('.'*185, DOT))

    story.append(Paragraph(_('Eksami katkestas ..................... eksaminandi (tuua ära nende eksamitööde koodid):'), DOT))
    story.append(Paragraph('.'*185, DOT))

    story.append(Paragraph(_('Eksamilt kõrvaldati ..................... eksaminandi (tuua ära nende eksamitööde koodid):'), DOT))
    story.append(Paragraph('.'*185, DOT))

    story.append(Paragraph(_('Märkusi (eksamil ilmnenud eksamikorrale mittevastavused ja muud eksamil tekkinud eriolukorrad):'), DOT))

    for n in range(3):
        story.append(Paragraph('.'*185, DOT))

    story.append(Paragraph(_('Tööd on suletud .................. ümbrikusse ning neis on kokku .............. eksamitööd.'), DOT))


    story.append(Spacer(10*mm,10*mm))

    TS = TableStyle([('TOPPADDING', (0,0), (-1,0), 6), # enne tabelit ruumi
                     ('BOTTOMPADDING', (0, 0), (-1, 0), 0), # punktiiri alla võimalikult vähe ruumi
                     ('TOPPADDING', (0, 1), (-1, 1), 0), # punktiiri all oleva sulgudes selgituse kohale vähe ruumi 
                     ('LEFTPADDING', (0,0),(0,-1), 0),
                     ('RIGHTPADDING', (-1,0),(-1,-1), 0),
                     ])

    if test.on_tseis:
        data = [[Paragraph(_('Eksamikomisjoni esimees'), DOT),
                 Paragraph('........................................................', DOTC)],
                ['',
                 Paragraph('(%s)' % _("nimi ja allkiri"), SC)]]
        story.append(Table(data, colWidths=(52*mm, 70*mm), style=TS, hAlign='LEFT'))

        data = [[Paragraph(_('Eksamikomisjoni liige'), DOT),
                 Paragraph('........................................................', DOTC)],
                ['',
                 Paragraph('(%s)' % _("nimi ja allkiri"), SC)]]
        story.append(Table(data, colWidths=(52*mm, 70*mm), style=TS, hAlign='LEFT'))

    else:
        data = [[Paragraph(_('Kooli eksamiskomisjoni esimees'), DOT),
                 Paragraph('........................................................', DOTC)],
                ['',
                 Paragraph('(%s)' % _("nimi ja allkiri"), SC)]]
        story.append(Table(data, colWidths=(52*mm, 70*mm), style=TS, hAlign='LEFT'))

        if toimumisaeg.vaatleja_maaraja:
            data = [[Paragraph(_('Välisvaatleja:'), DOT),
                     Paragraph('..................................', DOTC),
                     Paragraph('_ _ _ _ _ _ _ _ _ _ _', DOTC),
                     Paragraph('..................................', DOTC),
                     Paragraph('..................................', DOTC)],
                    ['',
                     Paragraph('(%s)' % _("NIMI trükitähtedega"), SC),
                     Paragraph('(%s)' % _("isikukood"), SC),
                     Paragraph('(%s)' % _("telefon"), SC),
                     Paragraph('(%s)' % _("allkiri"), SC)]]
            story.append(Table(data, colWidths=(22*mm, 35*mm, 38*mm, 35*mm, 35*mm), style=TS, hAlign='LEFT'))

            story.append(Spacer(100*mm, 12*mm))
            story.append(Paragraph(_('*Kui eksamit vaatleb enam kui üks välisvaatleja, kirjutavad teine, kolmas jne välisvaatleja oma andmed (nimi, isikukood, allkiri) lehe pöördele.'), S))

    story.append(PageBreak())

