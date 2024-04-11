import sys
import os
import subprocess
import zipfile
import tempfile
import shutil
import re
from lxml import etree, objectify
from lxml.builder import E
from io import BytesIO
import cgi

from eis.lib.base import *
from eis.lib.importpackage import ImportPackage
from eis.lib.block import BlockController
from eis.lib.qti import *

log = logging.getLogger(__name__)

# QTI nimeruumid
_IMSCP = '{%s}' % IMSCP
_IMSMD = '{%s}' % IMSMD
_IMSQTI = '{%s}' % IMSQTI
_MATH = '{%s}' % MATH
_EISNS = '{%s}' % EISNS

class QtiImportPackage(ImportPackage):
    def __init__(self, filename, storage):
        """ZIP-failist importimine.
        Tagastatakse QtiImportPackage objekt,
        millel on mõtet vaadata selliseid atribuute:
        is_error - kas õnnestus importimine või mitte
        messages - jada teadetest kasutajale (infoks)
        items - jada imporditud kirjetest
        """
        super(QtiImportPackage, self).__init__()
        if filename:
            rc = self.unzip_localfile(filename)
        else:
            rc = self.unzip_filestorage(storage)

        if rc:
            try:
                self.parse_manifest()
                model.Session.flush()
            except HandledError:
                pass
        self.clean()

    def unzip_filestorage(self, filedata):
        """Seda kasutab lahti pakkimiseks veebirakendus
        """
        self.dirname = tempfile.mkdtemp()
        try:
            self.files = _unzip(filedata, self.dirname)
        except zipfile.BadZipfile:
            # zipfile iga zippi ei suuda lahti pakkida
            fn_zip = _write_zip(filedata)
            self.files = _unzip_proc(fn_zip, self.dirname)
            os.unlink(fn_zip)
        if self.files is None:
            self.error('Viga lahtipakkimisel. See polnud vist ZIP-fail.')
            self.is_error = True
            return False
        return True

    def unzip_localfile(self, fn):
        """Seda kasutab lahtipakkimiseks import.py skript
        """
        self.dirname = tempfile.mkdtemp()
        self.files = _unzip_proc(fn, self.dirname)
        if self.files is None:
            self.error('Viga lahtipakkimisel. See polnud vist ZIP-fail.')
            self.is_error = True
            return False
        return True

    def clean(self):
        # kustutame kõik ajutised failid
        if not self.dirname:
            return
        try:
            shutil.rmtree(self.dirname)
        except:
            # failidel polnud kirjutusõigust, ei saa kustutada shutil abil
            sub_rc = subprocess.call(['rm', '-r', '-f', self.dirname])
            if sub_rc != 0:
                self.notice('Ajutiste failide kustutamine ebaõnnestus')

    def initialize(self, dirname, files):
        self.dirname = dirname
        self.files = files
        self.notice('Leiti failid:\n' + ', '.join(files))

    def parse_manifest(self):
        # otsime manifesti
        fn_manifest = 'imsmanifest.xml'
        if not fn_manifest in self.files:
            self.error('ZIP-failis puudub fail nimega %s' % fn_manifest)
            self.is_error = True
            raise HandledError()

        fn = os.path.join(self.dirname, fn_manifest)
        tree = etree.parse(fn)
        # manifest
        root = tree.getroot()

        # paketi metaandmed
        package_metadata = root.find(_IMSCP+'metadata')
        ids, titles, descriptions = \
            self._show_metadata(package_metadata)
        if len(titles):
            self.notice('Pakett: ' + ' '.join([t.text for t in titles]))
        package_language = package_metadata.find(_IMSMD+'lom/'+_IMSMD+'metametadata/'+_IMSMD+'language')
       
        for resource in root.findall(_IMSCP+'resources/'+_IMSCP+'resource'):
            metadata = resource.find(_IMSCP+'metadata')
            ids, titles, descriptions = self._show_metadata(metadata)
            if metadata is None:
                eis_metadata = None
                language = None
            else:
                eis_metadata = metadata.find(_IMSMD+'lom/'+_EISNS+'metadata')
                language = metadata.find(_IMSMD+'lom/'+_IMSMD+'metametadata/'+_IMSMD+'language')
            title = ' '.join([t.text for t in titles])
            r_fn = resource.get('href')
            r_type = resource.get('type')
            buf = '%s %s - \n' % (r_fn, title)

            if r_type == 'imsqti_item_xmlv2p0':
                self.error(buf + 'Ressurssi ei saa importida. Failis on kasutusel QTI versioon 2.0. EIS toetab QTI versiooni 2.1')
                
            elif r_type == 'imsqti_item_xmlv2p1':
                self.notice(buf + 'Ülesanne imporditakse')
                ylesanne = model.Ylesanne()
                ylesanne.logi('Importimine', None, None, const.LOG_LEVEL_GRANT)
                if ids:
                    ylesanne.kood = ids[0].text
                ylesanne.post_create()
                if language is not None:
                    ylesanne.lang = language.text
                elif package_language is not None:
                    ylesanne.lang = package_language.text
                else:
                    ylesanne.lang = const.LANG_ET
                ylesanne.set_lang()
                
                if titles:
                    ylesanne.nimi = titles[0].text
                else:
                    ylesanne.nimi = resource.get('identifier') or resource.get('href') or 'Nimeta'
                if descriptions:
                    ylesanne.markus = descriptions[0].text
                if eis_metadata is not None:
                    self._set_eis_metadata(ylesanne, eis_metadata)
                #ylesanne._global_session.autoflush = False        

                self.items.append(ylesanne)
                self._parse_resource_file(ylesanne, r_fn)
                # arvutame max pallid
                ylesanne.calc_max_pallid()                
            else:
                self.notice(buf + 'Ressurssi ignoreeritakse (tüüp %s)' % (r_type))
            #model.Session.flush()

    def _set_eis_metadata(self, ylesanne, node):
        for tag in ('etest', 'ptest', 'arvutihinnatav', 'adaptiivne'):
            item = node.find(_EISNS+tag)
            if item is not None:
                ylesanne.__setattr__(tag, True)

        for tag in ('staatus','vastvorm','hindamine'):
            item = node.find(_EISNS+tag)
            if item is not None:
                if tag == 'staatus':
                    kl_kood = 'Y_STAATUS'
                else:
                    kl_kood = tag.upper()
                kood = item.get('id')
                if not model.Klrida.get_by_kood(kl_kood, kood):
                    self.notice('Vigane klassifikaatori "%s" väärtus "%s"' % (kl_kood, kood))
                else:
                    ylesanne.__setattr__('%s_kood' % tag, item.get('id'))

        item = node.find(_EISNS+'aine')
        if item is not None:
            kl_kood = 'AINE'
            kood = item.get('id')
            if not model.Klrida.get_by_kood(kl_kood, kood):
                self.notice('Vigane klassifikaatori "%s" väärtus "%s"' % (kl_kood, kood))
            else:
                ya = model.Ylesandeaine(aine_kood=kood,
                                        seq=0,
                                        ylesanne=ylesanne)
                item = node.find(_EISNS+'oskus')
                if item is not None:
                    kl_kood = 'OSKUS'
                    kood = item.get('id')
                    if not model.Klrida.get_by_kood(kl_kood, kood):
                        self.notice('Vigane klassifikaatori "%s" väärtus "%s"' % (kl_kood, kood))
                    else:
                        ya.oskus_kood = kood
                for item in node.findall(_EISNS+'ylesandeteema'):
                    item_v = item.find(_EISNS+'teema')
                    item_t = item.find(_EISNS+'alateema')
                    teema_kood = item_v is not None and item_v.get('id')
                    alateema_kood = item_t is not None and item_t.get('id')
                    if teema_kood:
                        yt = model.Ylesandeteema(teema_kood=teema_kood,
                                                 alateema_kood=alateema_kood,
                                                 ylesandeaine=ya)
                        ya.ylesandeteemad.append(yt)

        # aste_mask = 0
        # for item in node.findall(_EISNS+'aste'):
        #     kood = item.get('id')
        #     aste_mask += const.ASTE_BIT.get(kood) or 0
        # ylesanne.aste_mask = aste_mask
        
        for item in node.findall(_EISNS+'mote'):
            mt = model.Motlemistasand(kood=item.get('id'), ylesanne=ylesanne)
            ylesanne.motlemistasandid.append(mt)
            
        for item in node.findall(_EISNS+'testiliik'):
            tl = model.Testiliik(kood=item.get('id'), ylesanne=ylesanne)
            ylesanne.testiliigid.append(tl)
            
    def _show_metadata(self, metadata):
        if metadata is not None:
            id = metadata.findall(_IMSMD+'lom/'+_IMSMD+'general/'+_IMSMD+'identifier')
            titles = metadata.findall(_IMSMD+'lom/'+_IMSMD+'general/'+\
                                      _IMSMD+'title/'+_IMSMD+'langstring')
            descriptions = metadata.findall(_IMSMD+'lom/'+_IMSMD+'general/'+\
                                      _IMSMD+'description/'+_IMSMD+'langstring')
            #if len(descriptions):
            #    buf += '<hr/>' + ' '.join([t.text for t in descriptions])
            return id,titles, descriptions
        return [],[],[]

      
    def _parse_resource_file(self, ylesanne, fn):
        # assessmentItem:
        #   responseDeclaration
        #   outcomeDeclaration
        #   itemBody:
        #      hottextInteraction[@responseIdentifier][@maxChoices]
        #   responseProcessing/responseCondition
        fn_full = os.path.join(self.dirname, fn)
        try:
            tree = etree.parse(fn_full)
        except IOError as ex:
            self.error('Ei saa lugeda faili %s. Tõenäoliselt viidatakse paketi sees failile, mida selle nime all paketis ei ole.' % (fn_full))
            self.is_error = True
            raise HandledError()

        self.current_dirname = os.path.dirname(fn_full)
       
        # assessmentItem
        item = tree.getroot()
        
        if item.tag != _IMSQTI+'assessmentItem':
            raise Exception('Ei saa importida. Failis %s pole XMLi juureelement {%s}assessmentItem' % (fn, IMSQTI))

        self._parse_outcomeDeclaration(item, ylesanne)
        self._parse_responseProcessing(item, ylesanne)
        self._parse_responseDeclaration(item, ylesanne)
        self._parse_body(item, ylesanne)
        
    def _parse_body(self, item, ylesanne):
        itemBody = item.find(_IMSQTI+'itemBody')
        self._parse_feedback(itemBody)

        for element in itemBody.findall('*'):
            # leiame õige sisuploki
            import_obj = QtiImportBlock.get(element)(ylesanne, element, self)
            # ja parsime
            import_obj.parse()

    def _parse_responseDeclaration(self, item, ylesanne):
        for rd in item.findall(_IMSQTI+'responseDeclaration'):
            kood=rd.get('identifier')
            if not kood:
                continue

            tulemus = model.Tulemus(kood=kood, ylesanne=ylesanne)
            tulemus.kardinaalsus = rd.get('cardinality')
            tulemus.baastyyp = rd.get('baseType')

            if not tulemus.baastyyp:
                tulemus.baastyyp = const.BASETYPE_IDENTIFIER

            corrects = []
            # leiame õiged vastused
            # osa neist võib korduda mappingus
            cr = rd.find(_IMSQTI+'correctResponse')
            if cr is not None:
                for value in cr.findall(_IMSQTI+'value'):
                    corrects.append(value.text)

            # leiame punktidega vastused
            mapping = rd.find(_IMSQTI+'mapping')
            if mapping is not None:
                tulemus.kardinaalsus = mapping.get('cardinality')
                tulemus.min_pallid = _float_none(mapping.get('lowerBound'))
                tulemus.max_pallid = _float_none(mapping.get('upperBound'))
                tulemus.vaikimisi_pallid = _float_none(mapping.get('defaultValue'))

                for mapEntry in mapping.findall(_IMSQTI+'mapEntry'):
                    tulemus.arvutihinnatav = True
                    mapKey = mapEntry.get('mapKey')
                    mappedValue = mapEntry.get('mappedValue')
                    pallid = model.Hindamismaatriks()
                    if tulemus.baastyyp in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
                        pallid.kood1, pallid.kood2 = mapKey.split(' ')
                    else:
                        pallid.kood1 = mapKey
                    pallid.pallid = _float_none(mappedValue)
                    pallid.tulemus = tulemus
                    if mapKey in corrects:
                        # kui vastus on õigete seas, siis teeme selle kohta märke
                        pallid.oige = True
                        corrects.remove(mapKey)

            # kui õige vastus polnud mappingus, siis teeme omaette kirje
            for value in corrects:
                tulemus.arvutihinnatav = True                
                pallid = model.Hindamismaatriks()
                if tulemus.baastyyp in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
                    pallid.kood1, pallid.kood2 = value.split(' ')
                else:
                    pallid.kood1 = value
                pallid.oige = True
                pallid.tulemus = tulemus

            # leiame punktidega vastused koordinaatide kohta
            mapping = rd.find(_IMSQTI+'areaMapping')
            if mapping is not None:
                tulemus.min_pallid = _float_none(mapping.get('lowerBound'))
                tulemus.max_pallid = _float_none(mapping.get('upperBound'))
                tulemus.vaikimisi_pallid = _float_none(mapping.get('defaultValue'))

                for mapEntry in mapping.findall(_IMSQTI+'areaMapEntry'):
                    tulemus.arvutihinnatav = True
                    shape = mapEntry.get('shape')
                    coords = mapEntry.get('coords')
                    mappedValue = mapEntry.get('mappedValue')
                    pallid = model.Hindamismaatriks()
                    pallid.kujund = shape
                    pallid.koordinaadid = _coords(coords, shape)
                    pallid.pallid = _float_none(mappedValue)
                    pallid.tulemus = tulemus

            ylesanne.tulemused.append(tulemus)
            #tulemus.ylesanne = ylesanne

    def _parse_outcomeDeclaration(self, item, ylesanne):
        for od in item.findall(_IMSQTI+'outcomeDeclaration'):
            kood=od.get('identifier')
            if not kood:
                continue
            valjund = model.Valjund(kood=kood)
            ylesanne.valjundid.append(valjund)
            #valjund.ylesanne = ylesanne
            valjund.kardinaalsus = od.get('cardinality')
            valjund.baastyyp = od.get('baseType')
            valjund.max_norm = od.get('normalMaximum')
            valjund.min_norm = od.get('normalMinimum')
            valjund.oskus_norm = od.get('masteryValue')

    def _parse_responseProcessing(self, item, ylesanne):
        rp = item.find(_IMSQTI+'responseProcessing')
        if rp is None:
            return
        template = rp.get('template')
        if template:
            t = model.Tulemusmall.query.filter_by(rp_uri=template).first()
            if not t:
                t = model.Tulemusmall()
                t.rp_uri = template
                t.rp_location = rp.get('templateLocation')
            ylesanne.rp_template = t
        else:
            t = model.Tulemusmall()
            t.rp_reeglid = outer_xml(rp)
            ylesanne.rp_template = t

    def _parse_feedback(self, root):
        for element in root.iterdescendants(_IMSQTI+'feedbackBlock'):
            element.getparent().remove(element)
        #for element in root.iterdescendants(_IMSQTI+'feedbackInline'):
        #    element.getparent().remove(element)            

    def _read_file_contents(self, fn):
        fn_full = os.path.join(self.current_dirname, fn)
        try:
            f = open(fn_full, 'rb')
            buf = f.read()
            f.close()
        except IOError as ex:
            self.error('Ei saa lugeda faili %s. Tõenäoliselt viidatakse paketi sees failile, mida selle nime all paketis ei ole.' % (fn_full))
            self.is_error = True
            raise HandledError()
        return buf

