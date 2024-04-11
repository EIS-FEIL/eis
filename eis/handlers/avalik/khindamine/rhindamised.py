from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class RhindamisedController(BaseResourceController):
    """Hindamine > Minu korraldatud testid (nimekirjade otsing, mida saan hinnata)
    """
    _permission = 'omanimekirjad'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = 'avalik/khindamine/rhindamised.mako'
    _LIST_TEMPLATE = 'avalik/khindamine/rhindamised_list.mako'
    _DEFAULT_SORT = 'hindamiskogum.id'
    _SEARCH_FORM = forms.avalik.hindamine.OtsingForm 
    _actions = 'index,update'
    
    def _query(self):
        # minu korraldatud testimiskorrata testid
        q = (model.SessionR.query(model.Testiruum.id, 
                                 model.Test.id, model.Test.nimi, model.Nimekiri.nimi)
             .join(model.Testiruum.nimekiri)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.testiosa)
             .join(model.Testiosa.test)
             .filter(model.Testikoht.toimumisaeg_id==None)
             .filter(model.Nimekiri.esitaja_kasutaja_id==self.c.user.id)
             .filter(model.Nimekiri.esitaja_koht_id==self.c.user.koht_id)
             .filter(model.Test.opetajale_peidus==False)
             .filter(model.Testiosa.testiylesanded.any(
                 sa.and_(model.Testiylesanne.liik == const.TY_LIIK_Y,
                         model.Testiylesanne.arvutihinnatav==False)))
             .outerjoin(model.Nimekiri.testimiskord)
             .filter(sa.or_(model.Testimiskord.id==None,
                            sa.and_(
                                sa.or_(model.Testimiskord.reg_kool_eis==True,
                                       model.Testimiskord.reg_kool_valitud==True),
                                model.Testimiskord.reg_kool_alates<=date.today(),
                                model.Testimiskord.reg_kool_kuni>=date.today())
                            ))
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        q = q.filter(model.Testiruum.sooritajate_arv > 0)
        if c.test_id:
            q_test = q = q.filter(model.Testiosa.test_id==int(c.test_id))
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)
        if c.t_nimi:
            q = q.filter(model.Test.nimi.ilike('%' + c.t_nimi + '%'))
        if c.n_nimi:
            q = q.filter(model.Nimekiri.nimi.ilike('%' + c.n_nimi + '%'))
        if not c.peidus:
            q = q.filter(model.Nimekiri.staatus == const.B_STAATUS_KEHTIV)

        if c.test_id and q.count() == 0:
            # kui testi ID on antud, aga tulemusi pole, siis selgitatakse,
            # miks see test ei vasta tingimustele
            other_result = q_test.count() > 0
            self._explain_test(other_result, q_test)
            # kuvatakse tulemused ainult testi ID järgi, muid otsingutingimusi arvestamata
            q = q_test            
            
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        return q


    def _explain_test(self, other_result, q_test):
        c = self.c
        errors = []

        def join_ja(li):
            if len(li) > 1:
                return ', '.join(li[:-1]) + _(" ja ") + li[-1]
            elif len(li) == 1:
                return li[-1]
            else:
                return ''

        def check_perm(q, test):
            ferrors = []
                
            if test.opetajale_peidus:
                ferrors.append(_("Test on peidetud."))
            q1 = (q.join(model.Test.nimekirjad)
                 .filter(model.Nimekiri.testimiskord_id==None)
                 .join(model.Nimekiri.testiruumid)
                 )
            # kas on oma korraldatud test või kellegi teise korraldatud
            q, errors2 = self._check_perm_test(q1, test.id)
            if errors2:
                ferrors.extend(errors2)

            if not ferrors:
                # kas on käsitsi hinnata?
                q = (q.join(model.Testiruum.testikoht)
                     .join(model.Testikoht.testiosa)
                     .filter(model.Testiosa.testiylesanded.any(
                         sa.and_(model.Testiylesanne.liik == const.TY_LIIK_Y,
                                 model.Testiylesanne.arvutihinnatav==False)))
                     )
                if q.count() == 0:
                    ferrors.append(_("Testis {id} ei ole käsitsi hinnatavaid ülesandeid.").format(id=test.id))
            
            # kas on testimiskorraga test?
            q1 = (model.SessionR.query(model.Labiviija.id)
                  .filter(model.Labiviija.kasutaja_id==self.c.user.id)
                  .filter(model.Labiviija.staatus!=const.L_STAATUS_KEHTETU)
                  .join(model.Labiviija.toimumisaeg)
                  .join(model.Toimumisaeg.testimiskord)
                  .filter(model.Labiviija.liik<=const.HINDAJA3)
                  .filter(model.Testimiskord.test_id==test.id)
                  )
            if q1.count() > 0:
                url = self.url('khindamised', test_id=test.id)
                ferrors.append(_('Tsentraalselt korraldatud testi hindamine toimub <a href="{url}">tsentraalsete testide</a> menüüs.').format(url=url))

            return ferrors
            
        def check_filter(q, test):
            # otsingutingimuste kontroll
            ferrors = []
            if c.aine:
                if test.aine_kood != c.aine:
                    ferrors.append(_("õppeaine"))
            if c.t_nimi:
                q1 = q.filter(model.Test.nimi.ilike('%' + c.t_nimi + '%'))
                if q1.count() == 0:
                    ferrors.append(_("testi nimetus"))
            if c.n_nimi:
                q1 = q.filter(model.Nimekiri.nimi.like('%' + c.n_nimi + '%'))
                if q1.count() == 0:
                    ferrors.append(_("nimekirja nimetus"))
            li = []
            if ferrors:
                li.append(_("Testil on erinev {omadused}.").format(omadused=join_ja(ferrors)))
            if not c.peidus:
                q1 = q.filter(model.Nimekiri.staatus == const.B_STAATUS_KEHTIV)
                if q1.count() == 0:
                    li.append(_("Nimekiri on peidetud."))
            if li:
                return ' '.join(li)
        
        q = model.SessionR.query(model.Test).filter_by(id=c.test_id)
        test = q.first()
        if test:
            # test on olemas
            if other_result:
                # test on kättesaadav, aga ei vasta otsingutingimustele
                err = check_filter(q_test, test)
                if err:
                    errors.append(err)
            else:
                errors.extend(check_perm(q, test))

            if errors:
                if other_result:
                    err = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test.id)
                else:
                    err = _("Test {id} ei vasta otsingutingimustele.").format(id=test.id)
                msg = err + ' ' + ' '.join(errors)
                self.warning(msg)

    def _check_perm_test(self, q1, test_id):
        """Kontrollitakse, kas on oma korraldatud test või muu hindamine.
        Üle laadida muudhindamised.py failis.
        """
        ferrors = []
        # kas on ise korraldatud test?
        q = q1.filter(model.Nimekiri.esitaja_kasutaja_id==self.c.user.id)
        if q.count() == 0:
            ferrors.append(_("Kasutaja pole seda testi ise korraldanud."))

        # kas on teiste korraldatud test, kuhu mind on hindajaks määratud? 
        q1m = q1.join((model.Labiviija,
                       sa.and_(model.Labiviija.testiruum_id==model.Testiruum.id,
                               model.Labiviija.kasutaja_id==self.c.user.id,
                               model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_K)))
        if q1m.count() > 0:
            url = self.url('muudhindamised', test_id=test_id)
            ferrors.append(_('Teiste läbiviijate poolt korraldatud testi hindamine toimub <a href="{url}">muude testide</a> menüüs.').format(url=url))                
        return q, ferrors
    
    def _prepare_header(self):
        header = [('test.id', _("Testi ID")),
                  ('test.nimi', _("Testi nimetus")),
                  ('nimekiri.nimi', _("Nimekiri")),
                  (None, _("Hindamata tööd"), 'hindamata'),
                  (None, _("Hindamine pooleli"), 'pooleli'),
                  (None, _("Hinnatud tööd"), 'kinnitatud'),
                  ]
        return header

    def _prepare_item(self, rcd, is_html=False):
        testiruum_id, test_id, test_nimi, n_nimi = rcd
        hindamata_arv, pooleli_arv, hinnatud_arv = get_rhindamiste_arvud(testiruum_id, None)
        item = [test_id,
                test_nimi,
                n_nimi,
                hindamata_arv,
                pooleli_arv,
                hinnatud_arv]
        if is_html:
            if hindamata_arv:
                badge = 'danger' # punane
            elif pooleli_arv:
                badge = 'warning' # kollane
            elif hinnatud_arv:
                badge = 'success' # roheline
            else:
                badge = 'secondary' # hall
            return item, testiruum_id, badge
        else:
            return item
    
    def __before__(self):
        pass
    
