from eis.lib.baseresource import *
_ = i18n._
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)

class KontrollController(BaseResourceController):
    """Registreerimise kontroll
    """
    _permission = 'nimekirjad'
    _INDEX_TEMPLATE = 'avalik/nimekirjad/kontroll.mako'
    _LIST_TEMPLATE = 'avalik/nimekirjad/kontroll_list.mako'
    _EDIT_TEMPLATE = 'avalik/nimekirjad/kontroll.tulemus.mako'
    _DEFAULT_SORT = 'opilane.paralleel,opilane.perenimi,opilane.eesnimi' # vaikimisi sortimine
    _no_paginate = True
    _get_is_readonly = False
    
    def _query(self):
        return None

    def _search(self, q1):
        self.c.prepare_row = self._prepare_row
        log.info('search (%s,%s)' % (self.c.klass, self.c.paralleel))
        if self.c.klass:
            if self.c.paralleel:
                self.c.paralleel = self.c.paralleel.upper()
            reg = ehis.Ehis(handler=self)
            kool_id = self.c.user.koht.kool_id
            klass = model.Klass.get_by_klass(kool_id, self.c.klass, self.c.paralleel)

            settings = self.request.registry.settings
            cache_hours = int(settings.get('ehis.cache.klass',0))
            #log.info('klass=%s %s' % (klass, klass and klass.seisuga))
            if not klass or not klass.seisuga or \
                    klass.seisuga < datetime.now() - timedelta(hours=cache_hours):
                log.info('oppurid_kool(%s,%s,%s)...' % (kool_id, self.c.klass, self.c.paralleel))
                message, oppimised = reg.oppurid_kool(kool_id,
                                                      self.c.klass, 
                                                      self.c.paralleel)
                if message:
                    self.error(message)
                else:
                    log.debug('update klass')
                    model.Opilane.update_klass(oppimised, 
                                               kool_id,
                                               self.c.klass, 
                                               self.c.paralleel)
                    model.Session.commit()
            # testide tingimused
            fli = [model.Sooritaja.kasutaja_id==model.Opilane.kasutaja_id]
            if self.c.testiliik:
                fli.append(model.Sooritaja.test.has(\
                    model.Test.testiliik_kood==self.c.testiliik))

            # testimiskordade tingimused
            ftk = [sa.or_(model.Testimiskord.sooritajad_peidus_kuni==None,
                          model.Testimiskord.sooritajad_peidus_kuni<datetime.now())]
            if self.c.sessioon_id:
                ftk.append(model.Testimiskord.testsessioon_id==self.c.sessioon_id)
            else:
                dt = date.today()
                oppeaasta = dt.month < 9 and dt.year or dt.year + 1
                ftk.append(model.Testimiskord.testsessioon.has(
                    model.Testsessioon.oppeaasta>=oppeaasta))
            fli.append(model.Sooritaja.testimiskord.has(sa.and_(*ftk)))

            # päring õpilaste leidmiseks
            q = model.Session.query(model.Opilane, model.Sooritaja).\
                filter_by(kool_id=kool_id).\
                filter_by(klass=self.c.klass).\
                outerjoin((model.Sooritaja, sa.and_(*fli)))

            if self.c.paralleel:
                q = q.filter(model.Opilane.paralleel==self.c.paralleel)

            if self.c.csv:
                return self._index_csv(q)
            return q

    def _prepare_items(self, q):
        c = self.c

        # tabeli päis
        header = [_("Isikukood"),
                  _("Eesnimi"),
                  _("Perekonnanimi"),
                  _("Paralleel"),
                  _("Test"),
                  _("Kursus"),
                  _("Keel"),
                  _("Olek"),
                  _("Eritingimused"),
                  ]
        
        # tabeli sisu
        items = []
        for rcd in q.all():
            row = self._prepare_row(rcd)
            items.append(row)

        return header, items
    
    def _prepare_row(self, rcd):
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h

        opilane, sooritaja = rcd
        row = [opilane.isikukood,
               opilane.eesnimi,
               opilane.perenimi,
               opilane.paralleel,
               sooritaja and sooritaja.test.nimi or '',
               sooritaja and sooritaja.kursus_nimi or '',
               sooritaja and sooritaja.lang_nimi or '',
               sooritaja and sooritaja.staatus_nimi or '',
               ]

        li_buf = []
        if sooritaja and sooritaja.on_erivajadused:
            if c.csv:
                mitu_testiosa = len(sooritaja.sooritused) > 1
                for tos in sooritaja.sooritused:
                    str_tos = tos.get_str_erivajadused('\n')
                    if str_tos:
                        li_buf.append(tos.testiosa.nimi + ':\n' + str_tos)
            else:
                li_buf.append('jah')
        row.append('\n'.join(li_buf))

        return row

    def _show_d(self):
        "Sooritaja tulemuse vaatamine"
        id = self.request.matchdict.get('id')
        self.c.item = self.Sooritaja.get(id)
        if not self.c.item:
            raise NotFound('Kirjet %s ei leitud' % id)        
        return self.response_dict

    def _show_erivajadus(self, id):
        self.c.sooritaja = model.Sooritaja.get(id)
        return self.render_to_response('avalik/nimekirjad/kontroll.erivajadused.mako')

    def _perm_params(self):
        if not self.c.user.koht:
            return False