interaction_tags = ('positionObjectStage',
                    'drawingInteraction',
                    'gapMatchInteraction',
                    "matchInteraction",
                    "graphicGapMatchInteraction",
                    "hotspotInteraction",
                    "graphicOrderInteraction",
                    "selectPointInteraction",
                    "graphicAssociateInteraction",
                    "sliderInteraction",
                    "choiceInteraction",
                    "inlineChoiceInteraction",
                    "hottextInteraction",
                    "orderInteraction",
                    "textEntryInteraction",
                    "extendedTextInteraction",
                    "uploadInteraction",
                    "associateInteraction",
                    "mediaInteraction",
                    "customInteraction"
                    )

class QtiImportBlock(object):
    is_interaction = False
    
    @classmethod
    def get(cls, element):
        """Leiame antud elemendi parsimiseks sobiva klassi
        """
        local_tag = _local_tag(element.tag)
        if local_tag in interaction_tags:
            # leidsime interaktsiooni
            clsname = '_' + local_tag
        elif local_tag == 'matchInteraction':
            clsname = 'match2Interaction'
        else:
            ## math, rubricBlock, image, inlineChoice, inlineTextEntry
            # math, rubricBlock, image
            clsname = '_textBlock'
        # if local_tag == 'math':
        #     clsname = '_math'
        # else:
        #     # leidsime teksti
        #     clsname = '_rubricBlock'
        return eval(clsname)
        
    def __init__(self, ylesanne, element, package):
        #log.info('init:element=%s' % element.tag)
        #print "SISUPLOKK:"+element.tag
        self.ylesanne = ylesanne
        self.element = element
        self.package = package
        self._detect_type()
        #print "QtiImportBlock() %s <%s> type=%s" % (self.__class__.__name__, _local_tag(element.tag), self.tyyp)

    def _detect_type(self):
        self.tyyp = None

    def _add_block(self):
        seq = len(self.ylesanne.sisuplokid) + 1
        self.plokk = model.Sisuplokk(tyyp=self.tyyp, seq=seq, ylesanne=self.ylesanne)
        self.package.notice('Sisuplokk: %s' % self.plokk.tyyp_nimi)
        self.plokk.post_create()
        self.ylesanne.sisuplokid.append(self.plokk)

    def parse_inline_images(self, element):
        """Leiame teksti sees olevad <img> elemendid
        ning laadime nende pildifailid.
        """
        li = element.iterdescendants(_IMSQTI+'img')
        for e in li:
            fn = e.get('src')
            if _is_local_file(fn):
                local_fn = fn.split('/')[-1] # eemaldame kataloogi "images/"
                found = False
                for obj in self.ylesanne.sisuplokid:
                    if obj.tyyp in (const.BLOCK_IMAGE, const.BLOCK_MEDIA, const.BLOCK_CUSTOM):
                        if obj.taustobjekt and obj.taustobjekt.filename == local_fn:
                            found = True
                            break

                if not found:
                    # kui pilti veel pole, siis
                    # tuleb teha pildi objekt
                    p = model.Sisuplokk(tyyp=const.BLOCK_IMAGE, staatus=const.B_STAATUS_KEHTETU, ylesanne=self.ylesanne)
                    obj = p.give_taustobjekt()
                    obj.filename = local_fn
                    obj.filedata = self.package._read_file_contents(fn)
                    fp = BytesIO(obj.filedata)
                    obj.set_image_size(None, fp, local_fn)
                    self.ylesanne.sisuplokid.append(p)
                    
                # muudame pildi URLi, lisame ette action='images'
                e.set('src', 'images/' + local_fn)

    def update_sisuvaade(self):
        """Peale plokk.sisu väärtustamist väärtustatakse plokk.sisuvaade.
        Kasutusel hottext, inlineTextEntry ja gapMathcInteraction
        tüüpi plokkides.
        """
        ctrl = BlockController.get(self.plokk, self.ylesanne, None)
        sisu, tree = ctrl.parse_sisu()
        ctrl._update_sisu(tree, False)
        ctrl._update_sisuvaade(tree)

    def parse_filedata(self, obj, fn):
        if fn.startswith('http:') or fn.startswith('https:'):
            # url
            obj.fileurl = fn
        else:
            # fail
            obj.filename = os.path.basename(fn)
            obj.filedata = self.package._read_file_contents(fn)
            fp = BytesIO(obj.filedata)
            try:
                obj.set_image_size(None, fp, obj.filename)
            except IOError as ex: 
                # kui ei ole pildifail
                pass
            
