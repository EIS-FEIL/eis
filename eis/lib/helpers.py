# Mako mallides kasutatavad kasutajaliidese koostamise abifunktsioonid

import mimetypes
from datetime import date, datetime, timedelta
from time import time as time_time
import re
import random
import json
import math
import base64
from webhelpers2 import html
from webhelpers2.html import escape, HTML, literal
from webhelpers2.html.tags import *
from webhelpers2.misc import NotGiven
from webhelpers2.html.tags import _set_id_attr, _make_safe_id_component, NL, BR
from webhelpers2.html.tools import update_params
from math import floor
import re
from sqlalchemy.engine.row import Row
import eiscore.const as const
import eiscore.utils as utils
import sys
import logging
log = logging.getLogger(__name__)
import eis
import eiscore.i18n as i18n
_ = i18n._

class RequestHelpers(object):
    def __init__(self, request):
        self.request = request
        self.c = request.handler.c

    def __getattr__(self, name):
        # kui mingit funktsiooni siin objektis pole, siis on see moodulis helpers
        # ja tagastame moodulis helpers oleva funktsiooni
        return getattr(sys.modules[__name__], name)
        #return eval(name)
    
    # JS laadimine
        
    def include_math(self):
        self.c.include_math = True
        return ''

    def include_raphael(self):
        self.c.include_raphael = True
        return ''

    def include_ckeditor(self):
        self.c.include_ckeditor = True
        return ''

    def include_jqueryui(self):
        self.c.include_jqueryui = True
        return ''

    def rqexp(self, visible=None, text=None):
        "Selgitus, et tärniga märgitud väljad on kohustuslikud"
        if visible is None:
            visible = self.c.is_edit or self.c.is_tr
        # jäetakse meelde, kas tärni näitamine on vajalik
        # (seda kasutatakse välja nimetuse kuvamisel)
        self.request.rq_visible = visible    
        if visible:
            if not text:
                text = _("Tärniga * märgitud väljad on kohustuslikud")
            return f'<div class="pt-1 px-1 bg-gray-50">{text}</div>'

    def _rqhint(self, rq):
        "Kohustusliku välja tärn"
        try:
            # rq=True on siis, kui väli on kohustuslik,
            if rq and self.request.rq_visible:
                # kui eelnevalt on tehtud rqexp() ja sellega on
                # leitud, et saab sisestada, siis kuvatakse tärn
                return ' <span class="rqhint">*</span>'
        except AttributeError:
            pass
        # tärni ei kuvata siis, kui ei toimu sisestamist
        # või kui väli pole kohustuslik
        return ''
        
    def flb(self, value, for_=None, col=None, rq=False):
        "Välja nimetus otsingufiltris"
        for_attr = ''
        if for_:
            for_ = _str_to_id(for_)
            for_attr = f'for="{for_}"'
        col_cls = col or ''
        # rq - kas on kohustuslik väli
        rq = self._rqhint(rq)
        return literal(f'<label class="font-weight-bold {col_cls}" {for_attr}>{value}{rq}</label>')
    
    def colHelper(self, col1, col2):
        h = self
        class ColHelper:
            def __init__(self, col1, col):
                self.col1 = col1
                self.col2 = col2
            def flb(self, value, for_=None, col=None, colextra=None, rq=False):
                col = col or self.col1 or ''
                if colextra:
                    col = col + ' ' + colextra
                return h.flb(value, for_, col, rq=rq)
        return ColHelper(col1, col2)
    
    def flb3(self, value, for_=None, class_='', rq=False):
        "Välja nimetus sisestusvormil"
        cls = 'col-md-3'
        if class_:
            cls += ' ' + class_
        return self.flb(value, for_, cls, rq=rq)

    def text(self, name, value, ronly=None, readonly=False, datafield=True, wide=True, pattern=None, title=None, spellcheck=False, **attrs):
        """Vaikimisi webhelpersi texti muudetud variant,
        mis paneb esimeseks atribuudiks value
        ja seetõttu saab tablesorteriga sorteerida veerge,
        mille sisuks on sisestusväli.
        ronly - kui on True, siis kuvatakse tekst (mitte sisestusväli)
        readonly - kui on True, siis lisatakse atribuut readonly
        """
        if isinstance(value, (float, int)):
            value = fstr(value)

        attrs['id'] = _str_to_id(attrs.get('id') or name)
        if ronly is None and not self.c.is_edit and not readonly:
            ronly = True
        if ronly:
            #attrs['disabled'] = True
            if attrs.get('size'):
                wide = False
            return readonly_text(value, name, wide)
        if readonly:
            attrs['readonly'] = 'readonly'
        if datafield:
            _add_class(attrs, 'form-control form-control-sm')
            if attrs.get('size') or not wide:
                _add_class(attrs, 'form-control-size')

        if pattern:
            attrs['pattern'] = pattern
        if title:
            attrs['title'] = title
            _add_class(attrs, 'noexample')             
        attrs['spellcheck'] = spellcheck and 'true' or 'false'        
        buf = html.tags.text(name, value, **attrs)
        # webhelpers sordib atribuudid tähestiku järgi
        # aga meil on vaja, et value oleks esimene atribuut, 
        # sest siis saaks tablesorteriga sortida tabeleid, 
        # mille veergudes on tekstiväljad
        n0 = buf.find(' ')
        n1 = buf.find(' value="')
        if n1 != n0 and n1 > -1:
            n2 = buf.index('"', n1+8)
            buf = buf[0:n0] + buf[n1:n2+1] + buf[n0:n1] + buf[n2+1:]
        return buf

    def text5(self, name, value, **attrs):
        attrs['size'] = 5
        return self.text(name, value, **attrs)

    def int5(self, name, value, **attrs):
        if not attrs.get('size'):
            attrs['size'] = 5
        if 'maxlength' not in attrs:
            attrs['maxlength'] = 9
        if 'pattern' not in attrs:
            attrs['pattern'] = '-?[0-9]{0,5}'
        _add_class(attrs, 'integer') 
        #attrs['type'] = 'number'  # ei saa kasutada, sest firefox kasutab miinuse asemel mõttekriipsu (dash)
        return self.text(name, value, **attrs)

    def int10(self, name, value, **attrs):
        if not attrs.get('size'):
            attrs['size'] = 10
        if 'maxlength' not in attrs:        
            attrs['maxlength'] = 9
        if 'pattern' not in attrs:
            attrs['pattern'] = '-?[0-9]{0,9}'
        _add_class(attrs, 'integer') 
        return self.text(name, value, **attrs)

    def posint(self, name, value, **attrs):
        _add_class(attrs, 'integer positive') 
        if 'maxlength' not in attrs:
            attrs['maxlength'] = 9
        if 'pattern' not in attrs:
            attrs['pattern'] = '[0-9]*'
        return self.text(name, value, **attrs)

    def posint10(self, name, value, **attrs):
        attrs['size'] = 10
        if 'maxlength' not in attrs:
            attrs['maxlength'] = 9
        if 'pattern' not in attrs:
            attrs['pattern'] = '[0-9]*'
        _add_class(attrs, 'integer positive') 
        return self.text(name, value, **attrs)

    def posint5(self, name, value, **attrs):
        if not attrs.get('size'):
            attrs['size'] = 5
        if 'maxlength' not in attrs:
            attrs['maxlength'] = 9
        if 'pattern' not in attrs:
            attrs['pattern'] = '[0-9]*'
        _add_class(attrs, 'integer positive') 
        return self.text(name, value, **attrs)

    def posint3(self, name, value, **attrs):
        if not attrs.get('size'):
            attrs['size'] = 3
        if 'maxlength' not in attrs:
            attrs['maxlength'] = 9
        if 'pattern' not in attrs:
            attrs['pattern'] = '[0-9]*'
        _add_class(attrs, 'integer positive') 
        return self.text(name, value, **attrs)

    def float5(self, name, value, **attrs):
        if not attrs.get('size'):
            attrs['size'] = 3
        if 'maxlength' not in attrs:
            attrs['maxlength'] = 9
        _add_class(attrs, 'float') 
        return self.text(name, value, **attrs)

    def float10(self, name, value, **attrs):
        if not attrs.get('size'):
            attrs['size'] = 10
        if 'maxlength' not in attrs:
            attrs['maxlength'] = 9
        _add_class(attrs, 'float')
        return self.text(name, value, **attrs)

    def money(self, name, value, **attrs):
        return self.posfloat(name, fstr(value), **attrs)

    def posfloat(self, name, value, size=None, maxlength=None, **attrs):
        attrs['size'] = size or 5
        attrs['maxlength'] = maxlength or 9
        _add_class(attrs, 'float positive') 
        return self.text(name, value, **attrs)

    def checkbox1(self, name, value='1', label=None, **attrs):
        attrs['id'] = _str_to_id(name)
        return self.checkbox(name, value, label, **attrs)

    def checkbox(self, name, value='1', label=None, checkedif=None, checked=False, ronly=None, datafield=True, disabled=False, display=True, nohelp=False, mr0=False, title=None, **attrs):
        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly or disabled:
            attrs['disabled'] = 'disabled'
        if checkedif is not None:
            if isinstance(checkedif, list):
                checked = bool(str(value) in checkedif or value in checkedif)
            else:
                checked = bool(str(checkedif) == str(value))
        if checked:
            attrs['checked'] = 'true'                
        _add_class(attrs, 'custom-control-input')
        attrs['name'] = name
        attrs['value'] = value
        if not "id" in attrs:
            attrs["id"] = _str_to_id("{0}_{1}".format(name, value))
        id = attrs['id']

        s_attrs = _ser_attrs(**attrs)
        buf_input = f'<input type="checkbox" {s_attrs}/>'

        mrcls = mr0 and 'mr-0' or ''
        buf = f'<label class="custom-control custom-checkbox custom-control-inline {mrcls}"' + \
          (title and f' title="{hm_str2(title)}"' or '') + \
          (not display and ' style="display:none"' or '') + '>' + \
              buf_input
        # hds ei kuva välja, kui puudub label
        label = hm_str2(label or '')
        labelcls = 'custom-control-label'
        if nohelp:
            labelcls += ' nohelp'
        if label:
            buf += f'<span class="{labelcls}" for="{id}">{label}</span>'
        else:
            buf += f'<span class="{labelcls}"></span>'
        buf += '</label>'
        return literal(buf)

    def radio(self, name, value='1', checkedif=None, checked=False, ronly=None, disabled=False, label=None, **attrs):
        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly or disabled:
            attrs['disabled'] = 'disabled'
        attrs['name'] = name
        attrs['value'] = value        
        if not "id" in attrs:
            attrs["id"] = _str_to_id("{0}_{1}".format(name, value))
        id = attrs['id']

        if checkedif is not None:
            if isinstance(checkedif, list):
                checked = bool(str(value) in checkedif)
            else:
                checked = bool(str(checkedif) == str(value))
        if checked:
            attrs['checked'] = 'true'
        _add_class(attrs, 'custom-control-input')

        s_attrs = _ser_attrs(**attrs)
        buf_input = f'<input type="radio"{s_attrs}/>'
              
        buf = '<label class="custom-control custom-radio custom-control-inline">' + \
              buf_input
        label = hm_str2(label or '')
        buf += f'<span class="custom-control-label" for="{id}">{label}</span>'
        buf += '</label>'
        # div/label ei toimi modaalses aknas
        return literal(buf)

    def checkradio(self, name, value='1', single=None, checkedif=None, **attrs):
        if single == 1:
            return radio(name, value, checkedif=checkedif, **attrs)
        else:
            return checkbox(name, value, checkedif=checkedif, **attrs)

    def select_bool(self, name, value, ronly=None, **attrs):
        BOOL = [html.tags.Option('Jah', '1'),
                html.tags.Option('Ei', '')]
        options = BOOL
        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly:
            buf = ''
            for opt in options:
                if bool(value) == bool(opt.value):
                    buf = opt.label
                    break
            return readonly_text(buf, name)

        return select(name, value, options, ronly=ronly, **attrs)

    def select(self, name, selected_values, options, empty=False, id=NotGiven, ronly=None, names=False, datafield=True, wide=True, disabled=False, add_missing=False, **attrs):
        # # Accept None as selected_values meaning that no option is selected
        if selected_values is None:
            selected_values = ('',)
        # Turn a single string or integer into a list
        elif isinstance(selected_values, (str, int)):
            selected_values = (selected_values,)
        # Cast integer values to strings
        selected_values = list(map(str, selected_values))
        id = _str_to_id(id == NotGiven and name or id)

        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly:
            return readonly_select(selected_values, options, name)

        if datafield:
            _add_class(attrs, 'custom-select custom-select-sm')
        if not wide:
            attrs['style'] = 'width:initial;display:inline-block;'
        if empty:
            # lisame tyhja valiku
            if not isinstance(empty, str):
                empty =  _("-- Vali --")
            prompt = empty
        else:
            prompt = None
            
        if disabled:
            attrs['disabled'] = 'disabled'
        if names:
            _set_id_attr(attrs, id, name)
            if prompt:
                attrs['prompt'] = prompt
            return _select_names(name, selected_values, options, **attrs)

        if add_missing:
            # lisame valikutele need väärtused, mis on valitud, aga mida pole valikus
            _opts = []
            keys = []
            for r in options:
                if isinstance(r, (list, tuple, Row)):
                    key = r[0]
                else:
                    key = r
                keys.append(key)
                _opts.append(r)
            for val in selected_values:
                if val and val not in keys:
                    keys.append(val)
                    _opts.append(val)
            options = _opts
            
        def _list2options(li, prompt=None):
            _opts = []
            for r in li:
                if isinstance(r, (list, tuple, Row)):
                    label, value = r[1], r[0]
                    attrs = len(r) == 3 and isinstance(r[2], dict) and r[2] or {}
                    if isinstance(value, list):
                        item = html.tags.OptGroup(label, _list2options(value))
                        _opts.append(item)
                        continue
                else:
                    label = value = r
                    attrs = {}
                if not isinstance(value, str):
                    value = str(value)

                item = OptionWithAttr(label, value, attrs)
                _opts.append(item)
            return OptionsWithAttr(_opts, prompt=prompt)

        _options = _list2options(options, prompt)
        return html.tags.select(name, selected_values, _options, id=id, **attrs)

    def select_entry(self, name, selected_values, options, **kw):
        """Vastuste sisestamisel kasutatav select.
        """
        options = [('', ' ')] + \
            list(options) + \
            [(const.ENTRY_VASTAMATA, _("9-vastamata")),
             (const.ENTRY_LOETAMATU, _("8-loetamatu"))]
        kw['wide'] = False
        kw['empty'] = False
        kw['class_'] = 'jumper jumper-entry'
        return self.select(name, selected_values, options, **kw)

    def select_checkbox(self, name, value, options, linebreak=False, **attrs):
        if value is None:
            value = ''
        if not isinstance(value, (list,tuple,Row)):
            value = (value)
        if len(value) and isinstance(value[0], int):
            value = [str(v) for v in value]

        if not self.c.is_edit:
            return readonly_select(value, options, name)

        buf = ""
        for item in options:
            id = item[0]
            label = ' '+item[1]+'  '
            attrs['checked'] = value and id in value
            buf_inp = self.checkbox(name, id, label=label, **attrs)
            if linebreak:
                buf_inp = f'<div>{buf_inp}</div>'
            buf += buf_inp + '\n'
        return buf

    def select_radio(self, name, value, options, linebreak=False, ronly=None, **attrs):
        if value is None:
            value = ''
        if not isinstance(value, (list,tuple,Row)):
            value = (value,)
        if len(value) and isinstance(value[0], int):
            value = [str(v) for v in value]

        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly:
            return readonly_select(value, options, name)

        buf = ""
        for item in options:
            id = item[0]
            label = ' '+item[1]+'  '
            attrs['checked'] = value and id in value
            buf += self.radio(name, id, label=label, ronly=False, **attrs) + '\n'
            if linebreak:
                buf += literal('<br/>')
        return buf

    def select2(self, name, value, options, class_=None, empty=False, **attrs):
        if self.c._arrayindexes != '':
            # vea parandamine
            value = self.c.params.getall(name)
            if len(options) and isinstance(options[0][0], int):
                value = list(map(int, value))
        if empty:
            # select2 ei kuva seda, aga see on vajalik, et algselt oleks valik tyhi 
            options = [('','')] + options
        js = self.select2_js(name, value, options, **attrs)
        script = "<script>$(function(){" + js + "})</script>"
        return self.select(name, value, options, multiple=attrs.get('multiple'), class_=class_) + literal(script)
    
    def select2_js(self, name, value, options, data=None, width=None, allowClear=None, multiple=False, max_sel_length=None, placeholder=None, url=None, min_length=3, multilevel=False, template_selection=None, mult_order=False, element=None, on_change=None, on_select=None, on_unselect=None, tags=False, selectOnClose=None, **attrs):
        if not width:
            width = '95%'
        if selectOnClose is None:
            selectOnClose = allowClear
        params = ['width:"%s"' % width,
                  'language: "%s"' % self.request.locale_name,
                  'selectOnClose: %s' % (selectOnClose and 'true' or 'false'),
                  ]
        if max_sel_length:
            params.append('maximumSelectionLength: %d' % max_sel_length)
            multiple = True
        params.append('multiple:%s' % (multiple and 'true' or 'false'))
        if data:
            if isinstance(data, list):
                data = json.dumps(data)
            params.append('data: %s' % data)
        if template_selection:
            params.append("templateSelection: %s" % template_selection)
        if data and multilevel:
            params.append("templateResult: function(n){return $('<span style=\"padding-left:'+(20*n.level)+'px;' + (n.level==0 ? 'font-weight:bold;' : '')+'\">' + n.text + '</span>'); }")
        if allowClear:
            params.append('allowClear: true')
        if tags:
            # kasutaja saab ise lisada uusi tekste
            params.append('tags: true') 
        if not placeholder:
            placeholder = _("Sisesta ja vali")
        if placeholder:
            params.append('placeholder: "%s"' % placeholder)
        if url:
            if min_length:
                params.append('minimumInputLength: %d' % min_length)
            params.append('ajax: {url:"%s", dataType: "json", quietMillis: 1200, function(term, page) {return {q: term};}, results: function(data, page){return {results: data};}}' % url)
        if not element:
            element = """$('select[name="%s"]')""" % (name)
        buf = "%s.select2({%s})" % (element, ','.join(params))
        if on_change:
            buf += ".on('change', %s)" % on_change
        if on_select:
            buf += ".on('select2:select', %s)" % on_select
        if on_unselect:
            buf += ".on('select2:unselect', %s)" % on_unselect
        if data and value:
            # kui valikud pole optionina, vaid data-na, siis on vaja eraldi algne väärtus seada
            buf += ".val(%s).trigger('change.select2')" % json.dumps(value)
            
        buf += ';'
        return buf

    def date_field(self, name, value, ronly=None, wide=True, allow_clear=False, **attrs):
        "Kuupäevaväli, fookus avab kalendri"
        value = self.str_from_date(value)

        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly:
            return roxt(value, wide=wide)
        else:
            locale = self.request.locale_name
            _add_class(attrs, 'form-control flatpickr-input')            
            if 'placeholder' not in attrs:
                attrs['placeholder'] = _("pp.kk.aaaa")
            if wide == False:
                attrs['style'] = 'width:100px'

            icons = '<div class="input-group-append">' +\
                         '<div class="input-group-text">' +\
                         '<i class="mdi mdi-calendar-month" aria-hidden="true"></i>'
            if allow_clear:
                icons +='<i class="mdi mdi-close" aria-hidden="true"></i>'
            icons += '</div></div>'

            buf = literal('<div class="input-group input-group-sm">') +\
                  self.text(name, value, lang=locale, **attrs) +\
                  literal(icons) +\
                  literal('</div>')

            if wide == False:
                buf = literal('<div class="d-inline-block">') + buf + literal('</div>')
            return buf

    def date_f(self, name, value, **attrs):
        "Ikooniga kuupäevaväli, ikoonil vajutades avaneb kalender"
        return self.date_field(name, value, **attrs)

    def time(self, name, value, default='', show0=False, ronly=None, is_timer=False, is_sec=False, allow_clear=True, wide=True, **attrs):
        if isinstance(value, datetime):
            # ajahetkest võetakse kellaaeg
            if is_sec:
                svalue = self.str_time_sec_from_datetime(value)
            else:
                svalue = self.str_time_from_datetime(value)
        else:
            svalue = value
        if not svalue or ((svalue == '00:00' or svalue == '00.00') and not show0):
            svalue = default

        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly:
            return roxt(svalue, wide=wide)
        else:
            locale = self.request.locale_name
            icon = is_timer and 'mdi-timer' or 'mdi-clock-outline'
            if is_sec:
                attrs['size'] = 7
                attrs['pattern'] = '[0-2]?[0-9][:.][0-5][0-9][:.][0-5]?[0-9]'
                _add_class(attrs, 'form-control flatpickr-time-input flatpickr-time-ss')
            else:
                attrs['size'] = 5
                attrs['pattern'] = '[0-2]?[0-9][:.][0-5][0-9]'
                _add_class(attrs, 'form-control flatpickr-time-input')            
            if 'placeholder' not in attrs:
                if is_sec:
                    attrs['placeholder'] = _("tt.mm.ss")
                else:
                    attrs['placeholder'] = _("tt.mm")

            if wide == False:
                attrs['style'] = 'width:100px'
            buf = literal('<div class="input-group input-group-sm">') +\
                  self.text(name, svalue, lang=locale, **attrs)
            if allow_clear:
                buf += literal('<div class="input-group-append">' +\
                               '<div class="input-group-text">' +\
                               '<i class="mdi mdi-close"></i>'+\
                               '</div>' +\
                               '</div>')
            buf += literal('</div>')
            if wide == False:
                buf = literal('<div class="d-inline-block">') + buf + literal('</div>')
            return buf

    def timedelta_min(self, name, value, **attrs):
        # hh.mm
        if isinstance(value, datetime):
            # ajahetkest võetakse kellaaeg
            svalue = self.str_time_from_datetime(value)
        else:
            # sekundite arv
            svalue = self.str_from_time(value)
        attrs['placeholder'] = _("tt.mm")
        return self.time(name, svalue, is_timer=True, **attrs)

    def timedelta_sec(self, name, value, **attrs):
        # hh.mm.ss
        if isinstance(value, datetime):
            # ajahetkest võetakse kellaaeg
            svalue = self.str_time_sec_from_datetime(value)
        else:
            # sekundite arv
            svalue = self.str_from_time_sec(value)
        attrs['placeholder'] = _("tt.mm.ss")
        return self.time(name, svalue, is_timer=True, is_sec=True, **attrs)
   
    def textarea(self, name, content, ronly=None, disabled=None, datafield=True, wide=True, pattern=None, justify=None, title=None, spellcheck=False, **attrs):
        if ronly is None and not self.c.is_edit and not disabled:
            ronly = True
        if ronly:
            return readonly_textarea(content, name)
        else:
            if disabled:
                attrs['disabled'] = 'disabled'
            if datafield:
                _add_class(attrs, 'form-control form-control-sm')
            if justify in const.JUSTIFIES:
                _add_class(attrs, 'text-align-%s' % justify)
            if pattern:
                attrs['pattern'] = pattern
            if title:
                attrs['title'] = title

            attrs['spellcheck'] = spellcheck and 'true' or 'false'
            return html.tags.textarea(name, content, **attrs)

    def ckeditor2(self, name, content, toolbar='basic', ronly=None, top_id=None):
        "CKEditor init_ckeditor kaudu"
        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly:
            return readonly_textarea(literal(content or ''), name, nl=False)
        field = self.textarea(name, content, ronly=False)
        locale = self.request.locale_name
        toolbar = self.ckeditor_toolbar(toolbar)
        js = f"init_ckeditor($('#{name}'), '{top_id or ''}', '{locale}', '{toolbar}', null, null, 'body16');"
        buf = field + literal('\n<script>$(function(){\n' + js + '});</script>')
        return buf
        
    def ckeditor(self, name, content, toolbar='basic', ronly=None, rows=None, height=300, css=None, resized=False, cols=None, justify=None, shared=None, with_js=True, icons=None, entermode=None, baseHref=None, srcmode=False, disain_ver=const.DISAIN_HDS, disabled=False, **attrs):
        "CKEditor"
        if ronly is None and not self.c.is_edit:
            ronly = True

        if ronly:
            return readonly_textarea(literal(content or ''), name, nl=False)
        buf = self.textarea(name, content, ronly=False, **attrs)
        if with_js:
            buf_js = self.ckeditor_js(name, toolbar, ronly, rows, height, css, resized, cols, justify, shared, icons=icons, entermode=entermode, baseHref=baseHref, srcmode=srcmode, disain_ver=disain_ver, **attrs)
            buf = buf + literal('\n<script>$(function(){\n' + buf_js + '});</script>')
        if disabled:
            buf = literal('<div class="ckeditor-disabled">') + buf + literal('</div>')
        return buf

    def ckeditor_js(self, name, toolbar='basic', ronly=None, rows=None, height=300, css=None, resized=False, cols=None, justify=None, shared=None, placeholder=None, icons=None, entermode=None, baseHref=None, spellcheck=False, srcmode=False, disabled=False, smart_quotes=True, disain_ver=const.DISAIN_HDS, upload_url=None, browse_url=None, maxlength=None, **attrs):
        "CKEditor"
        if ronly is None and not self.c.is_edit:
            ronly = True
        if ronly and not disabled:
            return ''

        params = []
        params.append("language: '%s'" % self.request.locale_name)
        if rows:
            height = '%spx' % (rows*24 + 8)
        params.append("height: '%s'" % (height))
        if cols:
            width = '%spx' % (cols * 10)
            params.append("width: '%s'" % (width))
        if justify in const.JUSTIFIES:
            params.append("bodyClass: 'text-align-%s'" % justify)
        if shared:
            params.append("sharedSpaces: {top:'%s_ckeditor_top'}" % (shared))

        extraPlugins = []
        removePlugins = []

        if toolbar == 'supsub' or icons and 'MatFraction' in icons:
            # et saaks murrujoont kuvada (MatFraction)
            removePlugins.extend(['showborders','magicline'])
            # et peale täisarvu murdu kirjutades ei tehtaks murd uuele reale
            if not entermode:
                params.append("enterMode: CKEDITOR.ENTER_BR")

        elif toolbar == 'inlinetext':
            removePlugins.append('showborders')
        if disabled:
            removePlugins.append('toolbar')
            icons = [None]
            extraPlugins.append('autogrow')
            params.append("autoGrow_onStartup: true")

        if entermode:
            params.append('enterMode: %s' % entermode)
        if srcmode:
            params.append("startupMode: 'source'")
        if maxlength:
            extraPlugins.append('wordcount')
            params.append('wordcount: {' + \
                          'showParagraphs: false, ' +\
                          'showCharCount: false, ' +\
                          'showWordCount: false, ' +\
                          'countHTML: true, ' +\
                          'countSpacesAsChars: true, ' +\
                          'maxCharCount: %s ' % maxlength +\
                          '}')
        if icons:
            toolbar = 'custom'
            params.append("toolbar_custom: %s" % self.ckeditor_icons(icons))
        toolbar = self.ckeditor_toolbar(toolbar)
        params.append("toolbar: '%s'" % (toolbar))
        if toolbar == 'feedback_src':
            # div plugina dialoogis kuvada tal:condition väli
            params.append("div_tal: true")
            # codemirrorit ei või kasutada sharedspace korral (vt ES-1641)
            extraPlugins.append('codemirror')

        if removePlugins:
            params.append("removePlugins: '%s'" % (','.join(removePlugins)))
        if extraPlugins:
            params.append("extraPlugins: '%s'" % (','.join(extraPlugins)))            
            
        if disain_ver == const.DISAIN_EIS1:
            # vana disain
            params.append("contentsCss: ['/static/eis/ckeditor_style.css', '/static/eis/ylesanne.eis1.css', '/static/lib/matheditor/lib/matheditor.min.css?1']")
    
        params.append("disableObjectResizing: true") # et firefox ei kuvaks tabeli ymber raami
        if spellcheck:
            params.append("disableNativeSpellChecker: false")
        if placeholder:
            params.append('placeholder:"%s"' % (placeholder.replace('"','')))
        if baseHref:
            params.append('baseHref: "%s"' % baseHref)

        if not smart_quotes:
            # et tagasisidevormi avaldistes saaks anda parameetreid
            params.append('autocorrect_enabled:false')

        if upload_url:
            params.append('filebrowserUploadUrl: "%s"' % upload_url)
        if browse_url:
            params.append('filebrowserBrowseUrl: "%s"' % browse_url)
        id = name.replace('.','')
        buf = "ckeditor_js('%s', {%s}, '%s', %s);" % (id,
                                                     ', '.join(params),
                                                     css or '',
                                                     resized and 'true' or 'false')
        return buf

    def ckeditor_toolbar(self, toolbar):
        """Kontrollitakse, kas kasutajal on lähtekoodi kasutamise õigus.
        Kui on, siis tagastatakse lähtekoodi nupuga toolbar
        """
        if toolbar in ('basic', 'span', 'gapmatchspan', 'html2png', 'meta', 'hottext', 'inlinetext', 'inlinechoice', 'gapmatch'):
            if self.c.user.has_permission('srcedit', const.BT_UPDATE):
                toolbar = toolbar + '_src'
        return toolbar
    
    def ckeditor_icons(self, icons):
        "Ülesande koostaja poolt valitud nuppudega toolbari konf"
        iconsets = (
            ['Source'],
            ['MetaBlock','ToggleButton','GapText'],
            ['NewPage'],
            ['Cut','Copy','Paste','PasteFromWord','PasteText'],
            ['Undo','Redo','Find','Replace','SelectAll','RemoveFormat'],
            ['Bold', 'Italic', 'Underline','mathck',
             'ckeditor_wiris_formulaEditor','ckeditor_wiris_formulaEditorChemistry',
             'Subscript','Superscript','SupSub','MatMultiply','MatDivide','MatFraction','ArrowUp','ArrowDown'],
            ['NumberedList','BulletedList','Outdent','Indent','Blockquote','CreateDiv'],
            ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
            ['Image','Html5audio','Table','SpecialChar','Link','Iframe','eszett'],
            ['Styles','Format','Font','FontSize','lineheight','TextColor','BGColor','gg'],
            ['Maximize', 'ShowBlocks'],
            )
        used_icons = []
        for iconset in iconsets:
            used_iconset = [r for r in iconset if r in icons]
            if used_iconset:
                used_icons.append(used_iconset)
        return str(used_icons)
    
    def url(self, route_name, **args):
        return self.request.handler.url(route_name, **args) 

    def url_current(self, action=None, **args):
        return self.request.handler.url_current(action, **args)

    def form_save(self, id, plainurl=None, form_name='form_save', **kw):
        """Vormi avamine sõltuvalt sellest, 
        kas vorm on uue kirje lisamiseks 
        või olemasoleva muutmiseks.
        """
        method = 'post'
        if not plainurl:
            if not id or self.request.handler.c.action == 'create':
                # kui loomisel on tekkinud viga, siis võib id olemas olla, aga pole andmebaasis
                plainurl = self.request.handler.url_current('create')
            else:
                plainurl = self.request.handler.url_current('update', id=id)
        if not kw.get('class_'):
            kw['class_'] = 'form-save'
        return form(plainurl, method=method, id=form_name, **kw)

    def ajax_submit_form(self, value=None, ckeditor=False):
        """Luuakse nupp, millele vajutamisel submititakse nupu kõrval asuv vorm.
        Vormil peab olemas olema "action".
        """
        if not value:
            value = _("Salvesta")

        if ckeditor:
            # kopeerime kireva teksti toimetist teksti vormiväljale
            # dynaamilise dialoogiakna korral see ise sinna ei lähe
            destroy_ck = 'destroy_ckeditor(f);'
            txt = "for(inst_id in CKEDITOR.instances){ CKEDITOR.instances[inst_id].updateElement();var buf=$('textarea#'+inst_id).val();};"
        else:
            destroy_ck = ''
            txt = ''
        success = "function(data){var f=$('form#form_dlg'),b=f.parent(); %s f.replaceWith(data);block_is_ready(b);}" % destroy_ck
        txt += "$.post($('form#form_dlg').attr('action'),$('form#form_dlg').serialize(),%s);" % (success)        
        return self.button(value, onclick=txt)

    def button(self, value, clicked=False, level=1, buttontype='button', htmlvalue=False, mdicls=None, mdicls2=None, **attrs):
        """Nupu loomine"""
        if level == 0:
            cls = 'iconbtn'
        elif level == 2:
            cls = 'btn btn-secondary'
        else:
            cls = 'btn btn-primary'
        _add_class(attrs, cls)

        if 'id' not in attrs:
            attrs['id'] = _str_to_id(value)
        onclick = attrs.get('onclick') or ''
        if onclick and clicked:
            # kaitse topeltkliki vastu
            msec = clicked > 100 and int(clicked) or 0
            attrs['onclick'] = "if(is_dblclick($(this), %d))return false;%s" % (msec, onclick)

        if not htmlvalue:
            value = hm_str2(value)
        if mdicls:
            if value:
                mdicls = mdicls + ' mr-2'
            value = f'<i class="mdi mdi-24px {mdicls}"></i>' + value
        if mdicls2:
            if value:
                mdicls2 = mdicls2 + ' ml-2'
            value = value + f'<i class="mdi mdi-24px {mdicls2}"></i>'
        if buttontype == 'submit':
            attrs['value'] = "1"
        title = attrs.get('title')
        if title and not attrs.get('aria-label'):
            attrs['aria-label'] = title
        return literal('<button type="%s" %s>%s</button>' % \
                      (buttontype, _ser_attrs(**attrs), value))


    def submit(self, value=None, out_form=False, confirm='', disabled=False, clicked=None, level=1, **attrs):
        """Submit-nupu loomine"""
        if not value:
            value = _("Salvesta")
        if 'id' not in attrs:
            attrs['id'] = _str_to_id(value)
        if 'name' not in attrs:
            attrs['name'] = attrs['id']

        onclick = attrs.get('onclick') or ''
        # (ei saa määrata onclick='set_spinner($(this));',
        # sest faili laadimise nupu korral on vaja spinner ka lõpetada)
        
        if clicked:
            # kaitse topeltkliki vastu
            onclick = "if(is_dblclick($(this)))return false;%s" % (onclick or '')
        if out_form:
            # nupp asub väljaspool vormi ja submit tuleb esile kutsuda javascriptiga
            onclick = "$('form#form_save').submit(); return false;"
        if confirm:
            onclick = "if(!confirm('%s'))return false;%s" % (confirm, onclick or '')
        if onclick:
            attrs['onclick'] = onclick
        if disabled:
            attrs['disabled'] = 'disabled'
        buttontype = 'submit'
        return self.button(value, buttontype='submit', level=level, **attrs)

    def submit_confirm(self, value=None, confirm='', **attrs):
        """Nupp kuvab confirm-dialoogi ja siis submitib ümbritseva vormi
        Vormi submit uuendab eeldatavasti terve lehe
        """
        if not value:
            value = _("Salvesta")
        if 'id' not in attrs:
            attrs['id'] = _str_to_id(value)

        # nupu id läheb vormi välja #op väärtuseks
        fok = "function(){f.find('input#op').val(op);f.submit();}"
        onclick = "var f=$(this.form),op=this.id;confirm_dialog($(this).attr('confirm'), %s);" % fok
        dblclick = "if(!is_dblclick($(this))){%s};return false" % (onclick)
        return self.button(value=value, confirm=confirm, onclick=onclick, **attrs)


    def file(self, name, value=None, id=None, files=[], **attrs):
        if not id:
            id = _str_to_id(name)
        buf = '<div class="custom-file-wrapper"><div class="custom-file">' + \
              f'<input type="file" class="custom-file-input" id="{id}" name="{name}" />' +\
              '<button type="button" class="btn btn-secondary mr-2">' +\
              '<i class="mdi mdi-upload mr-2" aria-hidden="true"></i>' +\
              (value or _("Vali fail")) +\
              '</button></div>' +\
              f'<label class="custom-file-label" for="{id}">' 
        if not files:
            buf += _("Faili pole valitud")
        buf += '</label>'
        for url, fn, fsize in files:
            if fsize is not None:
                fn += ' (%s)' % filesize(fsize)
            buf += f' <a href="{url}" class="p-2">{fn}</a> '
        buf += '</div>'

        return literal(buf)
    
    def btn_back(self, value=None, url='#'):
        if not value:
            value = _("Tagasi")
        return self.btn_to(value, url, level=2)

    def btn_new(self, plainurl, value=None, **attrs):
        if not value:
            value = _("Uus")
        return self.btn_to(value, plainurl, **attrs)

    def btn_search(self, value=None, clicked=False):
        if not value:
            value = _("Otsi")
        return self.submit(value, id="otsi", level=1, class_='searchb', clicked=clicked)
            
    def submit_dlg(self, value=None, container=None, clicked=False, onsuccess=None, method=None, op=None, in_dlg=False, **kw):
        """Luuakse nupp, millele vajutamisel submititakse dialoogis olev vorm
        Vormil peab olemas olema "action".
        """
        if not value:
            value = _("Salvesta")
        if in_dlg:
            # asendada dialoogiakna sisu
            container = "$(this).closest('.modal-body')"
        onclick = "submit_dlg(this, %s, %s, %s, null, %s, %s)" % \
                  (container or 'null',
                   method and "'%s'" % method or 'null',
                   clicked and 'true' or 'false',
                   onsuccess or 'null',
                   op and "'%s'" % op or 'null')
        return self.button(value, onclick=onclick, **kw)

    def form_search(self, url=None, id='form_search', **kw):
        if not url:
            url = self.request.handler.url_current('index')        
        # lisame unikaalse väärtusega parameetri, mis hoiab IE puhverdamast
        # ja sortimise parameetri, mida hakatakse listi sortimisel uuendama
        kw['hidden_fields'] = {'rid': str(random.random())[2:],
                               'sort': self.c.sort,
                               'psize': self.c.psize}
        return form(url, method='get', id=id, **kw)

    def toggle_filter(self, is_extra):
        buf = '<div class="mb-2 mr-2 d-flex justify-content-end">' +\
              '<a href="#" class="btn btn-link btn-toggle-filter">' +\
              '<i class="mdi mdi-filter mr-1" aria-hidden="true"></i>' +\
              (is_extra and _("Täiendavad tingimused") or _("Filter")) +\
              '</a></div>'
        return literal(buf)

    def hidefilter(self, value):
        # kui otsingutingimus on valitud (value) või kui soovitakse alati filtrit lahti hoida (c.filopen),
        # siis tavaline filtri klass;
        # muul juhul selline klass, mis jääb peitu kuni filtri ikoonil klikkimiseni
        if value:
            return 'filter'
        elif self.c.filopen:
            return 'filter filter-extra'
        else:
            return 'filter filter-extra filter-hide'

    def add(self, plainurl):
        return literal('<a href="%s" class="post"><i class="mdi mdi-file-document-box-plus mdi-24px" title="%s"></i></a>' % (plainurl, _("Lisa")))

    def edit_js(self, js):
        return literal('<a href="#" onclick="%s"><i class="mdi mdi-file-edit mdi-24px" title="%s"></i></a>' % (js, _("Muuda")))                

    def pager(self, 
              items=None, 
              partial=True, 
              msg_not_found=None,
              msg_found_one=None,
              msg_found_many=None,
              listdiv=None,
              form='#form_search',
              newline=False,
              list_url=None,
              is_all='',
              is_psize=True,
              is_psize_all=False):

        # items - pagineeritavad read
        # msg_not_found - teade siis, kui ridu pole
        # msg_found_one - teade siis, kui leiti 1 kirje
        # msg_found_many - teade siis, kui leiti mitu kirjet
        # listdiv - loetelu koha määratlus (jQuery) järgmise lk sisu asetamiseks
        # form - vormi määratlus (jQuery), kust loetakse otsingutingimused järgmise lk sisu jaoks
        # all_act - kas kuvada "Kõik" ja kas see on aktiivne
        if list_url:
            _list_url = list_url
        else:
            _list_url = self.get_list_url()

        # otsingu url ja sortimistingimused
        hiddens = self.hidden('list_url', _list_url, class_="list_url", id=None) + \
                  self.hidden('list_sort', self.c.sort, class_="list_sort", id=None)

        buf = ''
        try:
            cnt = items.item_count
            can_paginate = True
        except AttributeError:
            # items pole paginate objekt
            cnt = len(items)
            can_paginate = False

        if cnt == 0:
            msg = msg_not_found or _("Kirjeid ei leitud")
        elif cnt == 1:
            msg = msg_found_one or _("Leiti 1 kirje")
        else:
            if not msg_found_many:
                msg_found_many = _("Leiti {n} kirjet")
            msg = msg_found_many.format(n=cnt)

        if not can_paginate or cnt <= 1:
            return literal('<span role="status">' + msg + '</span>') + hiddens

        format = "$link_previous ~5~ $link_next"                
        if list_url:
            url_current = list_url
        else:
            url_current = self.url_current(None)

        sort = (self.request.params.get('sort') or '').replace(' ','+')
        if re.search(r'[^a-z\(\)A-Z0-9\_\.,-]', sort):
            sort = ''
        url = url_current + (url_current.find('?') > -1 and '&' or '?') + \
              "sort=%s" % (sort) +\
              "&partial=1&page=$page"

        # page current_page span last_page next_page prev_page
        def link_tag(item):
            item_type = item['type']
            text = item['value']
            target_url = item['href']
            attrs = item['attrs']

            tnext = _("Järgmine")
            tprev = _("Eelmine")
            if item_type == 'previous_page':
                buf = '<li class="page-item prev">' +\
                      f'<a class="page-link" href="{target_url}" title="{tprev}" aria-label="{tprev}">' +\
                      '<i class="mdi mdi-arrow-left" aria-hidden="true"></i>' +\
                      '</a></li>'
            elif item_type == 'next_page':
                buf = '<li class="page-item next">' +\
                      f'<a class="page-link" href="{target_url}" title="{tnext}" aria-label="{tnext}">' +\
                      '<i class="mdi mdi-arrow-right" aria-hidden="true"></i>' +\
                      '</a></li>'
            elif item_type == 'current_page':
                buf = '<li class="page-item active" aria-current="page">' +\
                      f'<a class="page-link" href="{target_url}">' +\
                      text +\
                      '</a></li>'
            elif item_type == 'span' or not target_url:
                buf = '<li class="page-item disabled">' +\
                      text +\
                      '</li>'
            else:
                # page, last_page
                buf = '<li class="page-item">' +\
                      f'<a class="page-link" href="{target_url}" title="{text}" aria-label="{text}">' +\
                      text +\
                      '</a></li>'
            return buf

        # teade
        msgbuf = '<span class="pager-msg d-none d-md-block" role="status">%s</span>' % (msg)

        # paginaatori nupud ul/li
        ulbuf = '<ul class="pagination flex-wrap mb-0" data-listdiv="%s" data-form="%s">' % (listdiv or '', form) +\
              items.pager(format,
                          url=url,
                          link_attr={'class':'valge_11 paginate'},
                          curpage_attr={'class':'valge_11 paginate_act'},
                          link_tag=link_tag)
        if is_all and items.page_count > 1:
            text = _("Kõik")
            if self.c.page == '0':
                # aktiivne on "Kõik"
                buf = '<li class="page-item active" aria-current="page">' +\
                      text +\
                      '</li>'
            else:
                url_all = url.replace('$page', '0')
                buf = '<li class="page-item">' +\
                      f'<a class="page-link" href="{url_all}" title="{text}" aria-label="{text}">' +\
                      text +\
                      '</a></li>'
        ulbuf += '</ul>'
        if is_all and items.page_count > 1:
            ulbuf += '<span class="helpable" id="%s"></span>' % is_all

        # kuvan korraga
        MIN_COUNT = 20
        ALL_COUNTS = (20, 50, 100)
        if is_psize and items and items.item_count > MIN_COUNT:
            # tulemusi on nii palju, et peab olema lk suuruse valikuväli
            navcls = 'nav-need-clone'
            psizefld = '<select name="ppsize" class="nosave custom-select" data-form="%s">' % form
            if self.c.psize == const.ITEMS_ALL:
                psize = self.c.psize
            else:
                try:
                    psize = int(self.c.psize)
                except:
                    try:
                        psize = items.items_per_page
                    except:
                        psize = None
            for n in ALL_COUNTS:
                psizefld += '<option value="{n}" {selected}>{n}</option>'.format(
                    n=n,
                    selected=n == psize and 'selected' or '')
            if is_psize_all:
                psizefld += '<option value="{sk}" {selected}>{title}</option>'.format(
                    sk=const.ITEMS_ALL,
                    title=_("Kõik"),
                    selected=psize == const.ITEMS_ALL and 'selected' or '')
            psizefld += '</select>'

            psizebuf = '<div class="form-inline d-flex justify-content-md-end">' + \
                       '<div class="form-group"><label class="mr-3">%s</label> %s</div></div>' % \
                       (_("Kuvan korraga:"), psizefld)
        else:
            navcls = ''
            psizebuf = ''

        buf = literal('<nav aria-label="%s" class="nav-pagin %s">' % (_("Paginaator"), navcls) + \
              '<div class="d-flex align-items-center justify-content-between flex-wrap mb-1">' + \
              '<div>' + msgbuf + '</div>' +\
              '<div>' + ulbuf + '</div>' +\
              '<div>' + psizebuf + '</div>' +\
              '</div>') + hiddens + literal('</nav>')
                
        return buf

    def get_list_url(self, nosort=False):
        """Loetelu vormi kuvamisel kutsutuna leiab URLi, millega seda loetelu taastada
        """
        params = self.request.params.mixed()
        
        # kas on parameetreid?
        # kui pole, siis võtame meeldejäetud parameetrid
        # neid läheb vaja, kui otsinguvorm on avatud meeldejäetud parameetritega
        handler = self.request.handler
        is_default = self.request.params.get('default')
        has_params = handler._has_search_params()
        if not is_default and not has_params:
            p = handler._get_default_params()
            if p:
                params = dict()
                for key, val in p.items():
                    if isinstance(val, date):
                        # form.from_python...
                        val = self.str_from_date(val)
                    params[key] = val
        if 'partial' in params:
            del params['partial']
            params['rid'] = True
        if nosort and 'sort' in params:
            del params['sort']
        return self.url_current(None, **params)

    def url_current_params(self, **kw):
        """Paginaator kasutab seda funktsiooni lehekülgede URLide genereerimiseks
        """
        search_url = self.request.url
        return update_params(search_url, **kw)

    def th_nosort(self, name, title, width=None, nowrap=None, colspan=None, class_=None):
        return self.th(title, width, nowrap, colspan, class_=class_, sorter=False)

    def th(self, title, width=None, nowrap=None, colspan=None, rowspan=None, align=None, sorter=None, style=None, class_=None, helpable_id=None, rq=False):
        if isinstance(title, (list, tuple)):
            return self.th_sort(title[0], title[1])
        
        attr = ''
        attr += ' scope="col"'
        if width:
            attr += ' width="%s"' % width
        if nowrap:
            attr += ' nowrap="nowrap"'
        if colspan:
            attr += ' colspan="%s"' % colspan
        if rowspan:
            attr += ' rowspan="%s"' % rowspan
        if align:
            attr += ' align="%s"' % align
        if style:
            attr += ' style="%s"' % style
        if class_:
            attr += ' class="%s"' % class_
        if sorter == False:
            sorter = 'false'
        if sorter:
            # tablesorteri kasutamise korral:
            # sortimisel kasutatava parseri nimi (text, digit, ipAddress, url, isoDate, percent...)
            # või kui ei soovi sortimist, siis "false"
            attr += ' sorter="%s"' % sorter
        title += self._rqhint(rq)
        if helpable_id:
            title = title + f' <span class="helpable" id="{helpable_id}"></span>'
        return literal('<th%s>%s</th>' % (attr, title))

    def th_sort(self, name, title, width=None, nowrap=None, colspan=None, class_=None, helpable_id=None):
        "(Pagineeritava) tabeli päis, mille järgi saab tabelit serveris sortida"
        # name on andmebaasiväli, mille järgi sorditakse
        # mitme välja järgi sortimisel eristada need tyhikuga, mitte komaga (et toimiks mõlemas suunas sortimine)
        if not name:
            return self.th(title, width=width, nowrap=nowrap, colspan=colspan, class_=class_, helpable_id=helpable_id, sorter=False)
        attr = ''
        attr += ' scope="col"'
        if width:
            attr += ' width="%s"' % width
        if nowrap:
            attr += ' nowrap="nowrap"'
        if colspan:
            attr += ' colspan="%s"' % colspan

        data = self.request.environ.get('QUERY_STRING')
        data = _remove_params(data, ['sort', 'partial']) 
        current_sort = self.request.params.get('sort') or ''
        li = current_sort and current_sort.split(',') or []
        buf = ''

        if class_:
            class_ += ' '
        else:
            class_ = ''
        if name in li:
            class_ += 'srv_headerSortUp'
        elif '-%s' % name in li:
            class_ += 'srv_headerSortDown'
        else:
            class_ += 'srv_header'
            
        if helpable_id:
            title = title + f' <span class="helpable" id="{helpable_id}"></span>'
        txt = '<th sortid="%s" class="%s"%s>%s</th>' % (name, class_, attr, title)
        return literal(txt)

    def page_id(self, template):
        # eemaldame .mako ja asendame /, kuna see on HTML elemendi ID sees tülikas
        p_id = template.uri[:-5].replace('/','-').replace('.','_')
        if p_id == 'avalik-ylesanded-sisuplokk':
            # kasutame innove vaates ja avalikus vaates sama abiinfot
            p_id = 'ekk-ylesanded-sisuplokk'
        return p_id

    def is_msie(self):
        agent = self.request.environ.get('HTTP_USER_AGENT')
        if agent:
            return agent.find('MSIE') > -1 or agent.find('Trident') > -1 or False

    def is_firefox(self):
        agent = self.request.environ.get('HTTP_USER_AGENT')
        if agent:
            return agent.find('Firefox') > -1

    def is_chrome(self):
        agent = self.request.environ.get('HTTP_USER_AGENT')
        if agent:
            return agent.find('Chrome') > -1

    def has_mathplayer(self):
        agent = self.request.environ.get('HTTP_USER_AGENT')
        return agent and agent.find('MathPlayer') > -1

    def is_mathml_capable(self):
        agent = self.request.environ.get('HTTP_USER_AGENT')
        if not agent:
            return False
        elif agent.find('Safari') > -1 or \
           agent.find('MSIE') > -1 and agent.find('MathPlayer') < 0:
            return False
        else:
            return True

    def qcode(self, kysimus, nl=False, ah=None):
        """Küsimuse kood ülesandes"""
        c = self.c
        if c.show_q_code:
            if ah or c.eksperdivaade:
                kood = kysimus.kood
                return literal('%s<span class="kysimus">%s</span>' % (nl and '<br/>' or '', kood))
            tulemus = kysimus.tulemus
            if tulemus and tulemus.arvutihinnatav:
                kood = kysimus.kood
                return literal('%s<span class="kysimus">%s</span>' % (nl and '<br/>' or '', kood))
        return ''

    def ccode(self, value):
        """Vastuse kood ülesandes"""
        if self.c.show_r_code:
            return literal('<span class="kood">%s</span>' % value)
        else:
            return ''

    def lang_orig(self, contents, lang=None, rtf=False):
        buf = ''
        if lang:
            buf = literal('<span class="lang-tag btn btn-light btn-tag">%s</span>' % lang)
        if isinstance(contents, (int, float)):
            contents = str(contents)
        if rtf:
            contents = literal(contents)
        return buf + \
               literal('<span class="lang-orig">') +\
               (contents or '') + \
               literal('</span>')

    def lang_tr(self, lang=None):
        if not lang:
            lang = self.c.lang
        return lang

    def lang_tag(self, lang=None):
        return ''

    def not_top(self):
        """Dialoogiaknas kasutamiseks, et vältida dialoogi sisu
        laadimist brauseri pealmises aknas.
        """
        return literal("""<script>
        if ((typeof jQuery == 'undefined') || !$('.page-wrapper').length) window.location.replace('%s');
        </script>""" % (self.url('avaleht')))

    def sbool(self, value):
        if value:
            return _("Jah")
        elif value is None:
            return '-'
        else:
            return _("Ei")

    def grid_add(self, js_extra=None):
        js = "grid_addrow($(this).closest('table').attr('id'));%s return false;" % (js_extra or '')
        return literal('<a href="#" onclick="%s" class="menu" title="%s"><span class="glyphicon glyphicon-plus"></span></a>' % (js, _("Lisa")))

    def form(self, url, method="post", multipart=False, hidden_fields=None, disablesubmit=False, preventsubmit=False, **attrs):
        if disablesubmit:
            attrs['onsubmit'] = "$(this).find('input[type=submit]').eq(0).attr('disabled','disabled');"
        elif preventsubmit:
            # teine ja vbl parem variant, kuna siis nupp jääb alles ja nupu nimi läheb postiga kaasa
            attrs['onsubmit'] = "if($(this).data('is_saving') == true){ event.preventDefault(); return; } $(this).data('is_saving', true);"
        return html.tags.form(url, method=method, multipart=multipart, hidden_fields=hidden_fields, **attrs)

    def button150(self, value, **attrs):
        """Nupu loomine"""
        return self.button(value, **attrs)

    def btn_to(self, value, plainurl, method='get', **attrs):
        """Nupu loomine, mis asendab lehekülje sisu.
        """
        _add_class(attrs, method)
        return self.button(value, href=plainurl, **attrs)

    def btn_to_dlg(self, value, plainurl, method='get', title=None, dlgtitle=None, width=None, size=None, form=None, confirm=None, params=None, dialog_id=None, beforeClose=None, **attrs):
        """Nupu loomine, mis avab dialoogiakna
        """
        # lisame midagi, mis teeb urli unikaalseks, et IE ei puhverdaks
        plainurl += (plainurl.find('?') > -1 and '&' or '?') + 'rid=%s' % rnd()
        s_attrs = "title: '%s'" % js_str1(dlgtitle or title or '')
        s_attrs += ", url: '%s'" % plainurl
        if form:
            s_attrs += ", form: %s" % form
        if method != 'get':
            s_attrs += ", method: '%s'" % method
        if params:
            s_attrs += ", params: %s" % params
        if size:
            s_attrs += ", size: '%s'" % size
        if dialog_id:
            s_attrs += ", dialog_id: '%s'" % dialog_id
        if beforeClose:
            s_attrs += ", beforeClose: %s" % beforeClose
        onclick = "open_dialog({%s});" % s_attrs
        if confirm:
            attrs['confirm'] = confirm
            onclick = "confirm_dialog($(this).attr('confirm'), function(){close_this_dialog(this);%s})" % onclick
        if title:
            attrs['title'] = title
        return self.button(value, onclick=onclick, **attrs)

    def link_breadcrumb(self, value, url):
        for item in reversed(c.pagehistory):
            if item.url == url or item.url.startswith(url+'?'):
                url = item.url
                break
        return self.link_to(value, url)

    def blink_to(self, label, url='', method='get', level=1, mdicls=None, **attrs):
        "Nupukujuline link"
        class_ = attrs.get('class_') or ''
        if mdicls:
            icon = literal(f'<i class="mdi {mdicls} mdi-24px mr-2"></i>')
            if label:
                label = icon + ' ' + label
            else:
                label = icon
        if not label:
            label = '-'
        if method == 'post':
            _add_class(attrs, method)
        if level == 2:
            _add_class(attrs, 'btn btn-secondary')
        else:
            _add_class(attrs, 'btn btn-primary')
        return html.tags.link_to(label, url=url, **attrs)

    def pdflink_to(self, url, label=''):
        return self.link_to(label, url, mdicls='mdi-file-pdf', title=_("Laadi PDF alla"))        

    def filelink_to(self, url, label=''):
        return self.link_to(label, url, mdicls='mdi-file', title=_("Laadi fail alla"))

    def link_to(self, label, url='', method='get', level=1, mdicls=None, mdicls2=None, **attrs):
        class_ = attrs.get('class_') or ''
        if mdicls:
            label = literal(f'<i class="mdi {mdicls} mdi-24px mr-2"></i>') + label
        elif mdicls2:
            label = label + literal(f'<i class="mdi {mdicls2} mdi-24px ml-2"></i>')
        elif not label:
            label = '-'
        if method == 'post':
            _add_class(attrs, method)
        title = attrs.get('title')
        if title:
            attrs['aria-label'] = title
        if level:
            if level == 2:
                _add_class(attrs, 'btn btn-link-secondary')
            else:
                _add_class(attrs, 'btn btn-link')
        return html.tags.link_to(label, url=url, **attrs)

    def link_to2(self, label, url='', **attrs):
        attrs['level'] = 2
        return self.link_to(label, url, **attrs)

    def link_to_container(self, value, plainurl, method='get', container=None, mdicls=None, **attrs):
        """Lingi loomine, mis kuvab tegevuse tulemuse plokis
        """
        onclick = "dialog_load('{plainurl}', null, '{method}', {container});return false;".\
                  format(container=container or 'null',
                         plainurl=plainurl,
                         method=method)
        if mdicls:
            value = literal(f'<i class="mdi {mdicls} mdi-24px mr-2"></i>') + value
        return self.link_to(value, url='#', onclick=onclick, **attrs)

    def link_to_bubble(self, value, plainurl, data=None, bubble_id=None, method='get', **attrs):
        """Lingi loomine, mis kuvab tegevuse tulemuse mullis
        """
        attrs['level'] = 2
        onclick = "load_bubble(this, '{plainurl}','{data}','{method}','{bubble_id}');return false;".\
                  format(bubble_id=bubble_id or '',
                         plainurl=plainurl or '',
                         data=data or '',
                         method=method)    
        return self.link_to(value, url='#', onclick=onclick, **attrs)

    def link_to_dlg(self, value, plainurl, method='get', title='', width=None, height=None, size=None, dialog_id=None, **attrs):
        """Lingi loomine, mis avab dialoogiakna
        """
        # lisame midagi, mis teeb urli unikaalseks, et IE ei puhverdaks
        plainurl += plainurl.find('?') > -1 and '&' or '?%s' % random.random()
        s_attrs = "title: '%s'" % js_str1(title)
        s_attrs += ", url: '%s'" % plainurl
        if size:
            s_attrs += ", size: '%s'" % size
        if dialog_id:
            s_attrs += ", dialog_id: '%s'" % dialog_id
        onclick = "open_dialog({%s});return false" % s_attrs
        return self.link_to(value, onclick=onclick, **attrs)

    def crumb(self, label, url=None, active=False):
        if url:
            lnk = link_to(label, url)
        else:
            lnk = label
        if active:
            li_attr = 'class="breadcrumb-item active" aria-current="page"'
        else:
            li_attr = 'class="breadcrumb-item"'
        return '<li %s>%s</li>' % (li_attr, lnk)

    def crumb_sep(self):
        return ''

    def grid_hide(self):
        onclick = "var tr=$(this).closest('tr');tr.hide();tr.find('input.deleted').val('1');return false;"
        buf = '<a href="#" class="xclose" onclick="%s"><i class="mdi mdi-delete mdi-24px"></i></a>' % onclick
        return literal(buf)

    def grid_remove(self, js_extra=None, title=None):
        "Tabelis rea kustutamine, salvestatakse hiljem koos vormiga"
        if not title:
            title = _("Eemalda")
        onclick = "var tr=$(this).parents('tr')[0];tr.parentNode.removeChild(tr);%s return false;" % (js_extra or '')
        buf = '<a href="#" class="xclose" onclick="%s" title="%s"><i class="mdi mdi-delete-forever mdi-24px"></i></a>' % (onclick, title)
        return literal(buf)

    def grid_s_remove(self, selector=None, confirm=False, onremove=None):
        onclick = "return grid_s_remove(this, %s, %s, %s)" % \
             (selector and "'%s'" % selector,
              confirm and 'true' or 'false',
              onremove or 'null')
        buf = '<a href="#" class="xclose" onclick="%s" title="%s"><i class="mdi mdi-delete-forever mdi-24px"></i></a>' % (onclick, _("Eemalda"))
        return literal(buf)

    def ajax_remove(self, plainurl, selector):
        onclick = "ajax_remove(this, $('%s'), true); return false;" % selector
        title = _("Eemalda")
        buf = f'<a href="{plainurl}" onclick="{onclick}" class="xclose" title="{title}" aria-label="{title}">' + \
            _mdi_icon('mdi-delete-forever', aria_hidden=False) + '</a>'
        return literal(buf)

    def remove(self, plainurl, confirm=None, icon=None, confirm_id=None):
        "Kustutamise ikoon, salvestatakse kohe"
        buf = '<a href="%s" class="delete"' % (plainurl)
        if confirm:
            buf += ' confirm="%s"' % (confirm)
        if confirm_id:
            buf += ' confirm_id="%s"' % (confirm_id)
        title = _("Eemalda")
        buf += f' title="{title}" aria-label="{title}"'
        if not icon:
            icon = 'mdi-delete-forever'
        buf = buf + '>' + _mdi_icon(icon, aria_hidden=False) + '</a>'
        return literal(buf)

    def bremove(self, plainurl, confirm=None, confirm_id=None):
        "Kustutamise nupp, salvestatakse kohe"
        buf = '<a href="%s" class="delete btn btn-secondary"' % (plainurl)
        if confirm:
            buf += ' confirm="%s"' % (confirm)
        if confirm_id:
            buf += ' confirm_id="%s"' % (confirm_id)
        buf = buf + '><i class="mdi mdi-delete-forever mdi-24px mr-2"></i>' + _("Eemalda") + '</a>'
        return literal(buf)

    def btn_remove(self, plainurl=None, id=None, value=None, confirm=None, **attrs):
        "Kustutamise  nupp, salvestatakse kohe"
        if not value:
            value = _("Kustuta")
        if not plainurl:
            if not id:
                id = self.c.item.id
            plainurl = self.request.handler.url_current('delete', id=id)
        if confirm:
            attrs['confirm'] = confirm
        return self.btn_to(value, plainurl, method='delete', level=2, **attrs)

    def dlg_edit(self, plainurl, dlgtitle=None, title=None, width=None, height=None, method='get', form=None, confirm=None, size='md', **attrs):
        """Nupu loomine, mis avab dialoogiakna
        """
        onclick = "open_dialog({'title': '%s', 'url': '%s', 'form': %s, 'method': '%s', size: '%s'})" % \
            (dlgtitle or title or '',
             plainurl,
             form or 'null',
             method,
             size)
        if confirm:
            onclick = "if(confirm('%s')){%s}" % (confirm, onclick)
        # href on vajalik, et brauser annaks fookuse    
        buf = f'<a href onclick="{onclick};return false;"'
        if title:
            buf += f' title="{title}" aria-label="{title}"'
        buf += '>' + _mdi_icon('mdi-file-edit', aria_hidden=False) + '</a>'
        return literal(buf)
        
    def _alert(self, alert_cls, msg, dismissable, mdicls='mdi-information-outline'):
        dismiss = dismissable and 'alert-dismissable' or ''
        buf = f"""<div class="alert {alert_cls} {dismiss} fade show" role="alert">
              <i class="mdi {mdicls}"></i> {msg}"""
        if dismissable:
            close = _("Peida teade")
            buf += f'<button type="button" class="close" data-dismiss="alert" title="{close}" aria-label="{close}">' + \
              _mdi_icon('mdi-close') + '</button>'
        buf += '</div>'
        return literal(buf)

    def alert_info(self, msg, dismissable=True, mdicls=None):
        return self._alert('alert-primary', msg, dismissable, mdicls=mdicls)

    def alert_notice(self, msg, dismissable=True, mdicls=None):
        return self._alert('alert-secondary', msg, dismissable, mdicls=mdicls)

    def alert_warning(self, msg, dismissable=True, mdicls=None):
        return self._alert('alert-warning', msg, dismissable, mdicls=mdicls)    

    def alert_success(self, msg, dismissable=True, mdicls=None):
        return self._alert('alert-success', msg, dismissable, mdicls=mdicls)

    def alert_error(self, msg, dismissable=True, mdicls=None):
        return self._alert('alert-danger', msg, dismissable, mdicls=mdicls)

    def alert_error2(self, msg):
        # väike veateade, ilma kinnipaneku võimaluseta ja ilma i-ikoonita
        return f'<div class="error">{msg}</div>'

    def poserr(self, name):
        # veateate jaoks lisatav eraldi väli, kui veateadet ei soovita tegeliku välja juurde
        # (peab kasutama enne tegelikku välja)
        return f'<input type="text" disabled="disabled" name="{name}" style="display:none"/>'

    def spinner(self, title=None, spinner_cls=None, hide=False):
        if not title:
            title = _("Laadin...")
        style_attr = hide and 'style="display:none"' or ''
        return literal(f'<div class="spinner-wrapper {spinner_cls}" {style_attr}><div class="spinner-bg spinner-border spinner-border-sm color-primary" role="status"><span class="sr-only">{title}</span></div></div>')

    def progress(self, percent, label, id=None, class_=None):
        attr_id = id and f'id="{id}"' or ''
        # class: bg-success (roheline), bg-info (sinine), bg-warning (kollane), bg-danger (punane)
        buf = f"""
          <div class="form-group mr-0" {attr_id}>
            <div class="progress">
              <div class="progress-bar {class_ or ''}" role="progressbar"
                style="width: {percent}%;" aria-label="{label}"
                aria-valuenow="{percent}" aria-valuemin="0" aria-valuemax="100">
              </div>
            </div>
            <div class="d-flex justify-content-end">
              <span>{percent}%</span>
            </div>
          </div>"""
        return literal(buf)

    def str2_from_timedelta(self, n):
        """Ajavahemiku esitus sõnadega
        """
        try:
            hours = int(n / 3600)
            minutes = int((n % 3600) / 60)
            seconds = n % 60
            buf = ''
            if hours:
                if hours == 1:
                    buf += _("1 tund")
                else:
                    buf += _("{n} tundi").format(n=hours)
            if minutes:
                if minutes == 1:
                    buf += ' ' + _("1 minut")
                else:
                    buf += ' ' + _("{n} minutit").format(n=minutes)
            if seconds:
                if seconds == 1:
                    buf += ' ' + _("1 sekund")
                else:
                    buf += ' ' + _("{n} sekundit").format(n=seconds)
            return buf
        except:
            return n or ''

    def mdi_icon(self, mdicls, size=24, **attrs):
        return literal(_mdi_icon(mdicls, size, **attrs))

    def badge_primary(self, text):
        # sinine
        return _badge(text, 'badge-primary')

    def badge_secondary(self, text):
        # hall (neutraalne)
        return _badge(text, 'badge-secondary')
    
    def badge_danger(self, text):
        # punane
        return _badge(text, 'badge-danger')

    def badge_success(self, text):
        # roheline
        return _badge(text, 'badge-success')
    
    def badge_warning(self, text):
        # kollane
        return _badge(text, 'badge-warning')
    
