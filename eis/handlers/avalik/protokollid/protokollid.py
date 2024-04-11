from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class ProtokollidController(BaseResourceController):
    """Testi toimumise protokollide otsing soorituskohas
    """
    _permission = 'toimumisprotokoll,tprotsisestus,aineopetaja'
    _MODEL = model.Toimumisprotokoll
    _INDEX_TEMPLATE = 'avalik/protokollid/otsing.mako'
    _LIST_TEMPLATE = 'avalik/protokollid/otsing_list.mako'
    _DEFAULT_SORT = '-testimiskord.alates,-testiruum.algus'

    def _search(self, q):
        if self.c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(self.c.testsessioon_id))
        return q

    def _query(self):
        self.c.kasutaja = self.c.user.get_kasutaja()
        # protokolli ei või täita enne toimumise päeva ES-3820
        tomorrow = date.today() + timedelta(days=1)
        q = (model.SessionR.query(model.Toimumisprotokoll,
                                 model.Test.nimi,
                                 model.Koht.nimi,
                                 model.Testikoht.tahised,
                                 model.Ruum.tahis)
             .join(model.Toimumisprotokoll.testimiskord)
             .filter(model.Testimiskord.osalemise_naitamine==True)
             .filter(model.Toimumisprotokoll.koht_id==self.c.user.koht_id)
             .join(model.Testimiskord.test)
             .join(model.Toimumisprotokoll.koht)
             .join(model.Toimumisprotokoll.testikoht)
             .filter(model.Testikoht.staatus==const.B_STAATUS_KEHTIV)
             .filter(model.Testikoht.alates < tomorrow)
             .outerjoin(model.Toimumisprotokoll.testiruum)
             .filter(sa.or_(model.Testiruum.id==None,
                            model.Testiruum.sooritajate_arv>0))
             .outerjoin(model.Testiruum.ruum)
             )
        if not self.c.user.on_avalikadmin:
            if not self.c.user.has_permission('tprotsisestus', const.BT_UPDATE):
                # ei ole õigust kõiki kooli protokolle sisestada
                # õigus on ainult enda läbiviidud protokollide ja enda õpilaste kohta
                q = q.filter(sa.or_(
                    model.Testikoht.labiviijad.any(model.Labiviija.kasutaja_id==self.c.user.id),
                    sa.exists().where(sa.and_(
                        model.Sooritaja.testiopetajad.any(
                            model.Testiopetaja.opetaja_kasutaja_id==self.c.user.id),
                        model.Sooritaja.id==model.Sooritus.sooritaja_id,
                        model.Sooritus.testikoht_id==model.Toimumisprotokoll.testikoht_id,
                        sa.or_(model.Sooritus.testiruum_id==model.Toimumisprotokoll.testiruum_id,
                               model.Toimumisprotokoll.testiruum_id==None)))
                    ))
        return q

    def _perm_params(self):
        if not self.c.user.koht_id:
            return False
