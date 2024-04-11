from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class YlesandeotsingController(BaseResourceController):
    "Ylesandekogude otsing"
    _permission = 'tookogumikud'

    _MODEL = model.Ylesanne
    _INDEX_TEMPLATE = 'avalik/tookogumikud/tookogumik.ylesandeotsing.mako'
    _LIST_TEMPLATE = 'avalik/tookogumikud/tookogumik.ylesandeotsing_list.mako'
    _SEARCH_FORM = forms.avalik.tookogumikud.YlesandeOtsingForm 
    _DEFAULT_SORT = 'ylesanne.nimi' # vaikimisi sortimine
    _upath = '/tookogumik/ylesandeotsing'
    _actions = 'index'
    
    def _query(self):
        q = (self._MODEL.query
             .filter_by(etest=True)
             .filter_by(adaptiivne=False)
             .filter_by(salastatud=0)             
             )
        return q
    
    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        """
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c

        if c.staatus and c.staatus in const.Y_ST_AV:
            # minu koostatud staatuse järgi otsimine
            q = (q.filter(model.Ylesanne.staatus==c.staatus)
                 .filter(model.Ylesanne.ylesandeisikud.any(
                     sa.and_(model.Ylesandeisik.kasutaja_id==c.user.id,
                             model.Ylesandeisik.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA)))
                 )
        elif c.staatus == const.Y_STAATUS_PEDAGOOG and c.user.on_pedagoog or \
             c.staatus == const.Y_STAATUS_AVALIK:
            # avaliku staatuse järgi otsimine
            q = q.filter(model.Ylesanne.staatus==c.staatus)
        else:
            # kõigi lubatud staatuste otsimine
            if c.user.on_pedagoog:
                fst = model.Ylesanne.staatus.in_((const.Y_STAATUS_AVALIK, const.Y_STAATUS_PEDAGOOG))
            else:
                fst = model.Ylesanne.staatus == const.Y_STAATUS_AVALIK
            st_av = (const.Y_STAATUS_AV_KOOSTAMISEL,
                     const.Y_STAATUS_AV_VALMIS)
            q = q.filter(sa.or_(fst,
                            sa.and_(model.Ylesanne.staatus.in_(st_av),
                                    model.Ylesanne.ylesandeisikud.any(
                                        sa.and_(model.Ylesandeisik.kasutaja_id==self.c.user.id,
                                                model.Ylesandeisik.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA))
                                    )
                            ))

        if c.ylesanne_id:
            q = q.filter_by(id=c.ylesanne_id)
            if q.count() == 0:
                item = model.Ylesanne.get(c.ylesanne_id)
                if item and item.staatus in const.Y_ST_AV and \
                         c.user.has_permission('avylesanded', const.BT_UPDATE, obj=item):
                    # avalikus vaates loodud ylesanne,
                    # mis ei tulnud päringus välja, sest pole kasutaja oma,
                    # aga kasutaja on admin või kasutajatugi ja saab seetõttu ligi
                    q = self._query().filter(model.Ylesanne.id==c.ylesanne_id)
                
        if c.aine:
            f_aine = model.Ylesandeaine.aine_kood==c.aine
            if c.teema:
                teema = model.Klrida.get_by_kood('TEEMA', kood=c.teema, ylem_kood=c.aine)            
                c.teema_id = teema and teema.id
                if c.alateema:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(sa.and_(model.Ylesandeteema.teema_kood==c.teema,
                                            model.Ylesandeteema.alateema_kood==c.alateema)
                                    )
                               )
                else:
                    f_teema = (model.Ylesandeaine.ylesandeteemad
                               .any(model.Ylesandeteema.teema_kood==c.teema))
                f_aine = sa.and_(f_aine, f_teema)
            if self.c.opitulemus_id:
                f_aine = sa.and_(f_aine, model.Ylesandeaine.ylopitulemused.any(
                    model.Ylopitulemus.opitulemus_klrida_id==self.c.opitulemus_id))
            q = q.filter(model.Ylesanne.ylesandeained.any(f_aine))
            
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste) or 0
            q = q.filter(model.Ylesanne.aste_mask.op('&')(aste_bit) > 0)
            
        if c.keeletase:
            q = q.filter_by(keeletase_kood=c.keeletase)
        if c.lang:
            q = q.filter(model.Ylesanne.skeeled.like('%' + c.lang + '%'))

        if c.kysimus:
            q = q.filter(model.Ylesanne.sisuplokid\
                             .any(model.Sisuplokk.tyyp==c.kysimus))
        if c.term:
            term = '%' + c.term + '%'
            Aine = sa.orm.aliased(model.Klrida, name='aine')
            Teema = sa.orm.aliased(model.Klrida, name='teema')
            Alateema = sa.orm.aliased(model.Klrida, name='alateema')
            Opitulemus = sa.orm.aliased(model.Klrida, name='opitulemus')
            li = (model.Ylesanne.nimi.ilike(term),
                  model.Ylesanne.markus.ilike(term),
                  model.Ylesanne.marksonad.ilike(term),
                  model.Ylesanne.trans.any(model.T_Ylesanne.marksonad.ilike(term)),
                  model.Ylesanne.ylesandeained.any(
                      sa.or_(model.Ylesandeaine.ylesandeteemad.any(
                          sa.and_(Aine.klassifikaator_kood=='AINE',
                                  Aine.kood==model.Ylesandeaine.aine_kood,
                                  Teema.kood==model.Ylesandeteema.teema_kood,
                                  Teema.klassifikaator_kood=='TEEMA',
                                  Teema.ylem_id==Aine.id,
                                  sa.or_(
                                      Teema.nimi.ilike(term),
                                      sa.exists().where(
                                          sa.and_(Alateema.nimi.ilike(term),
                                                  Alateema.klassifikaator_kood=='ALATEEMA',
                                                  Alateema.ylem_id==Teema.id))
                                      )
                                  )),
                             model.Ylesandeaine.ylopitulemused.any(
                                 sa.and_(
                                     model.Ylopitulemus.opitulemus_klrida_id==Opitulemus.id,
                                     Opitulemus.nimi.ilike(term)
                                 ))
                             )
                      )
                  )
            q = q.filter(sa.or_(*li))

        #model.log_query(q)
        return q

    def _showlist(self):
        template = self._LIST_TEMPLATE
        return self.render_to_response(template)