########################################################
# Abifunktsioonid mooduli sees kasutamiseks

def _badge(text, badgecls):
    buf = f'<span class="badge icon-badge {badgecls}">{text}<i class="mdi mdi-information-outline"></i></span>'
    return literal(buf)

def _mdi_icon(mdicls, size=24, aria_hidden=True, **attrs):
    if aria_hidden:
        attrs['aria-hidden'] = 'true'
    s_attrs = _ser_attrs(**attrs)    
    return f'<i class="mdi mdi-{size}px {mdicls}" {s_attrs}></i>'

def str_est_time_from_datetime(n):
    """Kellaaja esitus punktiga
    """
    try:
        return '%02i.%02i' % (n.hour, n.minute)
    except:
        return n or ''

def str_time_from_datetime(n):
    """Kellaaja esitus
    """
    try:
        return '%02i.%02i' % (n.hour, n.minute)
    except:
        return n or ''

def str_time_sec_from_datetime(n):
    """Kellaaja esitus
    """
    try:
        return '%02i.%02i.%02i' % (n.hour, n.minute, n.second)
    except:
        return n or ''
    
def str_from_time(n):
    """Aja esitus hh.mm
    """
    try:
        hours = int(n / 3600)
        minutes = int(n % 3600 / 60)
        return '%02i.%02i' % (hours, minutes)
    except:
        return n or ''

