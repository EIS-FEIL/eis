# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class KogusisuController(BaseResourceController):

    _permission = 'ylesandekogud'

    _MODEL = model.Ylesandekogu
    _SEARCH_FORM = forms.ekk.ylesandekogud.KogusisuForm
    _INDEX_TEMPLATE = 'ekk/ylesandekogud/kogusisu.mako' 
    _no_paginate = True
    _actions = 'index'
    _ignore_default_params = ['csvt','csvy','csvtk','csvyk','otsi']
    
    def _search(self, q):
        # tabelite ja ylesannete andmed
        c = self.c
        if c.kuni:
            c.kuni1 = c.kuni + timedelta(days=1)
        if c.csvt:
            header, items, footer = self._get_testid(c.item)
            data = self._csv_data(header, items)
            data = utils.encode_ansi(data)
            return utils.download(data, 'testid.csv', const.CONTENT_TYPE_CSV)
        elif c.csvy:
            header, items, footer = self._get_ylesanded(c.item)
            data = self._csv_data(header, items)
            data = utils.encode_ansi(data)
            return utils.download(data, 'ylesanded.csv', const.CONTENT_TYPE_CSV)
        elif c.csvtk:
            header, items = self._get_kasutajad(c.item, True)
            data = self._csv_data(header, items)
            data = utils.encode_ansi(data)
            return utils.download(data, 'testikasutajad.csv', const.CONTENT_TYPE_CSV)
        elif c.csvyk:
            header, items = self._get_kasutajad(c.item, False)
            data = self._csv_data(header, items)
            data = utils.encode_ansi(data)
            return utils.download(data, 'ylesandekasutajad.csv', const.CONTENT_TYPE_CSV)
            
        c.t_header, c.t_items, c.t_footer = self._get_testid(c.item)
        c.y_header, c.y_items, c.y_footer = self._get_ylesanded(c.item)

    def _search_default(self, q):
        return self._search(q)
        
    def _get_testid(self, item):
        # mis keeles on sooritajaid
        header, footer, keeled1, keeled2 = self._get_testid_header(item)
        items = []
        q = (model.Session.query(model.Test.id,
                                 model.Test.nimi,
                                 model.Test.autor)
             .join(model.Test.kogutestid)
             .filter(model.Kogutest.ylesandekogu_id==item.id)
             .outerjoin((model.Kasutaja, model.Kasutaja.isikukood==model.Test.creator))
             .order_by(model.Kogutest.id)
             )
        for test_id, test_nimi, autor in q.all():        
            row = self._get_testid_row(test_id, test_nimi, autor, keeled1, keeled2)
            items.append(row)

        footer[0] = _("Kokku {n} testi").format(n=len(items))
        return header, items, footer

    def _get_testid_header(self, item):
        c = self.c
        NL = c.csvt and '\n' or '<br/>'
        # mitu õpetajat on selle kogu teste suunanud
        # mitme nimekirjaga on selle kogu teste suunatud
        # mis keeles sooritajatele
        q1 = (model.Session.query(sa.func.count(sa.distinct(model.Nimekiri.esitaja_kasutaja_id)),
                                  sa.func.count(sa.distinct(model.Nimekiri.id)),
                                  model.Sooritaja.lang)
              .join(model.Sooritaja.nimekiri)
              .filter(model.Nimekiri.testimiskord_id==None)
              .join((model.Kogutest, model.Kogutest.test_id==model.Nimekiri.test_id))
              .filter(model.Kogutest.ylesandekogu_id==item.id)
              )
        if c.alates:
            q1 = q1.filter(model.Sooritaja.reg_aeg >= c.alates)
        if c.kuni1:
            q1 = q1.filter(model.Sooritaja.reg_aeg < c.kuni1)
        q1 = q1.group_by(model.Sooritaja.lang)
        esitanud = {lang: (cnt_i, cnt_k) for (cnt_i, cnt_k, lang) in q1.all()}
        keeled1 = self.c.opt.sorted_lang(list(esitanud.keys()))

        # mitu õpilast on selle kogu teste lahendanud
        # mitu korda on selle kogu teste lahendatud
        # mis keeles
        q2 = (model.Session.query(sa.func.count(sa.distinct(model.Sooritaja.kasutaja_id)),
                                  sa.func.count(model.Sooritaja.id),
                                  model.Sooritaja.lang)
              .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_POOLELI,
                                                   const.S_STAATUS_KATKESTATUD,
                                                   const.S_STAATUS_KATKESPROT,
                                                   const.S_STAATUS_TEHTUD)))
              .filter(model.Sooritaja.testimiskord_id==None)
              .join((model.Kogutest, model.Kogutest.test_id==model.Sooritaja.test_id))
              .filter(model.Kogutest.ylesandekogu_id==item.id)
              )
        if c.alates or c.kuni1:
            if c.alates and c.kuni1:
                f_sooritus = sa.and_(model.Sooritus.seansi_algus >= c.alates,
                                     model.Sooritus.seansi_algus < c.kuni1)
            elif c.alates:
                f_sooritus = model.Sooritus.seansi_algus >= c.alates
            else:
                f_sooritus = model.Sooritus.seansi_algus < c.kuni1
            q2 = q2.filter(model.Sooritaja.sooritused.any(f_sooritus))

        q2 = q2.group_by(model.Sooritaja.lang)
        lahendanud = {lang: (cnt_i, cnt_k) for (cnt_i, cnt_k, lang) in q2.all()}        
        keeled2 = self.c.opt.sorted_lang(list(lahendanud.keys()))
        
        footer = [None]
        header = [_("Testi ID"),
                  _("Testi nimetus"),
                  _("Autor")]

        if keeled1:
            header.append(_("Õpetajate arv"))
            header.append(_("Nimekirjade arv"))
            #header.append(_(u"Kasutatavus (õpetaja)"))
            header.append(_("Viimane kasutamisaeg"))

            opetajad = []
            suunamiskorrad = []
            for lang in keeled1:
                r = esitanud.get(lang)
                if r:
                    lang_nimi = model.Klrida.get_lang_nimi(lang)
                    opetajad.append('%d (%s)' % (r[0], lang_nimi))
                    suunamiskorrad.append('%d (%s)' % (r[1], lang_nimi))
            footer.append(NL.join(opetajad))
            footer.append(NL.join(suunamiskorrad))
            footer.append('')

        if keeled2:
            header.append(_("Lahendanud õpilaste arv"))
            header.append(_("Lahendamiste arv"))

            opilased = []
            lahendamiskorrad = []
            for lang in keeled2:
                r = lahendanud.get(lang)
                if r:
                    lang_nimi = model.Klrida.get_lang_nimi(lang)
                    opilased.append('%d (%s)' % (r[0], lang_nimi))
                    lahendamiskorrad.append('%d (%s)' % (r[1], lang_nimi))
            footer.append(NL.join(opilased))
            footer.append(NL.join(lahendamiskorrad))
            
        return header, footer, keeled1, keeled2

    def _get_testid_row(self, test_id, test_nimi, autor, keeled1, keeled2):
        c = self.c
        NL = c.csvt and '\n' or '<br/>'
        row = [test_id,
               test_nimi,
               autor]

        if keeled1:
            # mitu õpetajat on seda testi suunanud
            # mitme nimekirjaga on seda testi suunatud
            # mis keeles sooritajatele
            q1 = (model.Session.query(sa.func.count(sa.distinct(model.Nimekiri.esitaja_kasutaja_id)),
                                      sa.func.count(sa.distinct(model.Nimekiri.id)),
                                      model.Sooritaja.lang)
                  .join(model.Nimekiri.sooritajad)
                  .filter(model.Nimekiri.testimiskord_id==None)
                  .filter(model.Nimekiri.test_id==test_id)
                  )
            if c.alates:
                  q1 = q1.filter(model.Sooritaja.reg_aeg >= c.alates)
            if c.kuni1:
                q1 = q1.filter(model.Sooritaja.reg_aeg < c.kuni1)
            q1 = q1.group_by(model.Sooritaja.lang)
            esitanud = {lang: (cnt_i, cnt_k) for (cnt_i, cnt_k, lang) in q1.all()}
            #if test_id==2817: model.log_query(q1)
        
            # viimane kasutamisaeg
            q3 = (model.Session.query(sa.func.max(model.Sooritaja.reg_aeg))
                  .join(model.Sooritaja.nimekiri)
                  .filter(model.Nimekiri.testimiskord_id==None)
                  .filter(model.Nimekiri.test_id==test_id)
                  )
            if c.alates:
                  q3 = q3.filter(model.Sooritaja.reg_aeg >= c.alates)
            if c.kuni1:
                q3 = q3.filter(model.Sooritaja.reg_aeg < c.kuni1)

            viimati = q3.scalar()

            opetajad = []
            suunamiskorrad = []
            for lang in keeled1:
                r = esitanud.get(lang)
                if r:
                    lang_nimi = model.Klrida.get_lang_nimi(lang)
                    opetajad.append(('%d (%s)' % (r[0], lang_nimi), lang))
                    suunamiskorrad.append('%d (%s)' % (r[1], lang_nimi))
            if self.c.csvt:
                opetajad = '\n'.join(r[0] for r in opetajad)
            row.append(opetajad)
            row.append(NL.join(suunamiskorrad))
            row.append(self.h.str_from_date(viimati))

        if keeled2:
            # mitu õpilast on seda testi lahendanud
            # mitu korda on seda testi lahendatud
            # mis keeles
            q2 = (model.Session.query(sa.func.count(sa.distinct(model.Sooritaja.kasutaja_id)),
                                      sa.func.count(model.Sooritaja.id),
                                      model.Sooritaja.lang)
                  .filter(model.Sooritaja.test_id==test_id)
                  .filter(model.Sooritaja.testimiskord_id==None)
                  .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_POOLELI,
                                                       const.S_STAATUS_KATKESTATUD,
                                                       const.S_STAATUS_KATKESPROT,
                                                       const.S_STAATUS_TEHTUD)))
                  )
            if c.alates or c.kuni1:
                if c.alates and c.kuni1:
                    f_sooritus = sa.and_(model.Sooritus.seansi_algus >= c.alates,
                                         model.Sooritus.seansi_algus < c.kuni1)
                elif c.alates:
                    f_sooritus = model.Sooritus.seansi_algus >= c.alates
                else:
                    f_sooritus = model.Sooritus.seansi_algus < c.kuni1
                q2 = q2.filter(model.Sooritaja.sooritused.any(f_sooritus))

            q2 = q2.group_by(model.Sooritaja.lang)
            lahendanud = {lang: (cnt_i, cnt_k) for (cnt_i, cnt_k, lang) in q2.all()}

            opilased = []
            lahendamiskorrad = []
            for lang in keeled2:
                r = lahendanud.get(lang)
                if r:
                    lang_nimi = model.Klrida.get_lang_nimi(lang)
                    opilased.append('%d (%s)' % (r[0], lang_nimi))
                    lahendamiskorrad.append('%d (%s)' % (r[1], lang_nimi))
            row.append(NL.join(opilased))
            row.append(NL.join(lahendamiskorrad))

        return row
        
    def _get_ylesanded(self, item):
        # mis keeles on sooritajaid
        header, footer, keeled1, keeled2, on_alateema = self._get_ylesanded_header(item)
        items = []
        sum_pallid = 0
        q = (model.Session.query(model.Ylesanne.id,
                                 model.Ylesanne.nimi,
                                 model.Ylesanne.max_pallid,
                                 model.Ylesanne.staatus)
             .join(model.Ylesanne.koguylesanded)
             .filter(model.Koguylesanne.ylesandekogu_id==item.id)
             .order_by(model.Koguylesanne.id)
             )
        for y_id, y_nimi, pallid, staatus in q.all():
            sum_pallid += pallid or 0
            row = self._get_ylesanded_row(y_id, y_nimi, pallid, staatus, keeled1, keeled2, on_alateema)
            items.append(row)

        footer[0] = _("Kokku {n} ülesannet").format(n=len(items))
        footer[1] = self.h.fstr(sum_pallid)
        return header, items, footer

    def _get_ylesanded_header(self, item):
        c = self.c
        NL = c.csvy and '\n' or '<br/>'
        # esitanud õpetajate arv
        # esitatud nimekirjade arv
        # esitamise keeled
        q1 = (model.Session.query(sa.func.count(sa.distinct(model.Nimekiri.esitaja_kasutaja_id)),
                                  sa.func.count(sa.distinct(model.Nimekiri.id)),
                                  model.Sooritaja.lang)
              .join(model.Sooritaja.nimekiri)
              .join(model.Nimekiri.test)
              .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_TOO)))
              .join((model.Valitudylesanne, model.Valitudylesanne.test_id==model.Test.id))                  
              .join((model.Koguylesanne, model.Koguylesanne.ylesanne_id==model.Valitudylesanne.ylesanne_id))
              .filter(model.Koguylesanne.ylesandekogu_id==item.id)              
              )
        if c.alates:
            q1 = q1.filter(model.Sooritaja.reg_aeg >= c.alates)
        if c.kuni1:
            q1 = q1.filter(model.Sooritaja.reg_aeg < c.kuni1)
        q1 = q1.group_by(model.Sooritaja.lang)
        esitanud = {lang: (cnt_i, cnt_k) for (cnt_i, cnt_k, lang) in q1.all()}
        keeled1 = self.c.opt.sorted_lang(list(esitanud.keys()))

        # mitu õpilast on seda ylesannet lahendanud
        # mitu korda on ylesannet lahendatud
        # lahendamise keel
        q2 = (model.Session.query(sa.func.count(sa.distinct(model.Sooritaja.kasutaja_id)),
                                  sa.func.count(model.Ylesandevastus.id),
                                  model.Sooritaja.lang)
              .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_POOLELI,
                                                   const.S_STAATUS_KATKESTATUD,
                                                   const.S_STAATUS_KATKESPROT,
                                                   const.S_STAATUS_TEHTUD)))
              .join(model.Sooritaja.test)
              .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_TOO)))
              .join(model.Sooritaja.sooritused)
              .join((model.Ylesandevastus,
                     model.Ylesandevastus.sooritus_id==model.Sooritus.id))
              .join((model.Valitudylesanne,
                     model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
              .join((model.Koguylesanne,
                     model.Koguylesanne.ylesanne_id==model.Valitudylesanne.ylesanne_id))
              .filter(model.Koguylesanne.ylesandekogu_id==item.id)                            
              )
        if c.alates:
            q2 = q2.filter(model.Ylesandevastus.algus >= c.alates)
        if c.kuni1:
            q2 = q2.filter(model.Ylesandevastus.algus < c.kuni1)
        q2 = q2.group_by(model.Sooritaja.lang)
        lahendanud = {lang: (cnt_i, cnt_k) for (cnt_i, cnt_k, lang) in q2.all()}        
        keeled2 = self.c.opt.sorted_lang(list(lahendanud.keys()))        

        # kas mõnel kogu ylesandel on alateema?
        q1 = (model.Session.query(sa.func.count(model.Ylesandeteema.id))
              .filter(model.Ylesandeteema.alateema_kood!=None)
              .filter(model.Ylesandeteema.alateema_kood!='')
              .join(model.Ylesandeteema.ylesandeaine)
              .join((model.Koguylesanne, model.Koguylesanne.ylesanne_id==model.Ylesandeaine.ylesanne_id))
              .filter(model.Koguylesanne.ylesandekogu_id==item.id)
              )
        on_alateema = q1.scalar() > 0

        footer = [None, None]
        header = [_("Ülesande ID"),
                  _("Ülesande nimetus"),
                  _("Punktid"),
                  ]
        if on_alateema:
            header.append(_("Alateema"))
            footer.append('')
        if keeled1:
            header.append(_("Õpetajate arv"))
            header.append(_("Nimekirjade arv"))
            #header.append(_(u"Kasutatavus (õpetaja)"))
            header.append(_("Viimane kasutamisaeg"))

            opetajad = []
            suunamiskorrad = []
            for lang in keeled1:
                r = esitanud.get(lang)
                if r:
                    lang_nimi = model.Klrida.get_lang_nimi(lang)
                    opetajad.append('%d (%s)' % (r[0], lang_nimi))
                    suunamiskorrad.append('%d (%s)' % (r[1], lang_nimi))
            footer.append(NL.join(opetajad))
            footer.append(NL.join(suunamiskorrad))
            footer.append('')

        if keeled2:
            header.append(_("Lahendanud õpilaste arv"))
            header.append(_("Lahendamiste arv"))

            opilased = []
            lahendamiskorrad = []
            for lang in keeled2:
                r = lahendanud.get(lang)
                if r:
                    lang_nimi = model.Klrida.get_lang_nimi(lang)
                    opilased.append('%d (%s)' % (r[0], lang_nimi))
                    lahendamiskorrad.append('%d (%s)' % (r[1], lang_nimi))
            footer.append(NL.join(opilased))
            footer.append(NL.join(lahendamiskorrad))
            
        header.append(_("Olek"))
        footer.append('')
        return header, footer, keeled1, keeled2, on_alateema

    def _get_ylesanded_row(self, y_id, y_nimi, pallid, staatus, keeled1, keeled2, on_alateema):
        c = self.c
        NL = c.csvy and '\n' or '<br/>'
        row = [y_id,
               y_nimi,
               self.h.fstr(pallid),
               ]

        if on_alateema:
            alateemad = []
            q4 = (model.Session.query(model.Ylesandeteema)
                  .join(model.Ylesandeteema.ylesandeaine)
                  .filter(model.Ylesandeaine.ylesanne_id==y_id))
            for yt in q4.all():
                value = yt.alateema_nimi
                if value and value not in alateemad:
                    alateemad.append(value)
            row.append(NL.join(alateemad))

        if keeled1:
            # mitu õpetajat on seda ylesannet suunanud
            # mitme nimekirjaga on seda ylesannet suunatud
            q1 = (model.Session.query(sa.func.count(sa.distinct(model.Nimekiri.esitaja_kasutaja_id)),
                                      sa.func.count(sa.distinct(model.Nimekiri.id)),
                                      model.Sooritaja.lang)
                  .join(model.Nimekiri.sooritajad)
                  .join(model.Nimekiri.test)
                  .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_TOO)))
                  .join((model.Valitudylesanne, model.Valitudylesanne.test_id==model.Test.id))                  
                  .filter(model.Valitudylesanne.ylesanne_id==y_id)
                  )
            if c.alates:
                q1 = q1.filter(model.Sooritaja.reg_aeg >= c.alates)
            if c.kuni1:
                q1 = q1.filter(model.Sooritaja.reg_aeg < c.kuni1)
            q1 = q1.group_by(model.Sooritaja.lang)
            esitanud = {lang: (cnt_i, cnt_k) for (cnt_i, cnt_k, lang) in q1.all()}

            # viimane kasutamisaeg
            q3 = (model.Session.query(sa.func.max(model.Sooritaja.reg_aeg))
                  .join(model.Sooritaja.nimekiri)
                  .join(model.Nimekiri.test)
                  .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_TOO)))
                  .join((model.Valitudylesanne, model.Valitudylesanne.test_id==model.Nimekiri.test_id))
                  .filter(model.Valitudylesanne.ylesanne_id==y_id)
                  )
            if c.alates:
                q3 = q3.filter(model.Sooritaja.reg_aeg >= c.alates)
            if c.kuni1:
                q3 = q3.filter(model.Sooritaja.reg_aeg < c.kuni1)
            viimati = q3.scalar()
            opetajad = []
            suunamiskorrad = []
            for lang in keeled1:
                r = esitanud.get(lang)
                if r:
                    lang_nimi = model.Klrida.get_lang_nimi(lang)
                    opetajad.append(('%d (%s)' % (r[0], lang_nimi), lang))
                    suunamiskorrad.append('%d (%s)' % (r[1], lang_nimi))
            if self.c.csvy:
                opetajad = '\n'.join(r[0] for r in opetajad)
            row.append(opetajad)
            row.append(NL.join(suunamiskorrad))
            row.append(self.h.str_from_date(viimati))

        if keeled2:
            # mitu õpilast on seda ylesannet lahendanud
            # mitu korda on ylesannet lahendatud
            q2 = (model.Session.query(sa.func.count(sa.distinct(model.Sooritaja.kasutaja_id)),
                                      sa.func.count(model.Ylesandevastus.id),
                                      model.Sooritaja.lang)
                  .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_POOLELI,
                                                       const.S_STAATUS_KATKESTATUD,
                                                       const.S_STAATUS_KATKESPROT,
                                                       const.S_STAATUS_TEHTUD)))
                  .join(model.Sooritaja.test)
                  .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_TOO)))
                  .join(model.Sooritaja.sooritused)
                  .join((model.Ylesandevastus,
                         model.Ylesandevastus.sooritus_id==model.Sooritus.id))
                  .join((model.Valitudylesanne,
                         model.Valitudylesanne.id==model.Ylesandevastus.valitudylesanne_id))
                  .filter(model.Valitudylesanne.ylesanne_id==y_id)
                  )
            if c.alates:
                q2 = q2.filter(model.Ylesandevastus.algus >= c.alates)
            if c.kuni1:
                q2 = q2.filter(model.Ylesandevastus.algus < c.kuni1)
            q2 = q2.group_by(model.Sooritaja.lang)
            lahendanud = {lang: (cnt_i, cnt_k) for (cnt_i, cnt_k, lang) in q2.all()}

            opilased = []
            lahendamiskorrad = []
            for lang in keeled2:
                r = lahendanud.get(lang)
                if r:
                    lang_nimi = model.Klrida.get_lang_nimi(lang)
                    opilased.append('%d (%s)' % (r[0], lang_nimi))
                    lahendamiskorrad.append('%d (%s)' % (r[1], lang_nimi))
            row.append(NL.join(opilased))
            row.append(NL.join(lahendamiskorrad))

        row.append(model.Klrida.get_str('Y_STAATUS', str(staatus)))
        return row
              
    def _index_opetaja(self):
        "Õpetajad, kes on antud testi või ülesannet suunanud lahendamiseks"
        c = self.c
        form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
        form.validate()
        params = form.data

        c.lang = lang = self.params_lang()
        test_id = params.get('test_id')
        ylesanne_id = params.get('ylesanne_id')
        c.items = []

        alates = params.get('alates')
        kuni = params.get('kuni')

        # siin sisaldab sooritajate arv kõiki registreerituid, mitte ainult päriselt lahendanuid

        q = None
        if test_id:
            # mitu õpetajat on seda testi suunanud
            q = (model.Session.query(model.Nimekiri.esitaja_kasutaja_id,
                                     model.Kasutaja.nimi,
                                     model.Koht.nimi,
                                     sa.func.count(sa.distinct(model.Nimekiri.id)),
                                     sa.func.count(sa.distinct(model.Sooritaja.kasutaja_id)))
                 .filter(model.Nimekiri.test_id==test_id)
                 )
        elif ylesanne_id:
            # mitu õpetajat on seda ylesannet suunanud
            q = (model.Session.query(model.Nimekiri.esitaja_kasutaja_id,
                                     model.Kasutaja.nimi,
                                     model.Koht.nimi,
                                     sa.func.count(sa.distinct(model.Nimekiri.id)),
                                     sa.func.count(sa.distinct(model.Sooritaja.kasutaja_id)))
                 .join(model.Nimekiri.test)
                 .filter(model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_TOO)))
                 .join((model.Valitudylesanne,
                        sa.and_(model.Valitudylesanne.test_id==model.Test.id,
                                model.Valitudylesanne.ylesanne_id==ylesanne_id)))
                 )
        if test_id or ylesanne_id:
            q = (q.join(model.Nimekiri.esitaja_kasutaja)
                 .outerjoin(model.Nimekiri.esitaja_koht)
                 .join(model.Nimekiri.sooritajad)
                 .filter(model.Sooritaja.lang==lang)
                 )
            if alates:
                q = q.filter(model.Sooritaja.reg_aeg >= alates)
            if kuni:
                q = q.filter(model.Sooritaja.reg_aeg < kuni + timedelta(days=1))
            q = (q.group_by(model.Nimekiri.esitaja_kasutaja_id,
                            model.Kasutaja.nimi,
                            model.Koht.nimi)
                 .order_by(model.Kasutaja.nimi, model.Koht.nimi)
                 )
            for kasutaja_id, nimi, koht_nimi, nk_cnt, j_cnt in q.all():
                self.c.items.append((nimi, koht_nimi, nk_cnt, j_cnt))

        return self.render_to_response('ekk/ylesandekogud/kogusisu.kasutajad.mako')

    def _get_kasutajad(self, item, on_testid):
        "Kogus olevaid teste või ülesandeid kasutavate õpetajate loetelu CSV jaoks"
        c = self.c
        if on_testid:
            header = (_("Testi ID"),
                      _("Suunaja"),
                      _("Õppeasutus"),
                      _("Keel"),
                      _("Nimekirjad"),
                      _("Lahendajad"))
        else:
            header = (_("Ülesande ID"),
                      _("Suunaja"),
                      _("Õppeasutus"),
                      _("Keel"),
                      _("Nimekirjad"),
                      _("Lahendajad"))
        if on_testid:
            group = (model.Kogutest.test_id,
                     model.Kasutaja.nimi,
                     model.Koht.nimi,
                     model.Sooritaja.lang)
            q = (model.Session.query(*group,
                                     sa.func.count(sa.distinct(model.Nimekiri.id)),
                                     sa.func.count(sa.distinct(model.Sooritaja.kasutaja_id)))
                 .filter(model.Kogutest.ylesandekogu_id==item.id)
                 .join((model.Nimekiri, model.Nimekiri.test_id==model.Kogutest.test_id))
                 )
        else:
            group = (model.Koguylesanne.ylesanne_id,
                     model.Kasutaja.nimi,
                     model.Koht.nimi,
                     model.Sooritaja.lang)
            q = (model.Session.query(*group,
                                     sa.func.count(sa.distinct(model.Nimekiri.id)),
                                     sa.func.count(sa.distinct(model.Sooritaja.kasutaja_id)))
                 .filter(model.Koguylesanne.ylesandekogu_id==item.id)
                 .join((model.Valitudylesanne, model.Valitudylesanne.ylesanne_id==model.Koguylesanne.ylesanne_id))
                 .join((model.Test, sa.and_(model.Valitudylesanne.test_id==model.Test.id,
                                                 model.Test.testityyp.in_((const.TESTITYYP_AVALIK, const.TESTITYYP_TOO)))
                             ))
                 .join(model.Test.nimekirjad)
                 )
        q = (q.join(model.Nimekiri.esitaja_kasutaja)
             .outerjoin(model.Nimekiri.esitaja_koht)
             .join(model.Nimekiri.sooritajad)
             )
        if c.alates:
            q = q.filter(model.Sooritaja.reg_aeg >= c.alates)
        if c.kuni1:
            q = q.filter(model.Sooritaja.reg_aeg < c.kuni1)

        q = q.group_by(*group).order_by(*group)
        items = []
        for t_id, nimi, koht_nimi, lang, nk_cnt, j_cnt in q.all():
            lang_nimi = model.Klrida.get_lang_nimi(lang)
            items.append((t_id, nimi, koht_nimi, lang_nimi, nk_cnt, j_cnt))

        return header, items
        
    def _perm_params(self):
        return {'obj':self.c.item}

    def __before__(self):
        id = self.request.matchdict.get('kogu_id')
        self.c.item = model.Ylesandekogu.get(id)
        super(KogusisuController, self).__before__()
