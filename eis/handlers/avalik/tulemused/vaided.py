from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.vaideavaldus import VaideavaldusDoc
import eis.lib.ddocs as ddocs

log = logging.getLogger(__name__)

class VaidedController(BaseResourceController):
    """Vaide esitamine
    """
    _permission = 'sooritamine'
    _MODEL = model.Sooritaja
    _EDIT_TEMPLATE = 'avalik/tulemused/vaie.mako'
    _ITEM_FORM = forms.avalik.sooritamine.VaieForm
    _get_is_readonly = False
    _actions = 'show,edit,update,download,downloadfile,delete'
    
    def show(self):
        rc = self._check()
        if rc:
            return rc
        return BaseResourceController.show(self)

    def edit(self):
        rc = self._check()
        if rc:
            return rc

        id = self.request.matchdict.get('id')
        self._edit(self._MODEL.get(id))
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _edit(self, item):
        self.c.item = item
        self.c.vaie = self.c.item.give_vaie()
        if self.c.vaie.staatus and self.c.vaie.staatus != const.V_STAATUS_ESITAMATA:
            self.c.is_edit = False
        return self.response_dict
        #return self.render_to_response(self._EDIT_TEMPLATE)

    def update(self):
        rc = self._check()
        if rc:
            return rc
        return BaseResourceController.update(self)
    
    def _update(self, item):
        vaie = item.give_vaie()
        kasutaja = item.kasutaja
        # salvestame andmed
        vaie.from_form(self.form.data, 'f_')
        kasutaja.from_form(self.form.data,'k_')
        model.Aadress.adr_from_form(kasutaja, self.form.data, 'a_')        
        if vaie.otsus_epostiga:
            if not kasutaja.epost:
                errors = {'k_epost': _("Palun sisestada e-posti aadress, kuhu otsus saata")}
                raise ValidationError(self, errors)
        else:
            aadress_id = kasutaja.aadress_id
            aadress = aadress_id and model.Aadress.get(aadress_id)
            if not aadress or (not aadress.kood3 and not aadress.kood4 and not aadress.kood5 and not aadress.kood6 and not aadress.kood7 and not aadress.kood8 and not kasutaja.normimata):
                errors = {'a_adr_id': _("Palun sisestada aadress, kuhu otsus saata")}
                raise ValidationError(self, errors)                

        vaie.staatus = const.V_STAATUS_ESITAMATA
        vaie.esitamisaeg = datetime.now()
        if not vaie.vaide_nr:
            vaie.flush()
            vaie.vaide_nr = vaie.id

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        self.c.is_edit = False
        return self.edit()

    def _gen_avaldus_pdf(self, vaie):
        doc = VaideavaldusDoc(self, vaie)
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            return        
        return data

    def _update_prepare_signature(self, id):
        """Allkirjastamise alustamine: brauserilt on saadud sert,
        selle kohta arvutatakse allkirjastatav räsi.
        """
        item = model.Sooritaja.get(id)
        vaie = item.give_vaie()
        
        # loome avalduse PDFi
        avaldus_pdf = self._gen_avaldus_pdf(vaie)

        # alustame allkirjastamist
        filedata, res = ddocs.DdocS.prepare_signature(self, avaldus_pdf, 'avaldus.pdf')
        if filedata:
            # bdoc
            vaie.avaldus_dok = filedata
            model.Session.commit()

        return res
    
    def _update_finalize_signature(self, id):
        """Allkirjastamise lõpetamine: brauserilt on saadud allkiri,
        see lisatakse pooleli oleva DDOC-faili sisse.
        """
        item = model.Sooritaja.get(id)
        vaie = item.give_vaie()

        filedata, signers, dformat = ddocs.DdocS.finalize_signature(self, vaie.avaldus_dok)
        if filedata:
            # salvestame allkirjastatud kinnitamata faili
            vaie.avaldus_dok = filedata
            vaie.avaldus_ext = dformat
            vaie.staatus = const.V_STAATUS_ESITATUD
            vaie.esitamisaeg = datetime.now()            
            model.Session.commit()
            self._saada_komisjonile(item, vaie)
            self._saada_sooritajale(item, vaie)
            self.success(_("Vaie on esitatud!"))
        return self._after_delete()

    def _saada_komisjonile(self, sooritaja, vaie):
        """Kui vaidekomisjoni esimees pole veel allkirja andnud, siis saadetakse talle kiri.
        """
        today = date.today()
        test = sooritaja.test
        nimi = sooritaja.nimi
        # leiame vaidekomisjoni sekretäri
        q = (model.Session.query(model.Kasutaja.id,
                                 model.Kasutaja.epost,
                                 model.Kasutaja.isikukood,
                                 model.Kasutaja.nimi)
             .filter(model.Kasutaja.epost!=None)
             .filter(model.Kasutaja.kasutajarollid.any(
                 sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_VAIDEKOM_SEKRETAR,
                         model.Kasutajaroll.testiliik_kood==test.testiliik_kood,
                         model.Kasutajaroll.kehtib_alates<=today,
                         model.Kasutajaroll.kehtib_kuni>=today)))
             )
        kasutajad = [(k_id, epost, ik, nimi) for (k_id, epost, ik, nimi) in q.all()]
        epostid = [r[1] for r in kasutajad]
        if epostid:
            pw_url = self.request.registry.settings.get('eis.pw.url')
            vaie_url = f'{pw_url}/ekk/muud/vaided/{vaie.id}'
            data = {'sooritaja_nimi': nimi,
                    'vaide_nr': vaie.vaide_nr,
                    'vaide_url': vaie_url,
                    }
            subject, body = self.render_mail('mail/vaideavaldus.sekretarile.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(self).send(epostid, subject, body):
                s_epostid = ', '.join(epostid)
                log.debug(_("Teade on saadetud vaidekomisjoni sekretärile {s}").format(s=s_epostid))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                for k_id, epost, ik, nimi in kasutajad:
                    model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
                model.Session.commit()
        else:
            log.debug('Vaidekomisjoni sekretäri e-posti aadressi ei leitud')
            
    def _saada_sooritajale(self, sooritaja, vaie):
        """Sooritajale saadetakse teade, et vaie on esitatud
        """
        today = date.today()
        test = sooritaja.test
        nimi = sooritaja.nimi
        kasutaja = sooritaja.kasutaja

        data = {'sooritaja_nimi': nimi,
                'test_nimi': test.nimi,
                }
        subject, body = self.render_mail('mail/vaideavaldus.sooritajale.mako', data)
        body = Mailer.replace_newline(body)
        teatekanal = const.TEATEKANAL_EIS
        epost = kasutaja.epost
        if epost:
            if not Mailer(self).send(epost, subject, body):
                teatekanal = const.TEATEKANAL_EPOST
        kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                          sisu=body,
                          teema=subject,
                          teatekanal=const.TEATEKANAL_EPOST)
        model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=epost)
        model.Session.commit()
            
    def _downloadfile(self, id, file_id, format):
        "Vaidefaili allalaadimine"
        item = model.Sooritaja.get(id)
        vaie = item and item.give_vaie()
        filedata = filename = None
        if vaie and vaie.sooritaja.kasutaja_id == self.c.user.id:
            if file_id == 'otsus':
                filedata = vaie.otsus_dok
                filename = 'vaideotsus.%s' % (vaie.otsus_ext)
            elif file_id == 'avaldus':
                filedata = vaie.avaldus_dok
                filename = 'vaideavaldus.%s' % (vaie.avaldus_ext)
            else:
                vf = model.Vaidefail.get(file_id)
                if vf and vf.vaie_id == vaie.id:
                    filedata = vf.filedata
                    filename = vf.filename
        if filedata and filename:
            (mimetype, encoding) = mimetypes.guess_type(filename)
            return utils.download(filedata, filename, mimetype)            
        else:
            raise NotFound(_("Dokumenti ei leitud"))

    def _delete(self, item):
        item = item.vaie
        if item and item.staatus > const.V_STAATUS_ESITAMATA:
            self.error(_("Vaie on juba esitatud"))
        elif item:
            item.delete()
            model.Session.commit()
            self.success(_("Vaideavaldus on kustutatud"))

    def _after_delete(self, parent_id=None):
        sooritaja_id = self.request.matchdict.get('id')
        url = self.url('tulemus', id=sooritaja_id)
        return HTTPFound(location=url)
        
    def _check(self):
        id = self.request.matchdict.get('id')
        item = model.Sooritaja.get(id)
        tk = item and item.testimiskord
        saab = item and item.kasutaja_id == self.c.user.id and tk
        if saab:
            vaie = item.vaie
            if vaie and vaie.staatus > const.V_STAATUS_ESITAMATA:
                # esitatud vaiet saab ka hiljem vaadata
                saab = True
            else:
                # esitamata vaiet saab vaadata ainult seni, kuni on vaidlustamise aeg
                dt = date.today()
                saab = (not tk.vaide_algus or tk.vaide_algus <= dt) and \
                       tk.vaide_tahtaeg and tk.vaide_tahtaeg >= dt and \
                       tk.tulemus_kinnitatud and \
                       item.kasutaja_id == self.c.user.id and \
                       (item.hindamine_staatus == const.H_STAATUS_HINNATUD and item.pallid != None or \
                        item.staatus == const.S_STAATUS_EEMALDATUD)
        if not saab:
            return Response('Ligipääs puudub')
