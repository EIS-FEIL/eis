import json
import html
from pyramid.response import FileResponse
from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class TagasisidevarController(BaseResourceController):
    """Tagasisidevormi avaldise lisamine
    """
    _permission = 'ekk-testid'
    _EDIT_TEMPLATE = 'ekk/testid/tagasiside.fbvar.mako'
    _actions = 'new'
    _ITEM_FORM = forms.ekk.testid.TagasisideVarForm

    def new(self):
        return self._edit()
    
    def _edit(self):
        self._get_opt()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _get_opt(self):
        c = self.c
        liik = self.request.params.get('liik')
        try:
            liik = int(liik)
        except:
            pass

        if liik == model.Tagasisidevorm.LIIK_KIRJELDUS:
            # testi kirjeldus, ainult staatiline sisu
            self.error(_("Testi kirjelduse osas ei saa muutujaid kasutada!"))
            return
        is_individual = model.Tagasisidevorm.is_individual(liik)
        c.data1 = self._cmds_general(is_individual)
        c.data2 = self._cmds_opip(is_individual)
        c.data3 = self._cmds_loodus(is_individual)

    def _cmds_general(self, is_individual):
        "Yldised funktsioonid"
        data = [('T.test_nimi', 'string', _("Testi nimetus"))]
                     
        if is_individual:
            # õpilast kirjeldavad muutujad
            data += [('T.nimi', 'string', _("Sooritaja ees- ja perekonnanimi")),
                     ('T.sugu', 'string', _("Sooritaja sugu")),
                     ('T.sooritamiskpv', 'string', _("Sooritamise kuupäev")),
                     ('T.tookood', 'string', _("Töökood (esimeses testiosas)")),
                     ('T.AJAKULU', 'integer', _("Sooritamise ajakulu minutites")),
                     ('T.RESULT', 'float', _("Testi tulemus pallides")),
                     ('T.kasutaja_id', 'integer', _("EISi kasutaja ID")),
                     ('T.sooritaja_id', 'integer', _("Sooritaja ID")),
                     ('T.tasktime', 'integer', _("Ülesande ajakulu sekundites"),
                      [('kood','string', _("Ülesande kood kujul TASK_X"))]
                      ),
                     ('T.status', 'integer', _("Testiosa sooritamise olek, väärtused: 8 - tehtud, 9 - eemaldatud, 10 - puudus, 11 - vabastatud"),
                      [('jrk','integer',_("Testiosa jrk nr (alates 1-st)"))]
                      ),
                     ('T.pta', 'float', _("Hindamisaspekti pallid (kaaluga korrutatud)"),
                      [('kood','string', _("Hindamisaspekti kood"))]
                      ),
                     ('T.rpta', 'float', _("Hindamisaspekti punktid (kaaluga korrutamata)"),
                      [('kood','string', _("Hindamisaspekti kood"))]
                      ),
                     ('T.pt', 'float', _("Küsimuse pallid"),
                      [('kood','string', _("Küsimuse kood"))]
                      ),
                     ('T.rpt', 'float', _("Küsimuse punktid"),
                      [('kood','string', _("Küsimuse kood"))]
                      ),
                     ('T.rptmax1', 'float', _("Küsimuse punktid jagatuna max punktide arvuga"),
                      [('kood','string', _("Küsimuse kood"))]
                      ),
                     ('T.respn', 'float', _("Ülesannete, küsimuste või hindamisaspektide tulemus protsentides, välja jäetakse need, mille hindamisel on märgitud tehnilise vea tõttu null punkti"),
                      [('koodid','list', _("Ülesannete, küsimuste või aspektide koodid"))]
                      ),
                     ('T.val', 'list', _("Küsimuse vastuste jada"),
                      [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                      ),
                     ('T.val1', 'string', _("Küsimuse vastus (tekstina)"),
                      [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                      ),
                     ('T.val1n', 'integer', _("Küsimuse vastus (täisarvuna)"),
                      [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                      ),
                     ('T.val1f', 'float', _("Küsimuse vastus (reaalarvuna)"),
                      [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                      ),
                     ('T.match_count', 'integer', _("Tabamuste loenduri väärtus (täisarvuna)"),
                      [('kood', 'string', _("Ülesande ja loenduri kood kujul TASK_X.Y"))]
                      ),
                     ('T.np_name', 'string', _("Tagasiside tunnuse nimetus"),
                      [('kood', 'string', _("Tunnuse kood"))]
                      ),
                     ('T.np_val', 'list', _("Tagasiside tunnuse väärtuste jada"),
                      [('kood', 'string', _("Tunnuse kood"))]
                      ),
                     ('T.np_val1', 'string', _("Tagasiside tunnuse väärtus (tekstina)"),
                      [('kood', 'string', _("Tunnuse kood"))]
                      ),
                     ('T.np_val1n', 'integer', _("Tagasiside tunnuse väärtus (täisarvuna)"),
                      [('kood', 'string', _("Tunnuse kood"))]
                      ),
                     ('T.np_val1f', 'float', _("Tagasiside tunnuse väärtus (reaalarvuna)"),
                      [('kood', 'string', _("Tunnuse kood"))]
                      ),
                     ('T.np_val1p', 'float', _("Tagasiside tunnuse väärtus protsendina vahemiku maksimumist (tunnusel min ja max väärtused peavad olema kirjeldatud)"),
                      [('kood', 'string', _("Tunnuse kood"))]
                      ),
                     ('T.ns_txt', 'string', _("Tunnuse tagasiside õpilasele"),
                      [('kood', 'string', _("Tunnuse kood")),
                       ('seq', 'integer', _("Tagasiside jrk nr, võib puududa; kui on antud, siis väljastatakse tagasiside ainult juhul, kui sooritaja sai antud jrk nr-ga tagasiside"))]
                      ),
                     ('T.ns_txt_op', 'string', _("Tunnuse tagasiside õpetajale"),
                      [('kood', 'string', _("Tunnuse kood")),
                       ('seq', 'integer', _("Tagasiside jrk nr, võib puududa; kui on antud, siis väljastatakse tagasiside ainult juhul, kui sooritaja sai antud jrk nr-ga tagasiside"))]                       
                      ),
                    ]
        else:
            # gruppi kirjeldavad muutujad
            data += [('T.sooritamiskpv', 'string', _("Sooritamise kuupäev")),
                     ('T.klass', 'string', _("Klass")),
                     ('T.nimi', 'string', _("Kool ja klass")),
                     ('T.kool', 'string', _("Kool")),
                     ('T.opetaja', 'string', _("Õpetaja (õpetaja järgi pärides)")),
                     ('T.nimekiri', 'string', _("Nimekirja nimetus")),
                     ('T.AJAKULU', 'integer', _("Keskmine sooritamise ajakulu minutites")),
                     ('T.is_total', 'boolean', _("Kas on üleriigiline rühm (true) või koolisisene (false)")),
                     ('T.g_count', 'integer', _("Sooritajate arv rühmas"),
                      [('sugu', 'string', _("Sugu: M - poisid, N - tüdrukud; parameetri puudumisel mõlemad sood kokku"))]
                      ),
                     ('T.g_result_pro', 'float', _("Keskmine testitulemus protsentides"),
                      [],
                      ),
                      ]
        return data

    def _cmds_opip(self, is_individual):
        "Õpipädevustestide funktsioonid"
        if is_individual:
            data = []
        else:
            data = [('T.atgrupp_nimi', 'string', _("Grupi nimetus"),
                      [('grupp_id', 'integer', _("Grupi ID"))]
                      ),
                     ('T.np_name', 'string', _("Tagasiside tunnuse nimetus"),
                      [('kood', 'string', _("Tunnuse kood"))]
                      ),
                     ('T.np_nimi', 'string', _("Tagasiside tunnuse nimetus"),
                      [('np_id', 'integer', _("Tunnuse ID"))]
                      ),
                     ('T.list_atgrupid_id', 'list', _("Gruppide loetelu"),
                      [],
                      ),
                     ('T.list_atgrupp_np_id', 'list', _("Grupi tagasisidetunnuste loetelu"),
                      [('grupp_id', 'integer', _("Grupi ID (kui on None, siis väljastatakse grupita tunnuste loetelu)")),
                       ('on_opilane', 'boolean', _("Kas väljastada õpilase tagasiside tunnused")),
                       ('op_grupp', 'boolean', _("Kas väljastada rühma tagasiside tunnused")),
                       ]
                      ),
                     ('T.get_np_id', 'integer', _("Tagasiside tunnuse ID"),
                      [('kood', 'string', _("Tunnuse kood")),
                       ]
                      ),
                     ('T.is_npid_sryhm', 'integer', _("Kas tunnusel on sooritusrühmad"),
                      [('np_id', 'integer', _("Tunnuse ID"))],
                      ),
                     ('T.is_npid_sryhm_pooratud', 'integer', _("Kas tunnusel on sooritusrühmad ja kas värvid on pööratud järjekorras"),
                      [('np_id', 'integer', _("Tunnuse ID"))],
                      ),
                     ('T.npval_range', 'list', _("Sooritusrühmadeta tunnuse võimalike väärtuste loetelu (grupi profiililehe parempoolsete veergude kuvamiseks)"),
                      [],
                     ),
                     ('T.g_npid_sryhm_cnt', 'integer', _("Sooritajate arv antud sooritusrühmas"),
                      [('np_id', 'integer', _("Tunnuse ID")),
                       ('ps_protsent', 'integer', _("Sooritusrühm: 1 - madal; 2 - keskmine; 3 - kõrge")),
                       ]
                      ),
                     ('T.g_npid_resp_cnt', 'integer', _("Sooritajate arv rühmas, kellel antud tunnus on antud väärtusega"),
                      [('np_id', 'integer', _("Tunnuse ID")),
                       ('value', 'float|string', _("Tunnuse väärtus"))]
                      ),
                     ('T.g_npid_ns_txt_op', 'string', _("Tunnuse tagasiside tingimuse tekst õpetajale"),
                      [('np_id', 'integer', _("Tunnuse ID")),
                       ('seq', 'integer', _("Tagasiside tingimuse järjekorranumber (alates 0-st)"))]
                      ),
                     ('T.g_npid_ns_cnt', 'integer', _("Sooritajate arv rühmas, kellel antud tunnuse tagasiside vastab antud järjekorranumbriga tingimusele"),
                      [('np_id', 'integer', _("Tunnuse ID")),
                       ('seq', 'integer', _("Tagasiside tingimuse järjekorranumber (alatest 0-st)"))]
                      ),
                     ('T.g_np_ns_txt_op', 'string', _("Tunnuse tagasiside tingimuse tekst õpetajale"),
                      [('kood', 'string', _("Tunnuse kood")),
                       ('seq', 'integer', _("Tagasiside tingimuse järjekorranumber (alates 0-st)"))]
                      ),
                     ('T.g_np_ns_pro', 'float', _("Sooritajate protsent rühmas, kellel antud tunnuse tagasiside vastab antud järjekorranumbriga tingimusele, kõigist antud tunnuse tagasiside saanutest"),
                      [('kood', 'string', _("Tunnuse kood")),
                       ('seq', 'integer', _("Tagasiside tingimuse järjekorranumber (alatest 0-st)"))]
                      ),
                     ('T.g_np_ns_cnt', 'integer', _("Sooritajate arv rühmas, kellel antud tunnuse tagasiside vastab antud järjekorranumbriga tingimusele"),
                      [('kood', 'string', _("Tunnuse kood")),
                       ('seq', 'integer', _("Tagasiside tingimuse järjekorranumber (alatest 0-st)"))]
                      ),
                     ('T.g_lnk_np_ns_cnt', 'html', _("Sooritajate arv rühmas, kellel antud tunnuse tagasiside vastab antud järjekorranumbriga tingimusele, lingina, millel klikkimine kuvab nende sooritajate loetelu"),
                      [('kood', 'string', _("Tunnuse kood")),
                       ('seq', 'integer', _("Tagasiside tingimuse järjekorranumber (alatest 0-st)"))]
                      ),
                     
                    ]
        return data

    def _cmds_loodus(self, is_individual):
        "Loodusainete testide funktsioonid"
        
        data = [
            ('ltase', 'integer', _("Loodusteaduse tase (2017. aasta valem)"),
             [('Ta','float', _("Taseme A väärtus")),
              ('Tb','float', _("Taseme B väärtus")),
              ('Tc','float', _("Taseme C väärtus")),
              ('Td','float', _("Taseme D väärtus")),
              ]
             ),
            ('ltase2', 'integer', _("Loodusteaduse tase (2018. aasta valem)"),
             [('Ta','float', _("Taseme A väärtus")),
              ('Tb','float', _("Taseme B väärtus")),
              ('Tc','float', _("Taseme C väärtus")),
              ('Td','float', _("Taseme D väärtus")),
              ('Te','float', _("Taseme E väärtus")),
              ]
             ),
            ('T.a_resp_avg', 'float', _("Küsimuse keskmine vastus riigis (reaalarvuna)"),
             [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
             ),
            ('T.a_resp_min', 'float', _("Küsimuse min vastus riigis (reaalarvuna)"),
             [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
             ),
            ('T.a_resp_max', 'float', _("Küsimuse max vastus riigis (reaalarvuna)"),
             [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
             ),
            ]

        if not is_individual:
            data += [
                ('T.g_resp_avg', 'float', _("Küsimuse keskmine vastus rühmas (reaalarvuna)"),
                 [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                 ),
                ('T.g_resp_min', 'float', _("Küsimuse min vastus rühmas (reaalarvuna)"),
                 [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                ),
                ('T.g_resp_max', 'float', _("Küsimuse max vastus rühmas (reaalarvuna)"),
                 [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                 ),
                ('T.g_resp_pro', 'float', _("Küsimuse antud vastuse osakaal protsentides kõigist vastanutest rühmas"),
                 [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y")),
                  ('valik', 'string', _("Vastusevaliku kood"))]
                 ),
                ('T.g_resp_cnt', 'float', _("Küsimuse antud vastuse vastajate arv rühmas"),
                 [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y")),
                  ('valik', 'string', _("Vastus (valiku kood)"))]
                 ),
                ('T.g_np_resp_pro', 'float', _("Tagasiside tunnuse antud vastuse osakaal protsentides kõigist vastanutest rühmas"),
                 [('kood', 'string', _("Tunnuse kood")),
                  ('valik', 'integer|float|string', _("Vastus"))]
                 ),
                ('T.g_np_resp_avg', 'float', _("Tagasiside tunnuse keskmine vastus rühmas"),
                 [('kood', 'string', _("Tunnuse kood"))]
                 ),
                ('T.g_corr_np_k', 'float', _("Korrelatsiooni tagasiside tunnuse väärtuse ja valikküsimuse vastuse vahel rühmas (eeldusel, et tunnuse väärtus on arvuline ja küsimuse vastus on arvuline)"),
                 [('npkood', 'string', _("Tunnuse kood")),
                  ('tykood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                 ),
                ('T.g_resp_modes', 'list', _("Küsimuse kõige rohkem esinenud vastuste jada"),
                 [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                 ),
                ('T.g_resp_mode', 'float|string', _("Küsimuse kõige rohkem esinenud vastus"),
                 [('kood', 'string', _("Ülesande ja küsimuse kood kujul TASK_X.Y"))]
                 ),
                ]
            
        data += [
            ('T.g_np_resp_modes', 'list', _("Tagasiside tunnuse kõige rohkem esinenud vastuste jada"),
             [('kood', 'string', _("Tunnuse kood"))]
             ),
            ('T.g_np_resp_mode', 'float|string', _("Tagasiside tunnuse kõige rohkem esinenud vastus"),
             [('kood', 'string', _("Tunnuse kood"))]
             ),
            # ('T.get_keys', 'list', _("Küsimuse koodide list, mis vastavad antud regulaaravaldisele"),
            #  [('kood', 'string', _("Küsimuse koodi regulaaravaldis"))]
            #  ),
            ('cltase', 'string', _("Arvulise taseme vaste tähena"),
             [('tase', 'integer', _("Tase arvuna (0,1,2,3,4 või 5)")),
              ('tahed', 'string', _("Tasemetele vastavad tähed (nt 0ABCDE)"))]
             ),
            ('sltase', 'string', _("Arvulise taseme vaste sõnana (nulltase, algtase, kesktase, kõrgtase, tipptase)"),
             [('tase', 'integer', _("Tase arvuna (0,1,2,3 või 4)"))]
             ),
            ('sltase2', 'string', _("Arvulise taseme vaste sõnana"),
             [('tase', 'integer', _("Tase arvuna (0,1,2,3 või 4)")),
              ('sonad', 'dict', _("Vastavus arvude ja sõnade vahel"))]
             ),
            ('T.nptunnus_desc', 'string', _("Tagasiside tunnuse nimetus"),
             [('kood', 'string', _("Tunnuse kood"))]
             ),
            ('T.nptunnus_desc2', 'string', _("Tagasiside tunnuse kirjeldus"),
             [('kood', 'string', _("Tunnuse kood"))]
             ),
            ('T.nptunnus_desc3', 'string', _("Tagasiside tunnuse kirjeldus 2. isikus"),
             [('kood', 'string', _("Tunnuse kood"))]
             ),
            ]
        return data
            
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        c.testiosa_id = self.request.matchdict.get('testiosa_id')
        
    def _perm_params(self):
        return {'obj':self.c.test}

