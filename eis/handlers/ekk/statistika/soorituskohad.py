import pickle
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.soorituskohad import SoorituskohadDoc
log = logging.getLogger(__name__)

class SoorituskohadController(BaseResourceController):
    """Soorituskohtade statistika
    """
    _permission = 'aruanded-soorituskohad'
    _INDEX_TEMPLATE = 'ekk/statistika/soorituskohad.otsing.mako'
    _LIST_TEMPLATE = 'ekk/statistika/soorituskohad.list.mako'
    _DEFAULT_SORT = 'koht.nimi'
    _no_paginate = True
    _ignore_default_params = ['pdf', 'csv']
    
    def _query(self):
        return None

    def _search_default(self, q):
        self.c.sooritajad = True
        return None

    def _search(self, q1):
        """Põhiline otsing"""

        li_order = [model.Test.nimi,
                    model.Toimumisaeg.tahised,
                    model.Toimumisaeg.alates,
                    model.Piirkond.nimi,
                    model.Koht.nimi]
        li_group = li_order + [model.Piirkond.id,
                               model.Testikoht.id]
        if self.c.ruumid:
            li_group.append(sa.func.date(model.Toimumispaev.aeg))
            li_order.append(sa.func.date(model.Toimumispaev.aeg))            
            li_select = li_group + [sa.func.count(model.Testiruum.id)]
            q = model.SessionR.query(*li_select)
        else:
            q = model.SessionR.query(*li_group)
            
        q = q.join(model.Testikoht.koht).\
            outerjoin(model.Koht.piirkond).\
            join(model.Testikoht.toimumisaeg).\
            join(model.Toimumisaeg.testimiskord).\
            join(model.Testimiskord.test)

        if not self.c.koht_id and not self.c.testsessioon_id:
            self.error(_("Palun anda ette vähemalt testsessioon või soorituskoht"))
            return

        # soorituskoht
        if self.c.piirkond_id:
            piirkond = model.Piirkond.get(self.c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()
            q = q.filter(model.Koht.piirkond_id.in_(piirkonnad_id))
        if self.c.maakond_kood:
            tase, kood = self.c.maakond_kood.split('.')
            q = q.filter(model.Koht.aadress.has(\
                model.Aadress.kood1==kood))
        if self.c.koht_id:
            q = q.filter(model.Koht.id==self.c.koht_id)
        if self.c.regviis:
            if isinstance(self.c.regviis, list):
                q = q.filter(model.Testikoht.sooritused.any(\
                        model.Sooritus.sooritaja.has(\
                            model.Sooritaja.regviis_kood.in_(self.c.regviis))))
            else:
                q = q.filter(model.Testikoht.sooritused.any(\
                        model.Sooritus.sooritaja.has(\
                            model.Sooritaja.regviis_kood==self.c.regviis)))

        # test
        if self.c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==self.c.testsessioon_id)
        if self.c.testiliik:
            q = q.filter(model.Test.testiliik_kood==self.c.testiliik)
        if self.c.test_id:
            q = q.filter(model.Test.id==self.c.test_id)
        if self.c.testimiskord_id:
            q = q.filter(model.Testimiskord.id==self.c.testimiskord_id)
        if self.c.test_nimi:
            q = q.filter(model.Test.nimi.ilike(self.c.test_nimi))

        if self.c.ruumid:
            q = q.join(model.Testikoht.testiruumid).\
                join(model.Testiruum.toimumispaev)
            q = q.group_by(*li_group)
                         
        q = q.order_by(*li_order)
        self._prepare_data(q)

        if self.c.pdf:
            return self._index_pdf(self.c.items, self.c.keeled, self.c.sooritajad, self.c.vaatlejad, self.c.ruumid)

        if self.c.csv:
            return self._index_csv(q)
        return None

    def _prepare_data(self, q):
        keeled = set()
        items = []

        # items on jada toimumisaegade andmetest ta_data
        
        # ta_data on jada, milles:
        # - esimene liige on toimumisaja tähis
        # - teine kuni eelviimane liige on piirkonna andmed prk_data
        # - viimane liige on toimumisaja koond [None, {KEELED}, kokku, vaatlejaid]

        # prk_data on jada, milles:
        # - esimene liige on piirkonna nimi
        # - teine kuni eelviimane liige on soorituskoha andmed 
        #   [koha nimi, {KEELED}, kokku, vaatlejaid, [SUUNATUD]]
        # - viimane liige on piirkonna koond [None, {KEELED}, kokku, vaatlejaid]

        # suunatud koolide jada on jada koolidest, mille õpilased on 
        # sellesse kohta suunatud sooritama
        # jada element on kujul [kooli nimi, {KEELED}, kokku]

        prev_ta_tahised = None
        prev_prk_id = -1 # ei tohi olla None, et ei läheks sassi puuduva piirkonnaga

        ta_data = list()
        ta_keeled, ta_sooritajad, ta_vaatlejad = dict(), 0, 0        

        prk_data = list()
        prk_keeled, prk_sooritajad, prk_vaatlejad = dict(), 0, 0
            
        for rcd in q.all():
            t_nimi, ta_tahised, ta_alates, prk_nimi, k_nimi, prk_id, testikoht_id = rcd[:7]

            if self.c.ruumid:
                paev = rcd[7]
                paevaruumid = rcd[8]
            else:
                paev = None
                paevaruumid = None
                              
            #log.debug(str(rcd))

            if prev_ta_tahised != ta_tahised:
                if len(prk_data):
                    prk_data.append([None, prk_keeled, prk_sooritajad, prk_vaatlejad])
                    ta_data.append(prk_data)
                prk_keeled, prk_sooritajad, prk_vaatlejad = dict(), 0, 0
                prk_data = list()

                if len(ta_data):
                    ta_data.append([None, ta_keeled, ta_sooritajad, ta_vaatlejad])
                    items.append(ta_data)
                ta_keeled, ta_sooritajad, ta_vaatlejad = dict(), 0, 0
                ta_data = list()
                prev_prk_id = -1

                # toimumisaja listi esimene liige on toimumisaja nimi
                ta_data = ['%s %s' % (t_nimi, ta_tahised)]

            if prev_prk_id != prk_id:
                if len(prk_data):
                    prk_data.append([None, prk_keeled, prk_sooritajad, prk_vaatlejad])
                    ta_data.append(prk_data)
                prk_keeled, prk_sooritajad, prk_vaatlejad = dict(), 0, 0
                prk_data = list()

                # piirkonna listi esimene liige on piirkonna nimi
                prk_data = [prk_nimi or _("Piirkonnata")]

            if self.c.sooritajad:
                # sooritajate arv keelte lõikes
                q1 = model.SessionR.query(sa.func.count(model.Sooritaja.id),
                                         model.Sooritaja.lang)
                q1 = q1.join(model.Sooritaja.sooritused).\
                     filter(model.Sooritus.testikoht_id==testikoht_id).\
                     filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
                if self.c.regviis:
                    if isinstance(self.c.regviis, list):
                        q1 = q1.filter(model.Sooritaja.regviis_kood.in_(self.c.regviis))
                    else:
                        q1 = q1.filter(model.Sooritaja.regviis_kood==self.c.regviis)
                if self.c.ruumid:
                    q1 = q1.join(model.Sooritus.testiruum).\
                         join(model.Testiruum.toimumispaev).\
                         filter(sa.func.date(model.Toimumispaev.aeg)==paev)
                q1 = q1.group_by(model.Sooritaja.lang)
                k_keeled = {}
                sooritajad = 0
                for cnt, lang in q1.all():
                    keeled.add(lang)
                    k_keeled[lang] = cnt
                    prk_keeled[lang] = cnt + (prk_keeled.get(lang) or 0)
                    ta_keeled[lang] = cnt + (ta_keeled.get(lang) or 0)
                    sooritajad += cnt

                prk_sooritajad += sooritajad
                ta_sooritajad += sooritajad
            else:
                sooritajad = None
                k_keeled = None
                
            if self.c.sooritajad and self.c.suunatudkoolid:
                # kuvame, milliste koolide õpilased selles kohas sooritavad
                suunatud = []
                q2 = model.SessionR.query(model.Sooritaja.kool_koht_id, model.Koht.nimi).\
                     join(model.Sooritus.sooritaja).\
                     filter(model.Sooritus.testikoht_id==testikoht_id).\
                     outerjoin(model.Sooritaja.kool_koht).\
                     distinct().\
                     order_by(model.Koht.nimi)
                if self.c.ruumid:
                    q2 = q2.join(model.Sooritus.testiruum).\
                         join(model.Testiruum.toimumispaev).\
                         filter(sa.func.date(model.Toimumispaev.aeg)==paev)

                for kool_id, kool_nimi in q2.all():
                    # sooritajate arv keelte lõikes
                    q1 = model.SessionR.query(sa.func.count(model.Sooritaja.id),
                                             model.Sooritaja.lang)
                    q1 = q1.join(model.Sooritaja.sooritused).\
                         filter(model.Sooritus.testikoht_id==testikoht_id).\
                         filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA).\
                         filter(model.Sooritaja.kool_koht_id==kool_id)
                    if self.c.regviis:
                        if isinstance(self.c.regviis, list):
                            q1 = q1.filter(model.Sooritaja.regviis_kood.in_(self.c.regviis))
                        else:
                            q1 = q1.filter(model.Sooritaja.regviis_kood==self.c.regviis)
                    if self.c.ruumid:
                        q1 = q1.join(model.Sooritus.testiruum).\
                             join(model.Testiruum.toimumispaev).\
                             filter(sa.func.date(model.Toimumispaev.aeg)==paev)

                    q1 = q1.group_by(model.Sooritaja.lang)
                    kool_sooritajad = 0
                    kool_keeled = {}
                    for cnt, lang in q1.all():
                        kool_keeled[lang] = cnt
                        kool_sooritajad += cnt
                    if not kool_id:
                        # varemlõpetanuid nimetame eksamikeskuses registreerituteks
                        kool_nimi = _("Eksamikeskuses registreeritud")
                    suunatud.append([kool_nimi, kool_keeled, kool_sooritajad])
            else:
                suunatud = None
                    
            if self.c.vaatlejad:
                # läbiviijate arv - rollide arv, isik ei pea olema määratud
                q2 = model.SessionR.query(sa.func.count(model.Labiviija.id)).\
                     filter(model.Labiviija.testikoht_id==testikoht_id).\
                     filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_VAATLEJA)
                if self.c.ruumid:
                    q2 = q2.join(model.Labiviija.testiruum).\
                         join(model.Testiruum.toimumispaev).\
                         filter(sa.func.date(model.Toimumispaev.aeg)==paev)
                    
                vaatlejad = q2.scalar()
                ta_vaatlejad += vaatlejad
                prk_vaatlejad += vaatlejad
            else:
                vaatlejad = None

            prk_data.append([k_nimi, paev, paevaruumid, k_keeled, sooritajad, vaatlejad, suunatud])

            prev_ta_tahised = ta_tahised
            prev_prk_id = prk_id

        if len(prk_data):
            prk_data.append([None, prk_keeled, prk_sooritajad, prk_vaatlejad])
            ta_data.append(prk_data)

        if len(ta_data):
            ta_data.append([None, ta_keeled, ta_sooritajad, ta_vaatlejad])
            items.append(ta_data)
        
        self.c.items = items
        self.c.keeled = [lang for lang in const.LANG_ORDER if lang in keeled]

    def _index_pdf(self, items, keeled, sooritajad, vaatlejad, ruumid):
        doc = SoorituskohadDoc(items, keeled, sooritajad, vaatlejad, ruumid)
        data = doc.generate()
        filename = 'soorituskohad.pdf'
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)

    def _prepare_items(self, q):
        "CSV jaoks vormistamine"
        c = self.c
        header = [_("Toimumisaeg"),
                  _("Soorituspiirkond"),
                  _("Soorituskoht"),
                  ]
        if c.suunatudkoolid:
            header.append(_("Suunanud kool"))
        if c.ruumid:
            header.append(_("Kuupäev"))
            header.append(_("Ruumide arv"))
        if c.sooritajad:
            for lang in c.keeled:
                header.append(model.Klrida.get_lang_nimi(lang))
            header.append(_("Kokku"))
        if c.vaatlejad:
            header.append(_("Vaatlejaid"))

        items = []
        for ta_data in c.items:
            ta_nimi = ta_data[0]
            for prk_data in ta_data[1:-1]:
                prk_nimi = prk_data[0]
                for rcd in prk_data[1:-1]:
                    koht_nimi = rcd[0]
                    item = [ta_nimi, prk_nimi, koht_nimi]
                    if c.suunatudkoolid:
                        item.append('')
                    if c.ruumid:
                        item.append(self.h.str_from_date(rcd[1]))
                        item.append(rcd[2])
                    if c.sooritajad:
                        for lang in c.keeled:
                            item.append(rcd[3].get(lang) or 0)
                        item.append(rcd[4])
                    if c.vaatlejad:
                        item.append(rcd[5])
                    items.append(item)
                    
                    if rcd[6]:
                        # suunatud koolid
                        for rcd2 in rcd[6]:
                            kool_nimi = rcd2[0]
                            item = [ta_nimi, prk_nimi, koht_nimi, kool_nimi]
                            if c.ruumid:
                                item.append('')
                                item.append('')
                            if c.sooritajad:
                                for lang in c.keeled:
                                    item.append(rcd2[1].get(lang) or 0)
                                item.append(rcd2[2])
                            if c.vaatlejad:
                                item.append('')
                            items.append(item)

                if c.sooritajad:
                    rcd = prk_data[-1]
                    item = [ta_nimi, prk_nimi, _("Soorituspiirkonnas kokku")]
                    if c.suunatudkoolid:
                        item.append('')
                    if c.ruumid:
                        item.append('')
                        item.append('')
                    for lang in c.keeled:
                        item.append(rcd[1].get(lang) or 0)
                    item.append(rcd[2])
                    if c.vaatlejad:
                        item.append(rcd[3])
                    items.append(item)
                    
            if c.sooritajad:
                rcd = ta_data[-1]
                item = [ta_nimi, _("Toimumisajal kokku"), '']
                if c.suunatudkoolid:
                    item.append('')                
                if c.ruumid:
                    item.append('')
                    item.append('')
                for lang in c.keeled:
                    item.append(rcd[1].get(lang) or 0)
                item.append(rcd[2])
                if c.vaatlejad:
                    item.append(rcd[3])
                items.append(item)
                
        return header, items
                  
                  
