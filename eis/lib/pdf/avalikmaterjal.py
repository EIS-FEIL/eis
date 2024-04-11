# -*- coding: utf-8 -*- 
"Väljastusümbrikku lisatavate materjalide PDF dokument"

from .materjal import *
from .pages import toimumisprotokoll_taidetud_t as toimumisprotokoll_t
from .pages import toimumisprotokoll_pohikool as toimumisprotokoll_pohikool
from .pages import toimumisprotokoll_kutse as toimumisprotokoll_kutse

class AvalikMaterjalDoc(MaterjalDoc):
    def __init__(self, toimumisprotokoll):
        self.toimumisprotokoll = toimumisprotokoll
        self.testikoht = toimumisprotokoll.testikoht
        self._register_barcode_font()
        
    def gen_story(self):
        story = []
        testimiskord = self.toimumisprotokoll.testimiskord
        if not testimiskord:
            # kutseeksam
            tmpl = toimumisprotokoll_kutse
        elif testimiskord.prot_tulemusega:
            tmpl = toimumisprotokoll_pohikool
        elif testimiskord.prot_vorm == const.PROT_VORM_ALATULEMUS:
            # kutseeksam
            tmpl = toimumisprotokoll_kutse
        else:
            tmpl = toimumisprotokoll_t
        tmpl.generate(story, self.testikoht, self.toimumisprotokoll)            
        return story
