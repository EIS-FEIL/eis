"Meeldetuletus riigieksamil osalemise tasu maksmiseks"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, sooritaja):

    kasutaja = sooritaja.kasutaja
    test = sooritaja.test
    tasu = ('%.2f' % sooritaja.tasu).replace('.',',')

    story.append(Paragraph('Lp %s' % kasutaja.nimi, N))
    story.append(Spacer(5*mm,5*mm))

    buf = 'Meie andmetel on Teil tasumata riigilõiv %s eurot riigieksamile "%s" registreerimise eest.' % (tasu, test.nimi)
    story.append(Paragraph(buf, N))
    story.append(Spacer(3*mm,3*mm))

    buf = 'Vastavalt Riigilõivuseadusele (§ 58) peavad keskhariduse omandanud isikud tasuma sama õppeaine riigieksami korduvaks sooritamiseks registreerimise eest riigilõivu %s eurot.' % (tasu)
    story.append(Paragraph(buf, N))
    story.append(Spacer(3*mm,3*mm))

    buf = 'Palume riigilõiv maksta hiljemalt 25. jaanuariks Rahandusministeeriumi arveldusarvele:'
    story.append(Paragraph(buf, N))
    buf = ' • LHV Pank – EE777700771003813400'
    story.append(Paragraph(buf, N))
    buf = ' • Luminor Pank – EE701700017001577198'
    story.append(Paragraph(buf, N))
    buf = ' • SEB Pank – EE891010220034796011'
    story.append(Paragraph(buf, N))
    buf = ' • Swedbank – EE932200221023778606'
    story.append(Paragraph(buf, N))
    story.append(Spacer(3*mm,3*mm))

    buf = 'Viitenumbriks tuleb märkida 2900082401.'
    story.append(Paragraph(buf, N))
    story.append(Spacer(3*mm,3*mm))
    buf = 'Riigilõivu maksmata jätmisel ei ole Teil võimalik käesoleval aastal nimetatud riigieksamit sooritada.'
    story.append(Paragraph(buf, N))
    story.append(Spacer(13*mm,13*mm))
    
    buf = 'Haridus- ja Noorteamet<br/>' +\
        'Lõõtsa 4, Tallinn 11415<br/>' +\
        'Tel 7350 500<br/>' +\
        'https://www.harno.ee<br/>' +\
        'e-post: info@harno.ee'
    story.append(Paragraph(buf, N))

    story.append(PageBreak())

