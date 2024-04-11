"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from eis.model.test import *
_ = usersession._

class Testiarvuti(EntityHelper, Base):
    """Testi sooritamiseks registreeritud arvuti andmed
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer, nullable=False) # arvuti järjekorranumber testiruumis
    tahis = Column(String(25)) # arvuti unikaalne ID testimiskorral, kujul TESTIOSA-TESTIKOHT-SEQ
    parool = Column(String(256)) # arvuti brauserisse registreerimisel jäetud cookie
    ip = Column(String(15)) # arvuti IP-aadress (ei pruugi olla unikaalne)
    testiruum_id = Column(Integer, ForeignKey('testiruum.id'), index=True, nullable=False) # viide testiruumile
    testiruum = relationship('Testiruum', foreign_keys=testiruum_id, back_populates='testiarvutid')
    sooritused = relationship('Sooritus', back_populates='testiarvuti')
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek: 0 - kehtetu; 1 - kehtiv
    algne_id = Column(Integer) # arvuti unikaalne ID (kui arvutis on samaaegselt mitu registreeringut)
    kehtib_kuni = Column(Date, nullable=False) # kehtimise lõpp    
    _parent_key = 'testiruum_id'

    @classmethod
    def get_by_cookie(cls, parool):
        """Leitakse brauserisse paigaldatud küpsisele vastav arvuti
        """
        return cls.query.filter_by(parool=parool).\
            filter_by(staatus=const.B_STAATUS_KEHTIV).\
            first()

    @classmethod
    def get_by_request(cls, test_id, testiruum, toimumisaeg, request):
        """Kontrollitakse, kas brauseris on sellesse ruumi sobiv küpsis
        """
        error = None
        cookies = request.cookies

        # kas on olemas antud testiruumi registreering?
        arvuti = None
        arvutid2 = []
        for cookie_name in cookies:
            if cookie_name.startswith(f'{const.COOKIE_REG}_{test_id}_'):
                try:
                    cookie_reg, test_id, cookie_id = cookie_name.split('_')
                    cookie_id = int(cookie_id)
                except:
                    log.error(f'vigane cookie {cookie_name}')
                else:
                    item = Testiarvuti.get(cookie_id)
                    if not item:
                        log.debug(f'cookie {cookie_id} on kustutatud')
                    elif item.staatus == const.B_STAATUS_KEHTETU:
                        log.debug(f'cookie {cookie_id} on kehtetu')
                    else:
                        value = cookies.get(cookie_name)
                        if item.parool != value:
                            log.error(f'cookie {cookie_id} vale väärtus')
                        elif item.testiruum_id == testiruum.id:
                            # oma testiruumi cookie leitud
                            arvuti = item
                            break
                        else:
                            # mingi muu sama testi cookie, jätame meelde
                            arvutid2.append(item)
        if not arvuti:
            # kas või olla regatud muusse ruumi?
            on_reg_test = toimumisaeg and toimumisaeg.on_reg_test and testiruum.ruum_id
            if arvutid2 and on_reg_test:
                # oma testiruumi registreering puudus, aga on olemas mõne teise sama testi testiruumi reg
                # ja on lubatud teise testiruumi registreeringut kasutada
                testiruumid_id = testiruum.get_other_in_tk(toimumisaeg.testimiskord_id)
                for item in arvutid2:
                    if item.testiruum_id in testiruumid_id:
                        # on registreeritud samas füüsilises ruumis mõnes teises sama testimiskorra testiruumis
                        arvuti = item
                        break
                                
            if not arvuti:
                error = _("Arvuti pole registreeritud")

        return arvuti, error

    @classmethod
    def save(cls, test_id, testiruum, cookie_value, max_age, request):
        "Lisatakse uus testiarvuti"
        algne_id = seq = None
        old_cookies = []
        # cookie_name sisaldab testi ID, et saaks kiiresti leida, kas on olemas mõni antud testi cookie
        # vaatame, kas arvuti on sellesse juba testiruumi registreeritud
        for cookie_name in request.cookies:
            if cookie_name.startswith(const.COOKIE_REG):
                try:
                    cookie_reg, test2_id, cookie_id = cookie_name.split('_')
                    cookie_id = int(cookie_id)
                except:
                    log.error(f'vigane cookie {cookie_name}')
                else:
                    item = Testiarvuti.get(cookie_id)
                    if item and item.parool == request.cookies.get(cookie_name):
                        # kui on juba regatud mõnda ruumi, siis säilitame teadmise ruumi identiteedist
                        if not algne_id:
                            algne_id = item.algne_id
                        # kui on juba regatud samasse ruumi, siis kustutame varasema registreeringu
                        if item.testiruum_id == testiruum.id:
                            old_cookies.append(f'{const.COOKIE_REG}_{test_id}_{item.id}')
                            # säilitame arvuti jrk nr
                            seq = item.seq
                            item.staatus = const.B_STAATUS_KEHTETU

        kehtib_kuni = datetime.now() + timedelta(seconds=max_age)
        # uus registreering
        remote_addr = request.remote_addr
        arvuti = Testiarvuti(testiruum=testiruum,
                             ip=remote_addr,
                             parool=cookie_value,
                             staatus=const.B_STAATUS_KEHTIV,
                             kehtib_kuni=kehtib_kuni,
                             seq=seq,
                             algne_id=algne_id)
        Session.flush()
        arvuti.set_tahis(testiruum)
        cookie_name = f'{const.COOKIE_REG}_{test_id}_{arvuti.id}'
        return arvuti, cookie_name, old_cookies

    @classmethod
    def get_reg(cls, request):
        "Antud arvuti registreeringud"
        data = []
        for cookie_name in request.cookies:
            if cookie_name.startswith(const.COOKIE_REG):
                cookie = request.cookies.get(cookie_name)
                arvuti = Testiarvuti.get_by_cookie(cookie)
                if arvuti:
                    data.append(arvuti)
        return data

    def set_tahis(self, testiruum):
        "Unikaalne tunnus testi piires"
        try:
            osa_tahis = testiruum.testikoht.tahised.split('-')[1]
        except:
            self.tahis = f'{testiruum.tahis}-{self.seq}'
        else:
            self.tahis = f'{osa_tahis}-{testiruum.tahis}-{self.seq}'
    
    def info(self):
        testikoht = self.testiruum.testikoht
        testiosa = testikoht.testiosa
        test = testiosa.test
        koht = testikoht.koht
        buf = '%s, %s, %s' % (test.nimi, testiosa.nimi, koht.nimi)

        if self.testiruum.tahis:
            buf += ', ruum %s' % (self.testiruum.tahis)
        if self.testiruum.ruum:
            buf += ' (%s)' % (self.testiruum.ruum.tahis)
        if self.testiruum.algus:
            buf += ' ' + self.testiruum.algus.strftime('%d.%m.%Y %H.%M')
        buf += ', arvuti nr %s' % (self.seq)
        return buf
