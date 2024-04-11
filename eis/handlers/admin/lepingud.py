# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class LepingudController(BaseResourceController):
    _permission = 'lepingud'
    _MODEL = model.Leping
    _EDIT_TEMPLATE = 'admin/leping.mako'
    _INDEX_TEMPLATE = 'admin/lepingud.mako'
    _LIST_TEMPLATE = 'admin/lepingud_list.mako'
    _ITEM_FORM = forms.admin.LepingForm
    _DEFAULT_SORT = '-leping.aasta_kuni,-leping.id'
    _no_paginate = True
    _actions = 'index,edit,show,update,create,new,delete'
    
    def _search_default(self, q):
        self.c.aasta = date.today().year
        return self._search(q)

    def _search(self, q):
        c = self.c
        self.set_debug()        

        if c.aasta:
            aasta = int(c.aasta)
            q = (q.filter(sa.or_(model.Leping.aasta_alates==None,
                                 model.Leping.aasta_alates<=aasta))
                 .filter(sa.or_(model.Leping.aasta_kuni==None,
                                model.Leping.aasta_kuni>=aasta))
                 )
        return q

    def _new(self, item):
        copy_id = self.request.params.get('copy_id')
        if copy_id:
            orig = model.Leping.get(copy_id)
            if orig:
                item.testsessioon_id = orig.testsessioon_id
                item.nimetus = orig.nimetus
                item.url = orig.url
                item.sessioonita = orig.sessioonita
                item.yldleping = orig.yldleping
                item.aasta_alates = date.today().year
                item.aasta_kuni = date.today().year
                for o in orig.lepingurollid:
                    lroll = model.Lepinguroll(kasutajagrupp_id=o.kasutajagrupp_id,
                                              aine_kood=o.aine_kood,
                                              testiliik_kood=o.testiliik_kood)
                    item.lepingurollid.append(lroll)

    def _edit(self, item):
        c = self.c
        c.opt_aine = c.opt.klread_kood('AINE')
        c.opt_testiliik = c.opt.klread_kood('TESTILIIK')
        grupid_id = (const.GRUPP_HINDAJA_K,
                     const.GRUPP_HINDAJA_S,
                     const.GRUPP_HINDAJA_S2,
                     const.GRUPP_INTERVJUU,
                     const.GRUPP_HIND_INT,
                     const.GRUPP_KONSULTANT,
                     const.GRUPP_KOMISJON,
                     const.GRUPP_KOMISJON_ESIMEES,
                     const.GRUPP_VAATLEJA,
                     const.GRUPP_HINDAMISEKSPERT,
                     const.GRUPP_T_ADMIN,
                     )
        c.opt_kasutajagrupp = [(str(g_id), c.opt.grupp_nimi(g_id)) for g_id in grupid_id]
        c.opt_sessioon = [(str(r[0]), r[1]) for r in model.Testsessioon.get_opt()]

    def _update(self, item, lang=None):

        item.from_form(self.form.data, self._PREFIX)
        if not item.aasta_alates:
            item.aasta_alates = 2015

        lr = self.form.data['lr']
        uniq_lr = []
        uniq_keys = []
        for r in lr:
            key = r['kasutajagrupp_id'], r['aine_kood'], r['testiliik_kood']
            if key not in uniq_keys:
                uniq_keys.append(key)
                uniq_lr.append(r)
        BaseGridController(item.lepingurollid, model.Lepinguroll).save(uniq_lr)
        model.Session.flush()
        self._gen_testilepingud(item)

    def _gen_testilepingud(self, item):

        # leiame testimiskorrad, kus leping oli seni kasutusel
        q = (model.Session.query(model.Testileping.testimiskord_id)
             .distinct()
             .filter_by(leping_id=item.id))
        vanad_id = [tk_id for tk_id, in q.all()]

        # leiame testimiskorrad, mis vastavad uutele tingimustele
        q = (model.Session.query(model.Testimiskord.id)
             .join(model.Testimiskord.testsessioon)
             )
        if item.aasta_alates and item.aasta_alates == item.aasta_kuni:
            q = q.filter(model.Testsessioon.oppeaasta==item.aasta_alates)
        else:
            if item.aasta_alates:
                q = q.filter(model.Testsessioon.oppeaasta>=item.aasta_alates)
            if item.aasta_kuni:
                q = q.filter(model.Testsessioon.oppeaasta<=item.aasta_kuni)
        if item.testsessioon_id:
            q = q.filter(model.Testsessioon.id==item.testsessioon_id)
        q = q.filter(sa.exists().where(
            sa.and_(model.Lepinguroll.leping_id==item.id,
                    model.Lepinguroll.testiliik_kood==model.Test.testiliik_kood,
                    sa.or_(model.Lepinguroll.aine_kood==None,
                           model.Lepinguroll.aine_kood==model.Test.aine_kood)
                    )
            ))
        uued_id = [tk_id for tk_id, in q.all()]

        # uuendame testimiskordade testilepingud
        for tkord_id in (vanad_id + uued_id):
            tkord = model.Testimiskord.get(tkord_id)
            model.Testileping.give_for(tkord)
            log.debug(f'{tkord_id} - {len(tkord.testilepingud)} lepingut')

    def _delete(self, item):
        for r in item.lepingurollid:
            r.delete()
        for r in item.testilepingud:
            r.delete()
        for r in item.labiviijalepingud:
            r.delete()
        item.delete()
        model.Session.commit()
        self.success(_("Andmed on kustutatud"))
