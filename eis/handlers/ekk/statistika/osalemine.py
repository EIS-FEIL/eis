import pickle
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class OsalemineController(BaseResourceController):
    """Osalemise statistika
    """
    _permission = 'aruanded-osalemine'
    _INDEX_TEMPLATE = 'ekk/statistika/osalemine.otsing.mako'
    _LIST_TEMPLATE = 'ekk/statistika/osalemine.list.mako'
    _DEFAULT_SORT = 'test.aine_kood'
    _ignore_default_params = ['csv']

    def _query(self):
        return None

    def _search_default(self, q):
        self.c.testiliik = const.TESTILIIK_RIIGIEKSAM
        return None

    def _search(self, q1):
        self.c.prepare_row = self._prepare_row
        self.c.rcd_calc = self.rcd_calc

        Aine_kl = sa.orm.aliased(model.Klrida, name='aine_kl')
        li = [model.Test.aine_kood,
              Aine_kl.nimi,
              model.Testimiskord.aasta,
              ]
        if self.c.tkord:
            li = li + [model.Testimiskord.tahis,
                       model.Testimiskord.id,
                       model.Test.id]

        li_select = [sa.func.count(model.Sooritaja.id)] + li

        q = (model.SessionR.query(*li_select)
             .join(model.Test.testimiskorrad)
             .join(model.Testimiskord.sooritajad)
             .filter(model.Sooritaja.hindamine_staatus!=const.H_STAATUS_TOOPUUDU)
             .filter(model.Sooritaja.staatus >= const.S_STAATUS_KATKESTATUD)
             .join((Aine_kl, sa.and_(Aine_kl.klassifikaator_kood=='AINE',
                                     Aine_kl.kood==model.Test.aine_kood)))
             )

        # 2012-11-21 Hele soovil võetud ära tingimus, et tulemused peavad olema kinnitatud
        #filter(model.Testimiskord.tulemus_kinnitatud=True)

        if self.c.test_id:
            q = q.filter(model.Test.id==self.c.test_id)
        if self.c.aine:
            q = q.filter(model.Test.aine_kood==self.c.aine)
        if self.c.aasta_alates:
            q = q.filter(model.Testimiskord.aasta>=self.c.aasta_alates)
        if self.c.aasta_kuni:
            q = q.filter(model.Testimiskord.aasta<=self.c.aasta_kuni)
        if self.c.testiliik:
            q = q.filter(model.Test.testiliik_kood==self.c.testiliik)

        q = q.group_by(*li)

        if self.c.csv:
            return self._index_csv(q)

        return q

    def _order_able(self, q, field):
        """Kontrollitakse, kas antud välja järgi on võimalik sortida
        """
        if field == 'testimiskord.tahis' and not self.c.tkord:
            return False
        return BaseResourceController._order_able(self, q, field)

    def _index_csv(self, q):
        c = self.c

        # tabeli päis
        names = [_("Aasta"),
                 _("Õppeaine"),
                 ]
        if c.tkord:
            names.append(_("Test"))
            names.append(_("Testimiskord"))
        names.extend([_("Registreerunute arv"),
                      _("Puudus"),
                      _("Puudumise %"),
                      _("Eemaldatud"),
                      _("Eemaldatute %"),
                      _("Sooritajad"),
                      _("Sooritanute %"),
                      _("Keskmine tulemus"),
                      ])

        # tabeli sisu
        items = []
        for rcd in q.all():
            row = self._prepare_row(rcd)
            items.append(row)

        buf = ''
        for r in [names] + items:
            buf += ';'.join([str(v) for v in r]) + '\n'

        #buf = buf.encode('utf-8')
        buf = utils.encode_ansi(buf)
        response = Response(buf) 
        #response.content_type = 'text/csv; charset=utf-8' # ei mõju excelile
        response.content_type = 'text/csv'
        response.content_disposition = 'attachment;filename=osalemine.csv'
        return response

    def _prepare_row(self, rcd):
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h

        total = rcd[0]
        aine = rcd[1]
        aine_nimi = rcd[2]
        aasta = rcd[3]
        tkord_tahis = c.tkord and rcd[4] or None
        tkord_id = c.tkord and rcd[5] or None
        test_id = c.tkord and rcd[6] or None
        osalemine, keskmine = c.rcd_calc(aine, aasta, tkord_id)
       
        puudus = osalemine.get(const.S_STAATUS_PUUDUS) or 0
        tehtud = osalemine.get(const.S_STAATUS_TEHTUD) or 0
        eemaldatud = osalemine.get(const.S_STAATUS_EEMALDATUD) or 0

        puudus_pr = puudus * 100./total 
        tehtud_pr = tehtud * 100./total
        eemaldatud_pr = eemaldatud * 100./total

        row = [aasta,
               aine_nimi,
               ]
        if c.tkord:
            row.append(test_id)
            row.append(tkord_tahis)
        row.extend([total,
                    puudus,
                    h.fstr(puudus_pr),
                    eemaldatud,
                    h.fstr(eemaldatud_pr),
                    tehtud,
                    h.fstr(tehtud_pr),
                    h.fstr(keskmine),
                    ])
        return row

    def rcd_calc(self, aine_kood, aasta, tkord_id):
        q = model.SessionR.query(sa.func.count(model.Sooritaja.id),
                                model.Sooritaja.staatus).\
            join(model.Sooritaja.testimiskord).\
            join(model.Testimiskord.test).\
            filter(model.Sooritaja.hindamine_staatus!=const.H_STAATUS_TOOPUUDU).\
            filter(model.Testimiskord.aasta==aasta).\
            filter(model.Test.aine_kood==aine_kood).\
            filter(model.Test.testiliik_kood==self.c.testiliik)
        if self.c.test_id:
            q = q.filter(model.Test.id==self.c.test_id)
        if tkord_id:
            q = q.filter(model.Testimiskord.id==tkord_id)
        q = q.group_by(model.Sooritaja.staatus)
        osalemine = {}
        for rcd in q.all():
            cnt, staatus = rcd
            osalemine[staatus] = cnt

        q = model.SessionR.query(sa.func.avg(model.Sooritaja.pallid)).\
            join(model.Sooritaja.testimiskord).\
            join(model.Testimiskord.test).\
            filter(model.Testimiskord.aasta==aasta).\
            filter(model.Test.aine_kood==aine_kood).\
            filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD).\
            filter(model.Sooritaja.hindamine_staatus!=const.H_STAATUS_TOOPUUDU).\
            filter(model.Test.testiliik_kood==self.c.testiliik)            
        if tkord_id:
            q = q.filter(model.Testimiskord.id==tkord_id)
        keskmine = q.scalar()

        return osalemine, keskmine

