from itertools import groupby

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class LabiviijakaskkirjadController(BaseResourceController):
    """Läbiviijate käskkirjad
    """
    _permission = 'aruanded-labiviijakaskkirjad'
    _INDEX_TEMPLATE = 'ekk/otsingud/labiviijakaskkirjad.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/labiviijakaskkirjad_list.mako'
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi'
    _ignore_default_params = ['csv', 'format']
    _SEARCH_FORM = forms.ekk.otsingud.LabiviijakaskkirjadForm # valideerimisvorm otsinguvormile   
    
    def _query(self):
        # leiame (piirkondlikule) kasutajale lubatud piirkondade loetelu
        kasutaja = self.c.user.get_kasutaja()
        testiliik = self.request.params.get('testiliik')
        lubatud = kasutaja.get_piirkonnad_id(self._permission, const.BT_SHOW, testiliik=testiliik)
        if None not in lubatud:
            self.c.piirkond_filtered = lubatud
        else:
            self.c.piirkond_filtered = None
        
        return model.SessionR.query(model.Kasutaja.id)

    def _search_default(self, q):
        return None

    def _search(self, q1):
        c = self.c
        self.Aine_kl = sa.orm.aliased(model.Klrida, name='aine_kl')
        
        if not (c.khindajad or c.shindajad or c.intervjuu or c.vaatlejad or c.komisjoniliikmed):
            # paginaatorist tulles ei ole nuppu
            if c.nupp == 'khindajad':
                c.khindajad = True
            elif c.nupp == 'shindajad':
                c.shindajad = True                
            elif c.nupp == 'intervjuu':
                c.intervjuu = True                
            elif c.nupp == 'vaatlejad':
                c.vaatlejad = True
            elif c.nupp == 'komisjoniliikmed':
                c.komisjoniliikmed = True                

        if not (c.nousolek or c.polenous or c.kaskkirjas or c.leping or c.labiviijad):
            # peab valima vähemalt 1 linnukese
            c.labiviijad = True
                
        c.seotud_testiga = c.labiviijad or c.nousolek or c.polenous or c.leping

        format = self.request.params.get('format')       
        if format == 'csv':
            self.header, fields = self._header_csv()
            q = model.SessionR.query(*fields).distinct()
            q = self._filter_q(q, outer_leping=True)
            if q:
                q = q.outerjoin(model.Testileping.leping)
        else:
            join_koht = (c.shindajad or c.intervjuu) and c.labiviijad
            self.header, fields = self._header(join_koht)

            q = model.SessionR.query(*fields).distinct()
            q = self._filter_q(q, join_koht=join_koht)
        #model.log_query(q)
        return q

    def _header(self, join_koht):
        c = self.c
        li = [model.Kasutaja.id,
              model.Kasutaja.eesnimi,
              model.Kasutaja.perenimi,
              model.Kasutaja.isikukood,
              ]
        header = [('kasutaja.eesnimi', _("Eesnimi")),
                  ('kasutaja.perenimi', _("Perekonnanimi")),
                  ('kasutaja.isikukood', _("Isikukood")),
                  ]
                  
        if join_koht:
            li.append(model.Koht.nimi)
            header.append(('koht.nimi', _("Soorituskoht")))
                           
        if c.shindajad or c.khindajad or c.intervjuu:
            if c.seotud_testiga:
                li.append(self.Aine_kl.nimi)
                header.append(('aine_kl.nimi', _("Õppeaine")))
            li.append(model.Kasutaja.id)
            header.append((None, _("Töökoht"), self._get_tookoht))

        li.extend([model.Kasutaja.epost,
                   model.Kasutaja.telefon,
                   model.Aadress.tais_aadress,
                   model.Aadress.kood2,
                   model.Kasutaja.postiindeks,
                   model.Kasutaja.id,
                   model.Profiil.arveldusarve,
                   model.Profiil.on_pensionar,
                   model.Profiil.on_psammas,
                   model.Profiil.oma_markus,
                   ])
        header.extend([('kasutaja.epost', _("E-posti aadress")),
                       ('kasutaja.telefon', _("Telefon")),
                       ('aadress.tais_aadress', _("Postiaadress")),
                       ('aadress.kood2', _("Linn"), lambda x: model.Aadresskomponent.get_str_by_tase_kood(2, x, True) or ''),
                       ('kasutaja.postiindeks', _("Postiindeks")),
                       (None, _("Piirkond"), self._get_piirkond),
                       ('profiil.arveldusarve', _("Arveldusarve")),
                       ('profiil.on_pensionar', _("Vanaduspensionär"), self.h.sbool),
                       ('profiil.on_psammas', _("Liitunud kogumispensioni II sambaga"), self.h.sbool),
                       ('profiil.oma_markus', _("Läbiviija märkused")),
                       ])
        return header, li

    def _header_csv(self):
        c = self.c

        header = [('labiviijaleping.id', _("Lepingu ID")),
                  ('kasutaja.isikukood', _("Isikukood")),
                  ('kasutaja.perenimi', _("Perekonnanimi")),
                  ('kasutaja.eesnimi', _("Eesnimi")),
                  ('aadress.tais_aadress', _("Aadress")),                  
                  ('kasutaja.postiindeks', _("Indeks")),
                  ('kasutaja.telefon', _("Telefon")),
                  ('kasutaja.epost', _("E-post")),
                  ('profiil.arveldusarve', _("Arveldusarve nr")),
                  ('profiil.on_pensionar', _("On vanaduspensionär"), self.h.sbool),
                  ('profiil.on_psammas', _("On II pensionisammas"), self.h.sbool),
                  ('profiil.psammas_protsent', '2% / 3%'),
                  ('profiil.on_ravikindlustus', _("On kehtiv ravikindlustus"), self.h.sbool),
                  ('labiviijaleping.noustunud', _("Lepingu sõlmimise kuupäev"), self.h.str_from_date),
                  ('leping.nimetus', _("Lepingu liik")),
                  (None, _("Töökoht"), self._get_tookoht),
                  ('profiil.oma_markus', _("Läbiviija märkused")),
                  ]
                  
        li = [model.Kasutaja.id,
              model.Labiviijaleping.id,
              model.Kasutaja.isikukood,
              model.Kasutaja.perenimi,
              model.Kasutaja.eesnimi,
              model.Aadress.tais_aadress,
              model.Kasutaja.postiindeks,
              model.Kasutaja.telefon,
              model.Kasutaja.epost,
              model.Profiil.arveldusarve,
              model.Profiil.on_pensionar,
              model.Profiil.on_psammas,
              model.Profiil.psammas_protsent,
              model.Profiil.on_ravikindlustus,
              model.Labiviijaleping.noustunud,
              model.Leping.nimetus,
              model.Kasutaja.id,
              model.Profiil.oma_markus]

        return header, li

    def _order_able(self, q, field):
        """Kontrollitakse, kas antud välja järgi on võimalik sortida
        """
        c = self.c
        if field.startswith('aine_kl') and \
          (not c.seotud_testiga or not (c.shindajad or c.khindajad or c.intervjuu) \
           or self.request.params.get('format')):       
            # ei saa aine järgi sortida, aine pole väljundis
            rc = False
        else:
            rc = super()._order_able(q, field)
        log.debug(f'ORDER_ABLE {field}={rc}')
        return rc
    
    def _filter_q(self, q, outer_leping=False, join_koht=False):
        c = self.c

        vastvorm = None
        if c.khindajad:
            grupid_id = (const.GRUPP_HINDAJA_K,)
            nousolek_field = model.Nousolek.on_hindaja
            vastvorm = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I)
        elif c.shindajad:
            grupid_id = (const.GRUPP_HINDAJA_S, const.GRUPP_HINDAJA_S2)
            nousolek_field = model.Nousolek.on_hindaja
            vastvorm = (const.VASTVORM_SH, const.VASTVORM_SP)
        elif c.intervjuu:
            grupid_id = (const.GRUPP_INTERVJUU,)
            nousolek_field = model.Nousolek.on_intervjueerija
        elif c.vaatlejad:
            grupid_id = (const.GRUPP_VAATLEJA,)
            nousolek_field = model.Nousolek.on_vaatleja
        elif c.komisjoniliikmed:
            grupid_id = (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES)
            nousolek_field = None
        else:
            log.debug('ROLL VALIMATA')
            return

        # millistes piirkondades otsime
        piirkonnad_id = None
        if c.piirkond_id:
            piirkond = model.Piirkond.get(c.piirkond_id)
            piirkonnad_id = piirkond.get_alamad_id()

        # kas pole õigust kõigi piirkondade korraldamiseks?
        if c.piirkond_filtered:
            # piirkondlik korraldaja ei või kõiki kohti vaadata
            if piirkonnad_id:
                # jätame otsingust välja piirkonnad, kus pole lubatud
                piirkonnad_id = set(piirkonnad_id).intersection(c.piirkond_filtered)
            else:
                # otsime ainult lubatud piirkondades
                piirkonnad_id = c.piirkond_filtered
        
        if c.labiviijad:
            # läbiviijaks määratud isikud
            c.labiviijad = '1'
            q = (q.join(model.Kasutaja.labiviijad)
                 .filter(model.Labiviija.kasutajagrupp_id.in_(grupid_id))
                 .join(model.Labiviija.toimumisaeg)
                 )
            if join_koht:
                q = (q.join(model.Labiviija.testikoht)
                     .join(model.Testikoht.koht)
                     )
        if piirkonnad_id is not None:
            # otsime piirkonna järgi
            if join_koht:
                # otsime tegeliku läbiviimise piirkonna järgi
                q = q.filter(model.Koht.piirkond_id.in_(piirkonnad_id))
            else:
                # otsime piirkonna järgi, kus isik on nõus läbi viima
                q = q.filter(model.Kasutaja.kasutajapiirkonnad.any(
                    model.Kasutajapiirkond.piirkond_id.in_(piirkonnad_id)))
                    
        if c.nousolek or c.polenous:
            # nõusoleku teatanud isikud
            q = q.join(model.Kasutaja.nousolekud)
            if nousolek_field is None:
                # otsitakse komisjoniliikmeid, aga nemad ei saa nõusolekut anda
                self.error(_("Komisjoniliikmete nõusolekut ei küsita"))
                q = q.filter(model.Nousolek.id==-1)
            elif c.nousolek and c.polenous:
                q = q.filter(nousolek_field!=None)
            elif c.nousolek:
                q = q.filter(nousolek_field==True)
            elif c.polenous:
                q = q.filter(nousolek_field==False)
            if c.labiviijad:
                q = q.filter(model.Nousolek.toimumisaeg_id==model.Toimumisaeg.id)
            else:
                q = q.join(model.Nousolek.toimumisaeg)

        if c.seotud_testiga:
            # kui on olemas seos testiga
            q = (q.join(model.Toimumisaeg.testimiskord)
                 .join(model.Testimiskord.test)
                 )
            if vastvorm:
                q = q.join(model.Toimumisaeg.testiosa)
                q = q.filter(model.Testiosa.vastvorm_kood.in_(vastvorm))

        q = (q.outerjoin(model.Kasutaja.aadress)
             .outerjoin(model.Kasutaja.profiil)
             )

        if c.leping or outer_leping:
            # grupi tingimus
            if c.labiviijad:
                fg = model.Testileping.kasutajagrupp_id==model.Labiviija.kasutajagrupp_id
            elif len(grupid_id) == 1:
                fg = model.Testileping.kasutajagrupp_id==list(grupid_id)[0]
            else:
                fg = model.Testileping.kasutajagrupp_id.in_(grupid_id)

        if c.leping:
            # eraldame need, kellel vähemalt mõni vajalik leping on olemas
            q = (q.join(model.Kasutaja.labiviijalepingud)
                 .filter(sa.or_(model.Labiviijaleping.testsessioon_id==model.Testimiskord.testsessioon_id,
                                model.Labiviijaleping.testsessioon_id==None))
                 .filter(model.Labiviijaleping.leping.has(model.Leping.yldleping==False))
                 #.join(model.Labiviijaleping.leping)
                 #.filter(model.Leping.yldleping==False)
                 #.join(model.Leping.testilepingud)
                 .join((model.Testileping, model.Testileping.leping_id==model.Labiviijaleping.leping_id))
                 .filter(model.Testileping.testimiskord_id==model.Testimiskord.id)
                 .filter(fg))
            if c.lepingkpv:
                q = q.filter(model.Labiviijaleping.noustunud>=c.lepingkpv)
                
            # kontrollime, et kõik vajalikud lepingud oleks olemas
            f1 = (sa.select([model.Testileping.id])
                  .where(model.Testileping.testimiskord_id==model.Testimiskord.id)
                  .where(fg)
                  .correlate(model.Testimiskord)#.table)
                  )
            if c.labiviijad:
                f1 = f1.correlate(model.Labiviija)#.table)

            f2 = (sa.select([model.Labiviijaleping.id])
                  .where(model.Labiviijaleping.leping_id==model.Testileping.leping_id)
                  .where(model.Labiviijaleping.kasutaja_id==model.Kasutaja.id)
                  .where(model.Testimiskord.id==model.Testileping.testimiskord_id)
                  .where(sa.or_(
                      model.Labiviijaleping.testsessioon_id==model.Testimiskord.testsessioon_id,
                      model.Labiviijaleping.testsessioon_id==None)
                         )
                  .correlate(model.Testileping)#.table)
                  .correlate(model.Testimiskord)#.table)
                  .correlate(model.Kasutaja)#.table)
                  )
            # testimiskord ei eelda sellist lepingut, millega kasutaja pole nõustunud
            q = q.filter(~ sa.exists(f1.where(~ sa.exists(f2))))

        elif outer_leping:
            # leping pole nõutav, kuid näitame, kui see on (CSV korral)
            crit = sa.and_(model.Testileping.leping.has(model.Leping.yldleping==False), fg)
            if c.seotud_testiga:
                crit = sa.and_(crit, model.Testileping.testimiskord_id==model.Testimiskord.id)
            elif c.toimumisaeg_id:
                ta = model.Toimumisaeg.get(c.toimumisaeg_id)
                crit = sa.and_(crit, model.Testileping.testimiskord_id==ta.testimiskord_id)
                    
            q = q.outerjoin((model.Testileping, crit))

            crit = sa.and_(model.Labiviijaleping.kasutaja_id==model.Kasutaja.id,
                           model.Labiviijaleping.leping_id==model.Testileping.leping_id)
            if c.seotud_testiga:
                crit = sa.and_(crit,
                               sa.or_(model.Labiviijaleping.testsessioon_id==model.Testimiskord.testsessioon_id,
                                      model.Labiviijaleping.testsessioon_id==None))
            elif c.sessioon_id:
                crit = sa.and_(crit,
                               sa.or_(model.Labiviijaleping.testsessioon_id==c.sessioon_id,
                                      model.Labiviijaleping.testsessioon_id==None))

            q = q.outerjoin((model.Labiviijaleping, crit))

                    
        if c.kaskkirjas:
            # ainult käskkirja kantud
            f_kaskkirjas = []
            if c.vaatlejad:
                if c.kaskkirikpv:
                    f_kaskkirjas.append(model.Profiil.v_kaskkirikpv>=c.kaskkirikpv)
                else:
                    f_kaskkirjas.append(model.Profiil.v_kaskkirikpv!=None)
            if c.khindajad or c.shindajad or c.intervjuu:
                f = []
                f.append(model.Aineprofiil.kasutajagrupp_id.in_(grupid_id))
                if c.aine:
                    f.append(model.Aineprofiil.aine_kood==c.aine)
                elif c.seotud_testiga:
                    f.append(model.Aineprofiil.aine_kood==model.Test.aine_kood)                    
                if c.kaskkirikpv:
                    f.append(model.Aineprofiil.kaskkirikpv>=c.kaskkirikpv)
                else:
                    f.append(model.Aineprofiil.kaskkirikpv!=None)
                f_kaskkirjas.append(model.Kasutaja.aineprofiilid.any(sa.and_(*f)))
            if c.komisjoniliikmed:
                # komisjoniliikmed pole käskkirjas
                self.error(_("Komisjoniliikmeid ei märgita käskkirja"))
                f_kaskkirjas.append(model.Profiil.id==-1)
            q = q.filter(sa.or_(*f_kaskkirjas))

        if c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))

        if c.seotud_testiga:
            q = q.join((self.Aine_kl, sa.and_(self.Aine_kl.klassifikaator_kood=='AINE',
                                              self.Aine_kl.kood==model.Test.aine_kood)))
            q = self._filter_ta(q)
        model.log_query(q)
        return q
    
    def _filter_ta(self, q):
        if self.c.toimumisaeg_id:
            q = q.filter(model.Toimumisaeg.id==int(self.c.toimumisaeg_id))
        if self.c.alates:
            q = q.filter(model.Toimumisaeg.kuni>=self.c.alates)
        if self.c.kuni:
            q = q.filter(model.Toimumisaeg.alates<self.c.kuni+timedelta(1))
        if self.c.testiliik:
            q = q.filter(model.Test.testiliik_kood==self.c.testiliik)
        if self.c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(self.c.sessioon_id))
        if self.c.test_id:
            q = q.filter(model.Testimiskord.test_id==self.c.test_id)
        if self.c.aine:
            q = q.filter(model.Test.aine_kood==self.c.aine)
        return q

    def _get_tookoht(self, kasutaja_id):
        li = []
        for p in model.Pedagoog.query.\
                filter_by(kasutaja_id=kasutaja_id).\
                all():
            if p.kasutajagrupp_id == const.GRUPP_E_OPETAJA:
                buf = 'pedagoog'
            elif p.kasutajagrupp_id == const.GRUPP_E_ADMIN:
                buf = 'soorituskoha administraator'
            else:
                buf = ''
            if p.koht:
                buf = p.koht.nimi + ', ' + buf
            li.append(buf)
        if self.c.format == 'csv':
            buf = '|'.join(li)
        else:
            buf = ',<br/>\n'.join(li)
        return buf

    def _get_piirkond(self, kasutaja_id):

        if self.c.labiviijad or not self.c.nousolek:
            # kui otsitakse läbiviijaid ja nõusolijaid või ainult läbiviijaid
            # siis otsime läbiviimise piirkondi
            q = model.SessionR.query(model.Testikoht.koht_id).\
                join(model.Testikoht.toimumisaeg).\
                join(model.Toimumisaeg.testimiskord).\
                join(model.Testimiskord.test).\
                join(model.Testikoht.labiviijad).\
                filter(model.Labiviija.kasutaja_id==kasutaja_id)
            q = self._filter_ta(q)
            kohad_id = [koht_id for koht_id, in q.all()]
            q = model.SessionR.query(model.Piirkond.nimi)
            if kohad_id:
                q = q.filter(model.Piirkond.kohad.any(model.Koht.id.in_(kohad_id)))
            else:
                q = q.filter(model.Piirkond.id==-1) # ei ole tulemusi

        if self.c.nousolek and not (self.c.labiviijad and q.count()):
            # kui otsitakse ainult nõusolijaid või
            # nõusolijaid ja läbiviijaid, aga läbiviimispiirkonda ei leitud
            # siis otsime nõusoleku piirkondi
            q = model.SessionR.query(model.Piirkond.nimi).\
                filter(model.Piirkond.kasutajapiirkonnad.any(\
                model.Kasutajapiirkond.kasutaja_id==kasutaja_id))

        li = [p_nimi for p_nimi, in q.all()]
        if self.c.format == 'csv':
            buf = ', '.join(li)
        else:
            buf = ',<br/>\n'.join(li)
        return buf

    def _prepare_items(self, c_items=None):
        """Päringutulemuste paigutamine väljastamiseks sobivale kujule"""

        header = [r[:2] for r in self.header]
        items = []

        for rcd in c_items or self.c.items:
            item = []
            for n, r_header in enumerate(self.header):
                value = rcd[n+1]
                if len(r_header) > 2:
                    value = r_header[2](value)
                item.append(str(value or ''))
            items.append(item)

        return header, items

    def _paginate(self, q):
        # et failina laadimisel ei pagineeriks
        format = self.request.params.get('format')
        if format:
            return q.all()
        else:
            return BaseResourceController._paginate(self, q)

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        format = self.request.params.get('format')       
        if format == 'csv':
            data, filename = self._render_csv()
            mimetype = const.CONTENT_TYPE_CSV
            return utils.download(data, filename, mimetype)            

        self.c.prepare_items = self._prepare_items
        if self.request.params.get('partial'):
            return self.render_to_response(self._LIST_TEMPLATE)
        else:
            return self.render_to_response(self._INDEX_TEMPLATE)

    def _render_csv(self):
        header, items = self._prepare_items()
        data = self._csv_data(header, items)
        data = utils.encode_ansi(data)
        if self.c.khindajad:
            filename = 'khindajad.csv'
        elif self.c.shindajad:
            filename = 'shindajad.csv'
        elif self.c.intervjuu:
            filename = 'intervjueerijad.csv'
        elif self.c.vaatlejad:
            filename = 'vaatlejad.csv'
        elif self.c.komisjoniliikmed:
            filename = 'komisjoniliikmed.csv'            
        else:
            filename = 'labiviijad.csv'
        return data, filename

