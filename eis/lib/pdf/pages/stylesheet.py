# -*- coding: utf-8 -*- 
# $Id: stylesheet.py 533 2016-03-30 11:31:19Z ahti $
"Stiili kirjeldamine"

from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors

N = ParagraphStyle(name='Normal',
                   fontName='Times-Roman',
                   fontSize=10,
                   leading=12,
                   #backColor='#FFFF00',
                   spaceBefore=3,
                   spaceAfter=3)

NC = ParagraphStyle(name='NormalCentred',
                     parent=N,
                     alignment=TA_CENTER)

NL = ParagraphStyle(name='NormalLeft',
                     parent=N,
                     alignment=TA_LEFT)

NB = ParagraphStyle(name='NormalBold',
                    parent=N,
                    fontName='Times-Bold')

NI = ParagraphStyle(name='NormalItalic',
                    parent=N,
                    fontName='Times-Italic')

NBC = ParagraphStyle(name='NormalBoldCentred',
                    parent=NB,
                    alignment=TA_CENTER)

NBR = ParagraphStyle(name='NormalBoldRight',
                     parent=N,
                     fontName='Times-Bold',
                     alignment=TA_RIGHT)
NR = ParagraphStyle(name='NormalRight',
                     parent=N,
                     alignment=TA_RIGHT)

# normaalse ja suure fondi vaheline font
M = ParagraphStyle(name='Medium',
                   fontName='Times-Roman',
                   fontSize=12,
                   leading=14,
                   #backColor='#FFFF00',
                   spaceBefore=3,
                   spaceAfter=3)

MI = ParagraphStyle(name='MediumItalic',
                    parent=M,
                    fontName='Times-Italic')

MC = ParagraphStyle(name='MediumCentred',
                     parent=M,
                     alignment=TA_CENTER)

MCI = ParagraphStyle(name='MediumCentredItalic',
                     parent=MC,
                     fontName='Times-Italic')

MB = ParagraphStyle(name='MediumBold',
                    parent=M,
                    fontName='Times-Bold')

MBC = ParagraphStyle(name='MediumBoldCentred',
                    parent=MB,
                    alignment=TA_CENTER)

MBR = ParagraphStyle(name='MediumBoldRight',
                     parent=M,
                     fontName='Times-Bold',
                     alignment=TA_RIGHT)
MR = ParagraphStyle(name='MediumRight',
                     parent=M,
                     alignment=TA_RIGHT)

N11 = ParagraphStyle(name='Normal11',
                     parent=N,
                     fontSize=11)
NR11 = ParagraphStyle(name='NormalRight11',
                      parent=N11,
                      alignment=TA_RIGHT)    
NB11 = ParagraphStyle(name='NormalBold11',
                      parent=NB,
                      fontSize=11)

# punktiirjoont sisaldav tekst, milles suured reavahed
DOT = ParagraphStyle(name='Dot',
                     parent=N,
                     #fontSize=9,
                     # leading asemel kasutame spaceBefore,
                     # et sulgudes selgitus ilmuks punktiiri alla, mitte kaugele
                     spaceBefore=10,
                     spaceAfter=0)
#backColor='#FFFF00')

DOTC = ParagraphStyle(name='DotCentred',
                     parent=DOT,
                     alignment=TA_CENTER)


S = ParagraphStyle(name='Small',
                   parent=N,
                   fontSize=8,
                   leading=9,
                   spaceBefore=0,
                   spaceAfter=0)

SR = ParagraphStyle(name='SmallRight',
                    parent=S,
                    alignment=TA_RIGHT)

SB = ParagraphStyle(name='SmallBold',
                     parent=S,
                     fontName='Times-Bold')
SI = ParagraphStyle(name='SmallBoldItalic',
                     parent=S,
                     fontName='Times-Italic')

SBC = ParagraphStyle(name='SmallBoldCentred',
                     parent=S,
                     fontName='Times-Bold',
                     alignment=TA_CENTER)

SC = ParagraphStyle(name='SmallCentred',
                     parent=S,
                     alignment=TA_CENTER)

L = ParagraphStyle(name='Large',
                   parent=N,
                   leading=17,
                   fontSize=14)

