# -*- coding: utf-8 -*- 
# $Id: testitulemused.py 544 2016-04-01 09:07:15Z ahti $

import pickle
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TestitulemusedController(BaseResourceController):
    """Tulemuste võrdlus, kui sama isiku tulemuse vahe hilisemaga on väga suur
    """
    _permission = 'aruanded-testitulemused'
    _INDEX_TEMPLATE = 'ekk/statistika/testitulemused.mako'
    _LIST_TEMPLATE = 'ekk/statistika/testitulemused_list.mako'
    _DEFAULT_SORT = 'kasutaja.isikukood,sooritaja.id'
    _SEARCH_FORM = forms.ekk.otsingud.TestitulemusedForm
    _ignore_default_params = ['csv']

    def _query(self):
        self.c.get_alatulemused = self._get_alatulemused
        return 

    def _search(self, q1):

        # koostame valitud testi struktuurile vastava andmete väljastamise päringu

        if not self.c.test_id or not self.c.erinevus:
            if self.c.otsi or self.c.csv:
                self.error(_("Palun valida test"))
            return 

        # valitud test, mille tulemustega võrreldakse teisi
        test = self.c.test = model.Test.get(self.c.test_id)

        # koostame filtri, mis leiab need sooritajad, kelle tulemuste erinevus on suur
        Sooritaja2 = sa.orm.aliased(model.Sooritaja, name='sooritaja2')
        Test2 = sa.orm.aliased(model.Test, name='test2')
        Testimiskord2 = sa.orm.aliased(model.Testimiskord, name='testimiskord2')

        # võrdluses olevate soorituste paaride päring 
        q = model.SessionR.query(model.Kasutaja.isikukood,
                                model.Kasutaja.synnikpv,
                                model.Sooritaja.id,
                                model.Sooritaja.algus,
                                model.Sooritaja.pallid,
                                model.Sooritaja.tulemus_protsent,
                                Sooritaja2.id,
                                Sooritaja2.algus,
                                Sooritaja2.pallid,
                                Sooritaja2.tulemus_protsent,
                                Sooritaja2.test_id,
                                Sooritaja2.keeletase_kood,
                                Testimiskord2.aasta,
                                sa.sql.func.abs(model.Sooritaja.pallid-Sooritaja2.pallid)).\
            join(model.Kasutaja.sooritajad)

        # võrdluse paremal poolel olevate soorituste testide päring
        q_test = model.SessionR.query(Sooritaja2.test_id).distinct()

        def _filter(q):
            q = (q.filter(model.Sooritaja.test_id==self.c.test_id)
                 .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
                 .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
                 .join(model.Sooritaja.test)
                 .join((Sooritaja2, sa.and_(Sooritaja2.kasutaja_id==model.Sooritaja.kasutaja_id,
                                            Sooritaja2.id!=model.Sooritaja.id,
                                            Sooritaja2.hindamine_staatus==const.H_STAATUS_HINNATUD,
                                            Sooritaja2.staatus==const.S_STAATUS_TEHTUD)))
                 .join((Testimiskord2, Testimiskord2.id==Sooritaja2.testimiskord_id))
                 .join((Test2, sa.and_(Test2.id==Sooritaja2.test_id,                                     
                                       Test2.aine_kood==model.Test.aine_kood)))
                 .filter(sa.sql.func.abs(model.Sooritaja.pallid-Sooritaja2.pallid)>=(self.c.erinevus-.00001))
                 )

            if self.c.testimiskord_id:
                q = q.filter(model.Sooritaja.testimiskord_id==self.c.testimiskord_id)
                #q = q.filter(sa.or_(model.Sooritaja.testimiskord_id==self.c.testimiskord_id,
                #                    Sooritaja2.testimiskord_id==self.c.testimiskord_id))
            if not self.c.vrld or self.c.vrld == 'tkord':
                q = q.filter(Sooritaja2.test_id==self.c.test_id)
            elif self.c.vrld == 'aine':
                q = q.filter(Test2.testiliik_kood==model.Test.testiliik_kood)
            elif self.c.vrld == 'tase':
                max_keeletase_kood = self.c.test.keeletase_kood
                q = (q.join(Test2.testitasemed)
                     .filter(model.Testitase.seq==1)
                     .filter(model.Testitase.keeletase_kood==max_keeletase_kood)
                     )

            return q

        q_test = _filter(q_test)
        q = _filter(q)

        # leiame valitud testi testiosade ja alatestide nimetused
        self.c.alaosaindeks1, self.c.headers1 = self._get_alaosaindeks([test.id])
        
        # leiame kõigi võrreldavate testide testiosade ja alatestide nimetused
        testid_id = [t_id for t_id, in q_test.all()]
        self.c.alaosaindeks2, self.c.headers2 = self._get_alaosaindeks(testid_id)

        if self.c.csv:
            return self._index_csv(q)

        return q

    def _get_alaosaindeks(self, testid_id):
        """Tagastatakse:
           alaosaindeks - dict, milles on iga testiosa nime jaoks vastav veeruindeks
                                ja iga testiosanime ja alatesti paari jaoks vastav veeruindeks
           headers - list, milles on iga veeru jaoks nimetus
        """
        q = model.SessionR.query(model.Testiosa.nimi, model.Alatest.nimi).distinct().\
            filter(model.Testiosa.test_id.in_(testid_id)).\
            outerjoin(model.Testiosa.alatestid)
        if len(testid_id) == 1:
            q = q.order_by(model.Testiosa.seq, model.Alatest.seq)
        else:
            q = q.order_by(model.Testiosa.nimi, model.Alatest.seq)

        def _uniq(li): 
            uli = []
            [uli.append(i) for i in li if not uli.count(i)]
            return uli

        alaosanimed = _uniq(list(q.all()))

        alaosaindeks = {}
        headers = []
        n_headers = n = 0

        for testiosanimi, alatestinimi in alaosanimed:
            if testiosanimi not in alaosaindeks:
                alaosaindeks[testiosanimi] = n
                headers.extend([(_("Protokoll")),
                                (_("Test")),
                                ])
                n += 2 # testiosal on: prot, soorituskood

            alaosaindeks[(testiosanimi,alatestinimi)] = n
            n += 1

            alaosanimi = alatestinimi or testiosanimi
            alaosanimi = alaosanimi[:2]
            headers.append(alaosanimi)

        return alaosaindeks, headers

    def _index_csv(self, q):
        """CSV faili allalaadimine"""

        c = self.c
        h = self.h

        # tabeli päis
        names = [_("Isikukood"),
                 _("Kuupäev"),
                 _("Tulemus"),
                 _("Protsent"),
                 ] + c.headers1 + \
                 [_("Kuupäev"),
                  _("Tulemus"),
                  _("Protsent"),
                  ] + c.headers2
        if c.test.keeletase_kood:
            names.append(_("Tase"))
        names += [_("Vahe"),
                  _("Aasta"),
                  ]

        # tabeli sisu
        items = []
        for rcd in q.all():
            ik, synnikpv, sooritaja_id, algus, pallid, tulemus_protsent,\
                sooritaja2_id, algus2, pallid2, tulemus_protsent2,\
                test2_id, keeletase2, aasta2, vahe = rcd
            row1 = c.get_alatulemused(sooritaja_id, c.alaosaindeks1)
            row2 = c.get_alatulemused(sooritaja2_id, c.alaosaindeks2)
            item = [ik,
                    h.str_from_date(algus),
                    h.fstr(pallid),
                    h.fstr(tulemus_protsent),
                    ] + \
                    [row1.get(r) or '' for r in range(len(c.headers1))] +\
                    [h.str_from_date(algus2),
                     h.fstr(pallid2),
                     h.fstr(tulemus_protsent2),
                     ] + \
                     [row2.get(r) or '' for r in range(len(c.headers2))]
            if c.test.keeletase_kood:
                keeletase_nimi = model.Klrida.get_str('KEELETASE', keeletase2, ylem_kood=c.test.aine_kood)
                item.append(keeletase_nimi)
            item += [h.fstr(vahe),
                     aasta2,
                     ]
            items.append(item)

        buf = ''
        for r in [names] + items:
            buf += ';'.join([str(v) for v in r]) + '\n'

        buf = utils.encode_ansi(buf)
        response = Response(buf) 
        response.content_type = 'text/csv'
        response.content_disposition = 'attachment;filename=testitulemused.csv'
        return response

    def _get_alatulemused(self, sooritaja_id, alaosaindeks):
        "Ühe soorituse testiosade ja alatestide tulemuste ja tähiste pärimine"
        c = self.c
        h = self.h
        row = {}

        # osaoskuste andmed
        q = model.SessionR.query(model.Testiprotokoll.tahised,
                                model.Sooritus.tahised,
                                model.Testiosa.nimi,
                                model.Sooritus.staatus,
                                model.Sooritus.pallid,
                                model.Alatest.nimi,                                    
                                model.Alatestisooritus.staatus,
                                model.Alatestisooritus.pallid)
        q = (q.filter(model.Sooritus.sooritaja_id==sooritaja_id)
             .join(model.Sooritus.testiosa)
             .outerjoin(model.Sooritus.testiprotokoll)
             .join((model.Alatestisooritus, model.Alatestisooritus.sooritus_id==model.Sooritus.id))
             .join((model.Alatest, model.Alatest.id==model.Alatestisooritus.alatest_id))             
             .order_by(model.Testiosa.seq, model.Alatest.seq))

        for rcd in q.all():
            s_prot_tahised, s_tahised,\
                testiosanimi, s_staatus, s_pallid, \
                alatestinimi, a_staatus, a_pallid = rcd

            # testiosa soorituse protokoll ja soorituse tähis
            n_s = alaosaindeks.get(testiosanimi)
            row[n_s] = s_prot_tahised
            row[n_s+1] = s_tahised

            if a_staatus:
                # alatesti tulemus
                n_a = alaosaindeks.get((testiosanimi,alatestinimi))
                if a_staatus == const.S_STAATUS_TEHTUD and a_pallid is not None:
                    osatulemus = h.fstr(a_pallid)
                    #osatulemus = '%s' % (int(round(a_pallid)))
                else:
                    osatulemus = c.opt.S_STAATUS.get(a_staatus)
            else:
                # alatestideta testiosa tulemus
                if s_staatus == const.S_STAATUS_TEHTUD and s_pallid is not None:
                    osatulemus = h.fstr(s_pallid)
                else:
                    osatulemus = c.opt.S_STAATUS.get(s_staatus)

            n_s = alaosaindeks.get((testiosanimi, alatestinimi))
            row[n_s] = osatulemus

        return row
