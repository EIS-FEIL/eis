from eis.model.entityhelper import *
from eis.model.koht import Koht, Piirkond
from eis.model.klassifikaator import Klrida
from .kasutajagrupp import Kasutajagrupp
log = logging.getLogger(__name__)

class Kasutajaroll(EntityHelper, Base):
    """Kasutajaroll (kasutajagrupp koos kontekstiga)
    """
   
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='kasutajarollid')
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True, nullable=False) # viide kasutajagrupile
    kasutajagrupp = relationship('Kasutajagrupp', foreign_keys=kasutajagrupp_id, back_populates='kasutajarollid')
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True, nullable=False) # viide soorituskohale, kus kasutajagurupp kehtib
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='kasutajarollid')
    piirkond_id = Column(Integer, ForeignKey('piirkond.id'), index=True) # viide piirkonnale, kus kasutajagrupp kehtib
    piirkond = relationship('Piirkond')
    aine_kood = Column(String(10)) # viide õppeainele, milles kasutajagrupp kehtib, klassifikaator AINE
    oskus_kood = Column(String(10)) # viide osaoskusele, milles kasutajagrupp kehtib, klassifikaator OSKUS
    testiliik_kood = Column(String(10)) # viide testiliigile, milles kasutajagrupp kehtib, klassifikaator TESTILIIK
    kehtib_alates = Column(Date, nullable=False) # õiguse kehtimise algus
    kehtib_kuni = Column(Date, nullable=False) # õiguse kehtimise lõpp
    rolliplokk = Column(Integer) # kui pole NULL, siis muudetakse kõigi sama väärtusega kirjete andmeid koos, nt mitme aine ainespetsialisti korral; väärtuseks võetakse ühe kirje ID
    lang = Column(String(2)) # keele kood (kasutajaliidese tõlkija korral)
    allkiri_jrk = Column(Integer) # järjekord vaideotsuse allkirjastamisel (kui roll on vaidekomisjoni liige)
    allkiri_tiitel1 = Column(String(60)) # dokumendi jaluses allkirjastaja tiitli rida 1 (ametinimetus)
    allkiri_tiitel2 = Column(String(60)) # dokumendi jaluses allkirjastaja tiitli rida 2 (roll komisjonis)
    kasutajarollilogid = relationship('Kasutajarollilogi', order_by=sa.desc(sa.text('Kasutajarollilogi.id')), back_populates='kasutajaroll')
    logging = True

    def get_str_values(self, values):
        li = []
        aine = self.aine_kood
        def sdate(dt):
            if dt and not (dt == const.MIN_DATE or dt == const.MAX_DATE):
                return dt.strftime('%d.%m.%Y')
            return ''

        for key, value in values:
            key1 = key
            if key == 'kasutajagrupp_id':
                grupp = self.kasutajagrupp or Kasutajagrupp.get(value)
                value1 = grupp.nimi
                key1 = 'grupp'
            elif key == 'koht_id':
                koht = value and Koht.get(value)
                value1 = koht and koht.nimi or ''
                key1 = 'koht'
            elif key == 'piirkond_id':
                prk = value and Piirkond.get(value)
                value1 = prk and prk.nimi or ''
                key1 = 'piirkond'
            elif key == 'aine_kood':
                aine = value
                value1 = value and Klrida.get_str('AINE', value)
                key1 = 'aine'
            elif key == 'oskus_kood':
                value1 = value and Klrida.get_str('OSKUS', value, ylem_kood=aine)
                key1 = 'osaoskus'
            elif key == 'testiliik_kood':
                value1 = value and Klrida.get_str('TESTILIIK', value)
                key1 = 'testiliik'
            elif key == 'kehtib_alates':
                value1 = sdate(value)
                if not value1:
                    continue
                key1 = 'alates'
            elif key == 'kehtib_kuni':
                value1 = sdate(value)
                if not value1:
                    continue
                key1 = 'kuni'
            elif key == 'allkiri_jrk':
                key1 = 'allkirjastamisjärjekord'
                value1 = value or ''
            elif key == 'allkiri_tiitel1':
                key1 = 'tiitlirida 1'
                value1 = value or ''
            elif key == 'allkiri_tiitel2':
                key1 = 'tiitlirida 2'
                value1 = value or ''
            else:
                continue
            if value1 is None:
                value1 = ''
            li.append(f'{key1}: {value1}')
        return ', '.join(li)

    def get_str(self):
        values = (('kasutajagrupp_id', self.kasutajagrupp_id),
                  ('koht_id', self.koht_id),
                  ('piirkond_id', self.piirkond_id),
                  ('aine_kood', self.aine_kood),
                  ('oskus_kood', self.oskus_kood),
                  ('testiliik_kood', self.testiliik_kood),
                  ('kehtib_alates', self.kehtib_alates),
                  ('kehtib_kuni', self.kehtib_kuni_ui))
        values = [r for r in values if r[1]]
        return self.get_str_values(values)
    
    @property
    def kehtib_kuni_ui(self):
        """Andmebaasis on kuupäeval väärtus, mida kasutajale ei näidata.
        """
        if self.kehtib_kuni >= const.MAX_DATE:
            return None
        else:
            return self.kehtib_kuni

    @property
    def piirkond_nimi(self):
        return self.piirkond and self.piirkond.nimi

    @property
    def koht_nimi(self):
        return self.koht and self.koht.nimi

    @property
    def nimi(self):
        li = []
        if self.aine_kood:
            li.append(self.aine_nimi.lower())
        if self.oskus_kood:
            li.append(self.oskus_nimi.lower())
        buf = self.kasutajagrupp.nimi
        if li:
            buf += ' (%s)' % ', '.join(li)
        return buf

    @property
    def kehtiv(self):
        return not self.kehtib_kuni or self.kehtib_kuni >= date.today()

    @property
    def kehtiv_str(self):
        if self.kehtiv:
            return usersession.get_opt().STR_KEHTIV
        else:
            return usersession.get_opt().STR_KEHTETU

    def default(self):
        if not self.koht_id:
            self.koht_id = const.KOHT_EKK
        if not self.kehtib_alates:
            self.kehtib_alates = const.MIN_DATE
        if not self.kehtib_kuni:
            self.kehtib_kuni = const.MAX_DATE

