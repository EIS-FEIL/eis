from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)

class EhisopetajadController(BaseResourceController):
    _permission = 'kasutajad'
    _ITEM_FORM = forms.admin.EhisopetajadForm
    _INDEX_TEMPLATE = 'admin/ehisopetajad.mako'
    _LIST_TEMPLATE = 'admin/ehisopetajad_list.mako'    
    _actions = 'index,create'
    _get_is_readonly = False
    _DEFAULT_SORT = 'pedagoog.eesnimi,pedagoog.perenimi,aine.nimi,aste.nimi'
    
    def _query(self):
        c = self.c
        
        reg = ehis.Ehis(handler=self)
        reg.upd_klassifikaator('EHIS_AINE')
        reg.upd_klassifikaator('EHIS_ASTE')
        model.Session.commit()

        self._get_protsessid()

        c.prepare_item = self._prepare_item
        c.prepare_header = self._prepare_header

        c.opt_kool = self._get_opt_kool()
        c.opt_aste = [('', _("Kõik kooliastmed"))] + [(r[0], r[1]) for r in c.opt.EHIS_ASTE]
        c.opt_aine = [('', _("Kõik õppeained"))] + [(r[0], r[1]) for r in c.opt.EHIS_AINE]
        
        q = (model.Session.query(model.Pedagoog.isikukood,
                                 model.Pedagoog.eesnimi,
                                 model.Pedagoog.perenimi,
                                 model.Koht.nimi,
                                 model.Pedagoog.kool_id)
             .join(model.Pedagoog.koht)
             .join(model.Pedagoog.ainepedagoogid)
             )
        return q

    def _get_opt_kool(self):
        oppetasemed = (const.E_OPPETASE_ALUS,
                       const.E_OPPETASE_YLD,
                       const.E_OPPETASE_GYMN)
        q = (model.SessionR.query(model.Koht.kool_id, model.Koht.nimi)
             .filter(model.Koht.koolioppekavad.any(
                 model.Koolioppekava.kavatase_kood.in_(oppetasemed)
                 ))
             .filter(model.Koht.kool_id>0)
             .filter(model.Koht.staatus==const.B_STAATUS_KEHTIV)
             .order_by(model.Koht.nimi)
             )
        return [('', _("Kõik koolid"))] + [(k_id, k_nimi) for (k_id, k_nimi) in q.all()]
        
    
    def _search_default(self, q):
        return

    def _search(self, q):
        c = self.c
        if c.kool_id:
            q = q.filter(model.Koht.kool_id==c.kool_id)
        if c.aine:
            q = q.filter(model.Ainepedagoog.ehis_aine_kood==c.aine)
        if c.aste:
            q = q.filter(model.Ainepedagoog.ehis_aste_kood==c.aste)
        if c.kool_id or c.aine or c.aste:
            if c.csv:
                return self._index_csv(q)
            return q

    def _prepare_header(self):
        header = [('pedagoog.isikukood', _("Isikukood")),
                  ('pedagoog.eesnimi', _("Eesnimi")),
                  ('pedagoog.perenimi', _("Perekonnanimi")),
                  ('koht.nimi', _("Kool")),
                  ('pedagoog.kool_id', _("Kooli ID (EHIS)")),
                  ]
        return header

    def _prepare_item(self, rcd, n):
        "Loetelu kirje vormistamine CSV ja PDF jaoks"
        return rcd
        
    def _search_protsessid(self, q):
        q = q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_OPETAJAD)
        return q

    def _error_create(self):
        extra_info = self._index_d()
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=extra_info)
        return Response(html)

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
        return self._redirect('index')

    def _create(self):
        """Andmete uuendamine
        """
        kool_id = self.form.data['kool_id']
        aine = self.form.data['aine']
        aste = self.form.data['aste']

        buf = _('Õpetajate laadimine EHISest:') + ' %s, %s' % \
              (aine and model.Klrida.get_str('EHIS_AINE', aine) or _("kõik ained"),
               aste and model.Klrida.get_str('EHIS_ASTE', aste) or _("kõik kooliastmed"))
        if kool_id:
            q = (model.SessionR.query(model.Koht.nimi)
                 .filter(model.Koht.kool_id==kool_id))
            for k_nimi, in q.all():
                buf += ', ' + k_nimi

        params = {'liik': model.Arvutusprotsess.LIIK_OPETAJAD,
                  'kirjeldus': buf,
                  }
        childfunc = lambda rcd: _upd_ametikohad(self, rcd, kool_id, aste, aine)
        model.Arvutusprotsess.start(self, params, childfunc)
        self.success(_('Protsess on käivitatud'))
        return self._redirect('index', kool_id=kool_id, aine=aine, aste=aste)

