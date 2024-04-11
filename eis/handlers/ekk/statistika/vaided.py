import pickle
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class VaidedController(BaseResourceController):
    """Vaiete statistika
    """
    _permission = 'aruanded-vaided'
    _INDEX_TEMPLATE = 'ekk/statistika/vaided.otsing.mako'
    _LIST_TEMPLATE = 'ekk/statistika/vaided.list.mako'
    _DEFAULT_SORT = 'aine_kl.nimi'

    def _query(self):
        return None

    def _search_default(self, q):
        return None

    def _search(self, q1):
        """Põhiline otsing"""
        
        self.c.prepare_row = self._prepare_row
        self.c.rcd_calc = self.rcd_calc
        Aine_kl = sa.orm.aliased(model.Klrida, name='aine_kl')
        
        li_select = [sa.func.count(model.Sooritaja.id),
                     ]

        li = [model.Test.aine_kood,
              Aine_kl.nimi,
              model.Testimiskord.aasta,
              ]

        li_select = li_select + li
        q = model.SessionR.query(*li_select)

        # päringu tingimuste seadmine
        q = (q.join(model.Sooritaja.testimiskord)
             .join(model.Testimiskord.test)
             .filter(model.Test.testiliik_kood==self.c.testiliik)
             .filter(model.Sooritaja.staatus == const.S_STAATUS_TEHTUD)
             .join((Aine_kl, sa.and_(Aine_kl.klassifikaator_kood=='AINE',
                                     Aine_kl.kood==model.Test.aine_kood)))
            )

        if self.c.aine:
            q = q.filter(model.Test.aine_kood==self.c.aine)

        if not self.c.aasta_alates:
            self.c.aasta_alates = self.c.aasta_kuni or date.today().year
        if not self.c.aasta_kuni:
            self.c.aasta_kuni = self.c.aasta_alates
        if self.c.aasta_alates == self.c.aasta_kuni:
            q = q.filter(model.Testimiskord.aasta==self.c.aasta_alates)
        else:
            q = (q.filter(model.Testimiskord.aasta >= self.c.aasta_alates)
                 .filter(model.Testimiskord.aasta <= self.c.aasta_kuni))

        q = q.group_by(*li)

        if self.c.csv:
            return self._index_csv(q)

        return q


    def _index_csv(self, q):
        c = self.c

        # tabeli päis
        names = [_("Aasta"),
                 _("Õppeaine"),
                 _("Eksaminandide arv"),
                 _("Vaiete arv"),
                 _("Vaiete %"),
                 _("Vaietest vastatud %"),
                 _("Tõsteti"),
                 _("Ei muudetud"),
                 _("Langetati"),
                 _("Langetati %"),
                 ]

        # tabeli sisu
        items = []
        for rcd in q.all():
            row = self._prepare_row(rcd)
            items.append(row)

        buf = ''
        for r in [names] + items:
            buf += ';'.join([str(v) for v in r]) + '\n'

        buf = utils.encode_ansi(buf)
        response = Response(buf) 
        response.content_type = 'text/csv; charset=iso-8859-15'
        response.content_disposition = 'attachment;filename=vaided.csv'
        return response

    def _prepare_row(self, rcd):
        "Tabeli ühe rea väljade kokkupanek"
        c = self.c
        h = self.h

        total = rcd[0]
        aine = rcd[1]
        aine_nimi = rcd[2]
        aasta = rcd[3]

        vaided, otsustatud, langetatud, sama, tostetud = c.rcd_calc(aasta, aine)

        vaided_pr = vaided * 100./total
        otsustatud_pr = vaided and otsustatud * 100./vaided or 0
        langetatud_pr = otsustatud and langetatud * 100./otsustatud or 0

        row = [aasta,
               aine_nimi,
               total,
               vaided,
               h.fstr(vaided_pr),
               ]
        if vaided:
            row.extend([h.fstr(otsustatud_pr),
                        tostetud,
                        sama,
                        langetatud,
                        h.fstr(langetatud_pr),
                        ])
        return row

    def rcd_calc(self, aasta, aine_kood):
        q = (model.SessionR.query(sa.func.count(model.Sooritaja.id))
             .join(model.Sooritaja.testimiskord)
             .join(model.Testimiskord.test)
             .filter(model.Test.aine_kood==aine_kood)
             .filter(model.Testimiskord.aasta==aasta)
             .join(model.Sooritaja.vaie)
             )
        vaided = q.scalar()
        
        q = q.filter(model.Vaie.staatus==const.V_STAATUS_OTSUSTATUD)
        otsustatud = q.scalar()

        langetatud = q.filter(model.Vaie.pallid_enne>model.Vaie.pallid_parast).scalar()
        sama = q.filter(model.Vaie.pallid_enne==model.Vaie.pallid_parast).scalar()
        tostetud = q.filter(model.Vaie.pallid_enne<model.Vaie.pallid_parast).scalar()
        return vaided, otsustatud, langetatud, sama, tostetud

    def __before__(self):
        self.c.testiliik = const.TESTILIIK_RIIGIEKSAM