def strh_from_time(n):
    """Aja esitus HH h MM min
    """
    try:
        hours = int(n / 3600)
        minutes = int(n % 3600 / 60)
        if hours:
            return '%i h %i min' % (hours, minutes)
        else:
            return '%i min' % (minutes)
    except:
        return n or ''

def str_from_time_sec(n):
    """Aja esitus hh.mm.ss
    """
    try:
        hours = int(n / 3600)
        minutes = int((n % 3600) / 60)
        seconds = n % 60
        buf = '%02i.%02i.%02i' % (hours, minutes, seconds)
        return buf
    except:
        return n or ''

def str_from_time_mmss(n):
    """Aja esitus mm.ss
    """
    try:
        hours = int(n / 3600)
        minutes = int((n % 3600) / 60)
        seconds = n % 60
        buf = '%02i.%02i' % (minutes, seconds)
        if hours:
            buf = '%02i.%s' % (hours, buf)
            return buf
    except:
        return n or ''

def _remove_params(query, keys):
    """
    data - url.environ['QUERY_STRING']
    keys - list parameetritest, mis tuleb eemaldada
    """
    params = query.split('&')
    for key in keys:
        for param in params:
            if param.startswith(key+'='):
                params.remove(param)
    return '&'.join(params)

def _add_class(attrs, classname):
    if not classname:
        return attrs
    if 'class_' in attrs:
        c = attrs.pop('class_')
    else:
        c = attrs.get('class')
    if c:
        attrs['class'] = c + ' ' + classname
    else:
        attrs['class'] = classname
    return attrs

