# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class YlesandekogudController(BaseResourceController):

    _permission = 'ylesandekogud'

    _MODEL = model.Ylesandekogu
    _INDEX_TEMPLATE = 'ekk/ylesandekogud/otsing.mako'
    _EDIT_TEMPLATE = 'ekk/ylesandekogud/ylesandekogu.mako' 
    _LIST_TEMPLATE = 'ekk/ylesandekogud/otsing_list.mako'
    _SEARCH_FORM = forms.ekk.ylesandekogud.OtsingForm 
    _ITEM_FORM = forms.ekk.ylesandekogud.KoguForm
    _DEFAULT_SORT = 'ylesandekogu.id' # vaikimisi sortimine

    def _query(self):
        Ytbl = (model.SessionR.query(sa.func.coalesce(sa.func.sum(model.Ylesanne.max_pallid), 0).label('pallid'),
                                    sa.func.count(model.Ylesanne.id).label('cnt'))
                .join(model.Ylesanne.koguylesanded)
                .filter(model.Koguylesanne.ylesandekogu_id==model.Ylesandekogu.id)
                .correlate(model.Ylesandekogu)
                .subquery('p1'))
        Ttbl = (model.SessionR.query(sa.func.count(model.Test.id).label('cnt'))
                .join(model.Test.kogutestid)
                .filter(model.Kogutest.ylesandekogu_id==model.Ylesandekogu.id)
                .correlate(model.Ylesandekogu)                
                .subquery('p2'))
        self.Ptbl = (model.SessionR.query(Ytbl.columns.pallid.label('pallid'),
                                         Ytbl.columns.cnt.label('ylesannete_arv'),
                                         Ttbl.columns.cnt.label('testide_arv'))
                     .subquery()
                     .lateral('ptbl'))
        q = (model.SessionR.query(model.Ylesandekogu, self.Ptbl)
             .select_from(model.Ylesandekogu)
             .join((self.Ptbl, sa.sql.expression.literal_column('1')==1))
             )
        # 1=1 seepärast, et joinil peab olema tingimus
        # join on vaja eraldi teha, kuna muidu läheb lateral osa enne ylesandekogu
        # juhul, kui hiljem veel join tehakse (nt klaine.nimi järgi sortimisel)
        return q
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.id:
            q = q.filter(model.Ylesandekogu.id==c.id)
        if c.nimi:
            q = q.filter(model.Ylesandekogu.nimi.ilike('%' + c.nimi + '%'))
        if c.aste:
            aste_bit = c.opt.aste_bit(c.aste) or 0
            q = q.filter(model.Ylesandekogu.aste_mask.op('&')(aste_bit) > 0)
        if c.ainevald:
            q = q.filter(model.Ylesandekogu.ainevald_kood==c.ainevald)
        if c.aine:
            #q = q.filter(model.Ylesandekogu.aine_kood==c.aine)
            q = q.filter(sa.or_(model.Ylesandekogu.aine_kood==c.aine,
                                model.Ylesandekogu.seotud_ained.any(c.aine)))
        if c.valdkond:
            valdkond = model.Klrida.get_by_kood('TEEMA', kood=self.c.valdkond, ylem_kood=self.c.aine)            
            self.c.teema_id = valdkond and valdkond.id            
            if c.teema:
                q = q.filter(model.Ylesandekogu.koguteemad
                             .any(sa.and_(model.Koguteema.teema_kood==c.valdkond,
                                          model.Koguteema.alateema_kood==c.teema)
                                  )
                            )
            else:
                q = q.filter(model.Ylesandekogu.koguteemad
                             .any(model.Koguteema.teema_kood==c.valdkond))
        #c.on_keeletase = c.valdkond == const.AINEVALD_VRK or \
        #                 c.aine in (const.AINE_ET,const.AINE_EE,const.AINE_W)
        c.on_keeletase = c.aine and c.opt.klread_kood('KEELETASE', c.aine) and True or False
        if c.keeletase:
            q = q.filter_by(keeletase_kood=c.keeletase)
        if c.oskus:
            q = q.filter_by(oskus_kood=c.oskus)
        if c.staatus:
            if len(c.staatus) == 1:
                q = q.filter(model.Ylesandekogu.staatus==c.staatus[0])
            else:
                q = q.filter(model.Ylesandekogu.staatus.in_(c.staatus))
        if c.ylesanne_id:
            q = q.filter(model.Ylesandekogu.koguylesanded.any(
                model.Koguylesanne.ylesanne_id==c.ylesanne_id))
        if c.alates:
            q = q.filter(model.Ylesandekogu.created >= c.alates)
        if c.kuni:
            q = q.filter(model.Ylesandekogu.created < c.kuni + timedelta(days=1))
        if c.p_min:
            q = q.filter(self.Ptbl.columns.pallid >= c.p_min)
        if c.p_max:
            q = q.filter(self.Ptbl.columns.pallid <= c.p_max)
        if c.y_alates:
            q = q.filter(self.Ptbl.columns.ylesannete_arv >= c.y_alates)
        if c.y_kuni:
            q = q.filter(self.Ptbl.columns.ylesannete_arv <= c.y_kuni)            
        # if c.y_alates or c.y_kuni:
        #     groups = [r['expr'] for r in q.column_descriptions]
        #     q = (q.outerjoin(model.Ylesandekogu.koguylesanded)
        #          .group_by(*groups))
        #     if c.y_alates:
        #         q = q.having(sa.func.count(model.Koguylesanne.id) >= c.y_alates)
        #     if c.y_kuni:
        #         q = q.having(sa.func.count(model.Koguylesanne.id) <= c.y_kuni)                
        if c.csv:
            return self._index_csv(q)

        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        return q

    def _search_default(self, q):
        return self._search(q)

    def _order_join(self, q, tablename):
        if tablename == 'klaine':
            Klaine = sa.orm.aliased(model.Klrida, name='klaine')
            q = q.outerjoin((Klaine, sa.and_(Klaine.klassifikaator_kood=='AINE',
                                             Klaine.kood==model.Ylesandekogu.aine_kood)))
        return q
            
    def _prepare_header(self):
        header = [('ylesandekogu.id', _("ID")),
                  ('ylesandekogu.nimi', _("Nimetus")),
                  ('ylesandekogu.aste_kood ylesandekogu.aste_mask', _("Kooliaste")),
                  ('klaine.nimi', _("Õppeaine")),
                  (None, _("Teema")),
                  ]
        if self.c.on_keeletase:
            header.append(('ylesandekogu.keeletase_kood', _("Keeleoskuse tase")))
        header.extend([
                  ('ylesandekogu.staatus', _("Olek")),
                  ('ylesandekogu.created', _("Loodud")),
                  (None, _("Ülesannete arv / testide arv")),
                  (None, _("Punktid")),
                  ])
        return header
    
    
    def _prepare_item(self, row, n):
        rcd, max_pallid, ylesannete_arv, testide_arv = row
        li = []
        teemad = []
        for r in rcd.koguteemad:
            if r.teema_kood and r.teema_nimi not in teemad:
                teemad.append(r.teema_nimi)
        s_teema = ', '.join(teemad)
        item = [rcd.id,
                rcd.nimi,
                rcd.aste_nimed,
                rcd.aine_nimi,
                s_teema,
                ]
        if self.c.on_keeletase:
            item.append(rcd.keeletase_nimi)
        item.extend([
                rcd.staatus_nimi,
                self.h.str_from_date(rcd.created),
                '%s/%s' % (ylesannete_arv, testide_arv),
                self.h.fstr(max_pallid),
                ])
        return item

    def _update(self, item):
        # omistame vormilt saadud andmed
        if self.form.data.get('was_efile'):
            if not self.form.data.get('is_efile'):
                # eristuskirja fail kustutati
                kf = item.kogufail
                if kf:
                    kf.filename = None
                    kf.filedata = None
        if self.form.data['f_aine_kood'] != const.AINE_YLD:
            # seotud ained on ainult siis, kui põhiaine on yldõpetus
            self.form.data['f_seotud_ained'] = []
        item.from_form(self.form.data, self._PREFIX)
        if not item.oskus_kood:
            item.oskus_kood = None
        if not item.keeletase_kood:
            item.keeletase_kood = None
        if not item.id:
            item.logging = False
            model.Session.flush()
            item.logging = True
            item.log_insert()

        self._update_koguteemad(item)
        self._update_eristuskiri(item)

    def _update_eristuskiri(self, item):
        ek = item.kogufail
        ek_sisu = self.form.data.get('ek_sisu')
        ek_filedata = self.form.data.get('ek_filedata')
        if ek_filedata == b'' and not ek_sisu:
            if ek:
                ek.delete()
        else:
            if not ek:
                ek = model.Kogufail(ylesandekogu=item)
            ek.from_form(self.form.data, 'ek_')

    def _update_koguteemad(self, item):
        # salvestame kooliastmed, kodeerides need maskiks
        kooliastmed = self.form.data.get('kooliastmed')
        mask = 0
        for kood in kooliastmed or []:
            bit = self.c.opt.aste_bit(kood, item.aine_kood)
            mask += bit or 0            
        if mask != item.aste_mask:
            item.aste_mask = mask

        # salvestame teemad ja valdkonnad
        teemad2 = self.form.data.get('teemad2')
        for r in list(item.koguteemad):
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
            r = model.Koguteema(teema_kood=koodid[0],
                                alateema_kood=len(koodid) > 1 and koodid[1] or None)
            item.koguteemad.append(r)
        #ctrl = BaseGridController(item.koguteemad, model.Koguteema, None, self)        
        #ctrl.save(teemad)

    def _download(self, id, format=None):
        # eristuskirja allalaadimine
        ek = (model.Session.query(model.Kogufail)
              .filter_by(ylesandekogu_id=id)
              .first())
        if not ek or not ek.has_file:
            raise NotFound('Kirjet %s ei leitud' % id)
        return utils.download(ek.filedata, ek.filename, ek.mimetype)

    def _perm_params(self):
        return {'obj':self.c.item}

    def __before__(self):
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Ylesandekogu.get(id)
        super(YlesandekogudController, self).__before__()
