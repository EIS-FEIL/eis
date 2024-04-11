from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
log = logging.getLogger(__name__)
_ = i18n._

class IsikuandmedController(BaseResourceController):
    _permission = 'nousolekud'
    _MODEL = model.Labiviija
    _ITEM_FORM = forms.avalik.admin.NousolekudIsikuandmedForm
    _INDEX_TEMPLATE = '/avalik/nousolekud/isikuandmed.mako'
    _get_is_readonly = False
    
    def _index_d(self):
        self._list_lepingud()
        return self.response_dict

    def _list_lepingud(self):
        c = self.c
        year = date.today().year
        q = (model.SessionR.query(model.Testsessioon.id,
                                model.Testileping.leping_id,
                                model.Leping.sessioonita)
             .distinct()
             .filter(model.Testsessioon.staatus==const.B_STAATUS_KEHTIV)
             .filter(model.Testsessioon.oppeaasta>=year)
             .join(model.Testsessioon.testimiskorrad)
             .join(model.Testimiskord.test)
             .join(model.Testimiskord.testilepingud)
             .join(model.Testileping.leping)
             .join(model.Testimiskord.toimumisajad)
             .join(model.Toimumisaeg.testiosa)
             )
        # suulise testi grupid
        grupid_s = (const.GRUPP_HINDAJA_S,
                    const.GRUPP_HINDAJA_S2,
                    const.GRUPP_INTERVJUU)
        # läbiviijad
        grupid_l = (const.GRUPP_KOMISJON_ESIMEES,
                    const.GRUPP_KOMISJON,
                    const.GRUPP_KONSULTANT)
        vastvorm_k = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_KP)
        vastvorm_s = (const.VASTVORM_SH, const.VASTVORM_SP)
        # kasutaja profiil peab testi õppeaines läbiviija rolli võimaldama
        # ja kui toimumisaeg vajab käskkirja, siis peab olema käskkirja kantud
        f = sa.and_(model.Aineprofiil.kasutaja_id==c.kasutaja.id,
                    model.Aineprofiil.aine_kood==model.Test.aine_kood,
                    model.Aineprofiil.kasutajagrupp_id==model.Testileping.kasutajagrupp_id,
                    sa.or_(model.Testileping.kasutajagrupp_id.in_(grupid_l),
                           sa.and_(
                               sa.or_(sa.and_(model.Testiosa.vastvorm_kood.in_(vastvorm_k),
                                              model.Testileping.kasutajagrupp_id==const.GRUPP_HINDAJA_K),
                                      sa.and_(model.Testiosa.vastvorm_kood==const.VASTVORM_I,
                                              model.Testileping.kasutajagrupp_id==const.GRUPP_INTERVJUU),
                                      sa.and_(model.Testiosa.vastvorm_kood.in_(vastvorm_s),
                                              model.Testileping.kasutajagrupp_id.in_(grupid_s))),
                               sa.or_(sa.and_(model.Aineprofiil.kasutajagrupp_id==const.GRUPP_INTERVJUU,
                                              sa.or_(model.Toimumisaeg.intervjueerija_kaskkirikpv==None,
                                                     model.Toimumisaeg.intervjueerija_kaskkirikpv<=model.Aineprofiil.kaskkirikpv)),
                                      sa.and_(model.Aineprofiil.kasutajagrupp_id!=const.GRUPP_INTERVJUU,
                                              sa.or_(model.Toimumisaeg.hindaja_kaskkirikpv==None,
                                                     model.Toimumisaeg.hindaja_kaskkirikpv<=model.Aineprofiil.kaskkirikpv))),
                               sa.or_(sa.and_(model.Testiosa.vastvorm_kood.in_(vastvorm_k),
                                              model.Testileping.kasutajagrupp_id==const.GRUPP_HINDAJA_K),
                                      sa.and_(model.Testiosa.vastvorm_kood==const.VASTVORM_I,
                                              model.Testileping.kasutajagrupp_id==const.GRUPP_INTERVJUU),
                                      sa.and_(model.Testiosa.vastvorm_kood.in_(vastvorm_s),
                                              model.Testileping.kasutajagrupp_id.in_(grupid_s)))
                               ))
                    )

        f = sa.exists().where(f)
        profiil = c.kasutaja.profiil
        if profiil and profiil.on_vaatleja:
            if profiil.v_kaskkirikpv:
                f_v1 = sa.or_(model.Toimumisaeg.hindaja_kaskkirikpv==None,
                              model.Toimumisaeg.hindaja_kaskkirikpv<=profiil.v_kaskkirikpv)
            else:
                f_v1 = model.Toimumisaeg.hindaja_kaskkirikpv == None
            f_v = sa.and_(model.Testileping.kasutajagrupp_id==const.GRUPP_VAATLEJA,
                          model.Toimumisaeg.vaatleja_maaraja==True,
                          f_v1)
            q = q.filter(sa.or_(f, f_v))
        else:
            q = q.filter(f)

        q = q.order_by(model.Leping.sessioonita,
                       sa.desc(model.Testsessioon.seq),
                       model.Testileping.kasutajagrupp_id)
        #model.log_query(q)
        c.data = dict()
        c.sessioonid = list()
        for testsessioon_id, leping_id, sessioonita in q.all():
            #log.debug('sessioon %s, leping %s' % (testsessioon_id, leping_id))
            if sessioonita:
                testsessioon_id = None
            if testsessioon_id not in c.data:
                c.data[testsessioon_id] = list()
                sessioon = testsessioon_id and model.Testsessioon.get(testsessioon_id) or None
                c.sessioonid.append(sessioon)
            if leping_id not in c.data[testsessioon_id]:
                c.data[testsessioon_id].append(leping_id)

    def _create(self):
        """Andmete salvestamine
        """
        c = self.c
        c.kasutaja.from_form(self.form.data, 'k_')
        model.Aadress.adr_from_form(c.kasutaja, self.form.data, 'a_')
        c.profiil.from_form(self.form.data, 'p_')

        if self.request.params.get('rr'):
            # vajutati nupule "päri aadress RRst"
            xtee.set_rr_pohiandmed(self, c.kasutaja, muuda=True)

        self._save_lepingud()

    def _save_lepingud(self):
        c = self.c
        on_yldleping = on_teenusleping = False
        for rcd in self.form.data.get('lep'):
            sessioon_id = rcd['testsessioon_id']
            leping_id = rcd['leping_id']
            nous = rcd['nous']
            leping = model.Leping.get(leping_id)
            lleping = c.kasutaja.get_labiviijaleping(leping_id, sessioon_id)
            if not nous and lleping:
                lleping.delete()
            elif nous:
                if not lleping:
                    lleping = model.Labiviijaleping(kasutaja_id=c.kasutaja.id,
                                                   testsessioon_id=sessioon_id,
                                                   leping_id=leping_id)
                lleping.on_hindaja3 = rcd.get('on_hindaja3')
                if not lleping.noustunud:
                    lleping.noustunud = date.today()

                if leping.yldleping:
                    on_yldleping = True
                else:
                    on_teenusleping = True

        msg = None
        if self.form.data.get('kinnita'):
            if on_teenusleping:
                msg = _('Täname. Leping on vastu võetud')
            # ES-2265 - alates 2021 ei ole enam yldlepingut
            #if on_yldleping and on_teenusleping:
            #    msg = _('Täname. Leping on vastu võetud')
            #elif not on_yldleping and on_teenusleping:
            #    msg = _('Leping vastu võtmata. Puudu on nõusolek lepingu üldtingimustega.')
            if msg:
                self.notice(msg)
        return c.kasutaja

    def _error_create(self):
        extra_info = self._index_d()
        html = self.form.render(self._INDEX_TEMPLATE, extra_info=extra_info)
        return Response(html)

    def _after_update(self, id=None):
        """Kuhu peale salvestamist minna
        """
        if not self.has_errors():
            self.success()
        return HTTPFound(location=self.url_current('index'))

    def __before__(self):
        c = self.c
        c.kasutaja = c.user.get_kasutaja(write=True)
        if c.kasutaja:
            c.profiil = c.kasutaja.give_profiil()
