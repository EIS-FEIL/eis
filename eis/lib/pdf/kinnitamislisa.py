# -*- coding: utf-8 -*- 
# $Id: kinnitamislisa.py 9 2015-06-30 06:34:46Z ahti $

import sqlalchemy as sa
import eis.model as model
from eis.model import const

from . import pages_loader
from .pdfdoc import *
from .pages.pdfutils import *
from .pages import kinnitamislisa1, kinnitamislisa2

class KinnitamislisaDoc(PdfDoc):
    pagenumbers = True
    
    def __init__(self, testimiskord, lisa):
        self.testimiskord = testimiskord
        self.lisa = lisa
        
    def _doctemplate(self, output):
        "PDFi dokumendi loomine"
        return SimpleDocTemplate(output,
                                 pagesize=landscape(A4),
                                 topMargin=10*mm, bottomMargin=10*mm, 
                                 rightMargin=10*mm, leftMargin=10*mm)


    def gen_story(self):

        select_fields, headers, join_tables, staatus_jrk = self._compose_query()

        if self.lisa == 1:
            select_fields += [model.Sooritaja.pallid,
                              model.Sooritaja.tulemus_protsent,
                              model.Tunnistus.tunnistusenr,
                              ]
        elif self.lisa == 2:
            select_fields += [model.Sooritaja.pallid,
                              model.Sooritaja.tulemus_protsent,
                              ]
            
        q = model.SessionR.query(*select_fields).\
            filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).\
            join(model.Sooritaja.kasutaja).\
            filter(model.Sooritaja.testimiskord_id==self.testimiskord.id)

        for join in join_tables:
            q = q.join(join)
        q = q.join(model.Testikoht.koht).\
            outerjoin(model.Koht.aadress)

        if self.lisa == 1:
            q = q.filter(model.Sooritaja.tulemus_piisav==True).\
                join(model.Sooritaja.testitunnistused).\
                join(model.Testitunnistus.tunnistus).\
                filter(model.Tunnistus.staatus>const.N_STAATUS_KEHTETU)
        elif self.lisa == 2:
            q = q.filter(model.Sooritaja.tulemus_piisav==False)

        cnt = q.filter(model.Sooritaja.tulemus_protsent==None).count()
        if cnt:
            self.error = 'Lõplikku tulemust pole teada, kuna %d sooritaja tulemus on veel hindamata' % cnt
            return

        q = q.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)

        story = []
        if self.lisa == 1:
            if q.count() == 0:
                # kui tulemust ei tule, aga eksami läbinuid on, siis on tunnistused puudu
                piisavaid = model.SessionR.query(model.Sooritaja).\
                    filter(model.Sooritaja.testimiskord_id==self.testimiskord.id).\
                    filter(model.Sooritaja.tulemus_piisav==True).\
                    count()
                if piisavaid > 0:
                    self.error = 'Tunnistusi pole veel väljastatud'
                    return

            template = kinnitamislisa1
        else:
            template = kinnitamislisa2

        template.generate(story, self.testimiskord, q.all(), staatus_jrk, headers)
        return story


    def _compose_query(self):
        test = self.testimiskord.test

        join_tables = []
        select_fields = [model.Sooritaja.id,
                         model.Sooritaja.eesnimi,
                         model.Sooritaja.perenimi,
                         model.Kasutaja.isikukood,
                         model.Kasutaja.synnikpv,
                         model.Aadress.kood2,
                         model.Aadress.kood1,
                         ]
        headers = []
        n_sooritus = 0
        n_alatest = 0
        staatus_jrk = {} # staatuse indeksile vastab testiosa/alatesti väljade arv

        # tulemuses on: 
        # iga alatesti kohta 2 veergu - olek, protsent
        # iga alatestideta testiosa kohta 3 veergu - olek, protokoll, protsent
        # iga alatestidega testiosa kohta 2 + (alatestide arv * 2) veergu - olek, protokoll, alatestide veerud

        for testiosa in test.testiosad:
            n_sooritus += 1
            name = 'sooritus_%d' % n_sooritus
            Sooritus = sa.orm.aliased(model.Sooritus, name=name)
            join_tables.append((Sooritus,
                                sa.and_(Sooritus.testiosa_id==testiosa.id,
                                        Sooritus.sooritaja_id==model.Sooritaja.id)))

            if n_sooritus == 1:
                join_tables.append((model.Testikoht, model.Testikoht.id==Sooritus.testikoht_id))

            # testiosa soorituse staatuse indeks
            testiosa_staatus_jrk = len(select_fields)
            select_fields.append(Sooritus.staatus)

            Protokoll = sa.orm.aliased(model.Testiprotokoll)
            join_tables.append((Protokoll, Protokoll.id==Sooritus.testiprotokoll_id))
            
            select_fields.append(Protokoll.tahised)
            headers.append('Eksamiprotokolli number')
            
            if testiosa.on_alatestid:
                for alatest in testiosa.alatestid:
                    n_alatest += 1
                    name = 'alatest_%d' % n_alatest
                    Alatestisooritus = sa.orm.aliased(model.Alatestisooritus, name=name)
                    join_tables.append((Alatestisooritus,
                                        sa.and_(Alatestisooritus.alatest_id==alatest.id,
                                                Alatestisooritus.sooritus_id==Sooritus.id)))

                    # alatesti staatuse välja jrk nr-ile vastab alatesti väljade arv 1 (protsent)
                    staatus_jrk[len(select_fields)] = 1
                    select_fields.append(Alatestisooritus.staatus)
                    #select_fields.append(Alatestisooritus.pallid)
                    select_fields.append(Alatestisooritus.tulemus_protsent)

                    headers.append(alatest.nimi)
            else:
                #select_fields.append(Sooritus.pallid)
                select_fields.append(Sooritus.tulemus_protsent)
                headers.append(testiosa.nimi)

            # staatuse välja jrk nr-ile vastab selle staatusega testiosa väljade arv
            staatus_jrk[testiosa_staatus_jrk] = len(select_fields) - testiosa_staatus_jrk
            
        if n_sooritus <= 1 and n_alatest <= 1:
            # test koosneb yhestainsast testiosast/alatestist
            # jätame alles ainult soorituse koodi
            select_fields = select_fields[:-1]
            headers = headers[:-1]

        return select_fields, headers, join_tables, staatus_jrk