def _upd_ametikohad(handler, protsess, kool_id, aste, aine):
    "Andmete uuendamise läbiviimine"
    
    def request_data(kool_id, aste, aine):
        # EHISe päring
        message, ametikohad = reg.pedagoogAmetikoht(None, kool_id, aste, aine)
        if message:
            if message.startswith('Classification with such code does not exist!'):            
                return []
            raise Exception(message)
        else:
            return ametikohad

    def save_data(ametikohad):
        uuendatud = []
        for rcd in ametikohad:
            isikukood = rcd.isikukood
            r_kool_id = int(rcd.koolId)
            q = (model.Session.query(model.Pedagoog)
                 .filter(model.Pedagoog.isikukood==isikukood)
                 .filter(model.Pedagoog.kool_id==r_kool_id))
            pedagoog = q.first()
            if not pedagoog:
                pedagoog = model.Pedagoog(isikukood=isikukood,
                                          kool_id=r_kool_id)
            pedagoog.update_from_ehis(rcd, False)
            kasutaja = model.Kasutaja.get_by_ik(isikukood)
            if kasutaja and pedagoog.kasutaja_id != kasutaja.id:
                pedagoog.kasutaja_id = kasutaja.id
            if kasutaja:
                xtee.vrd_rr_nimi(handler, kasutaja, pedagoog.eesnimi, pedagoog.perenimi)
            model.Session.flush()
            uuendatud.append(pedagoog.id)
        return uuendatud

    def remove_old(now, uuendatud, kool_id, aste, aine): 
        cnt1 = 0
        # eemaldame vanad
        if kool_id and not aine and not aste:
            q = (model.Session.query(model.Pedagoog)
                 .filter_by(kool_id=kool_id)
                 .filter_by(on_ehisest=True))
            # kui päriti kooli kõiki õpetajaid, siis kustutame kooli õpetajad, keda ei uuendatud
            if uuendatud:
                q = q.filter(~ model.Pedagoog.id.in_(uuendatud))
            cnt1 = q.count()
            log.debug('Kustutan %d pedagoogi...' % cnt1)
            for pedagoog in q.all():
                for ap in list(pedagoog.ainepedagoogid):
                    ap.delete()
                pedagoog.delete()
        elif aine or aste:
            q = (model.Session.query(model.Ainepedagoog)
                 .filter(model.Ainepedagoog.seisuga < now))
            if aine:
                q = q.filter_by(ehis_aine_kood=aine)
            if aste:
                q = q.filter_by(ehis_aste_kood=aste)
            if kool_id:
                q = q.filter(model.Ainepedagoog.pedagoog.has(
                    model.Pedagoog.kool_id==kool_id))
            cnt1 = q.count()
            log.debug('Kustutan %d ametikohta...' % cnt1)
            for ap in q.all():
                ap.delete()
        return cnt1
    
    # luuakse x-tee klient
    reg = ehis.Ehis(handler=handler)
    buf = _('ametikohtade päring') + ' aine=%s, aste=%s, kool_id=%s' % (aine, aste, kool_id)
    if protsess:
        model.Arvutusprotsess.trace(buf)
    else:
        log.debug(buf)

    # EHISe päringul peab olema vähemalt 1 parameeter
    # aga et ei saaks timeouti, siis paneme alati nii astme kui ka aine (kui kooli pole)
    astmed = (kool_id or aste) and [aste] or [r[0] for r in handler.c.opt.EHIS_ASTE]
    ained = (kool_id or aine) and [aine] or [r[0] for r in handler.c.opt.EHIS_AINE]
    # mitu päringut vaja teha
    total_req = len(astmed) * len(ained)
    step = 99. / total_req
    n = total = total_d = 0
    for aste in astmed:
        for aine in ained:
            now = datetime.now()
            # pärime EHISest andmed
            buf = _("Ametikohtade päring") + f" {kool_id}, {aste}, {aine}..."
            model.Arvutusprotsess.trace(buf)
            
            ametikohad = request_data(kool_id, aste, aine)
            cnt = len(ametikohad)
            buf = _('Leitud {n} ametikohta').format(n=cnt)
            model.Arvutusprotsess.trace(buf)
            total += cnt
            if protsess:
                protsess.edenemisprotsent = (n + .5) * step
                model.Session.commit()

            # salvestame saadud andmed
            uuendatud = save_data(ametikohad)

            # kustutame need, keda enam pole
            total_d += remove_old(now, uuendatud, kool_id, aste, aine)
            uu = model.Pedagoogiuuendus.give(kool_id, aine, aste)
            uu.seisuga = now

            msg = 'Salvestatud {n} ametikohta'.format(n=total)
            if total_d:
                msg += ', kustutatud {n} ametikohta.'.format(n=total_d)
            if protsess:
                protsess.edenemisprotsent = (n + 1) * step
                protsess.set_viga(msg)
            model.Session.commit()
            n += 1

def uuenda_pedagoogid(handler, koht, force=False):
    if handler.c.user.on_kohteelvaade:
        # soorituskoha eelvaates on readonly andmebaasiühendus
        return
    kool_id = koht.kool_id
    if kool_id:
        aine = aste = None
        if not force:
            settings = handler.request.registry.settings
            cache_hours = float(settings.get('ehis.cache.ametikoht',24))
            if cache_hours > -1:
                uu = model.Pedagoogiuuendus.get_by(kool_id, aine, aste)
                if not uu or not uu.seisuga or \
                   uu.seisuga < datetime.now() - timedelta(hours=cache_hours):
                   # vaja on uuendada
                    force = True
        if force:
            try:
                _upd_ametikohad(handler, None, kool_id, aste, aine)
            except Exception as ex:
                log.error(ex)

def opt_koolipedagoogid(handler, koht_id):
    "Kooli õpetajate valik"
    if not koht_id:
        return []
    koht = model.Koht.get(koht_id)
    uuenda_pedagoogid(handler, koht)
    
    q = (model.Session.query(model.Pedagoog.id,
                             model.Pedagoog.eesnimi,
                             model.Pedagoog.perenimi,
                             model.Kasutaja.nimi)
         .filter(model.Pedagoog.koht_id==koht_id)
         .outerjoin(model.Pedagoog.kasutaja)
         .order_by(sa.func.coalesce(model.Kasutaja.nimi, model.Pedagoog.eesnimi),
                   model.Pedagoog.perenimi)
         )
    return [(r[0], r[3] or '%s %s' % (r[1], r[2])) for r in q.all()]
