from eis.lib.baseresource import *
from eis.forms import NotYetImplementedForm
_ = i18n._

log = logging.getLogger(__name__)

class TurvakotinumbridController(BaseResourceController):
    """Turvakottide numbrite sisestamine
    """
    _permission = 'sisestamine'
    _MODEL = model.Turvakott
    _INDEX_TEMPLATE = 'ekk/sisestamine/turvakotinumbrid.mako'
    _LIST_TEMPLATE = 'ekk/sisestamine/turvakotinumbrid.otsing_list.mako'
    _DEFAULT_SORT = 'piirkond.nimi,testipakett.lang,koht.nimi' # vaikimisi sortimine
    
    _no_paginate = True

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.suund == const.SUUND_VALJA:
            q = q.filter(model.Turvakott.suund==const.SUUND_VALJA)
        elif self.c.suund == const.SUUND_TAGASI:
            q = q.filter(model.Turvakott.suund==const.SUUND_TAGASI)

        if self.c.testikoht_tahis:
            q = q.filter(model.Testikoht.tahis.ilike(self.c.testikoht_tahis))

        if self.c.kotinr:
            q = q.filter(model.Turvakott.kotinr==self.c.kotinr)

        return q

    def _search_default(self, q):
        self.c.suund = 0
        return q

    def _query(self):
        q = model.SessionR.query(model.Turvakott,
                                model.Testikoht.tahis,
                                model.Koht.nimi,
                                model.Piirkond,
                                model.Testipakett.lang)
        q = q.join(model.Turvakott.testipakett).\
            join(model.Testipakett.testikoht).\
            filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id).\
            join(model.Testikoht.koht).\
            outerjoin(model.Koht.piirkond)
        return q


    def create(self):
        errors = {}
        li_kotinr = []
        for key in self.request.params:
            prefix = 'kotinr_'
            if key.startswith(prefix):
                kott_id = key[len(prefix):]
                if key not in self.request.params:
                    continue
                kotinr = self.request.params.get(key)
                if kotinr and kotinr in li_kotinr:
                    errors[key] = _('Kotinumber on sisestatud rohkem kui ühe korra')
                else:
                    kott = model.Turvakott.get(kott_id)
                    assert kott.testipakett.testikoht.toimumisaeg_id == self.c.toimumisaeg.id, _('Vale toimumisaeg')
                    if kott.kotinr != kotinr:
                        if kotinr:
                            teinekott = model.Turvakott.query.filter_by(kotinr=kotinr).first()
                            if teinekott:
                                testikoht = teinekott.testipakett.testikoht
                                toimumisaeg = testikoht.toimumisaeg
                                testiosa = toimumisaeg.testiosa
                                errors[key] = _('Kotinumber on juba kasutusel ({s1}, {s2}, {s3}, {s4})').format(
                                    s1=testiosa.test.nimi, s2=testiosa.tahis, s3=toimumisaeg.millal, s4=testikoht.koht.nimi) 
                                continue
                        kott.kotinr = kotinr 
                        if kotinr:
                            kott.staatus = const.M_STAATUS_VALJASTATUD

        if errors:
            self.form = Form(self.request, schema=NotYetImplementedForm)
            self.form.validate()
            self.form.errors = errors
            self.error('Palun kõrvalda vead')
            html = self.form.render(self._INDEX_TEMPLATE, extra_info=self._index_d())
            return Response(html)

        model.Session.commit()
        self.success()
        suund = self.request.params.get('suund')
        testikoht_tahis = self.request.params.get('testikoht_tahis')
        return self._redirect('index', suund=suund, testikoht_tahis=testikoht_tahis)

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.test = self.c.toimumisaeg.testimiskord.test
