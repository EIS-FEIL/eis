"""
Sisestusvormide väljade väärtuste valideerimine
"""
import logging
import formencode
from formencode import htmlfill
import re
import pyramid_simpleform

from eis import model
import eiscore.i18n as i18n
_ = i18n._
log = logging.getLogger(__name__)

def hds_error_formatter(error):
    return '<div class="alert alert-danger fade show p-1 m-0">' + \
           htmlfill.html_quote(error) +\
           '</div>'

class Form(pyramid_simpleform.Form):
    """Vormide valideerimise klassi mugandamine
    """
    def __init__(self, request, schema=None, method=None, variable_decode=True, **kw):
        """Muudetud on parameetrite method ja variable_decode vaikimisi väärtusi
        """
        state = pyramid_simpleform.State(request=request)
        pyramid_simpleform.Form.__init__(self,
                                         request,
                                         schema=schema,
                                         method=method,
                                         variable_decode=variable_decode,
                                         state=state,
                                         **kw)
        self.state._ = ''
        
    def validate(self):
        """Vormi valideerimine.
        Üle kirjutatud selleks, et tekitada c._arrayindexes
        (mille järgi loetelu kuvamisel teatakse makos arvestada
        lisatud kirjetega, mida vormi vigade tõttu ei saanud salvestada)
        """
        pyramid_simpleform.variabledecode.variable_decode = _variable_decode
        rc = pyramid_simpleform.Form.validate(self)
        if not rc:
            # vorm ei valideeru
            # PÕHJUS VÕIB OLLA VALE MEETOD (POST vs GET)
            handler = self.request.handler
            # see erind pole viskamiseks, vaid c array index täitmiseks
            ValidationError(handler, self.errors, is_schema_error=True)

        return rc

    def list_in_posted_order(self, key, data=None, prefix=''):
        """Formencode annab jada indeksite järjekorras,
        isegi kui jada elementide järjekorda on muudetud.
        See funktsioon leiab jada selles järjekorras, milles postitati,
        lisaks lisab igale elemendile _arr_ind sidumiseks post-parameetriga
        """
        order = []
        pattern = r'%s%s-(\d+)\..*' % (prefix, key)
        if data is None:
            data = self.data
        for p_key in self.request.params:
            # järjestus vastavalt postitamisele
            m = re.match(pattern, p_key)
            if m:
                ind = int(m.groups()[0])
                if ind not in order:
                    order.append(ind)
        #log.debug('order: %s' % order)
        li = data.get(key) or []
        for n, ind in enumerate(sorted(order)):
            li[n]['_arr_ind'] = ind
        li_posted = sorted(li, key=lambda r: order.index(r.get('_arr_ind')))
        return li_posted

    def render(self, template, extra_info=None):
        # self.form.data parameetrid on struktureeritud {'r':[{'id':...}]}
        # renderdamiseks on vaja struktureerimata parameetreid {'r-0.id':...}
        self.data = self.request.params.mixed()
        return pyramid_simpleform.Form.render(self,
                                              template,
                                              extra_info=extra_info,
                                              auto_error_formatter=hds_error_formatter,
                                              error_class='is-invalid',
                                              prefix_error=False
                                              )
    
class ValidationError(Exception):
    """
    Kui peale skeemiga parameetrite valideerimist veel soovitakse veateade esitada,
    siis visatakse erind ValidationError.
    ValidationError tuleb luua alati, sest siin koostatakse vajalik c._arrayindexes.
    """
    def __init__(self, handler, errors, message=None, is_schema_error=False, **args):
        """
        Tehakse vajalikke ettevalmistusi vigade kuvamiseks.

        handler
           kontrolleri objekt, mille kaudu saame kätte requesti
        errors
           dict vigadega, kus dicti indeks on vigase välja nimi
           ja väärtus on veateade (unicode).
        message
           kasutajale jäetav üldine teade
        is_schema_error
           kas viga saadi valideerimisskeemiga (True) või käsitsi (False)
        """
        model.Session.rollback()
        
        # teade kasutajale
        if message is None and not handler.has_errors():
            message = _("Palun kõrvaldada vead")
        if message:
            handler.error(message)            
        self._arrayindexes = handler.c._arrayindexes = ValidationError.arr_length(handler.request.params)
        if not is_schema_error and handler.form:
            # kui vormi valideerimine õnnestus, siis on nested vormi korral
            # andmed juba struktureeritud ja neid ei saa enam kasutada,
            # mistõttu võtame andmed requestist
            handler.form.data = handler.request.params.mixed()

        formencode.variabledecode.variable_encode = self._variable_encode
        log.debug(str(errors))
        self.errors = errors
        try:
            self.errors = errors.unpack_errors(True)
        except AttributeError:
            # errors on dict ja sellel pole sellist meetodit
            pass

    @classmethod
    def arr_length(cls, params):
        """Jadade indeksite korduvkasutus.
        Leitakse postitatud parameetrites olnud jadade indeksid
        eesmärgiga neid veavormi kuvamisel edasi kasutada.
        """
        arrayindexes = {}
        pattern = re.compile(r'(.+)-([0-9]+).*')
        for key in list(params.keys()):
            m = pattern.match(key)
            if m:
                prefix = m.groups()[0]
                index = int(m.groups()[1])
                if prefix not in arrayindexes:
                    arrayindexes[prefix] = []
                if index not in arrayindexes[prefix]:
                    arrayindexes[prefix].append(index)
        for prefix in arrayindexes:
            arrayindexes[prefix].sort()
        return arrayindexes
                
    def _variable_encode(self, d, prepend='', result=None, add_repetitions=True,
                         dict_char='.', list_char='-'):
        """
        Encodes a nested structure into a flat dictionary.
        Muudetud nii, et jadade indeksid säiliksid (kasutatakse c._arrayindexes),
        (st kui postitakse key-2, key-5, siis ei kodeeritaks key-0, key-1)
        """
        if result is None:
            result = {}
        if isinstance(d, dict):
            for key, value in list(d.items()):
                if key is None:
                    name = prepend
                elif not prepend:
                    name = key
                else:
                    name = "%s%s%s" % (prepend, dict_char, key)
                self._variable_encode(value, name, result, add_repetitions,
                                      dict_char=dict_char, list_char=list_char)
        elif isinstance(d, list):
            for i, value in enumerate(d):
                try:
                    i1 = self._arrayindexes[prepend][i]
                except:
                    # midagi imelikku
                    log.debug('no arrayindex: %s' % prepend)
                    i1 = i
                self._variable_encode(value, "%s%s%i" % (prepend, list_char, i1), result,
                                      add_repetitions, dict_char=dict_char, list_char=list_char)
            if add_repetitions:
                repName = ('%s--repetitions' % prepend
                           if prepend else '__repetitions__')
                result[repName] = str(len(d))
        else:
            result[prepend] = d
        return result

