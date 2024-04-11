"Läbiviija meeldetuletus"

from .labiviijateade import *
from eis.model.usersession import _

def generate(story, kasutaja, labiviijad, testiliik):

    story.append(Paragraph(_('MEELDETULETUS'), NBC))
    story.append(Spacer(1,10*mm))

    story.append(Paragraph(_('Lugupeetud {s}').format(s=kasutaja.nimi), N))
    story.append(Spacer(1,5*mm))

    if len(labiviijad) == 1:
        buf = _('Soovime Teile meelde tuletada, et olete registreeritud läbiviijaks järgmisele eksamile:')
    else:
        buf = _('Soovime Teile meelde tuletada, et olete registreeritud läbiviijaks järgmistele eksamitele:')
    story.append(Paragraph(buf, N))

    append_labiviijad(story, labiviijad)

    story.append(Spacer(1, 5*mm))
    story.append(Paragraph('Maie Jürgens', N))
    story.append(Paragraph(_('Tel 7350562, 56482403'), N))

    story.append(PageBreak())
