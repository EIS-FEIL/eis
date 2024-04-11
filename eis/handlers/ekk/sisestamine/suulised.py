from eis.lib.baseresource import *
from eis.handlers.ekk.sisestamine.vastused import sisestaja_soorituskoht
_ = i18n._

log = logging.getLogger(__name__)

class SuulisedController(BaseResourceController):
    """Suuliste testide hindamisprotokollide otsimine
    """
    _permission = 'sisestamine'
    _MODEL = model.Hindamisprotokoll
    _INDEX_TEMPLATE = 'ekk/sisestamine/suulised.otsing.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/suulised.otsing_list.mako'

    _DEFAULT_SORT = 'hindamisprotokoll.liik,testiprotokoll.tahised,sisestuskogum.tahis' # vaikimisi sortimine

    _vastvorm_kood = const.VASTVORM_SP

    def _query(self):
        self._set_opt_liik()
        self.c.opt_sessioon = self.c.opt.testsessioon
        q = model.SessionR.query(model.Hindamisprotokoll,
                                model.Testiprotokoll.tahised,
                                model.Testikoht.tahised,
                                model.Sisestuskogum.tahis,
                                model.Sisestuskogum.nimi,
                                model.Koht.nimi,
                                model.Ruum.tahis)
        q = q.join(model.Hindamisprotokoll.testiprotokoll).\
            join(model.Testiprotokoll.testiruum).\
            join(model.Testiruum.testikoht).\
            join(model.Hindamisprotokoll.sisestuskogum).\
            filter(model.Testiprotokoll.tehtud_toodearv>0).\
            filter(model.Hindamisprotokoll.tehtud_toodearv>0).\
            join(model.Testikoht.koht).\
            outerjoin(model.Testiruum.ruum)
        return q
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """

        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.join(model.Sisestuskogum.testiosa).\
                join(model.Testiosa.test).\
                filter(model.Test.testiliik_kood.in_(liigid))
            
        if self.c.liik:
            # on antud hindamise liik
            q = q.filter(model.Hindamisprotokoll.liik==self.c.liik)

        tpr_tahised = None
        sk_tahis = None
        ta = None
        li_ta = []
        
        if self.c.ta_tahised and (self.c.otsi or self.c.sisesta or not self.c.toimumisaeg_id):
            # on antud toimumisaja tähis ja vajutati nupule Otsi või Sisesta
            # või sisestusvormil Järgmine
            # (mitte ei valitud loetelust toimumisaega)
            self.c.ta_tahised = self.c.ta_tahised.strip().replace('+','-').upper()
            li_ta = self.c.ta_tahised.split('-')
            if len(li_ta) != 3:
                self.error(_('Sisesta toimumisaja tähis 3-osalisena'))
            else:
                ta = model.Toimumisaeg.query.filter_by(tahised=self.c.ta_tahised).first()
                if not ta:
                    self.error(_('Sellise tähisega toimumisaega ei leitud'))
                else:
                    self.c.toimumisaeg_id = ta.id
                    q = q.filter(model.Testikoht.toimumisaeg_id==ta.id)

        elif self.c.toimumisaeg_id:
            q = q.filter(model.Testikoht.toimumisaeg_id==int(self.c.toimumisaeg_id))
            ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
            if ta:
                self.c.ta_tahised = ta.tahised
                li_ta = self.c.ta_tahised.split('-')

        if self.c.tahis:
            # on antud hindamisprotokolli tähis (ilma toimumisaja tähiseta selle sees)
            li_t = self.c.tahis.split('-')
            if not self.c.ta_tahised:
                self.error(_('Sisesta toimumisaja tähis ka'))
            elif len(li_t) != 3:
                self.error(_('Sisesta hindamisprotokolli tähis 3-osalisena'))
            elif len(li_ta) == 3:
                # liidame toimumisaja tähise ja hindamisprotokolli tähise
                li = li_ta + li_t
                # testiprotokolli tähis on hpr tähis ilma sisestuskogumi tähiseta
                tpr_tahised = '-'.join(li[:5])
                sk_tahis = li[5]
                q = q.filter(model.Testiprotokoll.tahised==tpr_tahised).\
                    filter(model.Sisestuskogum.tahis==sk_tahis)

        if self.c.sisesta and self.request.params.get('sisestus') == 'p':
            # kasutaja vajutas parandamise vormil nupule "Järgmine"
            if not self.c.ta_tahised:
                self.error(_('Palun sisesta toimumisaja tähis'))
            else:
                rcd = q.filter(model.Hindamisprotokoll.staatus==const.H_STAATUS_POOLELI).\
                      filter(model.Hindamisprotokoll.staatus1==const.H_STAATUS_HINNATUD).\
                      filter(model.Hindamisprotokoll.staatus2==const.H_STAATUS_HINNATUD).\
                      order_by(model.Hindamisprotokoll.liik,
                               model.Testiprotokoll.tahised,
                               model.Sisestuskogum.tahis).\
                      first()
                hpr = rcd and rcd[0] or None
                if not hpr:
                    self.error(_('Ei ole sisestuserinevustega hindamisprotokolle, mille mõlemad sisestused on kinnitatud'))
                else:
                    return self._url_sisestama(hpr, 'p')

        elif self.c.sisesta:
            # kasutaja vajutas nupule "Sisesta" või sisestamise vormil "Järgmine" ja soovib kohe sisestama asuda
            if not self.c.ta_tahised:
                self.error(_('Palun sisesta toimumisaja tähis'))
            elif not self.c.tahis:
                self.error(_('Palun sisesta hindamisprotokolli tähis'))
            elif not self.c.liik:
                self.error(_('Palun vali hindamise liik'))
            elif tpr_tahised and sk_tahis:
                hpr = (model.SessionR.query(model.Hindamisprotokoll)
                       .filter(model.Hindamisprotokoll.liik==self.c.liik)
                       .join(model.Hindamisprotokoll.testiprotokoll)
                       .filter(model.Testiprotokoll.tahised==tpr_tahised)
                       .join(model.Hindamisprotokoll.sisestuskogum)
                       .filter(model.Sisestuskogum.tahis==sk_tahis)
                       .first()
                       )
                if not hpr:
                    self.error(_('Antud tähise ja liigiga hindamisprotokolli ei leitud'))
                else:
                    sisestus = self._get_sisestus(hpr)
                    if sisestus:
                        if self._sisestaja_soorituskoht(hpr):
                            self.error(_("Ümbriku kontroll. Palun edasta ümbrik korraldusspetsialistile."))                            
                        else:
                            # saab sisestada
                            return self._url_sisestama(hpr, sisestus)
        if self.c.sessioon_id:
            self.c.opt_toimumisaeg = model.Toimumisaeg.get_opt(self.c.sessioon_id, 
                                                               vastvorm_kood=self._vastvorm_kood)
        if ta:
            self.c.toimumisaeg = ta
            if ta.testimiskord.sisestus_isikukoodiga:
                if self.c.testikoht_id:
                    q = q.filter(model.Testikoht.id==self.c.testikoht_id)
                self.c.opt_testikoht = [(r.id, r.koht.nimi) for r in ta.testikohad if r.staatus]
            return q

    def _url_sisestama(self, hpr, sisestus):
        return HTTPFound(location=self.h.url('sisestamine_suulised_hindamised',
                                             hindamisprotokoll_id=hpr.id, 
                                             sisestus=sisestus))

    def _get_sisestus(self, hpr):
        """Leitakse sisestus
        """
        if self.c.sisestus == 'p' and self.c.user.has_permission('parandamine', const.BT_UPDATE):
            return 'p'

        ## esimest sisestust saan teha siis, kui olen ise I sisestaja 
        ## või seda veel pole ja ma pole II sisestaja
        if hpr.can_sis1(self.c.user.id):
            return 1

        ## teist sisestust saan teha siis, kui olen ise II sisestaja 
        ## või seda veel pole ja ma pole I sisestaja
        if hpr.can_sis2(self.c.user.id):
            return 2

        if self.c.user.has_permission('parandamine', const.BT_UPDATE):
            # olen parandaja
            return 'p'

        self.error(_('Mõlema sisestusega on juba alustatud'))

    def _search_default(self, q):

        # vaikimisi on esimene sessioon
        if len(self.c.opt_sessioon):
            self.c.sessioon_id = self.c.opt_sessioon[0][0]
        return self._search(q)

    def _set_opt_liik(self):
        self.c.opt_liik = [(const.HINDAJA1, 'I hindamine'),
                           (const.HINDAJA2, 'II hindamine'),
                           (const.HINDAJA3, 'III hindamine'),
                           ]

    def _sisestaja_soorituskoht(self, hpr):
        "Kontrollitakse, kas sisestaja tohib antud hindamisprotokolli sisestada"
        q = (model.SessionR.query(model.Testipakett.testikoht_id)
             .join(model.Testipakett.testiprotokollid)
             .join(model.Testiprotokoll.hindamisprotokollid)
             .filter(model.Hindamisprotokoll.id==hpr.id)
             )
        testikoht_id, = q.first()
        return sisestaja_soorituskoht(self.c.user.id, testikoht_id)
    
                    