def _variable_decode(d, dict_char='.', list_char='-'):
    """
    Decode the flat dictionary d into a nested structure.
    Muudetud nii, et jada algne positsioon jääks alles (_arr_ind)
    """
    result = {}
    dicts_to_sort = set()
    known_lengths = {}
    for key, value in d.items():
        keys = key.split(dict_char)
        new_keys = []
        was_repetition_count = False
        for key in keys:
            if key.endswith('--repetitions'):
                key = key[:-len('--repetitions')]
                new_keys.append(key)
                known_lengths[tuple(new_keys)] = int(value)
                was_repetition_count = True
                break
            elif list_char in key:
                maybe_key, index = key.split(list_char, 1)
                if not index.isdigit():
                    new_keys.append(key)
                else:
                    key = maybe_key
                    new_keys.append(key)
                    dicts_to_sort.add(tuple(new_keys))
                    new_keys.append(int(index))
            else:
                new_keys.append(key)
        if was_repetition_count:
            continue

        place = result
        for i in range(len(new_keys) - 1):
            try:
                if not isinstance(place[new_keys[i]], dict):
                    place[new_keys[i]] = {None: place[new_keys[i]]}
                place = place[new_keys[i]]
            except KeyError:
                place[new_keys[i]] = {}
                place = place[new_keys[i]]

        if new_keys[-1] in place:
            if isinstance(place[new_keys[-1]], dict):
                place[new_keys[-1]][None] = value
            elif isinstance(place[new_keys[-1]], list):
                if isinstance(value, list):
                    place[new_keys[-1]].extend(value)
                else:
                    place[new_keys[-1]].append(value)
            else:
                if isinstance(value, list):
                    place[new_keys[-1]] = [place[new_keys[-1]]]
                    place[new_keys[-1]].extend(value)
                else:
                    place[new_keys[-1]] = [place[new_keys[-1]], value]
        else:
            place[new_keys[-1]] = value

    to_sort_list = sorted(dicts_to_sort, key=len, reverse=True)
    for key in to_sort_list:
        to_sort = result
        source = None
        last_key = None
        for sub_key in key:
            source = to_sort
            last_key = sub_key
            to_sort = to_sort[sub_key]
        for k,v in to_sort.items(): # ahti
            if isinstance(v, dict):
                v['_arr_ind'] = int(k)
        if None in to_sort:
            noneVals = [(0, x) for x in to_sort.pop(None)]
            noneVals.extend(iter(to_sort.items()))
            to_sort = noneVals
        else:
            to_sort = iter(to_sort.items())
        to_sort = [x[1] for x in sorted(to_sort)]
        if key in known_lengths:
            if len(to_sort) < known_lengths[key]:
                to_sort.extend([''] * (known_lengths[key] - len(to_sort)))
        source[last_key] = to_sort

    return result

def neworder(handler, key, li):
    """Postitatud jada li pannakse tagasi sellesse järjekorda, milles see postitati
    (kasutamiseks kasutajaliideses Sortable abil muudetud järjekorra korral)
    """
    params = handler.request.params
    order = []
    for k in params:
        m = re.match(key + r'-(\d+)\.', k)
        if m:
            arr_ind = int(m.groups()[0])
            if arr_ind not in order:
                order.append(arr_ind)
    li.sort(key=lambda rcd: order.index(rcd['_arr_ind']))
    for seq, rcd in enumerate(li):
        rcd['seq'] = seq
    return li
    
        
    
