"Vaatleja meeldetuletus"

from .vaatlejateade import *

def generate(story, kasutaja, labiviijad, taiendavinfo):

    story.append(Paragraph('MEELDETULETUS', NBC))
    story.append(Spacer(10*mm,10*mm))

    story.append(Paragraph('Lugupeetud %s' % kasutaja.nimi, N))
    story.append(Spacer(5*mm,5*mm))

    buf = 'Soovime Teile meelde tuletada, et olete registreeritud välisvaatlejaks '
    if len(labiviijad) == 1:
        buf += ' järgmisele eksamile:'
    else:
        buf += ' järgmistele eksamitele:'
    story.append(Paragraph(buf, N))

    append_labiviijad(story, labiviijad)
    
    story.append(Spacer(15*mm, 15*mm))
    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, N))
    story.append(Paragraph('Kui Te ei saa mingil põhjusel eksamil osaleda, palume sellest viivitamatult teatada allpool toodud telefonidel või e-posti aadressil.', N))
    story.append(Spacer(5*mm, 5*mm))
    story.append(Paragraph('Maie Jürgens', N))
    story.append(Paragraph('Tel 7350562, 56482403', N))
    story.append(Paragraph('maie.jyrgens@harno.ee', N))

    story.append(PageBreak())
