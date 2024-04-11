# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
log = logging.getLogger(__name__)

class AvaldamineController(BaseResourceController):
    """Tunnistuste avaldamine
    """
    _permission = 'tunnistused'
    _MODEL = model.Tunnistus
    _INDEX_TEMPLATE = 'ekk/muud/tunnistused.avaldamine.mako'
    _LIST_TEMPLATE = 'ekk/muud/tunnistused.avaldamine_list.mako'
    _ignore_default_params = ['naita']

    def _search(self, q):
        c = self.c
        if not c.testiliik:
            c.testiliik = const.TESTILIIK_RIIGIEKSAM
        c.opt_sessioon = model.Testsessioon.get_opt(c.testiliik)
        if len(c.opt_sessioon):
            if not c.sessioon_id or \
                    int(c.sessioon_id) not in [r[0] for r in c.opt_sessioon]:
                c.sessioon_id = c.opt_sessioon[0][0]
        else:
            c.sessioon_id = None
        if not c.sessioon_id:
            return
        if c.partial:
            # paginaator, võtab järgmise lehekülje, koguseid pole vaja arvutada
            c.naita = True

        # kuvatakse kogu lehekülg, kuvatakse valitud sessiooni kogused
        q = q.filter(model.Tunnistus.testsessioon_id==c.sessioon_id)
        if c.testimiskord_id:
            q = q.filter(model.Tunnistus.testitunnistused.any(
                model.Testitunnistus.sooritaja.has(model.Sooritaja.testimiskord_id==c.testimiskord_id)))

        c.avaldatud = (q.filter(model.Tunnistus.staatus==const.N_STAATUS_AVALDATUD)
                       .count())
        c.salvestatud = (q.filter(model.Tunnistus.staatus==const.N_STAATUS_SALVESTATUD)
                         .count())
        c.salvestamata = (q.filter(model.Tunnistus.staatus==const.N_STAATUS_KEHTIV)
                          .count())

        if c.naita:
            staatus = c.staatus and int(c.staatus) or None
            q = q.filter(model.Tunnistus.staatus==staatus)
            return q

    def _search_default(self, q):
        return self._search(q)

    def _query(self):
        return model.Tunnistus.query

    def create(self):
        if self.request.params.get('salvesta_alus'):
            return self._create_alus()
        if self.request.params.get('delete_t'):
            return self._delete_t()
        
        avaldamisaeg = datetime.now()
        sessioon = model.Testsessioon.get(self.request.params.get('sessioon_id'))
        testiliik = self.request.params.get('testiliik')

        q = (model.Session.query(model.Tunnistus)
             .filter(model.Tunnistus.testsessioon_id==sessioon.id)
             .filter(model.Tunnistus.staatus==const.N_STAATUS_SALVESTATUD)
             )
        testimiskord_id = self.request.params.get('testimiskord_id')
        if testimiskord_id:
            q = q.filter(model.Tunnistus.testitunnistused.any(\
                    model.Testitunnistus.sooritaja.has(model.Sooritaja.testimiskord_id==testimiskord_id)))
        #q = q.filter(model.Tunnistus.testiliik_kood==testiliik)
        for tunnistus in q.all():
            tunnistus.staatus = const.N_STAATUS_AVALDATUD
            if not tunnistus.avaldamisaeg:
                tunnistus.avaldamisaeg = avaldamisaeg
        model.Session.commit()
        return HTTPFound(location=self.url_current('index', getargs=True))

    def _delete_t(self):
        # tunnistuste kustutamine,
        # näiteks siis, kui on loodud liigne duplikaat
        tunnistused_id = self.request.params.getall('t_id')
        q = (model.Tunnistus.query
             .filter(model.Tunnistus.id.in_(tunnistused_id))
             .filter(model.Tunnistus.staatus.in_((const.N_STAATUS_KEHTETU, const.N_STAATUS_KEHTIV)))
             )
        cnt = 0
        cnt_prev = 0
        for tunnistus in q.all():
            eelmine = tunnistus.eelmine
            # kui on olemas eelnev tunnistus, siis muudame selle kehtivaks
            if eelmine and eelmine.staatus == const.N_STAATUS_KEHTETU:
                #if eelmine.has_file and eelmine.fileext != 'pdf':
                eelmine.staatus = const.N_STAATUS_SALVESTATUD
                #else:
                #    eelmine.staatus = const.N_STAATUS_KEHTIV
                # kasutaja peab ise selle hiljem avalikuks kuulutama, kui vaja
                cnt_prev += 1

            for rcd in tunnistus.testitunnistused:
                rcd.delete()
            tunnistus.delete()
            cnt += 1
        model.Session.commit()
        self.notice('Kustutatud %s tunnistuse andmed' % cnt)
        if cnt_prev:
            self.notice('%s varem kehtetut tunnistust on muudetud kehtivaks, kuid mitte avaldatuks (vajadusel avalda)' % cnt_prev)
        return HTTPFound(location=self.url_current('index', getargs=True))
    
    def _create_alus(self):
        sessioon = model.Testsessioon.get(self.request.params.get('sessioon_id'))
        testiliik = self.request.params.get('testiliik')

        alus = self.request.params.get('alus')
        q = (model.Tunnistus.query
             .filter(model.Tunnistus.testsessioon_id==sessioon.id)
             .filter(model.Tunnistus.staatus>=const.N_STAATUS_SALVESTATUD)
             )
        testimiskord_id = self.request.params.get('testimiskord_id')
        if testimiskord_id:
            q = q.filter(model.Tunnistus.testitunnistused.any(\
                    model.Testitunnistus.sooritaja.has(model.Sooritaja.testimiskord_id==testimiskord_id)))

        n = 0
        for tunnistus in q.all():
            tunnistus.alus = alus
            n += 1
        model.Session.commit()
        self.success('Alus määratud %s tunnistusele' % n)
        return HTTPFound(location=self.url_current('index', getargs=True))

    def _download(self, id, format):
        """Näita faili"""
        item = self._MODEL.get(id)
        
        if not item:
            raise NotFound('Ei leitud')
        filename = item.filename
        filedata = item.filedata
        mimetype = item.mimetype
        if not filedata:
            raise NotFound('Dokumenti ei leitud')

        return utils.download(filedata, filename, mimetype)

