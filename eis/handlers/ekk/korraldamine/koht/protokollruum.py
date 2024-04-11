# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
log = logging.getLogger(__name__)

class ProtokollruumController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Testiruum
    _EDIT_TEMPLATE = '/ekk/korraldamine/koht.protokollruum.mako' 
    _ITEM_FORM = forms.ekk.korraldamine.KohtProtokollruumForm
    _actions = 'edit,update'

    def _update(self, item, lang=None):
        c = self.c
        r_algus = item.algus
        c.intervall = intervall = self.form.data['intervall']
        c.p_algus = p_algus = self.form.data['paus_algus']
        c.p_lopp = p_lopp = self.form.data['paus_lopp']
        if intervall and p_algus and p_lopp:
            paus_algus = datetime.combine(r_algus, time(p_algus[0], p_algus[1]))
            paus_lopp = datetime.combine(r_algus, time(p_lopp[0], p_lopp[1]))
        elif not intervall and (p_algus or p_lopp):
            raise ValidationError(self, {'intervall': _("Palun sisestada")})
        else:
            paus_algus = paus_lopp = None
            if intervall:
                if p_algus and not p_lopp:
                    raise ValidationError(self, {'paus_lopp': _("Palun sisestada")})
                elif p_lopp and not p_algus:
                    raise ValidationError(self, {'paus_algus': _("Palun sisestada")})
                
        protokollid = {r.id: r for r in item.testiprotokollid}
        for r in self.form.data['tpr']:
            protokoll = protokollid.get(r['id'])
            if protokoll:
                kell = r['kell']
                if kell:
                    algus = datetime.combine(r_algus, time(kell[0],kell[1]))
                else:
                    algus = r_algus

                on_kell = algus.hour or algus.minute
                # if on_kell and protokoll.algus and protokoll.algus != algus:
                #     # kellaaeg on varem juba määratud - leiame, kui palju kellaaeg muutus
                #     diff = algus - protokoll.algus
                # else:
                #     diff = None
                # #log.debug('PROTOKOLL %s kell %s (nihkub %s)' % (protokoll.tahis, algus, diff))

                # protokolliryhma algusaeg
                protokoll.algus = algus
                
                for tos in protokoll.sooritused:
                    if not on_kell:
                        # kellaaeg määramata, paneme 00:00
                        tos.kavaaeg = algus
                    elif intervall:
                        # määrame igale sooritajale uue aja, liites eelmise sooritaja ajale intervalli
                        kavaaeg = algus
                        if kavaaeg.date() > r_algus.date():
                            raise ValidationError(self, {}, _("Kõigile sooritajatele ei jätku samal päeval aega"))
                        tos.kavaaeg = kavaaeg
                        # arvutame valmis järgmise sooritaja aja
                        algus = algus + timedelta(minutes=intervall)
                        if paus_algus and paus_lopp:
                            lopp = algus + timedelta(minutes=intervall)
                            if algus < paus_lopp and lopp > paus_algus:
                                algus = paus_lopp
                    # elif diff is not None and tos.kavaaeg:
                    #     # nihutame olemasolevad sooritajate ajad samavõrra edasi
                    #     kavaaeg = datetime.combine(r_algus, tos.kavaaeg.time()) + diff
                    #     if kavaaeg.date() > r_algus.date():
                    #         #log.debug('ei jatku aega: ruum %s, aeg %s' % (r_algus, kavaaeg))
                    #         raise ValidationError(self, {}, _("Kõigile sooritajatele ei jätku samal päeval aega"))
                    #     tos.kavaaeg = kavaaeg
                    else:
                        # kui sooritajal või protokolliryhmal pole veel aega määratud,
                        # siis saab sooritaja ajaks protokolliryhma aeg
                        tos.kavaaeg = algus

                    
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            #self.success()
            return HTTPFound(location=self.url('korraldamine_koht_sooritajad',
                                               toimumisaeg_id=self.c.toimumisaeg.id,
                                               testikoht_id=self.c.testikoht_id))
        else:
            return self._redirect('edit', id)


    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
        self.c.testikoht_id = int(self.request.matchdict.get('testikoht_id'))
        self.c.testikoht = model.Testikoht.get(self.c.testikoht_id)
        self.c.pakett_id = int(self.request.matchdict.get('pakett_id'))
        
    def _perm_params(self):
        return {'obj':self.c.testikoht}

