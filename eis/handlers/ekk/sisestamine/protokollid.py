# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class ProtokollidController(BaseResourceController):
    """Eksami toimumise protokoll
    """
    _permission = 'sisestamine'
    #_MODEL = model.Toimumisaeg
    _INDEX_TEMPLATE = 'ekk/sisestamine/protokollid.otsing.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/protokollid.otsing_list.mako'
    _DEFAULT_SORT = '-toimumisprotokoll.id' # vaikimisi sortimine

    def _query(self):
        self.c.opt_sessioon = self.c.opt.testsessioon
        q = (model.SessionR.query(model.Toimumisprotokoll,
                                 model.Test.nimi,
                                 model.Koht.nimi,
                                 model.Koht.epost,
                                 model.Testikoht.tahised,
                                 model.Testiruum.tahis,
                                 model.Testiruum.algus,
                                 model.Ruum.tahis)
             .join(model.Toimumisprotokoll.testimiskord)
             .join(model.Testimiskord.test)
             .join(model.Toimumisprotokoll.koht)
             .join(model.Toimumisprotokoll.testikoht)
             .filter(model.Testikoht.staatus==const.B_STAATUS_KEHTIV)
             .outerjoin(model.Toimumisprotokoll.testiruum)
             .filter(sa.or_(model.Testiruum.id==None,
                            model.Testiruum.sooritajate_arv>0))
             .outerjoin(model.Testiruum.ruum)
             )

        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.filter(model.Test.testiliik_kood.in_(liigid))

        return q

    def _order_able(self, q, field):
        """Kontrollitakse, kas antud välja järgi on võimalik sortida
        """
        if field.replace('-','').startswith('sooritus.'):
            return False
        return True
    
    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.kinnitamata:
            q = q.filter(model.Toimumisprotokoll.staatus != const.B_STAATUS_KINNITATUD)
            q = q.filter(model.Toimumisprotokoll.staatus != const.B_STAATUS_EKK_KINNITATUD)
        if c.sisestamata:
            # sisestamata on siis, kui leidub mõni sooritus, mille staatus < katkestatud
            q = q.filter(sa.exists().where(sa.and_(
                model.Sooritus.staatus.in_((const.S_STAATUS_REGATUD,
                                            const.S_STAATUS_ALUSTAMATA,
                                            const.S_STAATUS_POOLELI)),
                model.Sooritus.testikoht_id==model.Toimumisprotokoll.testikoht_id,
                sa.or_(model.Toimumisprotokoll.testiruum_id==None,
                       model.Toimumisprotokoll.testiruum_id==model.Sooritus.testiruum_id),
                sa.or_(model.Toimumisprotokoll.lang==None,
                       model.Sooritus.sooritaja.has(model.Sooritaja.lang==model.Toimumisprotokoll.lang))
                )))

        ta = None
        if c.tahis:
            ta = model.Toimumisaeg.query.filter_by(tahised=c.tahis).first()
            if not ta:
                self.error(_("Sellise tähisega toimumisaega ei leitud"))
            else:
                q = q.filter(model.Testikoht.toimumisaeg_id==ta.id)
            
        elif c.toimumisaeg_id:
            ta = model.Toimumisaeg.get(c.toimumisaeg_id)
            if ta:
                q = q.filter(model.Testikoht.toimumisaeg_id==ta.id)
                if c.tk_tahis:
                    # järgmise soorituskoha tähis on antud eelmise soorituskoha protokolli vormilt
                    q = q.filter(model.Testikoht.tahised==c.tk_tahis)
                    if q.count() == 0:
                        self.error(_("Tähisega {s} soorituskohta ei leitud").format(s=c.tk_tahis))
                    else:
                        r = q.first()
                        mpr = r[0]
                        return HTTPFound(location=self.url('sisestamine_protokoll_osalejad', toimumisprotokoll_id=mpr.id))
        else:
            q = None

        if ta:
            if not c.sessioon_id:
                c.sessioon_id = ta.testimiskord.testsessioon_id
            c.on_ruumiprotokoll = ta.on_ruumiprotokoll
            
        if c.sessioon_id:
            c.opt_toimumisaeg = model.Toimumisaeg.get_opt(c.sessioon_id)

        if q:
            if c.csv:
                return self._index_csv(q)
            c.header = self._prepare_header()
            c.prepare_item = self._prepare_item
        return q

    def _search_default(self, q):

        # vaikimisi on esimene sessioon
        if len(self.c.opt_sessioon):
            self.c.sessioon_id = self.c.opt_sessioon[0][0]
        return self._search(q)

    def _download(self, id, format):
        "Näita faili"
        mprot = model.Toimumisprotokoll.get(id)
        if mprot:
            filedata = mprot.filedata
            if filedata:
                filename = 'protokoll-%s.%s' % (mprot.tahistus, mprot.fileext)
                return utils.download(filedata, filename)
        raise NotFound(_("Õpilasi ei leitud"))

    def _prepare_header(self):
        "Loetelu päis"
        li = [('koht.nimi', _("Testikoht")),
              ('koht.epost', _("E-post")),
              ('test.nimi', _("Testi nimetus")),
              ('testikoht.tahised', _("Tähis")),
              (None, _("Toimumise aeg")),
              self.c.on_ruumiprotokoll and ('ruum.tahis', _("Ruum")),
              self.c.on_ruumiprotokoll and (None, _("Protokollirühmad")),
              (None, _("Testi administraator")),
              ('toimumisprotokoll.lang', _("Keel")),
              ('toimumisprotokoll.staatus', _("Olek")),
              ]
        return [r for r in li if r]
    
    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        rcd, test_nimi, koht_nimi, koht_epost, tk_tahised, tr_tahis, r_algus, r_tahis = rcd
        koht = koht_nimi
        if rcd.testiruum_id:
            millal = self.h.str_from_date(r_algus)
        else:
            millal = rcd.testikoht.millal
        li = [koht_nimi,
              koht_epost,
              test_nimi,
              tk_tahised,
              millal,
              ]
        qa = (model.SessionR.query(model.Kasutaja.nimi)
              .join(model.Kasutaja.labiviijad)
              .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
              .filter(model.Labiviija.testikoht_id==rcd.testikoht_id))
        if self.c.on_ruumiprotokoll:
            li.append(r_tahis)
            testiruum = rcd.testiruum
            li.append(testiruum and ', '.join([prt.tahis for prt in rcd.testiruum.testiprotokollid]) or '')
            qa = qa.filter(model.Labiviija.testiruum_id==rcd.testiruum_id)
        t_adminid = ', '.join([r for r, in qa.order_by(model.Kasutaja.nimi).all()])
        li.append(t_adminid)
        li.append(rcd.lang_nimi)
        li.append(rcd.staatus_nimi)

        return li
