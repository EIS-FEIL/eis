# -*- coding: utf-8 -*-
"""Metaandmete väljastamine päringute analüüsiks ES-1459

https://eis.ekk.edu.ee/eis/metadata/ylesanded.csv
https://eis.ekk.edu.ee/eis/metadata/ylesandeteemad.csv
https://eis.ekk.edu.ee/eis/metadata/testid.csv
https://eis.ekk.edu.ee/eis/metadata/testiylesanded.csv
https://eis.ekk.edu.ee/eis/metadata/klassifikaator/AINE.csv
https://eis.ekk.edu.ee/eis/metadata/klassifikaator/ASTE.csv
https://eis.ekk.edu.ee/eis/metadata/klassifikaator/AINEVALD.csv
https://eis.ekk.edu.ee/eis/metadata/klassifikaator/TEEMA.csv
https://eis.ekk.edu.ee/eis/metadata/klassifikaator/ALATEEMA.csv
"""
from eis.lib.base import *
_ = i18n._

import logging
log = logging.getLogger(__name__)

class MetadataHandler(BaseController):
    """
    Metaandmed
    """

    _authorize = False
    _log_params_get = True
    
    def klassifikaator(self):
        kood = self.request.matchdict.get('kood')
        header = ['kood','nimetus','kehtib']
        items = []
        now = datetime.now()
        if kood in ('AINE', 'ASTE', 'TESTIKLASS', 'AINEVALD'):
            q = (model.Session.query(model.Klrida)
                 .filter(model.Klrida.klassifikaator_kood==kood)
                 .order_by(model.Klrida.jrk, model.Klrida.id))
            items = []
            for r in q.all():
                kehtib = r.kehtib and (not r.alates or r.alates < now) and (not r.kuni or r.kuni > now)
                row = [r.kood, r.nimi, kehtib]
                items.append(row)
        elif kood in ('TEEMA','ALATEEMA'):
            aste_nimed = ['Alusharidus', 'I kooliaste', 'II kooliaste', 'III kooliaste', 'Gümnaasium', 'Ülikool']
            aste_bitid = (32, 1, 2, 4, 8, 16)

            if kood == 'TEEMA':
                header = ['aine_kood', 'aine', 'teema_kood', 'teema', 'kehtib']  + aste_nimed
            elif kood == 'ALATEEMA':
                header = ['aine_kood', 'aine', 'teema_kood', 'teema', 'alateema_kood', 'alateema', 'kehtib']  + aste_nimed

            if self.is_devel and 0:
                header += ['loodud', 'looja', 'muudetud', 'muutja']
            Aine = sa.orm.aliased(model.Klrida)
            if kood == 'TEEMA':
                q = (model.Session.query(Aine, model.Klrida)
                     .filter(model.Klrida.klassifikaator_kood=='TEEMA')
                     .join((Aine, Aine.id==model.Klrida.ylem_id))
                     .order_by(Aine.kood, model.Klrida.jrk, model.Klrida.id))
            elif kood == 'ALATEEMA':
                Alateema = sa.orm.aliased(model.Klrida)
                q = (model.Session.query(Aine, model.Klrida, Alateema)
                     .filter(model.Klrida.klassifikaator_kood=='TEEMA')
                     .join((Aine, Aine.id==model.Klrida.ylem_id))
                     .join((Alateema, sa.and_(Alateema.klassifikaator_kood=='ALATEEMA',
                                              Alateema.ylem_id==model.Klrida.id)))
                     .order_by(Aine.kood, model.Klrida.jrk, model.Klrida.id, Alateema.jrk, Alateema.id))
                
            items = []
            for rcd in q.all():
                if kood == 'TEEMA':
                    aine, teema = rcd
                    r = teema
                elif kood == 'ALATEEMA':
                    aine, teema, alateema = rcd
                    r = alateema
                    
                kehtib = r.kehtib and (not r.alates or r.alates < now) and (not r.kuni or r.kuni > now)
                row = [aine.kood, aine.nimi, teema.kood, teema.nimi]

                if kood == 'ALATEEMA':
                    row.append(alateema.kood)
                    row.append(alateema.nimi)
                row.append(kehtib)
                for b in aste_bitid:
                    is_b = r.bitimask and r.bitimask & b
                    row.append(is_b and '1' or '')

                if self.is_devel and 0:
                    creator_n = model.Kasutaja.get_name_by_creator(r.creator)
                    modifier_n = model.Kasutaja.get_name_by_creator(r.modifier)
                    row += [self.h.str_from_date(r.created),
                            creator_n,
                            self.h.str_from_date(r.modified),
                            modifier_n]
                items.append(row)

        data = _csv_data(header, items)
        data = utils.encode_ansi(data)
        fn = ('%s.csv' % kood).lower()
        return utils.download(data, fn, const.CONTENT_TYPE_CSV)

    def ylesanded(self):
        qa = (model.Session.query(model.Klrida)
              .filter(model.Klrida.klassifikaator_kood=='AINE'))
        ained = {aine.kood: aine for aine in qa.all()}

        opt = self.c.opt
        def kooliastmed(mask):
            "Leiame astmete koodid"
            astmed = []
            for r in opt.astmed():
                aste_kood = r[0]
                bit = opt.aste_bit(aste_kood)
                if bit & mask:
                    #aste_nimi = map_astmed.get(aste_kood)
                    astmed.append(aste_kood)
            return astmed

        # leiame ylesanded
        q = (model.Session.query(model.Ylesanne.id,
                                 model.Ylesanne.created,
                                 model.Ylesanne.nimi,
                                 model.Ylesanne.aste_mask,
                                 model.Ylesandeaine.aine_kood)
             #.filter(model.Ylesanne.salastatud==const.SALASTATUD_POLE)
             .filter(model.Ylesanne.staatus!=const.Y_STAATUS_ARHIIV)
             .join(model.Ylesanne.ylesandeained)
             .filter(model.Ylesandeaine.seq==0)
             .order_by(model.Ylesanne.id))

        # id - identifikaator, mis on veebi URLis (a'la 1869 ülesande https://eis.ekk.edu.ee/eis/lahendamine/1869 puhul)
        # created - loomise kuupäev
        # title - pealkiri
        # class - millise klassi jaoks (kui on)
        # level - millise kooliastme jaoks (kui on)
        # educationalContext - haridusaste (kui on)
        # domain - ainevaldkond (kui on)
        # subject - aine nimetus
        header = ['id',
                  'created',
                  'title',
                  'class',
                  'level',
                  'educationalContext',
                  'domain',
                  'subject']
        items = []
        for y_id, created, nimi, aste_mask, aine_kood in q.all():
            aine = ained.get(aine_kood)
            if aine:
                ainevald_kood = aine.ryhm_kood
            else:
                ainevald_kood = ''

            astmed = aste_mask and kooliastmed(aste_mask) or ['']
            for aste in astmed:
                row = [y_id,
                       created.strftime('%Y-%m-%d %H:%M:%S'),
                       nimi,
                       '',
                       aste,
                       '',
                       ainevald_kood,
                       aine_kood]
                items.append(row)
        data = _csv_data(header, items)
        data = utils.encode_ansi(data)
        return utils.download(data, 'ylesanded.csv', const.CONTENT_TYPE_CSV)

    def ylesandeteemad(self):
        # leiame ylesanded
        Aine = sa.orm.aliased(model.Klrida)
        Teema = sa.orm.aliased(model.Klrida)
        Alateema = sa.orm.aliased(model.Klrida)
        q = (model.Session.query(model.Ylesanne.id,
                                 model.Ylesandeaine.aine_kood,
                                 model.Ylesandeteema.teema_kood,
                                 model.Ylesandeteema.alateema_kood,
                                 Teema.nimi,
                                 Alateema.nimi)
             .filter(model.Ylesanne.staatus!=const.Y_STAATUS_ARHIIV)
             .join(model.Ylesanne.ylesandeained)
             .filter(model.Ylesandeaine.seq==0)
             .join(model.Ylesandeaine.ylesandeteemad)
             .join((Aine, sa.and_(Aine.kood==model.Ylesandeaine.aine_kood,
                                  Aine.klassifikaator_kood=='AINE')))
             .join((Teema, sa.and_(Teema.kood==model.Ylesandeteema.teema_kood,
                                   Teema.ylem_id==Aine.id,
                                   Teema.klassifikaator_kood=='TEEMA')))
             .outerjoin((Alateema, sa.and_(Alateema.kood==model.Ylesandeteema.alateema_kood,
                                           Alateema.ylem_id==Teema.id,
                                           Alateema.klassifikaator_kood=='ALATEEMA')))
             .order_by(model.Ylesanne.id))

        header = ['id',
                  'aine_kood',
                  'teema_kood',
                  'alateema_kood',
                  'teema',
                  'alateema',
                  ]
        items = []
        for y_id, aine_kood, teema_kood, alateema_kood, teema, alateema in q.all():
            row = [y_id,
                   aine_kood,
                   teema_kood,
                   alateema_kood,
                   teema,
                   alateema]
            items.append(row)
        data = _csv_data(header, items)
        data = utils.encode_ansi(data)
        return utils.download(data, 'ylesandeteemad.csv', const.CONTENT_TYPE_CSV)

    def testid(self):
        qa = (model.Session.query(model.Klrida)
              .filter(model.Klrida.klassifikaator_kood=='AINE'))
        ained = {aine.kood: aine for aine in qa.all()}

        opt = self.c.opt
        def kooliastmed(mask):
            "Leiame astmete koodid"
            astmed = []
            for r in opt.astmed():
                aste_kood = r[0]
                bit = opt.aste_bit(aste_kood)
                if bit & mask:
                    astmed.append(aste_kood)
            return astmed

        # leiame testid
        q = (model.Session.query(model.Test.id,
                                 model.Test.created,
                                 model.Test.nimi,
                                 model.Test.testiklass_kood,
                                 model.Test.aste_mask,
                                 model.Test.aine_kood,
                                 model.Test.autor)
             #.filter(model.Test.salastatud==const.SALASTATUD_POLE)
             .filter(model.Test.staatus!=const.T_STAATUS_ARHIIV)
             .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_EKK)))
             .order_by(model.Test.id))

        header = ['id',
                  'created',
                  'title',
                  'class',
                  'level',
                  'educationalContext',
                  'domain',
                  'subject',
                  'author']
        items = []
        for y_id, created, nimi, testiklass_kood, aste_mask, aine_kood, autor in q.all():
            aine = ained.get(aine_kood)
            if aine:
                ainevald_kood = aine.ryhm_kood
            else:
                aine_nimi = ''

            # autor, väljaandja, teema, alateema. Kui on, siis üldpädevused ja läbivad teemad. 
            astmed = aste_mask and kooliastmed(aste_mask) or ['']
            for aste in astmed:
                row = [y_id,
                       created.strftime('%Y-%m-%d %H:%M:%S'),
                       nimi,
                       testiklass_kood,
                       aste,
                       '',
                       ainevald_kood,
                       aine_kood,
                       autor]
                items.append(row)
        data = _csv_data(header, items)
        data = utils.encode_ansi(data)
        return utils.download(data, 'testid.csv', const.CONTENT_TYPE_CSV)

    def testiylesanded(self):
        q = (model.Session.query(model.Test.id,
                                 model.Valitudylesanne.ylesanne_id)
             .distinct()
             .join(model.Valitudylesanne.test)
             .filter(model.Test.staatus!=const.T_STAATUS_ARHIIV)
             .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_EKK)))
             .order_by(model.Test.id,
                       model.Valitudylesanne.ylesanne_id)
             )
        header = ['test_id',
                  'ylesanne_id',
                  ]
        items = []
        for t_id, y_id in q.all():
            row = [t_id, y_id]
            items.append(row)
        data = _csv_data(header, items)
        data = utils.encode_ansi(data)
        return utils.download(data, 'testiylesanded.csv', const.CONTENT_TYPE_CSV)

def _csv_data(header, items):
    LINESEP = '\r\n'
    if header:
        data = ';'.join(header) + LINESEP
    else:
        data = ''
    for item in items:
        row = []
        for s in item:
            if s is None:
                s = ''
            elif isinstance(s, list):
                s = ', '.join(s)
            else:
                #s = unicode(s).replace('\n',' ').replace('\r', ' ')
                s = str(s).replace('\r', ' ')
            if ';' in s or '\n' in s:
                s = '"%s"' % s.replace('"','""')
            row.append(s)
        data += ';'.join(row) + LINESEP
    return data
        
