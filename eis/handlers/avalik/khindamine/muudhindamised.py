from eis.lib.baseresource import *
from .rhindamised import RhindamisedController, get_rhindamiste_arvud
_ = i18n._

log = logging.getLogger(__name__)

class MuudhindamisedController(RhindamisedController):
    """Õpetaja testide hindamine - otsinguvorm
    """
    _INDEX_TEMPLATE = 'avalik/khindamine/muudhindamised.mako'
    
    def _query(self):
        # testimiskorrata hindamised, kuhu mind on määratud hindajaks
        q = (model.SessionR.query(model.Testiruum.id, model.Labiviija.id,
                                 model.Test.id, model.Test.nimi, model.Nimekiri.nimi, model.Kasutaja.nimi)
             .join(model.Testiruum.nimekiri)
             .filter(model.Nimekiri.esitaja_kasutaja_id!=self.c.user.id)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.testiosa)
             .join(model.Testiosa.test)
             .filter(model.Testikoht.toimumisaeg_id==None)
             .join(model.Nimekiri.esitaja_kasutaja)
             .join((model.Labiviija,
                    sa.and_(model.Labiviija.testiruum_id==model.Testiruum.id,
                            model.Labiviija.kasutaja_id==self.c.user.id,
                            model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_K)))
             )
        self.c.opt_esitaja = self._get_opt_esitaja()
        return q
    
    def _get_opt_esitaja(self):
        q = (model.SessionR.query(model.Kasutaja.id, model.Kasutaja.nimi).distinct()
             .join(model.Nimekiri.esitaja_kasutaja)
             .join(model.Nimekiri.testiruumid)
             .join(model.Testiruum.labiviijad)
             .filter(model.Labiviija.kasutaja_id==self.c.user.id)
             .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_K)
             .order_by(model.Kasutaja.nimi))
        return [(k_id, k_nimi) for (k_id, k_nimi) in q.all()]

    def _check_perm_test(self, q1, test_id):
        "Kontrollitakse, kas on oma korraldatud test või muu hindamine"
        ferrors = []
        # kas on teiste korraldatud test, kuhu mind on hindajaks määratud? 
        q = q1.join((model.Labiviija,
                       sa.and_(model.Labiviija.testiruum_id==model.Testiruum.id,
                               model.Labiviija.kasutaja_id==self.c.user.id,
                               model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_K)))
        if q.count() == 0:
            ferrors.append(_("Kasutajat pole määratud selle testi hindajaks ilma tsentraalse korralduseta."))

        # kas on ise korraldatud test?
        q1 = q1.filter(model.Nimekiri.esitaja_kasutaja_id==self.c.user.id)            
        if q1.count() > 0:
            url = self.url('rhindamised', test_id=test_id)
            ferrors.append(_('Ise korraldatud testi hindamine toimub <a href="{url}">ise korraldatud testide</a> menüüs.').format(url=url))                

        return q, ferrors
    
    def _prepare_header(self):
        header = [('test.id', _("Testi ID")),
                  ('test.nimi', _("Testi nimetus")),
                  ('nimekiri.nimi', _("Nimekiri")),
                  (None, _("Hindamata tööd"), 'hindamata'),
                  (None, _("Hindamine pooleli"), 'pooleli'),
                  (None, _("Hinnatud tööd"), 'kinnitatud'),
                  (None, _("Nimekirja looja")),
                  ]
        return header
    
    def _prepare_item(self, rcd, is_html=False):
        testiruum_id, lv_id, test_id, test_nimi, n_nimi, esitaja_nimi = rcd
        hindamata_arv, pooleli_arv, hinnatud_arv = get_rhindamiste_arvud(testiruum_id, lv_id)
        item = [test_id,
                test_nimi,
                n_nimi,
                hindamata_arv,
                pooleli_arv,
                hinnatud_arv,
                esitaja_nimi]
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