class QtiImportInteraction(QtiImportBlock):
    is_interaction = True

    def _detect_type(self):
        """Leitakse sisuploki liik.
        Üldjuhul on see üksüheses vastavuses klassi nimega, kuid mitte alati.
        """
        self.tyyp = None
        for key in const.block_names:
            if const.block_names[key] == self.__class__.__name__[1:]:
                self.tyyp = key
        assert self.tyyp, 'Tüüp puudub'
        return self.tyyp

    def parse(self):
        assert self.tyyp, 'Tüüp puudub'
        self._add_block()
        self.parse_tag()
        self.parse_prompt()
        self.parse_more()

        # seome kysimused ja tulemused
        for k in self.plokk.kysimused:
            k.tulemus = self.ylesanne.get_tulemus(k.kood)
        
    def parse_more(self):
        pass

    def parse_tag(self, element=None):
        if element is None:
            element = self.element
        kysimus = self.plokk.kysimus
        for key, value in element.attrib.items():
            if key == 'responseIdentifier':
                kysimus.kood = value
                #log.debug('parse_tag %s' % value)
            if key == 'shuffle':
                kysimus.segamini = _sbool(value)
            elif key == 'maxAssociations':
                kysimus.max_vastus = int(value)
            elif key == 'minAssociations':
                kysimus.min_vastus = int(value)
            elif key == 'minChoices':
                kysimus.min_vastus = int(value)
            elif key == 'maxChoices':
                kysimus.max_vastus = int(value)
            elif key == 'expectedLength':
                kysimus.pikkus = int(value)

    def parse_choice_tag(self, element, item):
        for key, value in element.attrib.items():
            if key == 'matchMin':
                item.min_vastus = int(value)
            elif key == 'matchMax':
                nvalue = int(value)
                if nvalue != 0:
                    # 0 - piirang puudub
                    item.max_vastus = nvalue
            elif key == 'identifier':
                item.kood = value

    def parse_prompt(self):
        e = self.element.find(_IMSQTI+'prompt')
        if e is not None:
            self.parse_inline_images(e)
            self.plokk.nimi = inner_xml_without_ns(e)
            e.getparent().remove(e)
                
