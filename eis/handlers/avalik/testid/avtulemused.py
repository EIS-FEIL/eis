# avalikus vaates koostatud testi tulemused
from simplejson import dumps
from eis.lib.baseresource import *
from eis.lib.block import BlockController
from eis.lib.resultstat import ResultStat
from .testiosavalik import Testiosavalik
log = logging.getLogger(__name__)
_ = i18n._

class AvtulemusedController(BaseResourceController, Testiosavalik):

    _permission = 'omanimekirjad'
    _INDEX_TEMPLATE = 'avalik/testid/avtulemused.tulemused.mako'
    _EDIT_TEMPLATE = 'avalik/testid/avtulemused.tulemused.mako' 
    _no_paginate = True
    _get_is_readonly = False
    _actions = 'index,show,edit' # võimalikud tegevused
    
    def _search_default(self, q):
        return self._search(q)

    def _filter(self, q):
        testiruum_id = self.c.testiruum and self.c.testiruum.id or -1
        q = q.filter(model.Sooritus.testiruum_id==testiruum_id)
        return q

    def _query(self):
        pass

    def _search(self, q):
        c = self.c

        hindamiskogumid = [hk for hk in c.testiosa.hindamiskogumid if hk.staatus == const.B_STAATUS_KEHTIV]
        c.on_kasitsi = bool([hk for hk in hindamiskogumid if not hk.arvutihinnatav])

        if c.testiruum:
            q1 = self._query_sooritused()
            if c.csv:
                return self._index_csv(q1)
            c.sooritused = q1.all()
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item
        
    def _query_sooritused(self):
        # päritakse sooritajate nimekiri
        q = model.Session.query(model.Sooritus, 
                                model.Sooritaja.eesnimi,
                                model.Sooritaja.perenimi,
                                model.Kasutaja.isikukood)
        q = self._filter(q)
        q = (q.join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.kasutaja)
             .order_by(model.sa.desc(model.Sooritus.staatus),
                       model.Sooritaja.eesnimi,
                       model.Sooritaja.perenimi)
             )
        return q

    def _index_csv(self, q, fn='andmed.csv'):
        "Loetelu väljastamine CSV-na"
        header, items = self._prepare_items(q)
        data = self._csv_data(header, items)
        data = utils.encode_ansi(data)
        return utils.download(data, fn, const.CONTENT_TYPE_CSV)
    
    def _prepare_header(self):
        if self.c.csv:
            header = [(None, _("Õpilane")),
                      (None, _("Isikukood")),
                      (None, _("Olek")),
                    ]
        else:
            header = [(None, _("Õpilane")),
                      (None, _("Olek")),
                    ]
        if not self.c.test.protsendita:
            header.append((None, _("Tulemus")))
        if self.c.on_kasitsi:
            header.append((None, _("Hindamine")))
        header.append((None, _("Aeg (minutites)")))
        return header
    
    def _prepare_item(self, row, n):
        tos, eesnimi, perenimi, isikukood = row
        if self.c.csv:
            item = ['%s %s' % (eesnimi, perenimi),
                    isikukood,
                    tos.staatus_nimi,
                    ]
        else:
            item = ['%s %s' % (eesnimi, perenimi),
                    tos.staatus_nimi,
                    ]
            
        if not self.c.test.protsendita:
            if tos.staatus == const.S_STAATUS_TEHTUD \
              and tos.hindamine_staatus == const.H_STAATUS_HINNATUD \
              and tos.tulemus_protsent is not None:
                value = self.h.fstr(tos.tulemus_protsent,0) + '%'
            else:
                value = ''
            item.append(value)
        if self.c.on_kasitsi:
            if tos.staatus != const.S_STAATUS_TEHTUD:
                h_staatus = ''
            elif tos.hindamine_staatus == const.H_STAATUS_HINNATUD:
                h_staatus = _("Hinnatud")
            else:
                h_staatus = _("Hindamata")          
            self.c.ind_h = len(item)
            item.append(h_staatus)
        if tos.ajakulu is not None:
            value = self.h.fstr(tos.ajakulu/60.,0)
        else:
            value = ''
        item.append(value)
        return item
    
    def __before__(self):
        c = self.c
        Testiosavalik.set_test_testiosa(self)
            
    def _perm_params(self):
        c = self.c
        return {'obj': c.nimekiri or c.test}
