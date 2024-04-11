"Teade vaatlejale"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
from eis.model.usersession import _
import eis.lib.helpers as h

def generate(story, kasutaja, labiviijad, testiliik):

    story.append(Paragraph(_('Haridus- ja Noorteamet'), NBC))
    story.append(Paragraph(_('Lõõtsa 4, 11415 Tallinn'), SBC))
    story.append(Spacer(10*mm,10*mm))

    story.append(Paragraph(_('Lugupeetud {s}').format(s=kasutaja.nimi), N))
    story.append(Spacer(5*mm,5*mm))

    if testiliik == const.TESTILIIK_SEADUS:
        if len(labiviijad) == 1:
            buf = _('Olete määratud osalema peatselt toimuval Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksamil järgmises rollis:')
        else:
            buf = _('Olete määratud osalema peatselt toimuval Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksamil järgmistes rollides:')

    elif testiliik == const.TESTILIIK_TASE:
        if len(labiviijad) == 1:
            buf = _('Olete määratud osalema peatselt toimuval eesti keele tasemeeksamil järgmises rollis:')
        else:
            buf = _('Olete määratud osalema peatselt toimuval eesti keele tasemeeksamil järgmistes rollides:')            
    else:
        # riigieksam ja põhikooli lõpueksam
        if len(labiviijad) == 1:
            buf = _('Olete määratud järgmise eksami läbiviijaks:')
        else:
            buf = _('Olete määratud järgmiste eksamite läbiviijaks:')            

    story.append(Paragraph(buf, N))

    append_labiviijad(story, labiviijad)
    
    story.append(Spacer(15*mm, 15*mm))
    story.append(Paragraph('Maie Jürgens', NB))
    story.append(Paragraph('Tel 7350562, 56482403', NB))
    story.append(PageBreak())

def append_labiviijad(story, labiviijad):

    data = [[Paragraph(_('Kuupäev'), SB),
             Paragraph(_('Algusaeg'), SB),
             Paragraph(_('Eksam'), SB),
             Paragraph(_('Roll'), SB),             
             Paragraph(_('Eksamikoht'), SB),
             Paragraph(_('Aadress'), SB),
             ]]
    for lv in labiviijad:
        tr = lv.testiruum
        testikoht = lv.testikoht
        koht = testikoht and testikoht.koht
        tais_aadress = koht and koht.tais_aadress
        if tr and tr.algus:
            aeg_kpv = tr.algus.strftime('%d.%m.%Y')
            aeg_kell = tr.algus.strftime('%H.%M')
        else:
            aeg_kpv = aeg_kell = ''
        koht_nimi = koht and koht.nimi or ''
        ruum_tahis = tr and tr.ruum and tr.ruum.tahis or None
        if ruum_tahis:
            koht_nimi = '%s, %s %s' % (koht_nimi, _("ruum"), ruum_tahis)
        test = lv.toimumisaeg.testimiskord.test
        
        data.append([Paragraph(aeg_kpv, S),
                     Paragraph(aeg_kell, S),
                     Paragraph(test.nimi, S),
                     Paragraph(lv.kasutajagrupp.nimi, S),
                     Paragraph(koht_nimi or '', S),
                     Paragraph(tais_aadress or '', S),
                     ])

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[2] += vaba/4 
        col_widths[3] += vaba/4 
        col_widths[4] += vaba/4 
        col_widths[5] += vaba/4 
        
    story.append(Table(data,
                       colWidths=col_widths,
                       style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                         ]) 
                       ))    
