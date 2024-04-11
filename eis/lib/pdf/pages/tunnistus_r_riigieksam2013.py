"Riigieksamitunnistus kuni 2013"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis import model
from eis.model import const
import eis.lib.helpers as helpers

def generate(story, tunnistusenr, valjastamisaeg, nimi, kasutaja, sessioon, q_sooritajad, sooritaja1):
    # riigieksami tunnistuse korral on parameeter "sooritaja" alati None
    N10 = ParagraphStyle(name='N10',
                         fontName='Times-Roman',
                         fontSize=10,
                         leading=16)
    N12 = ParagraphStyle(name='N12',
                         fontName='Times-Roman',
                         fontSize=12,
                         leading=15)
    NC12 = ParagraphStyle(name='NC12',
                          fontName='Times-Roman',
                          fontSize=12,
                          leading=15,
                          alignment=TA_CENTER)
    NB12 = ParagraphStyle(name='NB12',
                          fontName='Times-Bold',
                          fontSize=12,
                          leading=18)
    NB18 = ParagraphStyle(name='NB18',
                          fontName='Times-Bold',
                          fontSize=18,
                          leading=22)
    NBC12 = ParagraphStyle(name='NBC12',
                           fontName='Times-Bold',
                           fontSize=12,
                           alignment=TA_CENTER,
                           leading=18)

    S1 = ParagraphStyle(name='S',
                        fontName='Times-Roman',
                        fontSize=15,
                        leading=21,
                        alignment=TA_CENTER)
    S2 = ParagraphStyle(name='S',
                        fontName='Times-Bold',
                        fontSize=26,
                        leading=32,
                        spaceBefore=3,
                        alignment=TA_CENTER)

    story.append(Paragraph('EESTI VABARIIK', S1))

    fn_img = os.path.join(IMAGES_DIR,  'eestivapp.jpg')
    story.append(Image(fn_img, width=48, height=48))

    story.append(Paragraph('RIIGIEKSAMITUNNISTUS', S2))
    story.append(Spacer(20*mm, 5*mm))

    story.append(Paragraph('Nr: %s' % tunnistusenr, NBC12))
    story.append(Spacer(20*mm,20*mm))

    story.append(Paragraph('<font size=12>Selle tunnistuse omanik</font> %s' % nimi.upper(), NB18))
    story.append(Spacer(20*mm, 5*mm))

    story.append(Paragraph('ISIKUKOOD %s' % kasutaja.isikukood, N10))
    story.append(Spacer(20*mm, 5*mm))

    story.append(Paragraph('sooritas järgmised riigieksamid:', N12))
    story.append(Spacer(20*mm, 5*mm))

    def get_kpv(sooritaja_id):
        "Leiame testi kuupäeva. Kui toimub mitmel päeval, siis kasutame kirjaliku osa kuupäeva."
        algus = None
        q_kpv = model.SessionR.query(model.Sooritus.algus, model.Testiosa.vastvorm_kood).\
                join(model.Sooritus.testiosa).\
                filter(model.Sooritus.sooritaja_id==sooritaja_id)
        for algus, vastvorm_kood in q_kpv.all():
            if vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
                break
        return algus
    
    # eksamitulemuste loetelu tabel

    rowdata = []
    for sooritaja, test in q_sooritajad.all():
        kuupaev = get_kpv(sooritaja.id)
        rowdata.append((kuupaev, sooritaja, test))

    data = [[Paragraph('Kuupäev', NB12),
             Paragraph('Õppeaine', NB12),
             Paragraph('Tulemus', NB12)]]
    for kuupaev, sooritaja, test in sorted(rowdata, key=lambda row: row[0] or const.MAX_DATETIME):
        aine_nimi = model.Klrida.get_str('AINE', test.aine_kood)
        pallid = helpers.fstr(sooritaja.pallid)
        data.append([Paragraph(helpers.str_from_date(kuupaev), N12),
                     Paragraph(aine_nimi, N12), 
                     Paragraph(pallid, N12)])

    TS = TableStyle([('LINEBELOW',(0,-1),(-1,-1), 0.5, colors.black),])
    story.append(Table(data, 
                       colWidths=(30*mm, 115*mm, 36*mm),
                       style=TS,
                       repeatRows=1))

    story.append(PageBreak())


def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    canvas.setFont('Times-Roman', 12)

    canvas.drawString(15*mm, 50*mm, 'Tallinnas %s' % (helpers.str_from_date(pdoc.valjastamisaeg)))
    canvas.drawString(15*mm, 45*mm, 'Allkirjastatud digitaalselt')

    if pdoc.oppeaasta < 2001:
        canvas.drawString(25*mm, 24*mm, 'Emakeele riigieksamit hinnati kümnepallisüsteemis, kõiki teisi eksameid sajapallisüsteemis.')
    else:
        canvas.drawString(60*mm, 24*mm, 'Riigieksamite tulemused on antud sajapallisüsteemis.')
    canvas.drawString(22*mm, 19*mm, 'TUNNISTUS ON KEHTIV KOOS KESKHARIDUST TÕENDAVA LÕPUTUNNISTUSEGA.')
    canvas.restoreState()

def later_pages(canvas, doc, pdoc):
    "Teise ja järgmiste lehekülgede jalus"
    return first_page(canvas, doc, pdoc)
