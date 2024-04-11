"Avamisprotokoll"

from datetime import date
from eis.model.usersession import _
from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, testipakett):

    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    if test.on_tseis:
        return generate_tseis(story, toimumisaeg, testikoht, testipakett)

    # riigieksami avamisprotokoll
    
    koht_nimi = testikoht.koht.nimi

    story.append(Paragraph(_('Toimumisaja tähis') + ': <font size="14"><b>%s</b></font>' % toimumisaeg.tahised, NR))
    story.append(Spacer(5*mm, 5*mm))
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        story.append(Paragraph(_('Protokoll riigieksamitööde paketi avamise kohta'), LC))
    elif test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        story.append(Paragraph(_('Protokoll põhikooli lõpueksamitööde paketi avamise kohta'), LC))        
       
    story.append(Spacer(100*mm, 12*mm))

    data = [[[Paragraph('<u>%s</u>' % testikoht.millal, NB),
              Paragraph('(%s)' % _("kuupäev"), S)],
             [Paragraph('<u>%s</u>' % testikoht.tahis, NBR),
              Paragraph('(%s)' % _("kooli kood"), SR)]],
            [[Paragraph('<u>%s, %s</u>' % (test.nimi, testiosa.nimi), NB),
              Paragraph('(%s)' % _("eksam"), S)],
             [Paragraph('<u>%s</u>' % koht_nimi, NBR),
              Paragraph('(%s)' % _("kooli nimi"), SR)]],
            ]
    lang = testipakett and testipakett.lang
    if lang:
        lang_nimi = testipakett.lang_nimi.capitalize()
        data.append([[Paragraph('<u>%s</u>' % lang_nimi, NB),
                      Paragraph('(%s)' % _("eksami sooritamise keel"), S)],
                     ''])

    TS = TableStyle([('ALIGN',(0,0),(0,-1), 'LEFT'),
                     ('ALIGN',(1,0),(1,-1), 'RIGHT'),
                     ('LEFTPADDING', (0,0),(-1,-1), 0),

                     ])        
    story.append(Table(data, colWidths=(83*mm, 83*mm), style=TS, hAlign='LEFT'))
        
    story.append(Paragraph(_('Komisjon koosseisus') + ' ' + '.'*148, DOT))
    for n in range(3):
        story.append(Paragraph('.'*183, DOT))

    if toimumisaeg.testiosa.vastvorm_kood == const.VASTVORM_SP:        
        buf = _('kinnitab, et {kool}, kooli kood {kood}, sai Haridus- ja Noorteametilt {test} eksamimaterjalid alljärgnevalt:').format(kool=koht_nimi, kood=testikoht.tahis, test='<u>%s</u>' % test.nimi)
        story.append(Paragraph(buf, DOT))

        row = [Paragraph(_('kuupäev') + ' ............................', DOT),
               Paragraph(_('ümbrikute arv') + ' ...........', DOT)]
        story.append(Table([row, row, row, row, row], colWidths=(45*mm, 35*mm)))
    else:
        buf = _('kinnitab, et {kool}, kooli kood {kood}, sai Haridus- ja Noorteametilt {test} eksamitööd {n} ümbrikus.').format(kool=koht_nimi, kood=testikoht.tahis, test='<u>%s</u>' % test.nimi, n='<u>%s</u>' % (testipakett and testipakett.valjastusymbrikearv or 0))        
        story.append(Paragraph(buf, DOT))
        
    story.append(Spacer(100*mm, 6*mm))
    story.append(Paragraph(_('Märkusi (saadetise sisu vastavus tellimusele, ümbrikute salastatus vm, millest peetakse vajalikuks informeerida Haridus- ja Noorteametit):'), DOT))

    for n in range(7):
        story.append(Paragraph('.'*183, DOT))

    story.append(Spacer(100*mm,15*mm))

    data = [[Paragraph(_('Kooli eksamikomisjoni esimees:'), NR),
             [Paragraph('.'*68, N),
              Paragraph('(%s)' % _("nimi ja allkiri"), SC)]],
            ]
    if toimumisaeg.vaatleja_maaraja:
        data.append(
            [Paragraph(_('Välisvaatleja:'), NR),
             [Paragraph('.'*68, N),
              Paragraph('(%s)' % _("nimi ja allkiri"), SC)]])
        
    TS = TableStyle([('ALIGN',(0,0),(0,-1), 'RIGHT'),
                     ('ALIGN',(1,0),(1,-1), 'LEFT'),
                     ('VALIGN',(0,0), (-1,-1), 'TOP'),
                     ])        
    story.append(Table(data, 
                       colWidths=(55*mm, 69*mm),
                       style=TS))

    story.append(PageBreak())
    