class QtiImportImageInteraction(QtiImportInteraction):
    is_interaction = True

    def parse_objekt(self, e, obj_cls=None, obj=None):
        if obj is None:
            obj = obj_cls()
        if e.get('data'):
            self.parse_filedata(obj, e.get('data'))
        if e.get('type'):
            obj.mimetype = e.get('type')
        if e.get('width'):
            value = e.get('width')
            if value:
                obj.laius = int(value)
        if e.get('height'):
            value = e.get('height')
            if value:
                obj.korgus = int(value)
        return obj

    def parse_taustobjekt(self):
        e = self.element.find(_IMSQTI+'object')
        if e is None:
            self.package.notice('Kummaline: "%s"' % _local_tag(self.element.tag) +\
                                ' ei sisalda elementi "object"')

            return
        self.parse_objekt(e, obj=self.plokk.give_taustobjekt())

    def parse_meediaobjekt(self):
        e = self.element.find(_IMSQTI+'object')
        if e is None:
            self.package.notice('Kummaline: "%s"' % _local_tag(self.element.tag) +\
                                ' ei sisalda elementi "object"')

            return
        obj = self.plokk.give_meediaobjekt()
        self.parse_objekt(e, obj=obj)
        obj.min_kordus = _int_none(e.get('minPlays'))
        obj.max_kordus = _int_none(e.get('maxPlays'))
        obj.autostart = e.get('autostart') == 'true'
        obj.isekorduv = e.get('loop') == 'true'        

    def parse_gapImg(self):
        seq = 0
        for element in self.element.findall(_IMSQTI+'gapImg'):            
            e = element.find(_IMSQTI+'object')
            obj = self.parse_objekt(e, model.Piltobjekt)
            seq += 1
            obj.seq = seq
            self.plokk.sisuobjektid.append(obj)
            obj.sisuplokk = self.plokk
            self.parse_choice_tag(element, obj)
    
    def parse_hotspots(self, tag):
        elements = self.element.findall(_IMSQTI+tag)
        seq = 0
        in_use = []
        for e in elements:
            seq += 1
            valik_kood = e.get('identifier')
            if valik_kood in in_use:
                self.package.notice('Kood %s on kasutusel mitmes valikus, imporditakse ainult esimene' % valik_kood)
                continue
            in_use.append(valik_kood)            
            obj = model.Valikupiirkond(seq=seq, kood=valik_kood)
            if e.get('matchMin'):
                obj.min_vastus = e.get('matchMin')
            if e.get('matchMax'):
                nvalue = e.get('matchMax')
                if nvalue != 0:
                    # 0 - piirang puudub
                    obj.max_vastus = e.get('matchMax')
            if e.get('shape'):
                obj.kujund = e.get('shape')
            if e.get('coords'):
                obj.koordinaadid = _coords(e.get('coords'), 
                                           obj.kujund, 
                                           self.plokk.taustobjekt)
            #obj.kysimus = self.plokk.kysimus
            self.plokk.kysimus.valikud.append(obj)


