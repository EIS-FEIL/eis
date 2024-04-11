"Protokollide ümbrike ja tagastusümbrike päis"
 
from .pdfutils import *
from .stylesheet import *

def header(story, toimumisaeg, tpakett, tpr=None, ymbrikuliik=None, tpr2=None):

    TB = TableStyle([('BOX',(0,0),(-1,-1), 1,colors.black),                         
                     ])

    TS = TableStyle([('FONTSIZE',(0,0),(-1,-1), 16),
                     ('GRID',(0,0),(-1,-1), 0.5,colors.black),                         
                     ])        

    test = toimumisaeg.testimiskord.test
    algus = toimumisaeg.alates.strftime('%d.%m.%Y')

    fn_img = os.path.join(IMAGES_DIR,  'haridus_ja_noorteamet_logo.png')    

    testikoht = tpakett.testikoht
    testiruum = tpakett.testiruum
    
    if tpr:
        tahised = tpr.tahised
        if tpr2:
            # ruumiymbrik 2 protokolliryhma kohta
            tahised += '/' + tpr2.tahis
    elif testiruum:
        # toimumisaeg.on_ruumiprotokoll
        tahised = '%s/%s' % (testikoht.tahised, testiruum.tahis)
    else:
        tahised = testikoht.tahised

    if tpr and ymbrikuliik:
        tahised_bar = '%s-%s' % (tahised, ymbrikuliik.tahis)
    else:
        if ymbrikuliik or tpr:
            # pole peaymbrik
            tahised_bar = tahised
        else:
            tahised_bar = '%s-%s' % (tahised, tpakett.lang)

    kood_txt = tahised
    if tpr:
        testiruum = tpr.testiruum
        ruum = testiruum.ruum
        if ruum:
            r_tahis = ruum.tahis
            if r_tahis:
                kood_txt += '<br/> ruum %s' % (r_tahis)
    BAR = ParagraphStyle(name='Barcode',
                         fontName='Barcode',
                         fontSize=36,
                         leading=12,
                         alignment=TA_RIGHT,
                         spaceBefore=3,
                         spaceAfter=3)
    EXLBR = ParagraphStyle(name='ExtraLarge',
                           parent=LBR,
                           fontSize=22)
    # 3of9 triipkoodi alguses ja lõpus peab olema tärn
    kood_table = [Paragraph('*%s*' % tahised_bar, BAR),
                  Paragraph('<br/>'+kood_txt, EXLBR)]

    buf = test.nimi

    kursus_nimi = tpr and tpr.kursus_nimi
    if kursus_nimi:
        buf += ' (%s)' % (kursus_nimi.lower())

    buf += '<br/>%s' % (algus)
    
    if ymbrikuliik:
        buf += '<br/>Eksami sooritamise keel: %s' % (tpakett.lang_nimi.lower())

    data = [[Image(fn_img, width=140, height=51),
             Paragraph(buf, LBR),
             kood_table
             ]]
    story.append(Table(data,
                       colWidths=(60*mm,90*mm,135*mm),
                       rowHeights=(30*mm,),
                       style=TableStyle([('LINEBELOW', (0,0),(-1,-1), 2,colors.black),
                                         ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
                                         ]) 
                       ))
    #('LINEAFTER', (1,0),(1,0), 2, colors.black),

    if ymbrikuliik:
        # kahe joone vaheline osa
        testiosa = toimumisaeg.testiosa
        data = [[Paragraph(test.testiliik_nimi, LB),
                 Paragraph(testiosa.nimi, LBC),
                 Paragraph(ymbrikuliik.nimi, LBR)]]

        story.append(Table(data,
                           colWidths=(90*mm,105*mm,90*mm),
                           style=TableStyle([('LINEBELOW', (0,0),(-1,-1), 1,colors.black),
                                             ])
                           ))


def body(story, left, middle, right):
    # terve tabel
    data = [[left, middle, right]]
    t = Table(data, 
              colWidths=(90*mm,105*mm,90*mm),
              style=TableStyle([('VALIGN', (0,0),(0,0), 'TOP'),
                                ('VALIGN', (1,0),(1,0), 'BOTTOM'),
                                ('VALIGN', (-1,0),(-1,0), 'TOP'),
                                ('ALIGN', (-1,-1),(-1,-1), 'CENTER'),
                                ('TOPPADDING', (0,0), (-1,-1), 0),
                                ('LEFTPADDING', (0,0), (-1,-1), 3),
                                ('RIGHTPADDING', (0,0), (-1,-1), 3),
                                ]))

    story.append(t)

def sooritused(sooritused):
    "Terve tabeli parempoolne osa"

    TS = TableStyle([('FONTSIZE',(0,0),(-1,-1), 8),
                     ('GRID',(0,0),(-1,-1), 0.5,colors.black),                         
                     ])        

    data = [[Paragraph('Märge eksamitöö olemasolust ümbrikus', N),
             Paragraph('Eksamitöö kood', N)]]
    tos_tahised = [tos.tahised or '' for tos in sooritused]
    tos_tahised.sort()
    for tahised in tos_tahised:
        data.append(['', tahised])
    
    sooritused = [Paragraph('Ümbrikusse panna ainult järgmiste koodidega eksamitööd:', N),
                  Table(data, style=TS, colWidths=(45*mm, 44*mm))]
    return sooritused