def _str_to_id(value):
    """Sõnadest moodustatakse id.
    """
    return _make_safe_id_component(value)

def _select_names(name, selected_values, options, **attrs):
    """Selline select, kus option võib lisaks 
    VALUE atribuudile omada ka NAME atribuuti.
    option antakse kujul (value,label,name)
    """
    attrs["name"] = name
    if attrs.get('multiple'):
        attrs['multiple'] = 'multiple'
    
    # Prepend the prompt
    prompt = attrs.pop("prompt", None)
    if prompt is not None:
        options = [("", prompt)] + list(options)
        
    # Create the options structure
    def gen_opt(val, label, name):
        kw = {'value': val}        
        if val in selected_values:
            kw['selected'] = 'selected'
        if name:
            kw['name'] = name
        return HTML.option(label, **kw)

    buf = literal('<select %s>' % _ser_attrs(**attrs))
    for opt in options:
        if isinstance(opt, (list,tuple,Row)):
            value = str(opt[0])
            label = str(opt[1])
            name = len(opt) > 2 and str(opt[2])
        else:
            value = label = opt
            name = None
        buf += gen_opt(value, label, name)
    buf += literal('</select>')
    return buf

def readonly_text(value, name=None, wide=True):
    attrs = ''
    if name:
        attrs += f'name="{name}"'
    wcls = not wide and 'readonly-notwide' or ''
    if value is None:
        value = ' '
    return literal(f'<div class="readonly {wcls}" {attrs}>{value}</div>')