# interaktsioonid
class _positionObjectStage(QtiImportImageInteraction):
    def _detect_type(self):
        self.tyyp = const.INTER_POS # ülemine element on PositionObjectStage, mitte -Interaction

    def parse(self):
        self._add_block()
        self.parse_taustobjekt()
        self.parse_position_obj()

        # seome kysimused ja tulemused
        for k in self.plokk.kysimused:
            k.tulemus = self.ylesanne.get_tulemus(k.kood)
            
    def parse_position_obj(self):
        seq = 0
        for item in self.element.findall(_IMSQTI+'positionObjectInteraction'):
            prompt = item.find(_IMSQTI+'prompt')
            if prompt is not None:
                if not self.plokk.nimi:
                    self.plokk.nimi = prompt.text
                else:
                    self.plokk.nimi += ' ' + prompt.text

            element = item.find(_IMSQTI+'object')
            obj = self.parse_objekt(element, model.Piltobjekt)
            seq += 1
            obj.seq = seq
            if item.get('maxChoices') is not None:
                obj.max_vastus = int(item.get('maxChoices'))
            if item.get('minChoices') is not None:
                obj.min_vastus = int(item.get('minChoices'))
            obj.sisuplokk = self.plokk
            obj.kood = item.get('responseIdentifier')
            self.plokk.sisuobjektid.append(obj)
        
class _customInteraction(QtiImportInteraction):
    def _detect_type(self):
        """Leitakse sisuploki liik.
        Kui on EISist imporditud, siis customInteraction@eistype atribuudist saab.
        """
        eistype = self.element.get('eistype')
        if eistype == 'audio':
            self.tyyp = const.INTER_AUDIO
        elif eistype == 'math':
            self.tyyp = const.INTER_MATH
        elif eistype == 'file':
            self.tyyp = const.BLOCK_CUSTOM

    def parse_more(self):
        if self.tyyp == const.BLOCK_CUSTOM:
            for a in self.element.iterdescendants(_IMSQTI+'a'):
                fn = a.get('href')
                if _is_local_file(fn):
                    obj = self.plokk.give_taustobjekt()
                    local_fn = fn.split('/')[-1] # eemaldame kataloogi "images/"
                    obj.filename = local_fn
                    obj.filedata = self.package._read_file_contents(fn)
                    break

class _drawingInteraction(QtiImportImageInteraction):
    def parse_more(self):
        self.parse_taustobjekt()
        self.plokk.kysimus.give_joonistamine()
   
class _gapMatchInteraction(QtiImportImageInteraction):
    def parse_more(self):
        self.plokk.sisu = self.parse_contents()
        self.update_sisuvaade()

    def parse_contents(self):
        # parsida <gapText> -> valikuteks
        li = self.element.iterdescendants(_IMSQTI+'gapText')
        #li = self.element.iterdescendants('gapText')
        seq = 0
        in_use = []
        bkysimus = self.plokk.give_kysimus(0)
        for element in li:
            if element.getchildren():
                bkysimus.rtf = True
                break
        for element in li:
            seq += 1
            valik_kood = element.get('identifier')
            if valik_kood in in_use:
                self.package.notice('Kood %s on kasutusel mitmes valikus, imporditakse ainult esimene' % valik_kood)
                continue                
            in_use.append(valik_kood)            
            item = model.Valik(seq=seq)
            self.parse_choice_tag(element, item)
            if bkysimus.rtf:
                item.nimi = inner_xml_without_ns(element)
            else:
                item.nimi = element.text
            #item.kysimus = self.plokk.kysimus
            bkysimus.valikud.append(item)
            element.getparent().remove(element)
            
        # asendada sisus <gap identifier=".."/> -> <input>
        li = self.element.iterdescendants(_IMSQTI+'gap')
        for e in li:
            new_e = E.input(value=e.get('identifier'))
            new_e.tail = e.tail
            e.getparent().replace(e, new_e)

        return inner_xml_without_ns(self.element)

class _matchInteraction(QtiImportInteraction):
    def _detect_type(self):
        self.tyyp = const.INTER_MATCH2
        return self.tyyp

    def parse_more(self):
        valetulemus = None # QTIs on maatriks paaridena
        res_id = self.element.get('responseIdentifier')
        if res_id:
            for t in self.ylesanne.tulemused:
                if t.kood == res_id:
                    valetulemus = t
                    break

        seq = 0
        for element in self.element.findall(_IMSQTI+'simpleMatchSet'):
            seq += 1
            valikuhulk = self.plokk.give_baaskysimus(seq)
            if seq == 1:
                # hulk 1 on kysimuste hulk
                valikuhulk.ridu = 1
            n = 0
            in_use = []
            for choice_element in element.findall(_IMSQTI+'simpleAssociableChoice'):
                n += 1
                kood = choice_element.get('identifier')
                if kood in in_use:
                    self.package.notice('Kood %s on kasutusel mitmes valikus, imporditakse ainult esimene' % kood)
                    continue                
                in_use.append(kood)
                item = model.Valik(seq=n)
                self.parse_choice_tag(choice_element, item)
                self.parse_inline_images(choice_element)
                item.nimi = inner_xml_without_ns(choice_element)
                if item.nimi.find('<') > -1:
                    valikuhulk.rtf = True
                valikuhulk.valikud.append(item)

        if valetulemus:
            self._fix_response(valetulemus)

    def _fix_response(self, valetulemus):
        # QTI response on paaridena,
        # EISis on yhe hylga valikud kysimused
        hindamismaatriksid = list(valetulemus.hindamismaatriksid)
        valikuhulk1 = self.plokk.get_baaskysimus(1)
        k_koodid = []
        if valikuhulk1:
            for ind, valik in enumerate(valikuhulk1.valikud):
                k_koodid.append(valik.kood)
                kysimus = self.plokk.give_kysimus(kood=valik.kood)
                kysimus.seq = ind + 1
                kysimus.min_vastus = valik.min_vastus
                kysimus.max_vastus = valik.max_vastus
                tulemus = kysimus.give_tulemus(True)
                self.ylesanne.tulemused.append(tulemus)
                tulemus.baastyyp = const.BASETYPE_IDENTIFIER
                tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE
                tulemus.arvutihinnatav = valetulemus.arvutihinnatav
                jrk = 0
                for hm in list(hindamismaatriksid):
                    if hm.kood1 == valik.kood:
                        # tõstame ymber teise tulemuse alla
                        jrk = jrk + 1
                        hm.kood1 = hm.kood2
                        hm.kood2 = None
                        hm.tulemus = tulemus
                        hm.jrk = jrk
                        tulemus.hindamismaatriksid.append(hm)
                        hindamismaatriksid.remove(hm)
            model.Session.flush()

            # kustutame liigsed kysimused
            for kysimus in list(self.plokk.pariskysimused):
                if kysimus.kood not in k_koodid:
                    tulemus = kysimus.tulemus
                    if tulemus:
                        tulemus.delete()
                        kysimus.tulemus_id = None
                    kysimus.delete()
            model.Session.refresh(valetulemus)
            valetulemus.delete()
            model.Session.flush()
            model.Session.refresh(self.ylesanne)
            
