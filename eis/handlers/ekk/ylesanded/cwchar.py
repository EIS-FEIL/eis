# -*- coding: utf-8 -*- 
"""Ristsõna etteantud tähe salvestamine
"""
import re
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class CwcharController(BaseController):
    _permission = 'ylesanded'
    _actions = 'new,create,delete'
    _EDIT_TEMPLATE = '/sisuplokk/icrossword.cwchar.mako'
    
    def new(self):
        c = self.c
        c.lang = self.params_lang()
        is_tr = self.request.params.get('is_tr') or c.lang
        c.pos_x = int(self.request.params.get('l.pos_x'))
        c.pos_y = int(self.request.params.get('l.pos_y'))
        c.vihje = self.request.params.get('data')
        if c.vihje.startswith('CHAR:'):
            c.vihje = c.vihje[5:]
        self._new_d()
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _new_d(self):
        c = self.c
        jdata = c.item.get_json_sisu(c.lang)
        chars = jdata and jdata.get('chars') or []
        if chars:
            for rx, ry, rch in chars:
                if rx == c.pos_x and ry == c.pos_y:
                    c.cw_exist = True
                    break

    def create(self):
        # andmed võetakse postitatud vormist, valideeritakse ja paigutatakse
        # ajutistesse objektidesse, mida ei salvestata, vaid kuvatakse ainult vormil
        c = self.c
        self.form = Form(self.request, schema=forms.ekk.ylesanded.CrosswordCharLahterForm)
        rc = self.form.validate()
        
        is_tr = self.request.params.get('is_tr')
        try:
            c.pos_x = pos_x = int(self.request.params.get('pos_x'))
            c.pos_y = pos_y = int(self.request.params.get('pos_y'))

            errors = {}
            c.vihje = vihje = self.request.params.get('vihje').upper()
            if not vihje:
                errors = {'vihje': _("puudub")}
                raise ValidationError(self, errors)

            jdata = self.c.item.get_json_sisu(self.c.lang) or {}
            chars = jdata.get('chars') or []
            value = (pos_x, pos_y, vihje)
            for ind, (rx, ry, rch) in enumerate(chars):
                if rx == pos_x and ry == pos_y:
                    chars[ind] = value
                    value = None
                    break
            if value:
                chars.append(value)
            jdata['chars'] = chars
            self.c.item.set_json_sisu(jdata, c.lang)
            
        except ValidationError as e:
            self.form.errors = e.errors
            self._new_d()
            return Response(self.form.render(self._EDIT_TEMPLATE, extra_info=self.response_dict))

        model.Session.commit()
        # genereerime peavormi uuesti
        updated_url = self.url('ylesanne_edit_sisuplokk', id=c.item.id, ylesanne_id=c.ylesanne.id, lang=c.lang)
        raise HTTPFound(location=updated_url)

    def delete(self):
        "Ristsõna küsimuse kustutamine"
        c = self.c
        assert c.item.tyyp == const.INTER_CROSSWORD, 'Vale tüüp'
        pos_x = int(self.request.params.get('pos_x'))
        pos_y = int(self.request.params.get('pos_y'))

        jdata = c.item.get_json_sisu(c.lang) or {}
        chars = jdata.get('chars') or []
        chars = [r for r in chars if r[0] != pos_x or r[1] != pos_y]
        jdata['chars'] = chars
        c.item.set_json_sisu(jdata, c.lang)
        model.Session.commit()
        return HTTPFound(location=self.url('ylesanne_edit_sisuplokk', id=c.item.id, ylesanne_id=c.ylesanne.id, lang=c.lang))

    def __before__(self):
        c = self.c
        id = self.request.matchdict.get('ylesanne_id')
        c.ylesanne = model.Ylesanne.get(id)
        c.can_update = c.user.has_permission('ylesanded', const.BT_UPDATE, c.ylesanne)
        c.can_update_sisu = c.can_update and not c.ylesanne.lukus
        c.can_update_hm = c.can_update and c.ylesanne.lukus_hm_muudetav

        c.lang = self.params_lang()
        if c.lang and c.lang not in c.ylesanne.keeled or \
                c.lang == c.ylesanne.lang:
            c.lang = None
        c.item = model.Sisuplokk.get(self.request.matchdict.get('sisuplokk_id'))
        super(CwcharController, self).__before__()

    def _perm_params(self):
        return {'obj':self.c.ylesanne}

