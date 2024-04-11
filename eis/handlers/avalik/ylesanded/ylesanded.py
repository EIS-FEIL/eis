from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class YlesandedController(BaseResourceController):

    _permission = 'avylesanded'

    _MODEL = model.Ylesanne
    _EDIT_TEMPLATE = 'avalik/ylesanded/yldandmed.mako' 
    _ITEM_FORM = forms.avalik.ylesanded.YldandmedForm
    _get_is_readonly = False
    _actions = 'index,new,create,show,edit,update,delete'
    
    def _new_d(self):
        c = self.c
        copy_id = self.request.params.get('id')
        if copy_id:
            # tehakse koopia olemasolevast ülesandest
            item = model.Ylesanne.get(copy_id)
            c.item = item.copy()
            c.item.staatus = const.Y_STAATUS_AV_KOOSTAMISEL
            try:
                BlockController.after_copy_task(c.item, self)
            except ValidationError as ex:
                self.error(_("Ülesannet {id} ei saa kopeerida, sest selles on vigu").format(id=copy_id))
            else:
                model.Session.flush()
                model.Tookogumik.lisa_ylesanne(c.user.id, c.item.id, None)
                c.item.logi(_("Loomine koopiana"), 'Alusülesanne %s' % copy_id, None, const.LOG_LEVEL_GRANT)
                model.Session.commit()
                self.success(_("Ülesanne on kopeeritud!"))
            return self.response_dict
        else:
            return BaseResourceController._new_d(self)

    def _new(self, item):
        item.ptest = False
        item.etest = True
        item.arvutihinnatav = True
        item.vastvorm_kood = const.VASTVORM_KE
        item.hindamine_kood = const.HINDAMINE_OBJ
        item.pallemaara = True
        item.max_pallid = 0
        item.kvaliteet_kood = const.KVALITEET_AV
        item.autor = self.c.user.fullname        

        # leiame viimati sama isiku loodud ylesande aine
        q = (model.Session.query(model.Ylesandeaine.aine_kood)
             .join((model.Ylesandeisik, model.Ylesandeisik.ylesanne_id==model.Ylesandeaine.ylesanne_id))
             .filter(model.Ylesandeisik.kasutaja_id==self.c.user.id)
             .filter(model.Ylesandeisik.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA)
             .order_by(sa.desc(model.Ylesandeaine.id))
             )
        for aine, in q.all():
            self.c.aine_kood = aine
            break
        
    def _create(self, **kw):
        item = model.Ylesanne.init(**kw)
        item.ptest = False
        item.etest = True
        item.vastvorm_kood = const.VASTVORM_KP
        item.hindamine_kood = const.HINDAMINE_OBJ
        item.pallemaara = True
        item.kvaliteet_kood = const.KVALITEET_AV        
        item.staatus = const.Y_STAATUS_AV_KOOSTAMISEL
        item.autor = self.c.user.fullname
        item.lang = const.LANG_ET
        item.set_lang()
        self._update(item)
        model.Session.flush()
        model.Tookogumik.lisa_ylesanne(self.c.user.id, item.id, None)
        item.logi('Loomine', None, None, const.LOG_LEVEL_GRANT)
        return item

    def _delete(self, item):
        if len(item.valitudylesanded) > 0:
            self.error(_("Ülesannet ei saa kustutada, sest see on testi koosseisus"))
            return self._after_update(item.id)
        return BaseResourceController._delete(self, item)

    def _after_delete(self, parent_id=None):
        self.prf()
        return HTTPFound(location=self.h.url('tookogumikud'))

    def _update(self, item):
        old_keeled = item.keeled
        old_lang = item.lang
        BaseResourceController._update(self, item)
        self._update_kooliastmed(item)
        self._update_ylesandeained(item)
        self._update_keeled(item, old_lang, old_keeled)
        self._update_vahendid(item)

    def _update_kooliastmed(self, item):
        # salvestame kooliastmed, kodeerides need maskiks
        peamine_aste_kood = self.form.data.get('f_aste_kood')
        kooliastmed = self.form.data.get('v_aste_kood')
        if peamine_aste_kood not in kooliastmed:
            kooliastmed = kooliastmed + [peamine_aste_kood]
        mask = 0
        for kood in kooliastmed:
            mask += self.c.opt.aste_bit(kood) or 0
        if mask != item.aste_mask:
            item.aste_mask = mask

    def _update_ylesandeained(self, item):
        yained = {r.id: r for r in item.ylesandeained}
        for seq, data in enumerate(self.form.data.get('ya')):
            ya_id = data['id']
            try:
                yaine = yained.pop(ya_id)
            except KeyError:
                yaine = model.Ylesandeaine(ylesanne=item)
            yaine.aine_kood = data['aine_kood']
            yaine.oskus_kood = data['oskus_kood']
            yaine.seq = seq
            
            # salvestame teemad ja valdkonnad
            teemad2 = data.get('teemad2')
            for r in list(yaine.ylesandeteemad):
                key = r.teema_kood
                if r.alateema_kood:
                    key += '.' + r.alateema_kood
                try:
                    teemad2.remove(key)
                    # oli alles
                except ValueError:
                    r.delete()
            for key in teemad2:
                koodid = key.split('.')
                r = model.Ylesandeteema(teema_kood=koodid[0],
                                        alateema_kood=len(koodid) > 1 and koodid[1] or None)
                yaine.ylesandeteemad.append(r)

            # salvestame õpitulemused
            opitulemused = data.get('opitulemused')
            for r in list(yaine.ylopitulemused):
                try:
                    opitulemused.remove(r.opitulemus_klrida_id)
                    # oli alles
                except ValueError:
                    r.delete()
            for klrida_id in opitulemused:
                r = model.Ylopitulemus(opitulemus_klrida_id=klrida_id)
                yaine.ylopitulemused.append(r)

        for yaine in list(yained.values()):
            yaine.delete()
        
    def _update_vahendid(self, item):
        vahendid = [{'vahend_kood': r} for r in self.form.data.get('vahend_kood')]
        #vahendid = self._unique_vahend_kood(self.form.data.get('vh'))
        ctrl = BaseGridController(item.vahendid, model.Vahend, None, self, pkey='vahend_kood')        
        ctrl.save(vahendid)        

    def _unique_vahend_kood(self, valikud):
        li = []
        koodid = []
        for n, v in enumerate(valikud):
            kood = v['vahend_kood']
            if kood not in koodid:
                koodid.append(kood)
                li.append(v)
        return li

    def _update_keeled(self, item, old_lang, old_keeled):
        item.lang = self.form.data.get('f_lang')
        item.skeeled = item.lang

    def _edit_kontroll(self, id):
        c = self.c
        c.item = model.Ylesanne.get(id)
        c.item.check(self)
        model.Session.commit()
        c.rc, c.y_errors, c.sp_errors, c.k_errors, c.k_warnings = BlockController.check_ylesanne(self, c.item)
        return self.render_to_response('ekk/ylesanded/kontroll.mako')

    def _perm_params(self):
        return {'obj':self.c.item}

    def __before__(self):
        """Väärtustame self.c.item ylesandega ning self.c.lang keelega,
        seejuures kontrollime, et self.c.lang oleks selle ülesande tõlkekeel.
        """
        self.c.lang = self.params_lang()
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Ylesanne.get(id)
            if self.c.lang and (self.c.lang == self.c.item.lang or self.c.lang not in self.c.item.keeled):
                self.c.lang = None
        else:
            self.c.lang = None
        super(YlesandedController, self).__before__()