class _graphicGapMatchInteraction(QtiImportImageInteraction):
    def parse_more(self):
        self.parse_taustobjekt()
        self.parse_gapImg()
        self.parse_hotspots('associableHotspot')

class _hotspotInteraction(QtiImportImageInteraction):
    def parse_more(self):
        self.parse_taustobjekt()
        self.parse_hotspots('hotspotChoice')

class _graphicOrderInteraction(QtiImportImageInteraction):
    def parse_more(self):
        self.parse_taustobjekt()
        self.parse_hotspots('hotspotChoice')

class _selectPointInteraction(QtiImportImageInteraction):
    def parse_more(self):
        self.parse_taustobjekt()

class _graphicAssociateInteraction(QtiImportImageInteraction):
    def parse_more(self):
        self.parse_taustobjekt()
        self.parse_hotspots('associableHotspot')

class _sliderInteraction(QtiImportInteraction):
    def parse_more(self):
        e = self.element
        kysimus = self.plokk.kysimus
        t = kysimus.give_kyslisa()
        if e.get('lowerBound'):
            t.min_vaartus = float(e.get('lowerBound'))
        if e.get('upperBound'):
            t.max_vaartus = float(e.get('upperBound'))
        if e.get('step'):
            t.samm = float(e.get('step'))
        if e.get('stepLabel'):
            t.samm_nimi = _sbool(e.get('stepLabel'))
        value = e.get('orientation')
        t.vertikaalne = value == 'vertical'
        
class _choiceInteraction(QtiImportInteraction):
    def parse_more(self):
        n = 0
        in_use = []
        for element in self.element.findall(_IMSQTI+'simpleChoice'):
            n += 1
            kood = element.get('identifier')
            if kood in in_use:
                self.package.notice('Kood %s on kasutusel mitmes valikus, imporditakse ainult esimene' % kood)
                continue
            in_use.append(kood)
            item = model.Valik(seq=n)
            self.parse_choice_tag(element, item)
            self.parse_inline_images(element)
            item.nimi = inner_xml_without_ns(element)
            if item.nimi.find('<') > -1:
                self.plokk.kysimus.rtf = True
            #item.kysimus = self.plokk.kysimus
            self.plokk.kysimus.valikud.append(item)

class _mediaInteraction(QtiImportImageInteraction):
    def parse_more(self):
        self.parse_meediaobjekt()

class _hottextInteraction(QtiImportInteraction):
    def parse_more(self):
        self.plokk.sisu = self.parse_contents()
        self.parse_inline_images(self.element)
        self.update_sisuvaade()

    def update_sisuvaade(self):
        """Peale plokk.sisu väärtustamist väärtustatakse plokk.sisuvaade.
        """
        ctrl = BlockController.get(self.plokk, self.ylesanne, None)
        sisu, tree = ctrl.parse_sisu()
        ctrl._update_sisuvaade(tree, is_upgrade=True)

    def parse_contents(self):
        # asendada hottext -> span
        #
        # Tekstiosad on kujul
        # <hottext identifier="KOOD">NIMI
        #  <var type="uitype">UITYPE</var>        
        #  <var type="group">GRUPP</var>
        # </hottext>        
        #
        # Viime kujule:
        # <span class="hottext" name="KOOD" group="GRUPP" uitype="UITYPE"
        #       style="background-color: rgb(192, 192, 254);">
        # (GRUPP:KOOD)NIMI
        # </span>

        li = self.element.iterdescendants(_IMSQTI+'hottext')
        for e in li:
            kood = e.get('identifier')
            uitype = 'checkbox'
            group = None
            for v in e.iterdescendants(_IMSQTI+'var'):
                if v.get('type') == 'group':
                    group = v.text
                elif v.get('type') == 'uitype':
                    uitype = v.text

            buf = '<span class="hottext" uitype="%s"' % uitype
            if group:
                buf += ' group="%s"' % group
            buf += ' name="%s" style="background-color: rgb(192, 192, 254);">' % (kood)

            if group:
                buf += '(%s:%s)' % (group, kood)
            else:
                buf += '(%s)' % kood

            buf += e.text or ''
            buf += '</span>'
            new_e = etree.XML(buf)
            new_e.tail = e.tail
            e.getparent().replace(e, new_e)
        return inner_xml_without_ns(self.element)

class _orderInteraction(QtiImportInteraction):
    def parse_more(self):
        n = 0
        in_use = []
        for element in self.element.findall(_IMSQTI+'simpleChoice'):
            n += 1
            kood = element.get('identifier')
            if kood in in_use:
                self.package.notice('Kood %s on kasutusel mitmes valikus, imporditakse ainult esimene' % kood)
                continue
            in_use.append(kood)
            item = model.Valik(seq=n)
            self.parse_choice_tag(element, item)
            item.nimi = element.text
            #item.kysimus = self.plokk.kysimus
            self.plokk.kysimus.valikud.append(item)
       
class _textEntryInteraction(QtiImportInteraction):
    def parse_more(self):
        pass
        #t = self.plokk.get_tekstkysimus()

class _inlineChoiceInteraction(QtiImportInteraction):
    def parse_more(self):
        pass
    
class _extendedTextInteraction(QtiImportInteraction):
    def parse_more(self):
        e = self.element
        t = self.plokk.kysimus
        # maxStrings, minStrings, expectedLines, 
        # format (plain/preFormatted/xhtml)
        if e.get('maxStrings'):
            t.max_vastus = int(e.get('maxStrings'))
        if e.get('minStrings'):
            t.min_vastus = int(e.get('minStrings'))
        if e.get('expectedLines'):
            t.ridu = int(e.get('expectedLines'))
        if e.get('format'):
            t.vorming_kood = _sformat(e.get('format'))

class _uploadInteraction(QtiImportInteraction):
    def parse_more(self):
        self.plokk.kysimus.give_kyslisa()

class _associateInteraction(QtiImportInteraction):
    def parse_more(self):
        n = 0
        in_use = []
        kysimus0 = self.plokk.kysimus
        for element in self.element.findall(_IMSQTI+'simpleAssociableChoice'):
            n += 1
            kood = element.get('identifier')
            if kood in in_use:
                self.package.notice('Kood %s on kasutusel mitmes valikus, imporditakse ainult esimene' % kood)
                continue
            in_use.append(kood)
            item = model.Valik(seq=n)
            self.parse_choice_tag(element, item)
            self.parse_inline_images(element)
            item.nimi = inner_xml_without_ns(element)            
            if item.nimi.find('<') > -1:
                kysimus0.rtf = True
            #item.kysimus = self.plokk.kysimus                
            kysimus0.valikud.append(item)
        if not kysimus0.max_vastus:
            kysimus0.max_vastus = int(len(kysimus0.valikud) / 2)
            
