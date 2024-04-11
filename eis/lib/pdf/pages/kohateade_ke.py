"Soorituskoha teade kutseeksamile registreerunule"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, sooritaja, sooritused, taiendavinfo):

    story.append(Paragraph('', NBC))
    story.append(Paragraph('', NBC))
    story.append(Spacer(3*mm,3*mm))
    story.append(Paragraph('Kutseeksami toimumise teade', NC))

    kasutaja = sooritaja.kasutaja
    #aadress: vahemikus 4-6 cm ülalt, vähemalt 2 cm vasakust äärest
    li = [kasutaja.nimi] 
    if kasutaja.aadress:
        li.extend(kasutaja.aadress.li_print_aadress(kasutaja))
    aadress = '<br/>'.join(li)

    story.append(Table([[Paragraph(aadress, N), 
                         Paragraph(h.str_from_date(date.today()), N)]],
                       colWidths=(130*mm,30*mm),
                       style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                         ]) 
                       ))    
    
    story.append(Spacer(5*mm, 5*mm))

    story.append(Paragraph('Lp %s' % kasutaja.nimi, N))
    story.append(Spacer(5*mm,5*mm))

    story.append(Paragraph('Teatame kutseeksami toimumise aja ja koha.', N))
    for s in sooritused:
        if s.testiosa.oma_kavaaeg:
            kavaaeg = s.kavaaeg
        else:
            kavaaeg = s.testiruum.algus
        if kavaaeg:
            buf = kavaaeg.strftime('<b>%d.%m.%Y kell %H.%M</b>') + ' - '
        elif s.testiruum.algus:
            buf = s.testiruum.algus.strftime('<b>%d.%m.%Y</b>') + ' - '
        else:
            buf = ''

        testiosa = s.testiosa
        koht = s.testikoht.koht
        ruum = s.testiruum.ruum
        buf += '%s (%s); ' % (testiosa.test.nimi, testiosa.nimi)
        buf += koht.nimi
        if ruum and ruum.tahis:
            buf += ', ruum %s' % ruum.tahis

        tais_aadress = koht.tais_aadress
        if tais_aadress:
            buf += '; %s' % (tais_aadress or '')
        buf += '.'
        
        story.append(Paragraph(buf, N))

    if taiendavinfo:
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(taiendavinfo, N))        

    story.append(PageBreak())

