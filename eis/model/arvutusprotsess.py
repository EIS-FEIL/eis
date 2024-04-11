"Testi andmemudel"
import traceback
import math
import subprocess
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import Opt
from eis.model.kasutaja import *
from eis.model.koht import *
from eis.s3file import S3File
from eis.lib.daemon import create_daemon
from eis.lib.exceptions import ProcessCanceled
from eis.lib.validationerror import ValidationError
import eis.model_s as model_s
import eis.model_log as model_log
import eis.lib.utils as utils
_ = usersession._

P_LOGDIR = '/srv/eis/log'

class Arvutusprotsess(EntityHelper, Base, S3File):
    """Toimumisaja tulemuste arvutamise protsesside logi
    """
    LIIK_TULEMUSED = 1 # testi tulemuste arvutamine
    LIIK_LOPETAMINE = 2 # lõpetamiste kontroll
    LIIK_STATRAPORT = 3 # statistikaraportite genereerimine
    LIIK_STATISTIKA = 4 # testi statistika arvutamine
    LIIK_OPPURID = 5 # EHISest õppurite andmete uuendamine
    LIIK_OPETAJAD = 6 # EHISest õpetajate andmete uuendamine
    LIIK_M_SOORITUSKOHT = 7 # Soorituskohateadete saatmine
    LIIK_M_TULEMUS = 8 # Sooritajatele tulemuste teavituste saatmine
    LIIK_M_LABIVIIJA = 9 # Läbiviijate teadete saatmine
    LIIK_M_VAATLEJA = 10 # Vaatlejate teadete saatmine
    LIIK_SALVESTAMINE = 11 # Tunnistuste salvestamine
    LIIK_VALJASTAMINE = 12 # Tunnistuste väljastamine
    LIIK_VALIM = 13 # Valimi eraldamine (testimiskorra kopeerimine)
    LIIK_REG = 14 # testisooritajate regamine
    LIIK_MUUSK = 15 # muu soorituskha teadete saatmine
    LIIK_MATERJAL = 16 # korraldamise PDF materjalide genereerimine
    LIIK_VASTUSED = 17 # testi vastuste failina väljavõtte koostamine
    LIIK_TULEMUSTE_STATISTIKA = 18 # tulemuste statistika csv
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    liik = Column(Integer) # protsessi liik: 1 - testi tulemuste arvutamine; 2 - lõpetamiste kontroll; 3 - statistikaraportite genereerimine; 4 - testi statistika arvutamine; 5 - EHISest õppurite andmete uuendamine; 6 - EHISest õpetajate andmete uuendamine
    test_id = Column(Integer, ForeignKey('test.id'), index=True)
    test = relationship('Test', foreign_keys=test_id) # viide testile, mille tulemusi arvutatakse
    testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True) # viide testimiskorrale, mille tulemusi arvutatakse
    testimiskord = relationship('Testimiskord', foreign_keys=testimiskord_id, back_populates='arvutusprotsessid')
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True) # viide toimumisajale, kui arvutatakse ühe toimumisaja tulemusi
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='arvutusprotsessid')
    aasta = Column(Integer) # aastaarv, mille lõpetamisi arvutatakse (lõpetamise kontrolli korral)
    nimekiri_id = Column(Integer, ForeignKey('nimekiri.id'), index=True) # viide nimekirjale, kui arvutatakse ühe nimekirja tulemusi
    nimekiri = relationship('Nimekiri', foreign_keys=nimekiri_id)
    testsessioon_id = Column(Integer) # testsessiooni ID, mille raporteid genereeritakse (statistikaraportite genereerimise korral)
    param = Column(String(90)) # muud parameetrid (nt regamise protsessis)
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    kirjeldus = Column(String(256)) # protsessi sisu kirjeldus protsesside logi tabelis kuvamiseks
    viga = Column(String(512)) # protsessis tekkinud vea kirjeldus
    pid = Column(Integer, nullable=False) # protsessi ID opsüsteemis
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # protsessi käivitanud kasutaja
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id)
    algus = Column(DateTime, nullable=False) # protsessi käivitamise aeg
    lopp = Column(DateTime) # protsessi lõppemise aeg
    edenemisprotsent = Column(Integer, nullable=False) # mitu protsenti tööst on tehtud 
    hostname = Column(String(48)) # rakendusserveri nimi

    _cache_dir = 'arvutusprotsess'

    def set_creator(self):
        EntityHelper.set_creator(self)
        self.set_host()

    @classmethod
    def get_host(cls):
        import subprocess
        try:
            p = subprocess.Popen('hostname', stdout=subprocess.PIPE)
        except BlockingIOError as ex:
            # cygwin
            return
        hostname, err = p.communicate()
        if hostname:
            return hostname.decode('ascii').strip()

    def set_host(self):
        hostname = self.get_host()
        if hostname:
            self.hostname = hostname[:48]

    def set_viga(self, value, errcnt=None):
        value = value.strip()
        if errcnt and errcnt > 100:
            # kui on liiga palju vigu nt kirjade saatmisel,
            # siis katkestame
            value = 'Katkestan\n' + value
            if len(value) > 512:
                value = value[:509] + '...'
            return True
        
        if len(value) > 512:
            value = value[:509] + '...'
        self.viga = value

    @classmethod
    def reconnect_db(cls, settings):
        # põhibaas
        engine = sa.engine_from_config(settings, 'sqlalchemy.')
        Session.bind = engine

        # logi andmebaas
        engine_log = sa.engine_from_config(settings, 'sqlalchemy_log.')
        model_log.meta.Base.metadata.bind = engine_log
        model_log.DBSession.bind = engine_log

        # seansside andmebaas
        engine_s = sa.engine_from_config(settings, 'sqlalchemy_s.')
        model_s.meta.Base.metadata.bind = engine_s
        model_s.DBSession.bind = engine_s

    @classmethod
    def start(cls, handler, prot_params, childfunc, use_t=False, debug=None, debug_p=False):
        "Uue arvutusprotsessi loomine"
        # dict prot_params peab sisaldama vähemalt: liik, kirjeldus
        # funktsioon childfunc(protsess) teeb tegeliku töö
        # debug_p - kui on debug ja protsessi pole, siis luua ikkagi protsessi kirje

        # kontrollime, et kirjeldus mahub väljale
        kirjeldus = prot_params.get('kirjeldus')
        if kirjeldus and len(kirjeldus) > 256:
            prot_params['kirjeldus'] = kirjeldus[:252] + '...'

        if debug is None:
            debug = handler.request.params.get('debug') or handler.c.is_debug
        if debug and debug != '0' and not debug_p:
            # eraldi protsessi ei käivita ja protsessi kirjet ka ei tee
            protsess = None
        else:
            # loome arvutusprotsessi kirje
            protsess = Arvutusprotsess(pid=0,
                                       kasutaja_id=handler.c.user.id,
                                       algus=datetime.now(),
                                       lopp=None,
                                       edenemisprotsent=0,
                                       **prot_params)
            Session.commit()
            
        if debug and debug != '0':
            # eraldi protsessi ei käivita
            resp = childfunc(protsess)
            if protsess:
                # protsessi kirje loodi, aga protsessi ennast pole (debug_p == True)
                protsess.edenemisprotsent = 100
                protsess.lopp = datetime.now()
            Session.commit()
            return resp

        protsess_id = protsess.id
        Session.rollback()
        pid = create_daemon()
        if pid > 0:
            # handler kuvab kasutajale vormi,
            # töö jätkub deemoni protsessis
            return pid
        if pid == 0:
            # deemoni töö
            try:
                pid = os.getpid()
                settings = handler.request.registry.settings
                cls.reconnect_db(settings)
                
                protsess = Arvutusprotsess.get(protsess_id)
                protsess.pid = pid
                try:
                    childfunc(protsess)
                except ProcessCanceled as ex:
                    # arvutamine katkestati
                    request = handler.request
                    protsess = Arvutusprotsess.get(protsess_id)                    
                    msg = _("Arvutamine katkestati ({n}%)").format(n=protsess.edenemisprotsent)
                    protsess.set_viga(msg)
                    protsess.lopp = datetime.now()
                    Session.commit()
                    Arvutusprotsess.trace(msg)
                except ValidationError as ex:
                    # protsessis tekkis valideerimise viga
                    Session.rollback()
                    protsess = Arvutusprotsess.get(protsess_id)                    
                    try:
                        error = ex.args[2]
                    except IndexError:
                        error = str(ex)
                    protsess.set_viga(error)
                    protsess.lopp = datetime.now()
                    Session.commit()
                    Arvutusprotsess.trace(ex=ex)
                    handler._error(ex, 'Taustaprotsessi viga', False)
                except Exception as ex:
                    # protsessis tekkis viga
                    Session.rollback()
                    protsess = Arvutusprotsess.get(protsess_id)                    
                    protsess.set_viga(str(ex))
                    protsess.lopp = datetime.now()
                    Session.commit()
                    Arvutusprotsess.trace(ex=ex)
                    handler._error(ex, 'Taustaprotsessi viga', False)
                else:
                    protsess = Arvutusprotsess.get(protsess_id)
                    if not protsess.lopp:
                        # protsess lõppes õnnelikult
                        protsess.edenemisprotsent = 100
                        protsess.lopp = datetime.now()
                    Session.commit()
            except Exception as ex:
                Arvutusprotsess.trace('EXCEPTION', ex=ex)               
            finally:
                Session.close()
                model_log.DBSession.close()
                model_s.DBSession.close()
                os._exit(0)

    @classmethod
    def iter_mail(cls, protsess, handler, total, items, itemfunc):
        "Kirjade saatmise protsessi tsykkel"
        # total - saadetavate kirjade eeldatav arv
        # items - kirjade päringu kirjed
        # itemfunc(item) - funktsioon yhe kirja saatmiseks,
        #     tagastab rc, err
        #     (rc - kas õnnestus saata, err - ebaõnnestunud aadress)
        cnt = errcnt = 0
        lierr = []
        MAX_ERRORS = 100
        
        def _notes(cnt, errcnt, lierr):
            request = handler.request
            buf_ok = cnt and _("Saadetud {n} kirja").format(n=cnt) or ''
            buf_err = errcnt and _("Ei saanud saata {n} kirja").format(n=errcnt) or ''
            if lierr:
                buf_err += '\n' + ', '.join(lierr)
            return buf_ok, buf_err

        for ind, r in enumerate(items):
            rc, err = itemfunc(r)
            if rc:
                cnt += 1
            else:
                errcnt += 1
                if err:
                    lierr.append(err)
            if protsess:
                protsess.edenemisprotsent = round((ind * 100) / total)
                buf_ok, buf_err = _notes(cnt, errcnt, lierr)
                protsess.set_viga(buf_ok + '\n' + buf_err)
            Session.commit()
            if errcnt >= MAX_ERRORS:
                # liiga palju vigu
                protsess.set_viga('Katkestan\n' + protsess.viga)

        if not protsess and handler:
            buf_ok, buf_err = _notes(cnt, errcnt, lierr)
            if buf_ok:
                handler.notice(buf_ok)
            if buf_err:
                handler.error(buf_err)

    @classmethod
    def run_parallel(cls, handler, label, total, child_cnt, worker, get_child_data, protsess_id, progress_start, progress_end):
        "Protsessi jooksutamine mitmes alamprotsessis, et kiiremini saaks"
        # label - protsessi kirjeldus logirea alguses
        # total - arvutusyhikute (sooritajate, kysimuste, koolide vms) koguarv
        # child_cnt - yhes alamprotsessis korraga arvutatavate arvutusyhikute arv
        # worker - funktsioon, mis alamprotsessis arvutab
        # get_child_data - funktsioon, mis leiab alamprotsessile uue portsu arvutada (käivitatakse vanemprotsessis)
        
        handled_cnt = 0 # arvutatud tk arv
        settings = handler.request.registry.settings
        FORKS = int(settings.get('calc.child_processes', 8)) # laste arv
        max_id = 0
        FORKS = min(FORKS, math.ceil(total / child_cnt)) or 1 # kui koole on eriti vähe, siis pole mitut last vaja
        if protsess_id:
            Arvutusprotsess.trace('%s Arvutada %d tk %d alamprotsessiga' % (label, total, FORKS))
            os.setpgrp()
        else:
            Arvutusprotsess.trace('%s Arvutada %d tk ilma taustaprotsessita %d jaos' % (label, total, FORKS))            

        processes = dict()
        
        def _create_process(min_id, max_id, child_data):
            freemem = utils.mem_available()
            if freemem < 600000:
                buf = 'vaba %s kB, ei tee uut protsessi (on %s protsessi)' % (freemem, len(processes))
                Arvutusprotsess.trace(buf)
                return False
            Session.commit()
            Session.close()
            Session.bind.dispose()
            model_log.DBSession.bind.dispose()
            model_s.DBSession.bind.dispose()
            pid = os.fork()
            if pid == 0:
                # alamprotsess
                try:
                    pid = os.getpid()
                    cls.reconnect_db(settings)

                    worker(min_id, max_id, child_data, pid)
                    os._exit(0)
                except Exception as e:
                    # protsessis tekkis viga
                    # kirjutame faili, kust parent hiljem loeb
                    Arvutusprotsess.trace(str(e), pid)
                    f = open(P_LOGDIR + '/eis.daemon.%s.err' % pid, 'w')
                    f.write(str(e))
                    f.close()
                    handler._error(e, _("Arvutusprotsessi viga "), rollback=True)
                    os._exit(os.EX_DATAERR)
                finally:
                    Session.close()
            else:
                # ylemprotsess
                return pid
            
        while max_id is not None:
            # korraga käivitame mitu protsessi
            # leiame portsu, mida korraga arvutada

            min_id, max_id, p_cnt, child_data = get_child_data(max_id, child_cnt)
            no_memory = False
            
            if p_cnt > 0 and not protsess_id:
                # arvutame ilma alamprotsessita
                worker(min_id, max_id, child_data, 0)
                Session.commit()
            elif p_cnt > 0:
                # on ports, mida arvutada
                pid = _create_process(min_id, max_id, child_data)
                if pid == False:
                    # ei õnnestunud protsessi käivitada
                    max_id = min_id
                    no_memory = True
                    if not processes:
                        # kui yhtki protsessi ei käi, siis pole vanemal ka mõtet kesta
                        raise Exception("liiga vähe vaba mälu")                                            
                else:
                    processes[pid] = (min_id, max_id, p_cnt, 0)
                    Arvutusprotsess.trace('%s Loodud protsess %s, %s-%s (kokku %s)' % (label, pid, min_id, max_id, p_cnt))
            else:
                # rohkem pole midagi arvutada
                max_id = None

            err = None
            while processes and (not max_id or len(processes) >= FORKS or no_memory):
                # kui enam midagi arvutada ei ole, aga protsessid on pooleli
                # või kui max protsesside arv on käigus,
                # siis ootame mõne protsessi lõpetamist

                pid, status = os.waitpid(0, 0)
                Arvutusprotsess.trace('%s protsess %s TEHTUD %s' % (label, pid, status or ''))
                done_min_id, done_max_id, done_cnt, n_try = processes.pop(pid)
                if status:
                    # lõpetas veaga
                    err = 'Protsessi %s viga %s' % (pid, status)                    
                    try:
                        # loeme failist veateate
                        fn = P_LOGDIR + '/eis.daemon.%s.err' % pid
                        if os.path.isfile(fn):
                            f = open(fn, 'r')
                            err = f.read()
                            f.close()
                            os.remove(fn)
                    except:
                        pass

                    done_cnt = 0

                    uuesti = False
                    if protsess_id and not uuesti:
                        # salvestame veateate kirjes
                        protsess = Arvutusprotsess.get(protsess_id)
                        protsess.set_viga(err)
                        protsess.lopp = datetime.now()
                        #Session.commit()
                        Arvutusprotsess.trace(err)
                        handler._error(None, _("Arvutusprotsessi viga ") + err, rollback=False)                        
                        return False
                    
                handled_cnt += done_cnt
                if protsess_id and done_cnt:
                    protsess = Arvutusprotsess.get(protsess_id)
                    if protsess.lopp:
                        # protsess on katkestatud, edasi ei arvuta
                        raise ProcessCanceled()

                    protsess.edenemisprotsent = progress_start + (progress_end - progress_start) * handled_cnt / total
                    Session.commit()
        return True

    @classmethod
    def trace(cls, buf='', pid=None, ex=None):
        log.debug(buf)
        try:
            with open(P_LOGDIR + '/arvutus.log', 'a') as f:
                if pid:
                    buf = '[%s] %s' % (pid, buf)
                if ex:
                    buf += '\n' + traceback.format_exc()
                f.write('%s %s\n' % (datetime.now(), buf))
        except Exception as ex:
            log.error(ex)
        