# teksti- ja metaplokk
class _textBlock(QtiImportBlock):
    # math, rubricBlock, image, inlineChoice, inlineTextEntry
    heading = None

    def _detect_type(self):
        # kui juurel on kaks elementi all
        # ja neist esimene on <strong>, mis ei sisalda elemente,
        # ja teine ei ole interaktsioon,
        # siis elemendiks võtame selle teise ja esimese võtame pealdiseks
        # sest niimoodi ise ekspordime
        children = self.element.findall('*')
        if len(children) == 2:
            tag1 = _local_tag(children[0].tag)
            tag2 = _local_tag(children[1].tag)
            if tag1 == 'strong' and not tag2 in interaction_tags:
                if len(children[0].findall('*')) == 0:
                    self.heading = children[0].text
                    self.element = children[1]

        # Leiame tyyp endale
        local_tag = _local_tag(self.element.tag)
        if local_tag == 'math':
            self.tyyp = const.BLOCK_MATH
        elif local_tag == 'img':
            self.tyyp = const.BLOCK_IMAGE
        elif list(self.element.iterdescendants(_IMSQTI+'inlineChoiceInteraction')):

            self.tyyp = const.INTER_INL_CHOICE
        elif list(self.element.iterdescendants(_IMSQTI+'textEntryInteraction')):
            self.tyyp = const.INTER_INL_TEXT
        elif local_tag == 'span' and self.element.find(_MATH+'math') is not None:
            self.tyyp = const.BLOCK_MATH
        else:
            self.tyyp = const.BLOCK_RUBRIC
        log.debug('TAG=%s tyyp=%s' % (local_tag, self.tyyp))
        return self.tyyp

    def parse(self):
        """Leiame sisuploki andmed.
        """
        self._add_block()
        self.plokk.nimi = self.heading

        if self.tyyp == const.BLOCK_IMAGE:
            self.parse_image()
            self.plokk.staatus = 1
        elif self.tyyp == const.BLOCK_MATH:
            self.plokk.sisu = self.element.text
        else:
            self.parse_branch(self.element)                   
            if self.tyyp == const.INTER_INL_TEXT:
                self.plokk.sisu = self.parse_inline_entries()
                self.update_sisuvaade()
            elif self.tyyp == const.INTER_INL_CHOICE:
                self.plokk.sisu = self.parse_inline_entries()
                self.update_sisuvaade()                
            else:
                self.plokk.sisu = outer_xml(self.element)

    def parse_inline_entries(self):

        # Asendada
        # <textEntryInteraction responseIdentifier=".." expectedLength=".."/>
        #
        # sellega:
        #
        # <input baastyyp="string" hm0="värviline/10/0" hm1="punane/20/0"
        #        max_pallid="10" min_pallid="3" pattern="\d+" size="10"
        #        type="text" vaikimisi_pallid="3" value="RESPONSE" />

        seq = 0
        li = self.element.iterdescendants(_IMSQTI+'textEntryInteraction')
        for e in li:
            kood = e.get('responseIdentifier')
            buf = '<input type="text" value="%s"' % kood
            buf += self._add_kysimus_tulemus(kood)
            #tulemus = self.plokk.ylesanne.get_tulemus(kood)            
            tulemus = self.ylesanne.get_tulemus(kood)            
            seq += 1
            kysimus = model.Kysimus(kood=kood, #tyyp=const.INTER_TEXT,
                                    seq=seq,
                                    tulemus=tulemus)
            self.plokk.kysimused.append(kysimus)

            value = e.get('expectedLength')
            if value:
                kysimus.pikkus = int(value)
                buf += ' size="%s"' % kysimus.pikkus

            value = e.get('mask')
            if value:
                kysimus.mask = value
                buf += ' pattern="%s"' % kysimus.mask

            buf += '/>'

            new_e = etree.XML(buf)
            new_e.tail = e.tail
            e.getparent().replace(e, new_e)

        # asendada inlineChoiceInteraction -> select
        li = self.element.iterdescendants(_IMSQTI+'inlineChoiceInteraction')
        for e in li:
            # vaatame, kas on kireva tekstiga valikuid
            is_rtf = False
            for option in e.findall(_IMSQTI+'inlineChoice'):
                buf = inner_xml_without_ns(option)
                if buf.find('<') > -1:
                    is_rtf = True
                    break

            kood = e.get('responseIdentifier')
            seq += 1
            kysimus = model.Kysimus(kood=kood, #tyyp=const.INTER_CHOICE,
                                    seq=seq)
            self.plokk.kysimused.append(kysimus)
            kysimus.rtf = is_rtf

            buf = '<select id="%s"' % kood
            buf += self._add_kysimus_tulemus(kood)
            if is_rtf:
                buf += ' rtf="1"'
            buf += '>'
            buf += '<option>%s</option>' % kood
            
            in_use = []
            n = 0
            for option in e.findall(_IMSQTI+'inlineChoice'):
                valik_kood = option.get('identifier')
                if valik_kood in in_use:
                    self.package.notice('Kood %s on kasutusel mitmes valikus, imporditakse ainult esimene' % valik_kood)
                    continue
                in_use.append(valik_kood)
                nimi = option.text or valik_kood
                if is_rtf:
                    nimi = nimi.replace('<', '&lt;').replace('>', '&gt;')
                n += 1
                buf += '<option value="%s">%s</option>' % (valik_kood, nimi)

            buf += '</select>'
            
            new_e = etree.XML(buf)
            new_e.tail = e.tail
            e.getparent().replace(e, new_e)

        return outer_xml(self.element)

    def _add_kysimus_tulemus(self, kood):
        buf = ''
        #tulemus = self.plokk.ylesanne.get_tulemus(kood)
        tulemus = self.ylesanne.get_tulemus(kood)
        if tulemus is not None:
            if tulemus.max_pallid is not None:
                buf += ' max_pallid="%s"' % tulemus.max_pallid
            if tulemus.min_pallid is not None:
                buf += ' min_pallid="%s"' % tulemus.min_pallid
            if tulemus.vaikimisi_pallid is not None:
                buf += ' vaikimisi_pallid="%s"' % tulemus.vaikimisi_pallid
            for n, h in enumerate(tulemus.hindamismaatriksid):
                if h.pallid is not None:
                    pallid = str(h.pallid)
                else:
                    pallid = ''
                buf += ' hm%d="%s/%s/%d"' % (n, h.kood1, pallid, h.oige and 1 or 0)
        return buf
        
    def parse_image(self):
        element = self.element
        obj = self.plokk.give_piltobjekt(0, True)
        if element.get('src'):
            self.parse_filedata(obj, element.get('src'))
        if element.get('longdesc'):
            self.plokk.nimi = element.get('longdesc').replace('&lt;', '<').replace('&gt;', '>')
        if element.get('width'):
            value = int(element.get('width'))
            if value:
                obj.laius = int(value)
        if element.get('height'):
            value = int(element.get('height'))
            if value:
                obj.korgus = int(value)
        
    def parse_branch(self, root):
        for element in root.findall('*'):
            new_block = True
            cls = QtiImportBlock.get(element)
            if cls == _textEntryInteraction and \
                    self.tyyp == const.INTER_INL_TEXT:
                new_block = False
            elif cls == _inlineChoiceInteraction and \
                    self.tyyp == const.INTER_INL_CHOICE:
                new_block = False                
            elif cls == _textBlock:
                obj = cls(self.ylesanne, element, self.package)
                if obj.tyyp in (const.BLOCK_RUBRIC, const.INTER_INL_TEXT) and\
                        self.tyyp == const.INTER_INL_TEXT:
                    new_block = False
                elif obj.tyyp in (const.BLOCK_RUBRIC, const.INTER_INL_CHOICE) and\
                        self.tyyp == const.INTER_INL_CHOICE:
                    new_block = False                    
                elif obj.tyyp == const.BLOCK_RUBRIC and \
                        self.tyyp == const.BLOCK_RUBRIC:
                    new_block = False

            if new_block == False:
                # ei tee uut sisuplokki
                self.parse_branch(element)
            else:
                # sellele elemendile vastab meil omaette sisuplokk
                # asendame elemendi kohatäitega
                #placeholder = etree.Element('div', {'class':'metablock'})
                placeholder = etree.Element('img', {'class':'metablock', 'src':'/static/images/placeholder.gif'})                
                placeholder.text = ' '
                placeholder.tail = element.tail
                root.replace(element, placeholder)
                # elemendist saab omaette sisuploki sisu
                cls(self.ylesanne, element, self.package).parse()