LB = ParagraphStyle(name='LargeBold',
                    parent=L,
                    fontName='Times-Bold')

LC = ParagraphStyle(name='LargeCentred',
                     parent=L,
                     alignment=TA_CENTER)

LR = ParagraphStyle(name='LargeRight',
                    parent=L,
                    alignment=TA_RIGHT)

LBI = ParagraphStyle(name='LargeBoldItalic',
                     parent=L,
                     fontName='Times-BoldItalic')

LBR = ParagraphStyle(name='LargeBoldRight',
                     parent=LR,
                     fontName='Times-Bold')

LBC = ParagraphStyle(name='LargeBoldCentred',
                     parent=L,
                     alignment=TA_CENTER,
                     fontName='Times-Bold')


H3 = ParagraphStyle(name='Heading3',
                    parent=N,
                    fontName = 'Times-BoldItalic',
                    fontSize=12,
                    leading=14,
                    spaceBefore=12,
                    spaceAfter=6)


H1 = ParagraphStyle(name='Heading1',
                    parent=N,
                    fontName = 'Times-Bold',
                    alignment=TA_CENTER,
                    fontSize=18,
                    leading=22,
                    spaceAfter=6)


# styles = getStyleSheet()
# N = styles['Normal']
# S = styles['Small']
# H1 = styles['Heading1']
# H2 = styles['Heading2']
# H3 = styles['Heading3']                        

# def getStyleSheet():
#     """Returns a stylesheet object"""
#     stylesheet = StyleSheet1()

#     stylesheet.add(ParagraphStyle(name='Normal',
#                                   fontName='Times-Roman',
#                                   fontSize=10,
#                                   leading=12,
#                                   spaceBefore=6)
#                    )

#     stylesheet.add(ParagraphStyle(name='Small',
#                                   parent=stylesheet['Normal'],
#                                   fontSize=8))
    
#     # stylesheet.add(ParagraphStyle(name='Comment',
#     #                               fontName='Times-Italic')
#     #                )

#     # stylesheet.add(ParagraphStyle(name='Indent0',
#     #                               leftIndent=18,)
#     #                )

#     # stylesheet.add(ParagraphStyle(name='Indent1',
#     #                               leftIndent=36,
#     #                               firstLineIndent=0,
#     #                               spaceBefore=1,
#     #                               spaceAfter=7)
#     #                )
    
#     # stylesheet.add(ParagraphStyle(name='Indent2',
#     #                               leftIndent=50,
#     #                               firstLineIndent=0,
#     #                               spaceAfter=100)
#     #                )

#     # stylesheet.add(ParagraphStyle(name='BodyText',
#     #                               parent=stylesheet['Normal'],
#     #                               spaceBefore=6)
#     #                )
#     # stylesheet.add(ParagraphStyle(name='Italic',
#     #                               parent=stylesheet['BodyText'],
#     #                               fontName = 'Times-Italic')
#     #                )

#     stylesheet.add(ParagraphStyle(name='Heading1',
#                                   parent=stylesheet['Normal'],
#                                   fontName = 'Times-Bold',
#                                   alignment=TA_CENTER,
#                                   fontSize=18,
#                                   leading=22,
#                                   spaceAfter=6),
#                    alias='h1')

#     stylesheet.add(ParagraphStyle(name='Heading2',
#                                   parent=stylesheet['Normal'],
#                                   fontName = 'Times-Bold',
#                                   fontSize=14,
#                                   leading=17,
#                                   spaceBefore=12,
#                                   spaceAfter=6),
#                    alias='h2')

#     stylesheet.add(ParagraphStyle(name='Heading3',
#                                   parent=stylesheet['Normal'],
#                                   fontName = 'Times-BoldItalic',
#                                   fontSize=12,
#                                   leading=14,
#                                   spaceBefore=12,
#                                   spaceAfter=6),
#                    alias='h3')

#     stylesheet.add(ParagraphStyle(name='Heading4',
#                                   parent=stylesheet['Normal'],
#                                   fontName = 'Times-BoldItalic',
#                                   spaceBefore=10,
#                                   spaceAfter=4),
#                    alias='h4')


#     return stylesheet

