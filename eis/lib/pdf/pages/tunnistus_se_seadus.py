# -*- coding: utf-8 -*- 
# $Id: tunnistus_se_seadus.py 9 2015-06-30 06:34:46Z ahti $
"Seaduse tundmise eksami tunnistus"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis import model
from eis.model import const
import eis.lib.helpers as helpers

def generate(story, tunnistusenr, valjastamisaeg, nimi, kasutaja, sessioon, q_sooritajad, sooritaja):
    # q_sooritajad on alati None

    N14 = ParagraphStyle(name='N14',
                         fontName='Times-Roman',
                         fontSize=14,
                         leading=16,
                         alignment=TA_CENTER)                         
    N16 = ParagraphStyle(name='N16',
                         fontName='Times-Roman',
                         fontSize=16,
                         leading=20,
                         alignment=TA_CENTER)                                                  
    NR16 = ParagraphStyle(name='NR16',
                          fontName='Times-Roman',
                          fontSize=16,
                          leading=18,
                          alignment=TA_RIGHT)
    NB16 = ParagraphStyle(name='NB16',
                          fontName='Times-Bold',
                          fontSize=16,
                          leading=18,
                          alignment=TA_CENTER)                                                   
    NB18 = ParagraphStyle(name='NB18',
                          fontName='Times-Bold',
                          fontSize=18,
                          leading=24,
                          alignment=TA_CENTER)                                                   
    NB20 = ParagraphStyle(name='NB20',
                          fontName='Times-Bold',
                          fontSize=20,
                          leading=24,
                          alignment=TA_CENTER)                                                   

    story.append(Spacer(5*mm, 50*mm))

    fn_img = os.path.join(IMAGES_DIR,  'eestivapp.jpg')
    story.append(Image(fn_img, width=96, height=96))

    story.append(Paragraph('Tunnistus nr %s' % tunnistusenr, N16))
    story.append(Spacer(5*mm,5*mm))

    story.append(Paragraph(nimi.upper(), NB20))
    story.append(Paragraph('(ees- ja perekonnanimi)', N14))
    story.append(Spacer(5*mm, 5*mm))

    story.append(Paragraph(kasutaja.isikukood or kasutaja.synnikpv.strftime('%d.%m.%Y'), NB18))
    story.append(Paragraph('(isikukood või sünniaeg)', N14))    
    story.append(Spacer(5*mm, 9*mm))

    story.append(Paragraph('on sooritanud Eesti Vabariigi põhiseaduse ja', N16))
    story.append(Paragraph('kodakondsuse seaduse tundmise eksami', N16))
    story.append(Paragraph('kodakondsuse seaduse § 9 lõikes 1 sätestatud nõuete', N16))
    story.append(Paragraph('kohaselt.', N16))        
    story.append(Spacer(5*mm, 5*mm))
    story.append(Paragraph('Eksam on sooritatud', N16))
    story.append(Spacer(5*mm, 2*mm))

    buf = ''   
    for sooritus in sooritaja.sooritused:
        if sooritus.staatus == const.S_STAATUS_TEHTUD:
            aadress = sooritus.testikoht.koht.aadress
            kohas = aadress and aadress.vald_liigita or ''
            if kohas:
                buf += '%s, ' % (model.Asukohamaarus.get_for(kohas))
            break
            
    protokollinr = sooritus.testiprotokoll.tahised
    # TSEISist imporditud protokollides esineb korduvaid numbreid, 
    # mis on EISi paigutamiseks tähistatud lõpuga .1 - eemaldame selle lõpu
    if protokollinr.endswith('.1'): 
        protokollinr = protokollinr[:-2]
    buf += '%s, pr %s' % (sooritus.algus.strftime('%d.%m.%Y'), protokollinr)

    story.append(Paragraph(buf, N16))
    story.append(Spacer(5*mm, 2*mm))
    story.append(Paragraph('(koht, kuupäev, protokolli number)', N14))

    story.append(Spacer(5*mm, 16*mm))

    buf = 'Haridus- ja Noorteamet<br/>allkirjastatud digitaalselt'
    story.append(Table([[Paragraph(buf, NR16)]], 
                       colWidths=(150*mm),
                       ))    

    
    story.append(PageBreak())