# # matemaatilise teksti plokk
# class _math(QtiImportBlock):
#     tyyp = const.BLOCK_MATH
#     def parse(self):
#         self.plokk = model.Sisuplokk(tyyp=self.tyyp)
#         ylesanne.sisuplokid.append(self.plokk)
#         self.plokk.sisu = etree.tostring(self.element)

def _sbool(s):
    if s == '':
        return None
    elif s in ('false', '0'):
        return False
    else:
        return True

def _sformat(s):
    if s == 'plain':
        return 'plain'
    elif s == 'xhtml':
        return 'xhtml'
    elif s == 'preFormatted':
        return 'pre'

def _coords(koordinaadid, kujund, taustobjekt=None):
    # koordinaadid on QTI kujul
    # viime need EISi kujule
    coords = ''
    if kujund == const.SHAPE_POLY:
        numbers = [int(float(n)) for n in koordinaadid.split(',')]
        points = []
        for i in range(len(numbers)/2):
            points.append('[%s,%s]' % (numbers[i*2],numbers[i*2+1]))
        coords = '['+','.join(points)+']'
    elif kujund == const.SHAPE_RECT:
        numbers = [int(float(n)) for n in koordinaadid.split(',')]
        (x1, y1, x2, y2) = numbers
        coords = "[[%s,%s],[%s,%s]]" % (x1, y1, x2, y2)
    elif kujund == const.SHAPE_CIRCLE:
        (cx, cy, r) = koordinaadid.split(',')
        cx = int(float(cx))
        cy = int(float(cy))
        if r.endswith('%'):
            pc = int(float(r[:-1]))
            if taustobjekt:
                size = min(taustobjekt.laius or 0, taustobjekt.korgus or 0)
                r = int(size)*pc/100
        else:
            r = int(float(r))
        coords = "[[%s,%s],[%s,%s]]" % (cx-r,cy-r,cx+r,cy+r)
    elif kujund == const.SHAPE_ELLIPSE:
        numbers = [int(float(n)) for n in koordinaadid.split(',')] 
        (cx, cy, hr, vr) = numbers
        coords = "[[%s,%s],[%s,%s]]" % (cx-hr,cy-vr,cx+hr,cy+vr)
        
    return coords

def _split_tag(tag):
    m = re.match(r'{(.+)}(.+)', tag)
    return m.groups()

def _local_tag(tag):
    #return tag[element.tag.find('}')+1:]
    return _split_tag(tag)[1]

def _is_local_file(url):
    if url is None:
        return None
    elif url.startswith('http:') or url.startswith('https:'):
        return False
    else:
        return True

def _makedirs(dirname, name):
    li = name.split('/')
    for dname in name.split('/')[:-1]:
        dirname = os.path.join(dirname, dname)
        if not os.path.exists(dirname):
            os.mkdir(dirname)

def _unzip(filedata, dirname):
    """Fail pakitakse lahti
    """
    zf = zipfile.ZipFile(filedata.file)
    for name in zf.namelist():
        _makedirs(dirname, name)
        if not name.endswith('/'):
            outfile = open(os.path.join(dirname, name), 'wb')
            outfile.write(zf.read(name))
            outfile.close()

    files = zf.namelist()
    zf.close()
    return files

def _write_zip(filedata):
    # kirjutame zip-faili kõvakettale
    fh, fn_zip = tempfile.mkstemp()
    f = os.fdopen(fh, 'wb')
    f.write(filedata.value)
    f.close()
    return fn_zip

def _unzip_proc(fn_zip, dirname):
    """Pakitakse lahti unzip programmiga
    """
    # pakime välises protsessis lahti
    #log.info(str(['unzip', fn_zip, '-d', dirname]))
    rc = subprocess.call(['unzip', fn_zip, '-d', dirname])
    if rc != 0:
        return None
    
    # leiame failid
    files = []
    for root, dirs, filenames in os.walk(dirname):
        for f in filenames:
            fn = os.path.join(root, f)[len(dirname)+1:]
            files.append(fn)
    return files

def _int_none(s):
    try:
        return int(s)
    except:
        return None

def _float_none(s):
    try:
        return float(s)
    except:
        return None
