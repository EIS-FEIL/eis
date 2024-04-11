from eis.lib.baseresource import *
_ = i18n._
from eis.lib.feedbackreport import FeedbackReport
from eis.handlers.avalik.regamine.avaldus.testid import save_vvkohad

log = logging.getLogger(__name__)

class TulemusedController(BaseResourceController):

    _permission = 'sooritamine,testpw'
    _MODEL = model.Sooritaja
    _INDEX_TEMPLATE = 'avalik/tulemused/otsing.mako'
    _LIST_TEMPLATE = 'avalik/tulemused/otsing_list.mako'
    _EDIT_TEMPLATE = 'avalik/tulemused/tulemus.mako'
    _DEFAULT_SORT = '-sooritaja.id'
    _actions = 'index,download,show,edit,update'
    
    def _query(self):
        return (model.Sooritaja.queryR
                .filter(model.Sooritaja.staatus>=const.S_STAATUS_TEHTUD)
                .join(model.Sooritaja.test)
                .filter(sa.or_(model.Test.testiliik_kood==None,
                               model.Test.testiliik_kood!=const.TESTILIIK_KOOLIPSYH))
                .outerjoin(model.Sooritaja.testimiskord)
                .filter(sa.or_(
                    sa.and_(model.Testimiskord.id==None,
                            model.Test.osalemise_peitmine==False),
                    model.Testimiskord.osalemise_naitamine==True))
                .filter(model.Sooritaja.regviis_kood!=const.REGVIIS_EELVAADE)
                )

    def _search(self, q):
        c = self.c
        if c.nimi:
            q = q.filter(model.Test.nimi.ilike(c.nimi))
        if c.testiliik:
            q = q.filter(model.Test.testiliik_kood==c.testiliik)

        c.kasutaja = c.user.get_kasutaja()
        if not c.kasutaja_id or not c.user.get_kasutaja().on_volitatud(c.kasutaja_id):
            c.kasutaja_id = c.user.id

        q = q.filter(model.Sooritaja.kasutaja_id==c.kasutaja_id)
        return q

    def _search_default(self, q):
        return self._search(q)

    def _order_field(self, q, is_desc, field):
        if field == 'sooritaja.algus':
            field = 'coalesce(sooritaja.algus,sooritaja.reg_aeg)'
            if is_desc:
                # DESC sort
                q = q.order_by(sa.desc(sa.text(field)))
            else:
                # ASC sort
                q = q.order_by(sa.text(field))
        else:
            q = BaseResourceController._order_field(self, q, is_desc, field)
        return q
        
    def _show(self, item):
        c = self.c
        id = self.request.matchdict.get('id')
        tk = item.testimiskord

        if tk:
            dt = date.today()
            c.saab_vaidlustada = not c.user.testpw_id and \
              (not tk.vaide_algus or tk.vaide_algus <= dt) and \
              tk.vaide_tahtaeg and tk.vaide_tahtaeg >= dt and \
              tk.on_avalik_vaie and \
              tk.tulemus_kinnitatud and \
              item.kasutaja_id == c.user.id and \
              (item.hindamine_staatus == const.H_STAATUS_HINNATUD and item.pallid != None or \
               item.staatus == const.S_STAATUS_EEMALDATUD)
            c.saab_tutvuda = not c.user.testpw_id and \
              (tk.tutv_taotlus_alates and tk.tutv_taotlus_alates <= dt) and \
              (tk.tutv_taotlus_kuni is None or tk.tutv_taotlus_kuni >= dt)

        c.test = test = item.test
        if item.staatus == const.S_STAATUS_TEHTUD and \
               item.hindamine_staatus == const.H_STAATUS_HINNATUD and \
               test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:
            roll = const.ISIK_SOORITAJA
            visibility = item.tulemus_nahtav(None, False, roll, test, tk)
            if visibility.is_ts:
                fr = FeedbackReport.init_opilane(self, test, item.lang, item.kursus_kood)
                if fr:
                    err, c.tagasiside_html = fr.generate(item)
        
    def _download(self, id, format=None):
        """Näita faili"""
        try:
            id = int(id)
        except ValueError:
            raise NotFound('Vigane URL')
        item = model.Sooritaja.getR(id)
        tk = item.testimiskord
        test = item.test
        if item.staatus == const.S_STAATUS_TEHTUD and \
               item.hindamine_staatus == const.H_STAATUS_HINNATUD and \
               test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:               
            roll = const.ISIK_SOORITAJA
            visibility = item.tulemus_nahtav(None, False, roll, test, tk)
            if visibility.is_ts:
                fr = FeedbackReport.init_opilane(self, test, item.lang, item.kursus_kood)
                if fr:
                    filedata = fr.generate_pdf(item)                
                    filename = 'tagasiside.pdf'
                    if filedata:
                        return utils.download(filedata, filename, const.CONTENT_TYPE_PDF)
        raise NotFound('Faili ei leitud')

    def _update(self):
        "Ainult kandideerimiskoolide salvestamise jaoks"
        sub = self._get_sub()
        if sub == 'vvk':
            id = self.request.matchdict.get('id')
            return eval('self._update_%s' % sub)(id)
        # viga
        return self._redirect('index')
    
    def _edit_vvk(self, sooritaja_id):
        "Kandideerimiskohtade valik"
        self.c.sooritaja = model.Sooritaja.get(sooritaja_id)
        assert self.c.sooritaja.kasutaja_id == self.c.user.id, 'vale kasutaja'
        return self.render_to_response('avalik/tulemused/tulemus.vvkohad.mako')

    def _update_vvk(self, sooritaja_id):
        "Kandideerimiskohtade salvestamine"
        # salvestame koolid, kes võivad tulemusi vaadata
        sooritaja = model.Sooritaja.get(sooritaja_id)
        assert sooritaja.kasutaja_id == self.c.user.id, 'vale kasutaja'
        vvkohad_id = self.request.params.getall('vvk')
        vvk_oma = self.request.params.get('vvk_oma')
        opilane = sooritaja.kasutaja.opilane
        save_vvkohad(sooritaja, vvkohad_id, vvk_oma, opilane)
        model.Session.commit()
        return self._redirect('show')
    
    def _perm_params(self):
        c = self.c
        sooritaja_id = self.request.matchdict.get('id')
        if sooritaja_id:
            try:
                sooritaja_id = int(sooritaja_id)
            except ValueError:
                raise NotFound('Vigane URL')
            item = model.Sooritaja.getR(sooritaja_id)
            if not item or not self.c.user.get_kasutaja().on_volitatud(item.kasutaja_id):
                return False
        if c.user.testpw_id and (not sooritaja_id or c.user.testpw_id != item.id):
            return False