def generate_tseis(story, toimumisaeg, testikoht, testipakett):
    # TE, SE avamisprotokoll
    
    test = toimumisaeg.testiosa.test
    koht_nimi = testikoht.koht.nimi
    ruum = testipakett.testiruum.ruum
    ruum_tahis = ruum and ruum.tahis or None

    story.append(Paragraph(_('Toimumisaja tähis') + ': <font size="14"><b>%s</b></font>' % toimumisaeg.tahised, NR))
    story.append(Spacer(5*mm, 5*mm))
    if test.testiliik_kood == const.TESTILIIK_TASE:
        story.append(Paragraph(_('Protokoll eesti keele {tase}-taseme eksami eksamitööde paketi avamise kohta').format(tase=test.keeletase_nimi), LC))
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:        
        story.append(Paragraph(_('Protokoll Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami eksamitööde paketi avamise kohta'), LC))
        
    story.append(Spacer(100*mm, 12*mm))

    data = [[Paragraph(testikoht.alates.strftime('%d.%m.%Y %H.%M'), NB),
             ]]

    if ruum_tahis:
        data[0].append(Paragraph('%s<br/>%s %s' % (koht_nimi, _("Ruum"), ruum_tahis), NBR))
        colWidths = (53*mm, 113*mm)
        TS = TableStyle([('ALIGN',(0,0),(0,-1), 'LEFT'),
                         ('ALIGN',(1,0),(1,-1), 'RIGHT'),
                         ('LEFTPADDING', (0,0),(-1,-1), 0),
                         ])        
    else:
        colWidths = (53*mm,)
        TS = TableStyle([('ALIGN',(0,0),(0,-1), 'LEFT'),
                         ('LEFTPADDING', (0,0),(-1,-1), 0),
                         ])  
      
    story.append(Table(data, colWidths=colWidths, style=TS, hAlign='LEFT'))
        
    story.append(Paragraph(_('Eksamikomisjon koosseisus') + ' ' + '.'*148, DOT))
    for n in range(3):
        story.append(Paragraph('.'*183, DOT))

    
    if ruum_tahis:
        kes = '%s, %s %s' % (koht_nimi, _("ruum"), ruum_tahis)
    else:
        kes = koht_nimi
    story.append(Paragraph(_('kinnitab, et {kool}<br/> sai Haridus- ja Noorteametilt _________ eksamitööd _________ ümbrikus.').format(kool=koht_nimi), DOT))
    story.append(Paragraph(_('Järgnevalt tagastab _________ täidetud eksamitööd ________ ümbrikus.'), DOT))
        
    story.append(Spacer(100*mm, 6*mm))
    story.append(Paragraph(_('Märkusi (materjalide vastavus tellimusele, ümbrikute salastatus vm, millest peetakse vajalikuks informeerida Haridus- ja Noorteametit):'), DOT))

    for n in range(7):
        story.append(Paragraph('.'*183, DOT))

    story.append(Spacer(100*mm,15*mm))

    data = [[Paragraph(_('Eksamikomisjoni esimees:'), NR),
             [Paragraph('.'*68, N),
              Paragraph('(%s)' % _("nimi ja allkiri"), SC)]],
            [Paragraph(_('Eksamikomisjoni liige:'), NR),
             [Paragraph('.'*68, N),
              Paragraph('(%s)' % _("nimi ja allkiri"), SC)]],
            ]
        
    TS = TableStyle([('ALIGN',(0,0),(0,-1), 'RIGHT'),
                     ('ALIGN',(1,0),(1,-1), 'LEFT'),
                     ('VALIGN',(0,0), (-1,-1), 'TOP'),
                     ])        
    story.append(Table(data, 
                       colWidths=(55*mm, 69*mm),
                       style=TS))

    story.append(PageBreak())
    
