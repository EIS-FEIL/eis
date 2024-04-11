from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AnalyyskvstatistikadController(BaseResourceController):
    "Kysimuste vastuste statistika kuvamine"
    _permission = 'vastusteanalyys'

    _MODEL = model.Kvstatistika
    _INDEX_TEMPLATE = 'sisuplokk/analysis.kvstatistikad_list.mako'
    _LIST_TEMPLATE = 'sisuplokk/analysis.kvstatistikad_list.mako'
    _EDIT_TEMPLATE = 'sisuplokk/analysis.kvstatistika.sooritused.mako'
    _default_items_per_page = 50

    @property
    def _DEFAULT_SORT(self):
        order = request.params.get('kvst_order')
        return self.c.sort
   
    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q1):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        c.is_edit = True        
        c.kysimus = model.Kysimus.get(c.kst.kysimus_id)
        tulemus = c.kysimus.tulemus 
        c.sp_tyyp = c.kysimus.sisuplokk.tyyp
        c.basetype = tulemus and tulemus.baastyyp or None
        c.kvstatistikad_list_url = self.url_current('index', kst_id=c.kst.id, kvst_order=c.kvst_order)
        c.can_edit_hm = self._can_edit_hm(c.user, c.test, c.kysimus)
        q = (model.Session.query(model.Kvstatistika)
             .filter_by(kysimusestatistika_id=c.kst.id)
             )

        return q
    
    def _order(self, q, sort=None):
        if self.c.kvst_order == 'oige':
            q = q.order_by(sa.desc(model.Kvstatistika.oige),
                           sa.desc(model.Kvstatistika.vastuste_arv),
                           model.Kvstatistika.kood1,
                           model.Kvstatistika.kood2,
                           model.Kvstatistika.sisu)
        elif self.c.kvst_order == 'sisu':
            q = q.order_by(model.Kvstatistika.kood1,
                           model.Kvstatistika.kood2,
                           model.Kvstatistika.sisu,
                           sa.desc(model.Kvstatistika.oige),
                           sa.desc(model.Kvstatistika.vastuste_arv))
        else:
            q = q.order_by(sa.desc(model.Kvstatistika.vastuste_arv),
                           model.Kvstatistika.kood1,
                           model.Kvstatistika.kood2,
                           model.Kvstatistika.sisu)
        return q

    def _paginate(self, q):
        items = BaseResourceController._paginate(self, q)
        self.c.kvstatistikad = items
        return items

    def get_items(self):
        q = self._order(self._search(self._query()))
        return self._paginate(q)                

    def _perm_params(self):
        return {'obj': self.c.test}

    def _show(self, item):
        "Leitakse sooritused, kus antud vastus anti"
        c = self.c
        q = (model.Session.query(model.Sooritus.id,
                                 model.Sooritus.testiosa_id,
                                 model.Toimumisaeg.tahised,
                                 model.Sooritus.tahised,
                                 model.Kasutaja.isikukood)
             .distinct()
             .join((model.Ylesandevastus,
                    model.Ylesandevastus.sooritus_id==model.Sooritus.id))
             .join(model.Ylesandevastus.kysimusevastused)
             .join(model.Kysimusevastus.kvsisud)
             .filter(model.Kysimusevastus.kysimus_id==c.kst.kysimus_id)
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.kasutaja)
             )
        q = self._show_filter(q)
        if item.sisu:
            kysimus = model.Kysimus.get(c.kst.kysimus_id)
            tulemus = kysimus.tulemus
            if kysimus.rtf and tulemus and not tulemus.tyhikud:
                q = q.filter(sa.func.html_resp(model.Kvsisu.sisu)==item.sisu)
            else:
                q = q.filter(model.Kvsisu.sisu==item.sisu)
        elif item.kood1:
            q = q.filter(model.Kvsisu.kood1==item.kood1)
            if item.kood2:
                q = q.filter(model.Kvsisu.kood2==item.kood2)
        else:
            # tyhi vastus
            q = (q.filter(model.Kvsisu.sisu==item.sisu)
                 .filter(model.Kvsisu.kood1==item.kood1))
            
        q = q.filter(model.Kvsisu.oige==item.oige)
        q = q.order_by(model.Toimumisaeg.tahised, model.Sooritus.tahised, model.Sooritus.id)
        c.items = q.limit(50).all()

    def _show_filter(self, q):
        c = self.c
        if not c.toimumisaeg:
            q = (q.outerjoin(model.Sooritus.toimumisaeg)
                 .filter(model.Sooritaja.test_id==c.test.id)
                 .filter(model.Sooritaja.testimiskord_id==None))
        else:
            q = q.join(model.Sooritus.toimumisaeg)
            tkord = c.toimumisaeg.testimiskord
            if tkord.analyys_eraldi:
                q = q.filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
            else:
                q = (q.join(model.Sooritaja.testimiskord)
                    .filter(model.Sooritaja.test_id==c.test.id)
                    .filter(model.Testimiskord.analyys_eraldi==False))
        return q
    
    def __before__(self):
        c = self.c
        c.toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(c.toimumisaeg_id)
        c.test = c.toimumisaeg.testiosa.test
        kst_id = self.request.matchdict.get('kst_id')
        c.kst = model.Kysimusestatistika.get(kst_id)
        c.kvst_order = self.request.params.get('kvst_order')

    def _can_edit_hm(self, user, test, kysimus):
        perm = 'vastusteanalyys'
        can_show = user.has_permission(perm, const.BT_SHOW, obj=test)
        can_edit_hm = False
        if user.has_permission(perm, const.BT_UPDATE, obj=test):
            # kasutajal on rolli kaudu yldine muutmise õigus
            can_edit_hm = True
        elif can_show:
            # kui kasutajal on testi koostaja grupp
            # ja samal ajal ylesande koostaja grupp,
            # siis ta võib maatriksit muuta
            if user.has_group(const.GRUPP_T_KOOSTAJA, test) or \
              user.has_group(const.GRUPP_T_OMANIK, test):
                ylesanne = kysimus.sisuplokk.ylesanne
                if user.has_group(const.GRUPP_Y_KOOSTAJA, ylesanne):
                    can_edit_hm = True
        return can_edit_hm