def roxt(value, wide=True):
    return readonly_text(value, wide=wide)

def readonly_textarea(value, name=None, nl=True):
    if not value:
        value = ' '
    attrs = ''
    if name:
        attrs = f'name="{name}"'        
    buf = literal(f'<div class="readonly mr-3" {attrs}>')
    if nl:
        # asendame reavahetused HTMLi reavahetustega
        for s in value.split('\n'):
            buf += s + literal('<br/>')
    else:
        buf += value
    buf += literal('</div>')
    return buf

def readonly_rtf(value):
    return literal('<div class="readonly mr-3">' + (value or '') + '</div>')

def td_field(title, field, id=None):
    return literal("<td class='fh'>%s</td><td nowrap>%s</td>" % (title, field))

def readonly_select(selected_values, options, name=None):
    li = []
    for opt in options:
        if isinstance(opt, (list,tuple,Row)):
            value = str(opt[0])
            label = str(opt[1])
        else:
            value = label = opt

        if value and value in selected_values:
            li.append(label)

    buf = ', '.join(li)
    return readonly_text(buf, name)

def image(src, alt=None, **attrs):
    if alt: 
        attrs['alt'] = alt
    return literal('<img src="%s" %s/>' % (src, _ser_attrs(**attrs)))

def origin(title):
    "Pildi algallika kohta info kuvamine pildi kõrval oleva küsimärgiga"
    if title:
        onclick = "open_dialog({contents_text: this.title})"
        return literal('<i class="mdi mdi-comment-question-outline mdi-24px" title="{}" onclick="{}"></i>').format(title, onclick)

