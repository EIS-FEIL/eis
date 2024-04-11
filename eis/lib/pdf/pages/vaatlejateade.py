"Teade vaatlejale"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, kasutaja, labiviijad, taiendavinfo):

    story.append(Paragraph('Haridus- ja Noorteamet', NBC))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn', SBC))
    story.append(Spacer(10*mm,10*mm))

    story.append(Paragraph('Lugupeetud %s' % kasutaja.nimi, N))
    story.append(Spacer(5*mm,5*mm))

    if len(labiviijad) == 1:
        story.append(Paragraph('Olete registreeritud välisvaatlejaks järgmise eksami läbiviimisel.', N))
    else:
        story.append(Paragraph('Olete registreeritud välisvaatlejaks järgmiste eksamite läbiviimisel.', N))

    append_labiviijad(story, labiviijad)
    
    story.append(Spacer(15*mm, 15*mm))
    if taiendavinfo:
        story.append(Paragraph(taiendavinfo, NB))
    story.append(Paragraph('Kui Te ei saa mingil põhjusel eksamil osaleda, palume sellest viivitamatult teatada allpool toodud telefonidel või e-posti aadressil.', NB))
    story.append(Spacer(5*mm, 5*mm))
    story.append(Paragraph('Maie Jürgens', NB))
    story.append(Paragraph('Tel 7350562, 56482403', NB))
    story.append(Paragraph('maie.jyrgens@harno.ee', NB))

    story.append(PageBreak())

def append_labiviijad(story, labiviijad):
    data = [[Paragraph('Kuupäev', SB),
             Paragraph('Algusaeg',SB),
             Paragraph('Eksam', SB),
             Paragraph('Eksamikoht', SB),
             Paragraph('Aadress', SB),
             ]]
    for lv in labiviijad:
        tr = lv.testiruum
        tais_aadress = tr.testikoht.koht.tais_aadress
        if tr.algus:
            aeg_kpv = tr.algus.strftime('%d.%m.%Y')
            aeg_kell = tr.algus.strftime('%H.%M')
        else:
            aeg_kpv = aeg_kell = ''
        koht_nimi = tr.testikoht.koht.nimi
        ruum_tahis = tr.ruum and tr.ruum.tahis or None
        if ruum_tahis:
            koht_nimi = '%s, ruum %s' % (koht_nimi, ruum_tahis)
        data.append([Paragraph(aeg_kpv, S),
                     Paragraph(aeg_kell, S),
                     Paragraph(lv.toimumisaeg.testimiskord.test.nimi, S),
                     Paragraph(koht_nimi, S),
                     Paragraph(tais_aadress or '', S),
                     ])

    story.append(Table(data,
                       colWidths=(16*mm,13*mm,36*mm,48*mm,60*mm),
                       style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                         ]) 
                       ))    
