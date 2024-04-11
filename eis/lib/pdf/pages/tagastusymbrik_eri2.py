# -*- coding: utf-8 -*- 
"ERI2. Tagastusümbrik alatestile, millel hindajad märgitakse hindamiskogumite kaupa"

from .tagastusymbrik_eri1 import generate_eri

def generate(story, toimumisaeg, testikoht, testipakett, tpr, ymbrikuliik):
    # hindajate tabelis peaks olema ümbrikuliigile vastava alatesti 
    # iga hindamiskogumi kohta üks rida, aga kuna ümbrikuliigid ja alatestid
    # ei ole süsteemis seotud 
    # ja yleyldse ei pruugi hindamiskogumid olla yhe alatesti piires,
    # siis ei saa täpset arvu kasutada
    hkogumid = [hk for hk in toimumisaeg.testiosa.hindamiskogumid if hk.staatus]
    hindajad_len = min(5, len(hkogumid))
    generate_eri(story, toimumisaeg, testikoht, testipakett, tpr, ymbrikuliik, hindajad_len)