def help_for(page_id, model):
    """Lisatakse abiinfo info selle lehekülje kõigi abiinfoga väljade jaoks
    """
    txt = ''
    fields = model.Abiinfo.get_fields(page_id)
    for field_id, text, url in fields:
        text = (text or '').replace('\n', '<br/>')
        txt += f'\n<div class="dhelpfld" data-field_id="{field_id}" data-url="{url or ""}">{text}</div>'
    if txt:
        # kui mõne välja kohta on abiinfot, siis lisatakse .dhelppage wrapper
        txt = f'<div class="dhelppage" data-page_id="{page_id}" aria-hidden="true" style="display:none">' +\
          txt +\
          '\n</div>'
        txt = literal(txt)
    return txt

def time_from_tuple(tu):
    if tu:
        return tu[0]*3600 + tu[1]*60

def fstr(f, digits=3):
    """Reaalarvu esitus.
    Kui arvul on komakohad, siis esitatakse koos komakohtadega.
    Kui arvul pole komakohti, siis esitatakse täisarvuna.
    """
    if not isinstance(f, (float, int)):
        return f
    if digits == 0:
        return str(int(round(f)))
    # 3 kohta peale koma
    buf = ('%.' + str(digits) + 'f') % f
    # aga ilma nullideta peale koma
    return re.sub(r'\,?0+$', '', buf.replace('.',','))

