import sys
import os
import pickle
import re

from eis.lib.base import *
from eis.lib.importpackage import ImportPackage
from eis.lib.helpers import fstr
_ = model.usersession._

log = logging.getLogger(__name__)

class GiftImportPackage(ImportPackage):
    def __init__(self, filename, storage, aine, lang):
        """Ülesannete laadimine Moodle GIFT-failist.
        Objekti atribuudid:
        is_error - kas õnnestus importimine või mitte
        messages - jada teadetest kasutajale (infoks)
        items - jada imporditud kirjetest        
        """
        super(GiftImportPackage, self).__init__()
        
        if not model.Klrida.get_str('AINE', aine):
            self.error(_("Tundmatu õppeaine {s}").format(s=aine))
            self.is_error = True
            return

        if not model.Klrida.get_lang_nimi(lang):
            self.error(_("Tundmatu keel {s}").format(s=lang))
            self.is_error = True
            return
            
        if filename:
            with open(filename, 'rb') as f:
                self._readfile(f, aine, lang)
        else:
            self._readfile(storage.file, aine, lang)

    def _readfile(self, file, aine, lang):
        # esmalt kaotame küsimuste sees reavahetused
        li_buf = []
        buf = comment = None

        self.current_test = None
        #self.current_task = None
        #self.task_title = None
        
        for n, line in enumerate(file):
            try:
                line = line.decode('utf-8')
            except UnicodeDecodeError as e:
                self.error(_("Fail pole UTF-8 kodeeringus"))
                self.is_error = True
                return
            if line[0] == '\ufeff':
                line = line[1:]
            line = line.strip()
            if not line:
                # vahe kysimuste vahel
                if buf:
                    err = self._parse_question(buf, aine, lang)
                    if err:
                        break
                buf = comment = None
            elif line.startswith('//'):
                # kommentaar
                comment = line
            else:
                # kysimus jätkub
                if buf:
                    buf = buf + ' ' + line
                else:
                    buf = line
        if buf and not err:
            err = self._parse_question(buf, aine, lang)
        if err:
            if comment:
                err += comment
            err += ' (rida {n})'.format(n=n)
            self.error(err)

    def _parse_question(self, buf, aine, lang):
        # iga line on omaette kysimus
        if buf.startswith('$CATEGORY:'):
            # Faili esimese kategooria nimi saab testi nimeks
            if not self.current_test:
                test_title = buf.split(':', 1)[-1].split('/')[-1]
                self.current_test = self._create_test(test_title, aine, lang)
            return
        else:
            # lisame uue sisuploki
            task_title = 'Ülesanne'
            if buf.startswith('::'):
                # question title
                li = buf.split('::', 2)
                if len(li) > 2:
                    task_title = li[1]
                    buf = li[2]

            # Moodle kysimus = EISi ylesanne
            task = self._create_ylesanne(task_title, aine, lang)
            sp_title = ''
            m = re.match(r'(\[[a-z]+\])(.*)', buf)
            if m:
                # format: [html], [moodle], [plain], [markdown]
                q_format, buf = m.groups()
            else:
                q_format = '[moodle]'

            if q_format not in ('[html]', '[plain]'):
                self.is_error = True
                err = _("Formaadis {s} teksti importimise võimalust ei ole tehtud").format(s=q_format)
                return err
            
            # kas on valikud?
            m = re.match(r'(.*){(.*)}(.*)', buf)
            if m:
                # on valikud
                buf1, choices, buf2 = m.groups()
                
                # kas lynk ______ on teksti keskel?
                m = re.match(r'([^_]*)(__+)([^_]*)', buf1)
                if m:
                    buf1, lynk, buf12 = m.groups()
                    buf2 = buf12 + ' ' + buf2
                    
                self._add_sp_choice(sp_title, q_format, buf1, choices, buf2)
            else:
                self._add_sp_rubric(sp_title, q_format, buf)

            if self.current_test:
                model.Session.flush()
                task.check(self.handler)
                self.ty_seq = self.ty_seq + 1
                ty = model.Testiylesanne(
                    testiosa=self.current_testiosa,
                    hindamiskogum=self.current_hk,
                    seq=self.ty_seq,
                    valikute_arv=1,
                    tahis=str(self.ty_seq),
                    arvutihinnatav=task.arvutihinnatav,
                    max_pallid=task.get_max_pallid())
                vy = ty.give_valitudylesanne(self.current_komplekt, ylesanne_id=task.id)
                vy.koefitsient = 1.
                
    def _add_sp_choice(self, sp_title, format, buf1, buf_choices, buf2):
        task = self.current_task

        if buf1:
            # lisame kysimuse alustekstina
            self._add_sp_rubric(sp_title, format, buf1)            
            sp_title = ''

        self.sp_seq = self.sp_seq + 1
        tyyp = const.INTER_CHOICE
        sp = model.Sisuplokk(ylesanne=task,
                             seq=self.sp_seq,
                             staatus=const.B_STAATUS_KEHTIV,
                             naide=False,
                             ymardamine=False,
                             tyyp=tyyp,
                             nimi=sp_title)
        task.sisuplokid.append(sp)

        if buf2:
            self._add_sp_rubric('', format, buf2)

        sp.logging = False
        kood = task.gen_kysimus_kood(koodid=self.koodid)
        self.koodid.append(kood)
        kysimus = model.Kysimus(kood=kood,
                                seq=1,
                                segamini=False,
                                max_vastus=1,
                                sisuplokk=sp,
                                sonadearv=False,
                                pseudo=False)
        kysimus.rtf = True
        tulemus = model.Tulemus(kood=kysimus.kood,
                                baastyyp=const.BASETYPE_IDENTIFIER,
                                kardinaalsus=const.CARDINALITY_MULTIPLE,
                                min_pallid=0,
                                vaikimisi_pallid=0,
                                ylesanne=task,
                                arvutihinnatav=True)
        kysimus.tulemus = tulemus
        task.tulemused.append(tulemus)

        # jagame puhvri valikuteks, iga valiku ees on ~ (vale vastus) või = (õige vastus)
        lines = []
        in_tag = False
        v_buf = ''
        for ch in buf_choices:
            if format == '[html]':
                if ch == '<':
                    in_tag = True
                elif ch == '>':
                    in_tag = False
            if ch in ('~','=') and not in_tag:
                if v_buf:
                    lines.append(v_buf)
                    v_buf = ''
            v_buf += ch
        if v_buf:
            lines.append(v_buf)
        
        v_seq = 0
        max_vastus = 0
        for line in lines:
            line = line.strip()

            if line:
                pallid = 0
                v_kood = chr(65 + v_seq) # A,B,C,...
                if line[0] == '=':
                    # õige vastus
                    line = line[1:]
                    pallid = 1
                elif line[0] == '~':
                    # vale vastus
                    line = line[1:]
                    # kas on punkti protsendid?
                    m = re.match(r'%(-?[0-9\.]+)%(.*)', line)
                    if m:
                        sprot, line = m.groups()
                        try:
                            prot = float(sprot)
                        except:
                            self.is_error = True
                            self.error('Vigane protsent {s}'.format(s=sprot))
                            return
                        else:
                            pallid = prot / 100
                if pallid:
                    if pallid > 0:
                        max_vastus += 1
                    hm = model.Hindamismaatriks(kood1=v_kood,
                                                oige=pallid>0,
                                                pallid=pallid,
                                                maatriks=1,
                                                tulemus=tulemus)

                v_nimi = self._text(line, format)
                v = model.Valik(seq=v_seq,
                                kood=v_kood,
                                nimi=v_nimi,
                                kysimus=kysimus)
                v_seq += 1
        kysimus.max_vastus = max_vastus or 1
        
    def _add_sp_rubric(self, sp_title, format, buf):
        task = self.current_task
        tyyp = const.BLOCK_RUBRIC
        sisu = self._text(buf, format)
        self.sp_seq = self.sp_seq + 1
        sp = model.Sisuplokk(ylesanne=task,
                             seq=self.sp_seq,
                             staatus=const.B_STAATUS_KEHTIV,
                             naide=False,
                             ymardamine=False,
                             tyyp=tyyp,
                             nimi=sp_title,
                             sisu=sisu,
                             sisuvaade=sisu)
        task.sisuplokid.append(sp)

    def _text(self, buf, format):
        buf = buf.replace('\\n',' ').replace('\\:', ':')
        # if format == '[html]':
        #     buf = buf.replace('\\n', '<br/>')
        # else:
        #     buf = buf.replace('\\n', '\n')
        return buf

    def _create_ylesanne(self, task_title, aine, lang):
        task = model.Ylesanne(nimi=task_title,
                              staatus=const.Y_STAATUS_TEST,
                              vastvorm_kood=const.VASTVORM_KE,
                              hindamine_kood=const.HINDAMINE_OBJ,
                              arvutihinnatav=True,
                              adaptiivne=False,
                              ptest=True,
                              etest=True,
                              lang=lang,
                              kasutusmaar=0,
                              ymardamine=False,
                              pallemaara=False,
                              skeeled=lang)
        ya = model.Ylesandeaine(aine_kood=aine,
                                ylesanne=task,
                                seq=0)
        self.items.append(task)                        
        self.current_task = task
        self.sp_seq = 0
        self.koodid = []
        return task
    
    def _create_test(self, test_title, aine, lang):
        test = model.Test(testityyp=const.TESTITYYP_EKK,
                          staatus=const.T_STAATUS_KOOSTAMISEL,
                          nimi=test_title,
                          aine_kood=aine,
                          lang=lang,
                          avaldamistase=const.AVALIK_EKSAM,
                          ymardamine=False,
                          arvutihinde_naitamine=True)
        test.skeeled = lang
        test.set_lang()
        test.logi('Importimine (Moodle GIFT)', None, None, const.LOG_LEVEL_GRANT)

        osa = test.give_testiosa()
        osa.vastvorm_kood = const.VASTVORM_KE
        kv = osa.give_komplektivalik()
        komplekt = kv.give_komplekt()
        komplekt.gen_tahis()
        komplekt.staatus = const.K_STAATUS_KOOSTAMISEL
        komplekt.copy_lang(test)
        hkogum = kv.give_default_hindamiskogum()
        
        # testi looja saab kohe testiga seotud isikuks koostaja rollis
        test.add_testiisik(const.GRUPP_T_OMANIK)
        model.Session.flush()
        self.items.append(test)                        
        self.current_test = test
        self.current_testiosa = osa
        self.current_komplekt = komplekt
        self.current_hk = hkogum
        self.ty_seq = 0
        return test
