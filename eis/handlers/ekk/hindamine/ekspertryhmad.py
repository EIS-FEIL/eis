from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class EkspertryhmadController(BaseResourceController):
    """Vaide korral hindajate ekspertrühma koostamine
    """
    _permission = 'ekspertryhmad'
    _INDEX_TEMPLATE = 'ekk/hindamine/ekspert.ryhmad.mako'
    _ITEM_FORM = forms.ekk.hindamine.EkspertryhmadForm

    _index_after_create = True

    def index(self):
        q = model.Kasutaja.query.\
            join(model.Kasutaja.kasutajarollid).\
            filter(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
            filter(model.Kasutajaroll.kehtib_kuni>date.today()).\
            filter(model.Kasutajaroll.aine_kood==self.c.test.aine_kood)
        self.c.eksperdid = q.filter(~ model.Kasutaja.labiviijad.any(\
            sa.and_(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT,
                    model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id))).\
            order_by(model.Kasutaja.nimi).\
            all()

        self.c.ryhmaliikmed = model.Labiviija.query.\
            filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
            filter(model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id).\
            join(model.Labiviija.kasutaja).\
            order_by(model.Kasutaja.nimi).\
            all()

        if len(self.c.eksperdid) == 0 and len(self.c.ryhmaliikmed) == 0:
            self.error(_("Aines {s} pole ühtki eksperti").format(s=self.c.test.aine_nimi))

        return self.render_to_response(self._INDEX_TEMPLATE)

    def _new_d(self):
        return self.response_dict

    def _create(self):
        # ekspertide määramine ekspertrühmadesse
        for rcd in self.form.data.get('k'):
            kasutaja = model.Kasutaja.get(rcd['kasutaja_id'])
            lv = model.Labiviija.query.\
                 filter(model.Labiviija.kasutaja_id==kasutaja.id).\
                 filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
                 filter(model.Labiviija.toimumisaeg_id==self.c.toimumisaeg.id).\
                 first()

            lv_id = rcd.get('lv_id')
            if lv_id is None:
                # ei kuulu ekspertrühma
                if lv:
                    if len(lv.labivaatused) > 0 or \
                            len(lv.kysimusehindemarkused) > 0 or \
                            len(lv.aspektihindemarkused) > 0 or \
                            len(lv.ylesandehindemarkused) > 0:
                        self.error(_("{s} on juba töid läbi vaadanud ja teda ei saa enam rühmast eemaldada").format(s=kasutaja.nimi))
                    else:
                        lv.delete()
            else:
                # kuulub rühma
                if not lv:
                    lv = model.Labiviija(kasutaja_id=kasutaja.id,
                                         kasutajagrupp_id=const.GRUPP_HINDAMISEKSPERT,
                                         toimumisaeg_id=self.c.toimumisaeg.id,
                                         liik=const.HINDAJA5)

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.test = self.c.toimumisaeg.testiosa.test

    def _perm_params(self):
        return {'obj': self.c.test}