def rstr(f):
    """Reaalarvu esitus täisarvuna.
    """
    if isinstance(f, float):
        return int(round(f))
    elif isinstance(f, int):
        return f
    else:
        return ''

def mstr(f, digits=2, nbsp=False):
    """Rahaarvu esitus.
    Kui arvul on komakohad, siis esitatakse koos 2 komakohaga.
    Kui arvul pole komakohti, siis esitatakse täisarvuna.
    """
    if not isinstance(f, (float, int)):
        return f
    if f % 1:
        # 2.5
        buf = (('%.' + str(digits) + 'f €') % f ).replace('.',',')
    else:
        # 2
        buf = '%i €' % f
    if nbsp:
        buf = buf.replace(' ', '&nbsp;')
    return buf

def fround(f, digits=2):
    """Reaalarvu ümardamine (võib olla None)"""
    if not isinstance(f, float):
        # arv oli None või täisarv
        return f
    f1 = round(f, digits)
    if digits > 0 and round(f) == f1:
        # tagastame täisarvu, kui see võrdub ümaradatud reaalarvuga
        return round(f)
    # tagastame reaalarvu
    return f1

def html_nl(value):
    buf = ''
    if value:
        try:
            value.__html__
            # value on literal
            br = literal('<br/>')
        except:
            # value on lihtsalt tekst
            br = '<br/>'
        for s in value.split('\n'):
            buf += s + br
    return buf

