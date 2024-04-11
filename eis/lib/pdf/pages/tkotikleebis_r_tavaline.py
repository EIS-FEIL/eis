"Tagastamise turvakoti kleebis kuupäevadega"

from eis.model import const

from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, testikoht, testipakett, turvakott, n):
    gen_kleebis(story, toimumisaeg, testikoht, testipakett, turvakott, True, n)

def gen_kleebis(story, toimumisaeg, testikoht, testipakett, turvakott, on_kpv, n):
    test = toimumisaeg.testimiskord.test
    koht_nimi = testikoht.koht.nimi
    if testipakett.testiruum and testipakett.testiruum.ruum:
        koht_nimi = '%s, ruum %s' % (koht_nimi, testipakett.testiruum.ruum.tahis)

    if testikoht.koht.piirkond:
        story.append(Paragraph(testikoht.koht.piirkond.get_nimi_ylematega(), MC))
    story.append(Paragraph(koht_nimi, MC))

    story.append(Paragraph(test.nimi, MBC))
    if len(test.testiosad) > 1:
        story.append(Paragraph(toimumisaeg.testiosa.nimi, MC))
    
    if on_kpv:
        li_kpv = list(set([tr.algus.date() for tr in testikoht.testiruumid if tr.algus]))
        li_kpv.sort()
        skpv = ', '.join([kpv.strftime('%d.%m.%Y') for kpv in li_kpv])
        story.append(Paragraph(skpv, MC))

    story.append(Paragraph('Eksami sooritamise keel: %s' % (testipakett.lang_nimi.lower()), MC))
    
    if turvakott.suund == const.SUUND_TAGASI:
        story.append(Paragraph('Tagastuskott %d (%d)' % (n, testipakett.tagastuskottidearv), MC))
    else:
        story.append(Paragraph('Väljastuskott %d (%d)' % (n, testipakett.valjastuskottidearv), MC))

    story.append(PageBreak())

