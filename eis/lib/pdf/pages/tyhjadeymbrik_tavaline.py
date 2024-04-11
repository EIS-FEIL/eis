"Tühjade tööde tagastamise ümbrik"
from eis.model import const
from .pdfutils import *
from .stylesheet import *
from . import tagastusymbrikupais_t

def generate(story, toimumisaeg, testikoht, testipakett, yliik, kursus_nimi):

    test = toimumisaeg.testimiskord.test
    koht = testikoht.koht

    story.append(Spacer(50*mm,50*mm))
    
    story.append(Paragraph('Haridus- ja Noorteamet', LC))
    story.append(Paragraph(koht.nimi, LC))
    if testipakett.testiruum and testipakett.testiruum.ruum:
        # on_ruumiprotokoll
        story.append(Paragraph('ruum %s' % testipakett.testiruum.ruum.tahis, LC))
    test_nimi = test.nimi
    if kursus_nimi:
        test_nimi += ' (%s)' % (kursus_nimi.lower())
    story.append(Paragraph(test_nimi, LBC))
    story.append(Paragraph(yliik.nimi, LBC))
    story.append(Paragraph('Eksamikeel: %s' % testipakett.lang_nimi.lower(), LC))
    
    story.append(Spacer(100*mm, 12*mm))

    story.append(Paragraph('Tühjade tööde tagastamise ümbrik', LC))
    story.append(PageBreak())