def html_lt(buf):
    return buf and buf.replace('<', '&lt;') or ''

def str_from_date(dd):
    if not dd:
        return ''
    elif isinstance(dd, date) or isinstance(dd, datetime):
        return dd.strftime('%d.%m.%Y')
    else:
        return str(dd)[:10]

def is_null_time(dt):
    "Kas kellaaeg on määramata (määramata tähenduses on kasutusel 00.00)"
    return not (dt and (dt.hour or dt.minute))
    
def str_from_datetime(dt, seconds=False, microseconds=False, hour0=True, hour23=True, skell=False):
    """
    Aja vormistamine stringina

    dt
        date, datetime või string
    """
    if not dt:
        return ''
    elif isinstance(dt, datetime):
        if not hour0 and is_null_time(dt):
            # kui kell on 00.00, siis on kell määramata ja kuvame ainult kuupäeva
            return dt.strftime('%d.%m.%Y')
        elif not hour23 and dt.hour == 23 and dt.minute == 59:
            # kui kell on 23.59, siis kehtib kuni päeva lõpuni ja kuvame ainult kuupäeva
            return dt.strftime('%d.%m.%Y')
        else:
            kpv = dt.strftime('%d.%m.%Y')
            if microseconds:
                kell = dt.strftime('%H.%M.%S.%f')
            elif seconds:
                kell = dt.strftime('%H.%M.%S')
            else:
                kell = dt.strftime('%H.%M')
            if skell:
                # kuvada sõna "kell"
                return _("{kpv} kell {kell}").format(kpv=kpv, kell=kell)
            else:
                return f'{kpv} {kell}'
    elif isinstance(dt, date):
        return dt.strftime('%d.%m.%Y')
    else:
        if seconds:
            return str(dt)[:10]
        else:
            return str(dt)[:8]            

def jstr(s):
    """Reavahed asendatakse nii, et sobib javascripti stringiks.
    """
    return literal('\\\n'.join(s.split('\n')))

def jsparam(s):
    """Reavahed ja jutumärgid asendatakse nii, et sobib javascripti atribuudiks
    """
    if s is None:
        return ''
    elif isinstance(s, str):
        return literal(s.replace('\r', '').replace('\\', '\\\\').replace('\n','\\\n').replace('"','\\"'))
    else:
        # arv
        return s

def toid(name):
    """Tehakse lollikindel HTML elemendi ID"""
    return name.replace('-','_').replace('.','_')

def width(obj, css=False):
    if obj is None:
        value = None
    elif isinstance(obj, (int, float)):
        value = obj
    else:
        value = obj.laius
    if value:
        if css:
            return 'width:%spx; ' % value
        else:
            return literal('width="%s"' % value)
    return ''

def height(obj, css=False):
    if obj is None:
        value = None
    elif isinstance(obj, (int, float)):
        value = obj
    else:
        value = obj.korgus
    if value:
        if css:
            return 'height:%spx; ' % value
        else:
            return literal('height="%s"' % value)
    return ''

def print_input(cols=10, rows=1):
    if not rows or rows == 1:
        return '...'*(cols or 10)
    else:
        buf = ('...'*(cols or 50)+'<br/>')*rows
        return literal('<div class="inputlines">%s</div>' % buf)

def literal(buf):
    if not buf:
        return ''
    else:
        return html.literal(buf)

def javascript_link(*urls, **attrs):
    try:
        src = attrs.pop('src')
    except KeyError:
        src = None
    li = []
    for url in urls:
        # kaitse puhverdamise vastu
        url += '?%s' % (eis.__static_version__)
        if src or src is None and ('source' in url  or 'src' in url):
            # minimeerimata js faile (arenduskeskkonnas) ei soovi yldse kunagi puhverdada
            url += '?.%s' % rnd()
        li.append(url)
    return html.tags.javascript_link(*li, **attrs)

def stylesheet_link(*urls, **attrs):
    try:
        src = attrs.pop('src')
    except KeyError:
        src = False
    li = []
    for url in urls:
        # kaitse puhverdamise vastu
        url += '?%s' % eis.__static_version__
        if src or 'source' in url  or 'src' in url:
            # minimeerimata js faile (arenduskeskkonnas) ei soovi yldse kunagi puhverdada
            url += '?.%s' % rnd()        
        li.append(url)
    return html.tags.stylesheet_link(*li, **attrs)

def bread_sep():
    return literal('<td width="15"><div align="center" class="brown">»</div></td>')

def rnd():
    return ('%s' % (random.random()))[2:]

def filesize(b):
    if b is None:
        return
    elif b < 1024:
        return '%d B' % b
    elif b < 1000000:
        return '%s kB' % fstr(b/1024.,1)
    else:
        return '%s MB' % fstr(b/1048576.,1)

def b64encode2s(buf):
    "Sisend on bytes, väljund selle base64-kodeering stringina"
    return base64.b64encode(buf).decode('ascii').strip()

def url_to_link(buf):
    urls = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)", re.MULTILINE|re.UNICODE)
    value = urls.sub(r'<a href="\1" target="_blank">\1</a>', buf or '')
    return value

class OptionWithAttr(html.tags.Option):
    def __init__(self, label, value=None, attrs={}):
        self.label = label
        self.value = value
        self.attrs = attrs
        
class OptionsWithAttr(html.tags.Options):
    def _render(self, options, selected_values):
        tags = []
        for opt in options:
            if isinstance(opt, html.tags.OptGroup):
                content = self._render(opt, selected_values)
                tag = html.tags.HTML.tag("optgroup", NL, content, label=opt.label)
                tags.append(tag)
            else:
                value = opt.value if opt.value is not None else opt.label
                selected = value in selected_values
                try:
                    attrs = opt.attrs
                except AttributeError:
                    attrs = {}
                tag = html.tags.HTML.tag("option", opt.label, value=opt.value,
                    selected=selected, **attrs)
                tags.append(tag)
        return html.tags.HTML(*tags, nl=True)

########################################################
# Abifunktsioonid mooduli sees kasutamiseks

def chk_w(value):
    "Peab olema sõna"
    return re.sub(r'[^\w]','', value or '')

def escape_tags(value):
    "Eemaldatakse <>"
    if value:
        return value.replace('<', '&lt;').replace('>','&gt;')

def escape_script(value):
    "Tehakse kahjutuks <script>"
    if isinstance(value, str):
        return re.sub(r"(?i)<(/?script)", "&lt;\\1", value or '')
    else:
        return value

def js_str1(value):
    "Tekst javascriptis ylakomade vahel kasutamiseks"
    if isinstance(value, str):
        return value and value.replace("'","\\'").replace('\n','\\n').replace('\r','') or ''
    else:
        return value

def hm_str2(value):
    "Tekst HTMLis jutumärkide vahel kasutamiseks"
    if isinstance(value, str):
        return value and value.replace('"','&quot;') or ''
    else:
        return value
    
def _ser_attrs(**attrs):
    buf = ''
    for key in attrs:
        value = attrs[key]
        if key == 'disabled':
            if value:
                value = 'disabled'
            else:
                # button[value=False] disableb ikkagi
                continue
        if value is None:
            continue
        if key.endswith('_'):
            key = key[:-1]
        if key.startswith('data_'):
            key = 'data-' + key[5:]
        buf += ' %s="%s"' % (key.lower(), hm_str2(value))
    return buf

def _remove_params(query, keys):
    """
    data - url.environ['QUERY_STRING']
    keys - list parameetritest, mis tuleb eemaldada
    """
    params = query.split('&')
    for key in keys:
        for param in params:
            if param.startswith(key+'='):
                params.remove(param)
    return '&'.join(params)

def _add_class(attrs, classname):
    if not classname:
        return attrs
    if 'class_' in attrs:
        c = attrs.pop('class_')
    else:
        c = attrs.get('class')
    if c:
        attrs['class'] = c + ' ' + classname
    else:
        attrs['class'] = classname
    return attrs