def get_rhindamiste_arvud(testiruum_id, lv_id):
    if lv_id:
        # hindaja ei hinda kõiki ylesandeid
        q1 = (model.SessionR.query(model.Labiviijaylesanne.testiylesanne_id)
              .filter(model.Labiviijaylesanne.labiviija_id==lv_id))
        tyy_id = [ty_id for ty_id, in q1.all()]
    else:
        tyy_id = []

    # tööde arv
    q2 = (model.SessionR.query(sa.func.count(model.Sooritus.id))
          .filter(model.Sooritus.testiruum_id==testiruum_id)
          .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
          )
    if tyy_id:
        # arvestame ainult neid töid, milles on minu hinnatavaid ylesandeid lahendatud
        q2 = q2.filter(sa.exists().where(
            sa.and_(model.Ylesandevastus.sooritus_id==model.Sooritus.id,
                    model.Ylesandevastus.testiylesanne_id.in_(tyy_id),
                    model.Ylesandevastus.mittekasitsi==False))
                       )
    hinnatud_arv = q2.filter(model.Sooritus.hindamine_staatus==const.H_STAATUS_HINNATUD).scalar()
    pooleli_arv = q2.filter(model.Sooritus.hindamine_staatus==const.H_STAATUS_POOLELI).scalar()
    hindamata_arv = q2.filter(model.Sooritus.hindamine_staatus==const.H_STAATUS_HINDAMATA).scalar()
    return hindamata_arv, pooleli_arv, hinnatud_arv

