from simplejson import dumps
from eis.lib.baseresource import *
from eis.lib.xtee import ehis
import eis.lib.pdf as pdf
_ = i18n._
log = logging.getLogger(__name__)

class RegkontrollController(BaseResourceController):
    """Registreerimise kontroll
    """
    _permission = 'regkontroll'
    _MODEL = model.Opilane
    _INDEX_TEMPLATE = 'ekk/muud/regkontroll.mako'
    _LIST_TEMPLATE = 'ekk/muud/regkontroll_list.mako'
    _DEFAULT_SORT = 'koht.nimi,opilane.perenimi,opilane.eesnimi' # vaikimisi sortimine
    _SEARCH_FORM = forms.ekk.muud.RegkontrollForm

    def _query(self):
        return None
    
    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        if c.klass == '9':
            return self._search9()
        elif c.klass == '12':
            return self._search12()

    def _order_able(self, q, field):
        if self.c.klass != '9':
            if field.find('eestik') > -1 \
               or field.find('matem') > -1 \
               or field.find('valik') > -1:
                # 12. klassi otsingus ei saa nende järgi sortida
                return False
        return super()._order_able(q, field)
            
    def _search9(self):
        "9. klassi kontroll ES-3352"
        # otsime nende seast, kelle andmeid on peale 1. septembrit uuendatud
        today = date.today()
        year = today.month < 9 and today.year - 1 or today.year
        seisuga = date(year, 9, 1)

        f_regatud_voi_piisav = sa.or_(model.Sooritaja.staatus==const.S_STAATUS_REGATUD,
                                      model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
        # Kohustuslikud eksamid
        # 1) Eesti keel või eesti keel teise keelena

        Eesti = (model.Session.query(model.Sooritaja.kasutaja_id)
                 .join(model.Sooritaja.test)
                 .filter(model.Sooritaja.testimiskord_id!=None)
                 .filter(model.Test.testiliik_kood==const.TESTILIIK_POHIKOOL)
                 .filter(model.Test.aine_kood.in_((const.AINE_ET, const.AINE_ET2)))
                 .filter(f_regatud_voi_piisav)
                 .subquery()
                 )

        # 2) matemaatika 
        Matem = (model.Session.query(model.Sooritaja.kasutaja_id)
                 .join(model.Sooritaja.test)
                 .filter(model.Sooritaja.testimiskord_id!=None)
                 .filter(model.Test.testiliik_kood==const.TESTILIIK_POHIKOOL)
                 .filter(model.Test.aine_kood==const.AINE_M)
                 .filter(f_regatud_voi_piisav)
                 .subquery()
                 )

        # 3) valik (ainult regatud, mitte tehtud) 
        Valik = (model.Session.query(model.Sooritaja.kasutaja_id,
                                     sa.func.count(model.Sooritaja.id).label('cnt'))
                 .join(model.Sooritaja.test)
                 .filter(model.Sooritaja.testimiskord_id!=None)
                 .filter(model.Test.testiliik_kood==const.TESTILIIK_POHIKOOL)
                 .filter(~ model.Test.aine_kood.in_((const.AINE_ET, const.AINE_ET2, const.AINE_M)))
                 .filter(model.Sooritaja.staatus==const.S_STAATUS_REGATUD)
                 .group_by(model.Sooritaja.kasutaja_id)
                 .subquery()
                 )

        RIIKLIKUD_OPPEKAVAD = ('1010101',
                               '2010101',
                               '3010101')
        q = (model.Session.query(model.Opilane.id,
                                 model.Opilane.isikukood,
                                 model.Opilane.eesnimi,
                                 model.Opilane.perenimi,
                                 model.Koht.nimi,
                                 sa.func.count(Eesti.columns.kasutaja_id).label('eestik'),
                                 sa.func.count(Matem.columns.kasutaja_id).label('matem'),
                                 sa.func.coalesce(Valik.columns.cnt,0).label('valik')
                                 )
             .filter(model.Opilane.klass=='9')
             .filter(model.Opilane.seisuga>seisuga)
             .filter(model.Opilane.oppekava_kood.in_(RIIKLIKUD_OPPEKAVAD))
             .outerjoin(model.Opilane.kasutaja)
             .outerjoin(model.Opilane.koht)
             .outerjoin((Eesti, Eesti.columns.kasutaja_id==model.Kasutaja.id))             
             .outerjoin((Matem, Matem.columns.kasutaja_id==model.Kasutaja.id))
             .outerjoin((Valik, Valik.columns.kasutaja_id==model.Kasutaja.id))             
             .filter(sa.or_(Eesti.columns.kasutaja_id==None,
                            Matem.columns.kasutaja_id==None,
                            Valik.columns.kasutaja_id==None,
                            Valik.columns.cnt!=1
                            ))
             .group_by(model.Opilane.id,
                       model.Opilane.isikukood,
                       model.Opilane.eesnimi,
                       model.Opilane.perenimi,
                       model.Koht.nimi,
                       Valik.columns.cnt)
             )
        #model.log_query(q)
        if self.c.xls:
            return self._index_xls(q)

        self.c.prepare_header = self._prepare_header
        self.c.prepare_item = self._prepare_item
        return q

    def _search12(self):
        "12. klassi kontroll"
        # otsime nende seast, kelle andmeid on peale 1. septembrit uuendatud
        today = date.today()
        year = today.month < 9 and today.year - 1 or today.year
        seisuga = date(year, 9, 1)

        # Meil on vaja teha päring registreerimise kontrolli kohta ja selle väljundiks on nimekiri 12. klassi õpilastest,
        # kes ei ole registreeritud kolmele kohustuslikule eksamile või ei ole esitanud tunnistust riigieksami asendamiseks

        # on regatud või on varem sooritanud
        f_regatud_voi_piisav = sa.or_(model.Sooritaja.staatus==const.S_STAATUS_REGATUD,
                                      sa.and_(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD,
                                              sa.or_(model.Sooritaja.pallid >= 20,
                                                     sa.and_(model.Sooritaja.pallid >= 1,
                                                             sa.or_(model.Sooritaja.oppeaasta < 2002,
                                                                    model.Sooritaja.oppeaasta >= 2014)))
                                              )
                                      )

        # Kohustuslikud eksamid
        # 1)	Eesti keel (peab olema täidetud üks kolmest tingimusest):
        #     -Eesti keel 
        #     -eesti keel teise keelena
        #     -väljastatud eesti keele C1-taseme või kõrgtaseme tunnistus
       
        tasemed = (const.KEELETASE_C1, const.KEELETASE_KORG)
        Eesti = (model.Session.query(model.Sooritaja.kasutaja_id)
                 .join(model.Sooritaja.test)
                 .filter(model.Sooritaja.testimiskord_id!=None)
                 .filter(sa.or_(
                     sa.and_(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM,
                             model.Test.aine_kood.in_((const.AINE_ET, const.AINE_ET2)),
                             f_regatud_voi_piisav),
                     sa.and_(model.Test.testiliik_kood.in_((const.TESTILIIK_TASE, const.TESTILIIK_RIIGIEKSAM)),
                             model.Sooritaja.keeletase_kood.in_(tasemed),
                             model.Sooritaja.tulemus_piisav==True)
                     ))
                 .subquery()
                 )

        # 2)matemaatika riigieksam
        Matem = (model.Session.query(model.Sooritaja.kasutaja_id)
                 .join(model.Sooritaja.test)
                 .filter(model.Sooritaja.testimiskord_id!=None)
                 .filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM)
                 .filter(model.Test.aine_kood==const.AINE_M)
                 .filter(f_regatud_voi_piisav)
                 .subquery()
                 )

        # 3)Võõrkeeleksam (täidetud peab olema üks järgmistest tingimustest)
        #     -Inglise keele riigieksam või rahvusvaheline eksam
        #     -Saksa, vene või prantsuse keele rahvusvaheline eksam B1 või B2 tase
        #     -Sisestatud rahvusvaheliselt tunnustatud võõrkeeleeksami tunnistus
        Voork = (model.Session.query(model.Sooritaja.kasutaja_id)
                 .join(model.Sooritaja.test)
                 .filter(model.Sooritaja.testimiskord_id!=None)
                 .filter(sa.or_(
                    sa.and_(model.Test.testiliik_kood.in_((const.TESTILIIK_RIIGIEKSAM,
                                                           const.TESTILIIK_RV)),
                            model.Test.aine_kood==const.AINE_EN),
                    sa.and_(model.Test.testiliik_kood==const.TESTILIIK_RV,
                            model.Test.aine_kood.in_((const.AINE_DE, const.AINE_RU, const.AINE_FR)),
                            model.Test.testitasemed.any(
                                model.Testitase.keeletase_kood.in_((const.KEELETASE_B1, const.KEELETASE_B2))))
                    ))
                 .filter(f_regatud_voi_piisav)               
                 .subquery()
                 )
        Rvtun = (model.Session.query(model.Tunnistus.kasutaja_id)
                 .join(model.Tunnistus.rvsooritaja)
                 .filter(model.Rvsooritaja.arvest_lopetamisel==True)
                 .subquery()
                 )

        q = (model.Session.query(model.Opilane.id,
                                 model.Opilane.isikukood,
                                 model.Opilane.eesnimi,
                                 model.Opilane.perenimi,
                                 model.Koht.nimi,
                                 sa.func.count(Eesti.columns.kasutaja_id),
                                 sa.func.count(Matem.columns.kasutaja_id),
                                 sa.func.count(Voork.columns.kasutaja_id),
                                 sa.func.count(Rvtun.columns.kasutaja_id))
             .filter(model.Opilane.klass.in_(('G3', 'G12')))
             .filter(model.Opilane.seisuga>seisuga)
             .outerjoin(model.Opilane.kasutaja)
             .outerjoin(model.Opilane.koht)
             .outerjoin((Eesti, Eesti.columns.kasutaja_id==model.Kasutaja.id))             
             .outerjoin((Matem, Matem.columns.kasutaja_id==model.Kasutaja.id))
             .outerjoin((Voork, Voork.columns.kasutaja_id==model.Kasutaja.id))             
             .outerjoin((Rvtun, Rvtun.columns.kasutaja_id==model.Kasutaja.id))             
             .filter(sa.or_(Eesti.columns.kasutaja_id==None,
                            Matem.columns.kasutaja_id==None,
                            sa.and_(Voork.columns.kasutaja_id==None,
                                    Rvtun.columns.kasutaja_id==None)
                            ))
             .group_by(model.Opilane.id,
                       model.Opilane.isikukood,
                       model.Opilane.eesnimi,
                       model.Opilane.perenimi,
                       model.Koht.nimi)
             )
        #model.log_query(q)
        if self.c.xls:
            return self._index_xls(q)

        self.c.prepare_header = self._prepare_header
        self.c.prepare_item = self._prepare_item
        return q
    
    def _prepare_header(self):
        "Loetelu päis"
        if self.c.klass == '9':
            return [('opilane.isikukood', _("Isikukood")),
                    ('opilane.eesnimi', _("Eesnimi")),
                    ('opilane.perenimi', _("Perekonnanimi")),
                    ('koht.nimi', _("Kool")),
                    ('eestik', _("Eesti keel")),
                    ('matem', _("Matemaatika")),
                    ('valik', _("Valik"))]
        else:
            return [('opilane.isikukood', _("Isikukood")),
                    ('opilane.eesnimi', _("Eesnimi")),
                    ('opilane.perenimi', _("Perekonnanimi")),
                    ('koht.nimi', _("Kool")),
                    (None, _("Eesti keel")),
                    (None, _("Matemaatika")),
                    (None, _("Võõrkeel"))]

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        h = self.h
        if self.c.klass == '9':
            cnt_v = rcd[7]
            item = [rcd[1],
                    rcd[2],
                    rcd[3],
                    rcd[4],
                    h.sbool(rcd[5]),
                    h.sbool(rcd[6]),
                    cnt_v > 1 and cnt_v or h.sbool(cnt_v),
                    ]
        else:
            item = [rcd[1],
                    rcd[2],
                    rcd[3],
                    rcd[4],
                    h.sbool(rcd[5]),
                    h.sbool(rcd[6]),
                    h.sbool(rcd[7] or rcd[8]),
                    ]
        return item
    
