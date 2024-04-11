from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class KorrasooritajadController(BaseResourceController):
    """Eksamikeskuse testi sooritajate nimekirja kuvamine
    ja sinna sooritajate lisamine
    """
    _permission = 'nimekirjad'
    _MODEL = model.Testimiskord
    _INDEX_TEMPLATE = 'avalik/nimekirjad/nimekiri.mako'
    _DEFAULT_SORT = 'sooritaja.perenimi,sooritaja.eesnimi'
    _no_paginate = True
    
    def _query(self):
        q = (model.Session.query(model.Sooritaja,
                                 model.Kasutaja.isikukood)
             .filter(model.Sooritaja.testimiskord_id==self.c.testimiskord_id)
             .join(model.Sooritaja.kasutaja)
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        c.on_vvkoht = self._on_vvkoht()
        c.kand = c.on_vvkoht and c.kand == '1' and '1' or ''
        if c.kand:
            q = (q.with_entities(model.Sooritaja,
                                 model.Kasutaja.isikukood,
                                 model.Kasutaja.epost,
                                 model.Koht.nimi,
                                 model.Kandideerimiskoht.automaatne)
                 .outerjoin(model.Sooritaja.kool_koht)
                 .join(model.Sooritaja.kandideerimiskohad)
                 .filter(model.Kandideerimiskoht.koht_id==c.user.koht_id)
                 .filter(model.Kandideerimiskoht.automaatne==False)
                 )
        else:
            omaflt = model.Sooritaja.kool_koht_id==c.user.koht_id
            if c.testimiskord.reg_voorad:
                # näitame ka neid, kes on antud koolis regatud, aga võõrad
                omaflt = sa.or_(omaflt,
                                sa.and_(model.Sooritaja.esitaja_koht_id==c.user.koht_id,
                                        model.Sooritaja.regviis_kood==const.REGVIIS_KOOL_EIS))
            q = q.filter(omaflt)

            # kas mõni sooritaja sooritab testi mõnes teises koolis?
            q1 = q.filter(sa.exists().where(sa.and_(
                model.Sooritus.sooritaja_id==model.Sooritaja.id,
                model.Sooritus.testikoht_id==model.Testikoht.id,
                model.Testikoht.koht_id!=c.user.koht_id)))
            c.naita_soorituskoht = q1.count() > 0
            
        if self.c.csv:
            # väljastame CSV
            return self._index_csv(q)

        c.cnt = q.filter(model.Sooritaja.staatus>=const.S_STAATUS_REGATUD).count()
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        return q

    def _on_vvkoht(self):
        """Kas test on sisseastumistest ja kas kasutaja kool
        on testimiskorra seadetes märgitud vastuvõtvaks kooliks
        """
        c = self.c
        if c.test.testiliik_kood != const.TESTILIIK_SISSE:
            return False
        q = (model.Session.query(sa.func.count(model.Regkoht_kord.koht_id))
             .filter_by(testimiskord_id=c.testimiskord.id)
             .filter_by(koht_id=c.user.koht_id))
        return q.scalar() > 0

    def _prepare_header(self):
        c = self.c
        on_kursus = c.test.on_kursused
        on_tasu = c.testimiskord.osalemistasu or c.testimiskord.kordusosalemistasu
        header = [_("Isikukood"),
                  _("Nimi"),
                  c.kand and _("Õppeasutus"),
                  c.kand and _("E-post"),
                  _("Keel"),
                  on_kursus and _("Kursus"),
                  _("Olek"),
                  _("Registreerija"),
                  on_tasu and _("Tasutud"),
                  c.naita_soorituskoht and _("Soorituskoht"),
                  _("Eritingimus"),
                  _("Tugiisik"),
                  ]
        return [r for r in header if r]
    
    def _prepare_item(self, rcd, n=None):
        c = self.c
        on_kursus = c.test.on_kursused
        on_tasu = c.testimiskord.osalemistasu or c.testimiskord.kordusosalemistasu
        peidus = c.testimiskord.sooritajad_peidus   

        if c.kand:
            sooritaja, ik, epost, kool_nimi, automaatne = rcd
        else:
            sooritaja, ik = rcd
        s_peidus = peidus and '*' * 11 or None
        item = [s_peidus or ik,
                s_peidus or f'{sooritaja.eesnimi} {sooritaja.perenimi}',
                ]
        if c.kand:
            #if automaatne:
            #    kool_nimi += ' (%s)' % _("automaatselt lisatud")
            item.append(kool_nimi)
            item.append(epost)
        item.append(sooritaja.lang_nimi)
        if on_kursus:
            item.append(sooritaja.kursus_nimi)
        item.append(sooritaja.staatus_nimi)

        regviis = sooritaja.regviis_nimi
        if sooritaja.regviis_kood == const.REGVIIS_KOOL_EIS:
            regviis += f' ({sooritaja.esitaja_kasutaja.nimi})'
        item.append(regviis)

        if on_tasu:
            item.append(self.h.sbool(sooritaja.tasutud))
        if c.naita_soorituskoht:
            q = (model.Session.query(sa.distinct(model.Koht.nimi))
                 .filter(model.Sooritus.sooritaja_id==sooritaja.id)
                 .join(model.Sooritus.testikoht)
                 .join(model.Testikoht.koht)
                 .order_by(model.Koht.nimi))
            li = [nimi for nimi, in q.all()]
            item.append(li and ', '.join(li) or None)
                 
        item.append(self.h.sbool(sooritaja.on_erivajadused or None))
    
        q = (model.Session.query(model.Kasutaja.nimi, model.Testiosa.nimi)
             .join(model.Sooritus.tugiisik_kasutaja)
             .join(model.Sooritus.testiosa)
             .filter(model.Sooritus.sooritaja_id==sooritaja.id)
             .order_by(model.Testiosa.seq))
        li = []
        for k_nimi, osa_nimi in q.all():
            if c.mitu_osa:
                k_nimi += f' ({osa_nimi})'
            li.append(k_nimi)
        if c.csv:
            item.append(', '.join(li))
        else:
            item.append('<br/>'.join(li))

        return item    
    
    def _create(self):
        staatus = self.request.params.get('staatus')
        nimi = self.request.params.get('nimi')
        if staatus:
            self._update_staatus(item, staatus)

    def _update_staatus(self, item, staatus):
        """Muudame sooritajate olekut - lubame kohe alustada testi sooritamist.
        See on vajalik siis, kui on niisugune test, mida pole vaja klassiruumis teha.
        """
        if staatus and int(staatus) == const.S_STAATUS_ALUSTAMATA:
            # anname loa kohe alustada
            cnt = 0
            for rcd in self._get_sooritajad():
                rc = False
                if rcd.staatus == const.S_STAATUS_REGATUD:
                    rcd.staatus = const.S_STAATUS_ALUSTAMATA
                    rc = True
                for rcd2 in rcd.sooritused:
                    if rcd2.staatus == const.S_STAATUS_REGATUD:
                        rcd2.staatus = const.S_STAATUS_ALUSTAMATA
                        rc = True
                if rc:
                    cnt += 1

            model.Session.flush()
            if cnt:
                self.success(_("{n} sooritaja olek muudetud").format(n=cnt))
            else:
                self.success(_("Loa ootel sooritajaid ei olnud"))

    def __before__(self):
        c = self.c
        c.testimiskord_id = int(self.request.matchdict.get('testimiskord_id'))
        c.testimiskord = model.Testimiskord.get(c.testimiskord_id)
        c.test = c.testimiskord.test        
        c.mitu_osa = len(c.test.testiosad) > 1
        
    def _perm_params(self):
        # testi vaatamise õigus, et igaüks saaks oma teste suunata
        # õppealajuhatajatel peab olema neile suunata lubatud testidele see õigus
        if not self.c.user.koht_id:
            return False
        return {'obj': self.c.testimiskord}

