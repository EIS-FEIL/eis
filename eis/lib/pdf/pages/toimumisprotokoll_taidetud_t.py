"Eksami toimumise protokoll täidetud EISi kantud toimumise andmetega"

from datetime import date
import eis.model as model
import eiscore.const as const
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
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        buf = _('Protokoll riigieksami toimumise kohta')
    elif test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        buf = _('Protokoll põhikooli lõpueksami toimumise kohta')
    elif test.testiliik_kood == const.TESTILIIK_TASE:
        buf = _('Protokoll eesti keele {s}-taseme eksami toimumise kohta').format(s=test.keeletase_nimi)
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:
        buf = _('Protokoll Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami toimumise kohta')
    else:
        buf = _('Protokoll eksami toimumise kohta')
    story.append(Paragraph(buf, LC))
    story.append(Spacer(100*mm, 12*mm))

    kuupaev = testikoht.millal or date.today().strftime('%d.%m.%Y')
    data = [[[Paragraph('<u>%s</u>' % kuupaev, NB),
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
        
    q = (model.SessionR.query(model.Sooritus.tahis)
         .join(model.Sooritus.testiprotokoll)
         .filter(model.Sooritus.testikoht_id==testikoht.id)
         .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
         .join(model.Sooritus.sooritaja)
         .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
         )
    if toimumisprotokoll.lang:
        q = q.filter(model.Sooritaja.lang==toimumisprotokoll.lang)
    if testiruum:
        q = q.filter(model.Sooritus.testiruum_id==testiruum.id)
        
    nimi_jrk = toimumisprotokoll.testikoht.toimumisaeg.nimi_jrk

    def get_sooritus_list(staatus):
        q1 = q.filter(model.Sooritus.staatus==staatus)
        if nimi_jrk:
            q1 = q1.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
        else:
            q1 = q1.order_by(model.Sooritus.tahis)
        return [rcd[0] for rcd in q1.all()]
    
    osalenud = get_sooritus_list(const.S_STAATUS_TEHTUD)
    puudunud = get_sooritus_list(const.S_STAATUS_PUUDUS)
    katkestanud = get_sooritus_list(const.S_STAATUS_KATKESPROT)    
    korvaldatud = get_sooritus_list(const.S_STAATUS_EEMALDATUD)

    if len(osalenud) == 1:
        story.append(Paragraph(_('Eksamil osales {n} õpilane.').format(n='<b>1</b>'), DOT))
    else:
        story.append(Paragraph(_('Eksamil osales {n} õpilast.').format(n='<b>%d</b>' % len(osalenud)), DOT))
    buf = _('Eksamile registreerunutest puudus {n} õpilast').format(n=len(puudunud))
    if len(puudunud) and not (None in puudunud):
        buf += ': <b>' + ', '.join(puudunud) + '</b>.'
    else:
        buf += '.'
    story.append(Paragraph(buf, N))


    if len(katkestanud) == 1:
        buf = _('Eksami katkestas {n} eksaminand').format(n='<b>1</b>')
    else:
        buf = _('Eksami katkestas <b>{n}</b> eksaminandi').format(n='<b>%d</b>' % len(katkestanud))
    if len(katkestanud) and not (None in katkestanud):
        buf += ': <b>' + ', '.join(katkestanud) + '</b>.'
    else:
        buf += '.'
    story.append(Paragraph(buf, N))


    if len(korvaldatud) == 1:
        buf = _('Eksamilt kõrvaldati {n} õpilane').format(n='<b>1</b>')
    else:
        buf = _('Eksamilt kõrvaldati {n} õpilast').format(n=len(korvaldatud))
    if len(korvaldatud) and not (None in korvaldatud):
        buf += ': <b>' + ', '.join(korvaldatud) + '</b>.'
    else:
        buf += '.'
    story.append(Paragraph(buf, N))


    if toimumisprotokoll.markus:
        story.append(Paragraph(_('Märkusi (eksamil ilmnenud eksamikorrale mittevastavused ja muud eksamil tekkinud eriolukorrad):'), N))
        story.append(Paragraph('<b>%s</b>' % toimumisprotokoll.markus, N))

    toodearv = len(osalenud) + len(katkestanud) + len(korvaldatud)
    for testipakett in toimumisprotokoll.testipaketid:
        if testipakett.tagastusymbrikearv:
            story.append(Paragraph(_('Tööd on suletud {n1} ümbrikusse ning neis on kokku {n2} eksamitööd.').format(n1=testipakett.tagastusymbrikearv, n2=toodearv), N))
        break
    
    cnt = len(toimumisprotokoll.ruumifailid)
    if cnt:
        story.append(Paragraph(_('Protokollile on lisatud {n} faili.').format(n='<b>%d</b>' % cnt), N))

    story.append(Spacer(10*mm,10*mm))

    TS = TableStyle([('TOPPADDING', (0,0), (-1,0), 6), # enne tabelit ruumi
                     ('BOTTOMPADDING', (0, 0), (-1, 0), 0), # punktiiri alla võimalikult vähe ruumi
                     ('TOPPADDING', (0, 1), (-1, 1), 0), # punktiiri all oleva sulgudes selgituse kohale vähe ruumi 
                     ('LEFTPADDING', (0,0),(0,-1), 0),
                     ('RIGHTPADDING', (-1,0),(-1,-1), 0),
                     ])

    if test.on_tseis:
        esimehed = []
        liikmed = []
        for lv in toimumisprotokoll.testiruum.labiviijad:
            if not lv.kasutaja:
                continue
            k_nimi = lv.kasutaja.nimi
            if lv.kasutajagrupp_id == const.GRUPP_KOMISJON_ESIMEES:
                esimehed.append(k_nimi)
            elif lv.kasutajagrupp_id == const.GRUPP_KOMISJON:
                liikmed.append(k_nimi)

        for nimi in esimehed:
            data = [[Paragraph(_('Eksamikomisjoni esimees'), DOT),
                     Paragraph('%s...................................' % nimi, DOTC)],
                    ['',
                     Paragraph('(%s)' % _("nimi ja allkiri"), SC)]]
            story.append(Table(data, colWidths=(52*mm, 70*mm), style=TS, hAlign='LEFT'))
        for nimi in liikmed:
            data = [[Paragraph(_('Eksamikomisjoni liige'), DOT),
                     Paragraph('%s...................................' % nimi, DOTC)],
                    ['',
                     Paragraph('(%s)' % _("nimi ja allkiri"), SC)]]
            story.append(Table(data, colWidths=(52*mm, 70*mm), style=TS, hAlign='LEFT'))
        
    else:
        data = [[Paragraph(_('Kooli eksamikomisjoni esimees:'), DOT),
                 Paragraph('........................................................', DOTC)],
                ['',
                 Paragraph('(%s)' % _("nimi ja allkiri"), SC)]]
        story.append(Table(data, colWidths=(52*mm, 70*mm), style=TS, hAlign='LEFT'))

        for lv in testikoht.labiviijad:
            if not lv.kasutaja:
                continue
            if lv.kasutajagrupp_id == const.GRUPP_VAATLEJA and lv.kasutaja_id:
                data = [[Paragraph(_('Välisvaatleja:'), DOT),
                         Paragraph(lv.kasutaja.nimi.upper(), DOTC),
                         Paragraph(lv.kasutaja.isikukood, DOTC),
                         Paragraph(lv.kasutaja.telefon or '.....................................', DOTC),
                         Paragraph('.....................................', DOTC)],
                        ['',
                         Paragraph('(%s)' % _("NIMI trükitähtedega"), SC),
                         Paragraph('(%s)' % _("isikukood"), SC),
                         Paragraph('(%s)' % _("telefon"), SC),
                         Paragraph('(%s)' % _("allkiri"), SC)]]
                story.append(Table(data, colWidths=(22*mm, 35*mm, 38*mm, 35*mm, 35*mm), style=TS, hAlign='LEFT'))

    story.append(PageBreak())
    
