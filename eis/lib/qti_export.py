# -*- coding: utf-8 -*- 

import sys
import os
import zipfile
import tempfile
import shutil
import re
import html
from lxml import etree
from lxml.builder import ElementMaker
from lxml.builder import E
import html

from eis.lib.base import *
from eis.lib.qti import * 
from eis.lib.block import BlockController
from eis.lib.blockview import BlockView

log = logging.getLogger(__name__)

_IMSQTI = '{%s}' % IMSQTI

EC = ElementMaker(namespace=IMSCP, nsmap={None:IMSCP})
EM = ElementMaker(namespace=IMSMD, nsmap={None:IMSMD}) # imsmd
EQ = ElementMaker(namespace=IMSQTI, nsmap={None:IMSQTI}) # imsqti
EXSI = ElementMaker(namespace=XSI, nsmap={'xsi':XSI})
EIS = ElementMaker(namespace=EISNS, nsmap={None:EISNS})

def export_zip(ylesanne, lang=None):
    # koostame failid ja pakime zipiks
    return QtiExport(ylesanne, lang).export()

def export_xml(ylesanne, lang=None):
    # koostame failid ja pakime zipiks
    return QtiExport(ylesanne, lang).create_assessment()

class QtiExport(object):
    """Ülesande eksportimine
    """
    def __init__(self, ylesanne, lang=None):
        self.ylesanne = ylesanne
        self.dirname = tempfile.mkdtemp() # ajutiste failide koht
        self.fn = os.path.join(self.dirname, 'ylesanne.zip')
        self.zf = zipfile.ZipFile(self.fn, "w")
        self.files = []
        if not lang or \
                (lang != ylesanne.lang and not ylesanne.has_lang(lang)):
            #lang not in [tk.lang for tk in ylesanne.tolkekeeled]):
                lang = ylesanne.lang
        self.lang = lang

    def export(self):
        # loome zip-faili
        self.create_zip()
        # paneme selle kinni
        self.zf.close()

        # loeme tehtud zipi sisu
        f = open(self.fn, 'rb')
        data = f.read()
        f.close()
        
        # kustutame kõik failid
        shutil.rmtree(self.dirname)
        
        # tagastame zipi sisu
        return data

    def create_zip(self):
        self.add_assessment()               
        self.add_manifest()
        
    def add_file(self, fn, data):
        fn_full = os.path.join(self.dirname, fn)
        _write_file(fn_full, data)
        # if isinstance(fn, str):
        #     # ZipFile ei talu unicode
        #     fn = fn.encode('utf-8')
        # if isinstance(fn_full, str):
        #     fn_full = fn_full.encode('utf-8')
        self.zf.write(fn_full, fn, zipfile.ZIP_DEFLATED)

    @property
    def assessment_id(self):
        if self.ylesanne.kood and False:
            return _identifier(self.ylesanne.kood)
        else:
            return 'Y%s' % self.ylesanne.id

    @property
    def manifest_id(self):
        return 'MANIFEST-EIS-%s' % self.ylesanne.id

    @property
    def resource_id(self):
        return 'RES-EIS-%s' % self.ylesanne.id

    def add_manifest(self):
        self.add_file('imsmanifest.xml', self.create_manifest())

    def add_assessment(self):
        self.fn_resource = 'ylesanne-%s.xml' % (self.assessment_id)
        self.files.append(self.fn_resource)
        self.add_file(self.fn_resource, self.create_assessment())

    @property
    def _composite(self):
        if len(self.ylesanne.sisuplokid) > 1:
            return 'true'
        else:
            return 'false'

    def create_manifest(self):

        resource_params = [EC.file(href=fn) for fn in self.files]

        qtiMetadata_params = [
            EQ.timeDependent('false'),
            EQ.feedbackType('none'),
            EQ.solutionAvailable('false'),
            EQ.composite(self._composite),
            EQ.toolName(eis.__product_name__),
            EQ.toolVersion(eis.__version__),
            EQ.toolVendor(eis.__vendor__)
            ]
        
        # leiame ülesandes kasutatavate interaktsioonitüüpide loetelu
        type_names = []
        for b in self.ylesanne.sisuplokid:
            if b.is_interaction:
                stype = b.type_name_qti
                type_names.append(stype)
        for s in set(type_names):
            qtiMetadata_params.append(EQ.interactionType(s))

        # ZIP-paki metaandmed
        manifest_lom = EM.lom(
            EM.general(
                EM.title(
                    EM.langstring('Ülesandepakett', {'{%s}lang' % XML:const.LANG_ET})
                    )
                ),
            #EM.lifecycle(),
            #EM.metametadata(
            #    EM.metadata_schema('LOMv1.0'),
            #    EM.metadata_schema('IMSQTIv2.1'),
            #    EM.language('et')
            #    ),
            EM.technical(
                # text/x-imsqti-item-xml
                # text/x-imsqti-test-xml 
                # application/xml
                EM.format('text/x-imsqti-item-xml')
                #EM.format('image/png')
                ),
            EM.rights(
                EM.description(
                    EM.langstring('(C) Haridus- ja Noorteamet', {'{%s}lang' % XML:const.LANG_ET})
                    )
                )
            )

        # Mitte-QTI metaandmed
        eis_metadata = EIS.metadata()
        if self.ylesanne.etest:
            eis_metadata.append(EIS.etest('true'))
        if self.ylesanne.ptest:
            eis_metadata.append(EIS.ptest('true'))
        if self.ylesanne.arvutihinnatav:
            eis_metadata.append(EIS.arvutihinnatav('true'))
        if self.ylesanne.adaptiivne:
            eis_metadata.append(EIS.adaptiivne('true'))
            
        eis_metadata.append(EIS.staatus(self.ylesanne.staatus_nimi, id=str(self.ylesanne.staatus)))
        for ya in self.ylesanne.ylesandeained:
            eis_metadata.append(EIS.aine(ya.aine_nimi or '', id=ya.aine_kood))
            if ya.oskus_kood:
                if ya.oskus_nimi:
                    eis_metadata.append(EIS.oskus(ya.oskus_nimi, id=ya.oskus_kood))        
            for rcd in ya.ylesandeteemad:
                if rcd.teema_nimi:
                    e = EIS.ylesandeteema(EIS.teema(rcd.teema_nimi, id=rcd.teema_kood))
                    if rcd.alateema_kood:
                        e.append(EIS.alateema(rcd.alateema_nimi, id=rcd.alateema_kood))
                    eis_metadata.append(e)
        for rcd in self.ylesanne.motlemistasandid:
            eis_metadata.append(EIS.mote(rcd.nimi, id=rcd.kood))        
        if self.ylesanne.keeletase_kood:
            if self.ylesanne.keeletase_nimi:
                eis_metadata.append(EIS.keeletase(self.ylesanne.keeletase_nimi, id=self.ylesanne.keeletase_kood))
        # for aste_kood in self.ylesanne.kooliastmed:
        #     aste_nimi = model.Klrida.get_str('ASTE', aste_kood)
        #     eis_metadata.append(EIS.aste(aste_nimi, id=aste_kood))        
        if self.ylesanne.vastvorm_kood:
            if self.ylesanne.vastvorm_nimi:
                eis_metadata.append(EIS.vastvorm(self.ylesanne.vastvorm_nimi, id=self.ylesanne.vastvorm_kood))        
        if self.ylesanne.hindamine_kood:
            if self.ylesanne.hindamine_nimi:
                eis_metadata.append(EIS.hindamine(self.ylesanne.hindamine_nimi, id=self.ylesanne.hindamine_kood))
        for rcd in self.ylesanne.testiliigid:
            testiliik_nimi = rcd.nimi
            if testiliik_nimi:
                eis_metadata.append(EIS.testiliik(rcd.nimi, id=rcd.kood))

        # Ülesande metaandmed
        resource_lom = EM.lom(
            EM.general(
                EM.identifier(self.assessment_id),
                EM.title(
                    EM.langstring(self.ylesanne.tran(self.lang).nimi, {'{%s}lang' % XML:self.lang})
                    ),
                EM.description(
                    EM.langstring(self.ylesanne.markus or '', {'{%s}lang' % XML:'et'}),
                    )
                ),
            #EM.lifecycle(),
            EM.metametadata(
                EM.metadata_schema('LOMv1.0'),
                EM.metadata_schema('IMSQTIv2.1'),
                EM.language(self.lang)
                ),
            EM.technical(
                # text/x-imsqti-item-xml
                # text/x-imsqti-test-xml 
                # application/xml
                EM.format('text/x-imsqti-item-xml')
                #EM.format('image/png')
                ),
            EM.rights(
                EM.description(
                    EM.langstring('EIS', {'{%s}lang' % XML:const.LANG_ET})
                    )
                ),
            eis_metadata
            )
        

        tree = (
            EC.manifest(
                EC.metadata(
                    EC.schema('IMS Content'),
                    EC.schemaversion('1.2'),
                    manifest_lom
                    ),
                EC.organizations(),
                EC.resources(
                    EC.resource(
                        EC.metadata(
                            EQ.qtiMetadata(*qtiMetadata_params),
                            resource_lom
                            ),
                        identifier=self.resource_id,
                        href=self.fn_resource,
                        type='imsqti_item_xmlv2p1',
                        *resource_params
                        #EC.file(href='choice.xml'),
                        #EC.file(href='images/sign.png'),
                        )
                    ),
                {'{%s}schemaLocation' % XSI: "http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p1.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p4.xsd http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/imsqti_v2p1.xsd",
                 'identifier': self.manifest_id,
                 }
                )
            )
        return etree.tostring(tree, 
                              xml_declaration=True, 
                              encoding='utf-8',
                              pretty_print=True)

    def create_assessment(self):

        tree = EQ.assessmentItem({
                'identifier':self.assessment_id,
                'toolName':eis.__product_name__,
                'toolVersion': eis.__version__,
                'title': self.ylesanne.nimi or '',
                'adaptive': 'false',
                'timeDependent': 'false',
                '{%s}schemaLocation' % XSI: "http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p1.xsd http://www.imsglobal.org/xsd/imsmd_v1p2 imsmd_v1p2p4.xsd http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/imsqti_v2p1.xsd",
                })

        self._append_responseDeclaration(tree)
        self._append_outcomeDeclaration(tree)
        self._append_itemBody(tree)
        self._append_responseProcessing(tree)

        self._append_shared(tree)
        return etree.tostring(tree, 
                              xml_declaration=True, 
                              encoding='utf-8', 
                              pretty_print=True)


    def _append_responseDeclaration(self, tree):
        for tulemus in self.ylesanne.tulemused:
            rd = EQ.responseDeclaration(identifier=_identifier(tulemus.kood))
            kardinaalsus = tulemus.kardinaalsus
            if kardinaalsus in (const.CARDINALITY_ORDERED_SEQ,
                                const.CARDINALITY_ORDERED_SQ1,
                                const.CARDINALITY_ORDERED_ADJ,
                                const.CARDINALITY_ORDERED_POS,
                                const.CARDINALITY_ORDERED_COR):
                kardinaalsus = const.CARDINALITY_ORDERED
            rd.set('cardinality', kardinaalsus)
            if tulemus.baastyyp:
                rd.set('baseType', tulemus.baastyyp)
            
            li = [p for p in tulemus.hindamismaatriksid if p.is_correct and not p.is_areaMapEntry]
            if len(li):
                correctResponse = EQ.correctResponse()
                for pallid in li:
                    if tulemus.baastyyp in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
                        mapKey = '%s %s' % (_identifier(pallid.kood1), 
                                            _identifier(pallid.kood2))
                    elif tulemus.baastyyp == const.BASETYPE_POINT:
                        mapKey = '%s %s' % (pallid.cx, pallid.cy)
                    elif tulemus.baastyyp == const.BASETYPE_IDENTIFIER:
                        mapKey = _identifier(pallid.kood1)
                    else:
                        mapKey = pallid.tran(self.lang).kood1
                    correctResponse.append(EQ.value(mapKey))
                rd.append(correctResponse)

            li = [p for p in tulemus.hindamismaatriksid if p.is_mapEntry]
            if len(li):
                mapping = EQ.mapping()
                if tulemus.vaikimisi_pallid is not None:
                    mapping.set('defaultValue', str(tulemus.vaikimisi_pallid))
                if tulemus.max_pallid is not None:
                    mapping.set('upperBound', str(tulemus.max_pallid))
                if tulemus.min_pallid is not None:
                    mapping.set('lowerBound', str(tulemus.min_pallid))
                for pallid in li:
                    if tulemus.baastyyp in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
                        mapKey = '%s %s' % (_identifier(pallid.kood1), 
                                            _identifier(pallid.kood2))
                    elif tulemus.baastyyp == const.BASETYPE_IDENTIFIER:
                        mapKey = _identifier(pallid.kood1)
                    else:
                        mapKey = _identifier(pallid.tran(self.lang).kood1)
                    mapping.append(EQ.mapEntry(mapKey=mapKey,
                                               mappedValue=str(pallid.pallid)))
                rd.append(mapping)
                    
            li = [p for p in tulemus.hindamismaatriksid if p.is_areaMapEntry]
            if len(li):
                areaMapping = EQ.areaMapping()
                if tulemus.vaikimisi_pallid is not None:
                    areaMapping.set('defaultValue', str(tulemus.vaikimisi_pallid))
                if tulemus.max_pallid is not None:
                    areaMapping.set('upperBound', str(tulemus.max_pallid))
                if tulemus.min_pallid is not None:
                    areaMapping.set('lowerBound', str(tulemus.min_pallid))
                for pallid in li:
                    entry = EQ.areaMapEntry(shape=pallid.kujund,
                                            coords=_coords(pallid.koordinaadid, pallid.kujund),
                                            mappedValue=str(pallid.get_pallid())) 
                    areaMapping.append(entry)
                rd.append(areaMapping)
            tree.append(rd)

    def _append_outcomeDeclaration(self, tree):
        for valjund in self.ylesanne.valjundid:
            od = EQ.outcomeDeclaration(identifier=_identifier(valjund.kood))
            if valjund.kardinaalsus is not None:
                od.set('cardinality', valjund.kardinaalsus)
            if valjund.baastyyp is not None:
                od.set('baseType', valjund.baastyyp)
            if valjund.interpretatsioon is not None:
                od.set('interpretation', valjund.interpretatsioon)
            if valjund.max_norm is not None:
                od.set('normalMaximum', valjund.max_norm)
            if valjund.min_norm is not None:
                od.set('normalMinimum', valjund.min_norm)
            if valjund.oskus_norm is not None:
                od.set('masteryValue', valjund.oskus_norm)
            tree.append(od)

    def _append_itemBody(self, tree):
        buf = '<itemBody>'+self.create_body()+'</itemBody>'
        # asendada &, kui selle järel pole #[0-9]+; ega lt; gt;
        p = re.compile('&([^#lg])')
        buf = p.sub(r'&amp;\1', buf)
        buf = buf.replace('<', '\n<')
        ib = etree.XML(buf)
        tree.append(ib)

    def _append_responseProcessing(self, tree):
        self.ylesanne.set_tulemusmall()
        if self.ylesanne.tulemusmall:
            t = self.ylesanne.tulemusmall
            if not t.rp_uri and t.rp_reeglid:
                rp = etree.XML(t.rp_reeglid)
            else:
                rp = EQ.responseProcessing()
                if t.rp_uri:
                    rp.set('template', t.rp_uri)
                if t.rp_location:
                    rp.set('templateLocation', t.rp_location)
            tree.append(rp)

    def _append_shared(self, tree):
        """Lisatakse pakki ühisfailid, kui neid ülesandes on kasutatud.
        """
        shared_prefix = 'shared/'
        for e in tree.iterdescendants('img'):
            fn = e.get('src')
            if fn.startswith(shared_prefix):
                # on ühisfail
                if not fn in self.files:
                    # pole veel lisatud
                    shared_fn = fn[len(shared_prefix):]
                    t_obj = model.Yhisfail.get_by_name(shared_fn)
                    if t_obj is not None:
                        self.add_object(t_obj.filedata, fn)

    def create_body(self):
        """Tagastatakse list ülesande sisu elementidest.
        Ühest sisuplokist võib saada mitu elementi.
        Mitu sisuplokki on igaüks eraldi elementides, kui teine pole esimese sees.
        """
        #elements = []
        buf_xml = ''
        for plokk in self.ylesanne.sisuplokid:
            item_obj = QtiExportBlock.get(plokk, self, self.lang)
            item_xml = item_obj.export()
            if not item_xml:
                continue
            # ei tohi muuta atribuutide sisus &lt;
            #item_xml = html.unescape(item_xml)
            try:
                etree.XML(item_xml)
            except Exception as e:
                # vbl yks EISi sisuplokk tegi mitu QTI sisuplokki
                try:
                    etree.XML('<div>' + item_xml + '</div>')
                except Exception as e:
                    log.error('Vigane XML sisuplokis %s %s' % (plokk.id, str(e)))
                    raise

            if plokk.staatus == const.B_STAATUS_KEHTIV:
                # ploki elemendid tuleb lisada kusagile vahele, 
                # kui on PLACEHOLDER kohad
                # kui pole neid kohti, siis lisada listile lõppu
                buf_xml = BlockView.replace_placeholder(buf_xml, item_xml, literal=False)
        return buf_xml

    def add_object(self, filedata, fn):
        """Lisatakse sisuobjekt.
        """
        self.files.append(fn)
        self.add_file(fn, filedata)
        
class QtiExportBlock(object):
    @classmethod
    def get(cls, plokk, package, lang):
        """Ülesande sisuploki sidumine oma klassiga
        """
        clsname = '_' + plokk.type_name
        #log.warn(clsname)
        return eval(clsname)(plokk, package, lang)

    def __init__(self, plokk, package, lang):
        """
        item - model.Ylesanne
        """
        self.plokk = plokk # ylesande sisuplokk
        self.package = package # QtiExport objekt
        self.lang = lang

    def export(self):
        """Eksport.
        Üle kirjutada.
        Tagastab XML stringina.
        """
        pass

    def _parse_sisu(self):
        tree = None
        sisu = self.plokk.tran(self.lang).sisu
        if sisu:
            try:
                tree = etree.XML(sisu)
            except Exception as e:
                log.error(str(e))
        return tree

class QtiExportText(QtiExportBlock):
    """Sisuplokid, mille korral tuleb item.sisu eksportida.
    """
    def export(self):
        contents = self.export_contents()
        nimi = self.plokk.tran(self.lang).nimi
        if nimi:
            buf = '<strong>%s</strong>' % nimi
            try:
                etree.XML(buf)
            except Exception as e:
                # eemaldame HTMLi, kuna see on vigaselt koostatud
                nimi = re.sub(r'<[^>]*>', '', nimi)
                buf = '<strong>%s</strong>' % nimi                
            buf = '<p>%s %s</p>' % (buf, contents)
        else:
            return contents

    def export_contents(self):
        # sisu tuleks vajadusel muuta
        raise Exception('sisu teisendus tegemata')
        #return self.plokk.sisu
      
class QtiExportInteraction(QtiExportBlock):

    @property
    def tag(self):
        """Eksport-XML-i juurelemendi nimi
        """
        return self.__class__.__name__[1:]

    def export_prompt(self):
        """Interaktsioonide korral on pealkiri <prompt> sees.
        """
        buf = ''
        nimi = self.plokk.tran(self.lang).nimi
        if nimi:
            buf = '<prompt>%s</prompt>' % nimi
            try:
                etree.XML(buf)
            except Exception as e:
                # eemaldame HTMLi, kuna see on vigaselt koostatud
                nimi = re.sub(r'<[^>]*>', '', nimi)
                buf = '<prompt>%s</prompt>' % nimi
        return buf

    def export_tag(self, **attrs):
        """Eksport-XML-i juure elemendi koostamine
        """
        buf = '<%s' % self.tag
        kysimus = self.plokk.kysimus
        buf += ' responseIdentifier="%s"' % (_identifier(kysimus.kood) or 'RESPONSE')
        for key in attrs:
            if key == 'shuffle':
                if kysimus.segamini is not None:
                    buf += ' shuffle="%s"' % _sbool(kysimus.segamini)
            elif key == 'maxAssociations':
                if kysimus.max_vastus is not None:
                    buf += ' maxAssociations="%s"' % kysimus.max_vastus
            elif key == 'minAssociations':
                if kysimus.min_vastus is not None:
                    buf += ' minAssociations="%s"' % kysimus.min_vastus
            elif key == 'minChoices':
                if kysimus.min_vastus is not None:
                    buf += ' minChoices="%s"' % kysimus.min_vastus
            elif key == 'maxChoices':
                buf += ' maxChoices="%s"' % (kysimus.max_vastus or 0)
            elif key == 'expectedLength':
                if kysimus.pikkus is not None:
                    buf += ' expectedLength="%s"' % kysimus.pikkus
            elif key == 'mask':
                if kysimus.mask is not None:
                    buf += ' mask="%s"' % kysimus.mask
            else:
                value = attrs[key]
                if value is not None:
                    buf += ' %s="%s"' % (key, value)
        buf += '>'
        buf += self.export_prompt()
        buf += self.export_tag_contents()
        buf += '</%s>' % self.tag
        return buf

    def export_tag_contents(self):
        """Eksport-XML-i juure elemendi all oleva osa koostamine
        """
        return ''

    def _interaction_name(self):
        return self.__class__.__name__[1:]

class QtiExportImageInteraction(QtiExportInteraction):
    """Pildiga ülesanded
    """
    image_path = 'images'

    def add_obj(self, obj, t_obj):
        fn = os.path.join(self.image_path, obj.filename)
        if fn in self.package.files:
            # on juba lisatud
            return fn
            # lisame unikaalse nime all
            # for n in range(1,1000):
            #    fn_new = _unique_fn(fn, n)
            #    if fn_new not in self.package_files:
            #        fn = fn_new
            #        break
        self.package.add_object(t_obj.filedata or obj.filedata, fn)
        return fn

    def export_obj(self, obj):
        """Sisuobjekti eksportimine
        """
        if obj:
            t_obj = obj.tran(self.lang)
            if t_obj.fileurl:
                fn = t_obj.fileurl
            elif obj.filename and t_obj.has_file:
                fn = self.add_obj(obj, t_obj)
            else:
                return ''
            buf = "<object"
            buf += ' data="%s"' % fn
            buf += ' type="%s"' % obj.mimetype
            if obj.laius:
                buf += ' width="%s"' % obj.laius
            if obj.korgus:
                buf += ' height="%s"' % obj.korgus
            buf += '>'
            buf += '</object>'
            return buf
        else:
            return ''

    def export_img(self, obj, heading):
        """Pildi eksportimine pildiplokis
        """
        if obj:
            t_obj = obj.tran(self.lang)
            fn = self.add_obj(obj, t_obj)
            buf = "<img"
            buf += ' src="%s"' % fn            
            if heading:
                buf += ' longdesc="%s"' % heading.replace('<', '&lt;').replace('>', '&gt;')
            if obj.laius:
                buf += ' width="%s"' % obj.laius
            if obj.korgus:
                buf += ' height="%s"' % obj.korgus
            buf += '/>'
            return buf
        else:
            return ''

    def export_link(self, obj, heading):
        """Pildi eksportimine pildiplokis
        """
        if obj:
            t_obj = obj.tran(self.lang)
            fn = self.add_obj(obj, t_obj)
            buf = '<a href="%s">%s</a>' % (fn, fn)
            return buf
        else:
            return ''

    def export_hotspots(self, tag):
        buf = ''
        for obj in self.plokk.kysimus.valikud:
            # obj on Valikupiirkond
            buf += '<%s' % tag
            buf += ' identifier="%s"' % _identifier(obj.kood)
            if obj.min_vastus is not None:
                buf += ' matchMin="%s"' % obj.min_vastus
            if obj.max_vastus is not None:
                buf += ' matchMax="%s"' % obj.max_vastus
            if obj.kujund is not None:
                buf += ' shape="%s"' % obj.kujund
            buf += ' coords="%s"' % _coords(obj.koordinaadid, obj.kujund)
            buf += '/>'
        return buf


#########################################################
# Vastuseta sisuplokid

class _header(QtiExportText):
    def export_contents(self):
        return ''
    
class _formula(QtiExportText):
    def export_contents(self):
        return ''

class _rubricBlock(QtiExportText):

    def export_contents(self):
        return self.plokk.tran(self.lang).sisu

class _math(QtiExportText):
    def export_contents(self):
        return self.plokk.tran(self.lang).sisu # latex

class _image(QtiExportImageInteraction):
    def export(self):
        buf = ''
        for obj in self.plokk.piltobjektid:
            buf += self.export_img(obj, self.plokk.tran(self.lang).nimi)
        return buf

class _customInteraction(QtiExportImageInteraction):
    tag = 'customInteraction'
    def export(self):
        return self.export_tag(eistype='file')

    def export_tag_contents(self):
        buf = ''
        obj = self.plokk.taustobjekt
        if obj:
            buf = self.export_link(obj, self.plokk.tran(self.lang).nimi)
        return buf

class _geogebraInteraction(_customInteraction):
    pass

class _trailInteraction(_customInteraction):
    pass

class _graphicOrdAssociateInteraction(_customInteraction):
    pass

class _crosswordInteraction(_customInteraction):
    pass

class _colorareaInteraction(_customInteraction):
    pass

class _uncoverInteraction(_customInteraction):
    pass

class _select2PointInteraction(_customInteraction):
    pass

class _positionObject2Interaction(_customInteraction):
    pass
    
class _txpos2Interaction(_customInteraction):
    pass

class _txgapInteraction(_customInteraction):
    pass

class _txassInteraction(_customInteraction):
    pass

class _mediaInteraction(QtiExportImageInteraction):
    def export(self, **attrs):
        """Eksport-XML-i juure elemendi koostamine
        """
        buf = '<%s' % self.tag
        kysimus = self.plokk.kysimus
        obj = self.plokk.meediaobjekt

        buf += ' responseIdentifier="%s"' % (_identifier(kysimus.kood) or 'RESPONSE')
        buf += ' autostart="%s"' % _sbool(obj.autostart)
        if obj.min_kordus:
            buf += ' minPlays="%s"' % obj.min_kordus
        if obj.max_kordus:
            buf += ' maxPlays="%s"' % obj.max_kordus
        if obj.isekorduv is not None:
            buf += ' loop="%s"' % _sbool(obj.isekorduv)
        buf += '>'
        buf += self.export_prompt()
        buf += self.export_tag_contents()
        buf += '</%s>' % self.tag
        return buf

    def export_tag_contents(self):
        """Eksport-XML-i juure elemendi all oleva osa koostamine
        """
        return self.export_obj(self.plokk.meediaobjekt)

        
#class _customInteraction(QtiExportInteraction):
#    pass

#########################################################
# Valikud

class _match2Interaction(QtiExportInteraction):
    tag = 'matchInteraction'
    
    def export(self):
        return self.export_tag(shuffle=True, maxAssociations=True)

    def export_tag_contents(self):
        buf = ''
        for i in (1,2):
            valikuhulk = self.plokk.get_baaskysimus(i)
            buf += '<simpleMatchSet>'
            for valik in valikuhulk.valikud:
                buf += '<simpleAssociableChoice'
                buf += ' identifier="%s"' % _identifier(valik.kood)
                if valik.min_vastus is not None:
                    buf += ' matchMin="%s"' % valik.min_vastus
                if valik.max_vastus is not None:
                    buf += ' matchMax="%s"' % valik.max_vastus
                buf += '>'
                sisu = valik.tran(self.lang).nimi
                if not valikuhulk.rtf:
                    sisu = html.escape(sisu)
                buf += sisu
                buf += '</simpleAssociableChoice>'
            buf += '</simpleMatchSet>'
        return buf

class _match3Interaction(QtiExportInteraction):
    tag = 'matchInteraction'
    
    def export(self):
        return self.export_tag(shuffle=True, maxAssociations=True)

    def export_tag_contents(self):
        buf = ''
        for i in (1,2):
            valikuhulk = self.plokk.get_baaskysimus(i)
            buf += '<simpleMatchSet>'
            for valik in valikuhulk.valikud:
                buf += '<simpleAssociableChoice'
                buf += ' identifier="%s"' % _identifier(valik.kood)
                if valik.min_vastus is not None:
                    buf += ' matchMin="%s"' % valik.min_vastus
                if valik.max_vastus is not None:
                    buf += ' matchMax="%s"' % valik.max_vastus
                buf += '>'
                sisu = valik.tran(self.lang).nimi
                if not valikuhulk.rtf:
                    sisu = html.escape(sisu)
                buf += sisu
                buf += '</simpleAssociableChoice>'
            buf += '</simpleMatchSet>'
        return buf

class _choiceInteraction(QtiExportInteraction):
    def export(self):
        return self.export_tag(shuffle=True, maxChoices=True)

    def export_tag_contents(self):
        buf = ''
        kysimus = self.plokk.kysimus
        for valik in kysimus.valikud:
            buf += '<simpleChoice'
            buf += ' identifier="%s"' % _identifier(valik.kood)
            buf += '>'
            sisu = valik.tran(self.lang).nimi
            if not kysimus.rtf:
                sisu = html.escape(sisu)
            buf += sisu 
            buf += '</simpleChoice>'
        return buf

class _mchoiceInteraction(QtiExportInteraction):
    def export(self):
        return ''

class _associateInteraction(QtiExportInteraction):
    def export(self):
        return self.export_tag(shuffle=True, maxAssociations=True)

    def export_tag_contents(self):
        buf = ''
        for valik in self.plokk.kysimus.valikud:
            buf += '<simpleAssociableChoice'
            buf += ' identifier="%s"' % _identifier(valik.kood)
            if valik.min_vastus is not None:
                buf += ' matchMin="%s"' % valik.min_vastus
            if valik.max_vastus is not None:
                buf += ' matchMax="%s"' % valik.max_vastus               
            buf += '>'
            buf += valik.tran(self.lang).nimi
            buf += '</simpleAssociableChoice>'
        return buf

class _orderInteraction(QtiExportInteraction):
    def export(self):
        return self.export_tag(shuffle=True, maxChoices=True)

    def export_tag_contents(self):
        buf = ''
        kysimus = self.plokk.kysimus
        for valik in kysimus.valikud:
            buf += '<simpleChoice'
            buf += ' identifier="%s"' % _identifier(valik.kood)
            buf += '>'
            sisu = valik.tran(self.lang).nimi
            if not kysimus.rtf:
                sisu = html.escape(sisu)
            buf += sisu
            buf += '</simpleChoice>'
        return buf

#########################################################
# Tekstid

class _hottextInteraction(QtiExportInteraction):
    def export(self):
        return self.export_tag(minChoices=True, maxChoices=True)
    
    def export_tag_contents(self):
        tree = self._parse_sisu()
        if tree is None:
            return ''

        # Tekstiosad on kujul
        # <span class="hottext" name="KOOD" group="GRUPP" uitype="UITYPE"
        #       style="background-color: rgb(192, 192, 254);">
        # (GRUPP:KOOD)NIMI
        # </span>
        #
        # Viime kujule:
        # <hottext identifier="KOOD">NIMI
        #  <var type="uitype">UITYPE</var>        
        #  <var type="group">GRUPP</var>
        # </hottext>        
        #
        # kus <var type="uitype">UITYPE</var> esineb ainult siis, kui UITYPE="underline"
        # ja <var type="group">GRUPP</var> esineb ainult siis, kui GRUPP pole tühi

        for field in tree.xpath('//span[@class="hottext"]'):
            kood = field.get('name')
            group = field.get('group')
            uitype = field.get('uitype')

            nimi = field.text
            n = nimi.find(')')
            if n > -1:
                nimi = nimi[n+1:]
                
            if not kood:
                # midagi on sassis
                field.getparent().remove(field)
                continue

            buf = '<hottext identifier="%s">' % _identifier(kood)
            buf += nimi or ''
            if uitype == 'underline':
                buf += '<var type="uitype">%s</var>' % uitype
            if group:
                buf += '<var type="group">%s</var>' % group
            buf += '</hottext>' 
            new_field = etree.XML(buf)
            new_field.tail = field.tail
            field.getparent().replace(field, new_field)

        return outer_xml(tree)

class _colortextInteraction(_hottextInteraction):
    # tekstiosa värvimine eksporditakse tekstiosa valikuna, värvid lähevad kaduma
    tag = 'hottextInteraction'

class _inlineTextInteraction(QtiExportText):

    def export_contents(self):
        tree = self._parse_sisu()
        if tree is None:
            return ''

        # asendada
        # <input baastyyp="string" hm0="värviline/10/0" hm1="punane/20/0"
        #        max_pallid="10" min_pallid="3" pattern="\d+" size="10"
        #        type="text" vaikimisi_pallid="3" value="RESPONSE" />
        # sellega:
         #<textEntryInteraction responseIdentifier=".." expectedLength=".."/>

        for field in tree.xpath('//input[@type="text"]'):
            kood = field.get('value')
            kysimus = self.plokk.get_kysimus(kood)
            if not kysimus:
                # midagi on sassis
                field.getparent().remove(field)
                continue
            nfield = E.textEntryInteraction(responseIdentifier=_identifier(kysimus.kood))
            if kysimus.pikkus:
                nfield.set('expectedLength',str(kysimus.pikkus))
            if kysimus.mask:
                nfield.set('pattern', kysimus.mask)
            nfield.tail = field.tail
            field.getparent().replace(field, nfield)            

        return outer_xml(tree)

class _inlineChoiceInteraction(QtiExportText):
    def export_contents(self):
        tree = self._parse_sisu()
        if tree is None:
            return ''

        # asendada select -> inlineChoiceInteraction
        for field in tree.xpath('//select'):
            label = field.find('option')
            kood = label is not None and label.text and label.text.strip()
            if not kood:
                kood = field.get('name') or field.get('id') # tagasiyhilduvus
            kysimus = self.plokk.get_kysimus(kood)
            if not kysimus:
                # midagi on sassis
                field.getparent().remove(field)
                continue
            nfield = E.inlineChoiceInteraction(responseIdentifier=_identifier(kood))
            for o in field.iterdescendants('option'):
                o_kood = o.get('value')
                if o_kood:
                    if kysimus.rtf:
                        o_text = utils.descape(o.text)
                    else:
                        o_text = o.text                       
                    nfield.append(E.inlineChoice(o_text, identifier=o.get('value')))
            nfield.tail = field.tail
            field.getparent().replace(field, nfield)
        return outer_xml(tree)

class _gapMatchInteraction(QtiExportInteraction):
    def export(self):
        return self.export_tag(shuffle=True)

    def export_tag_contents(self):
        buf = ''
        bkysimus = self.plokk.kysimus
        for valik in bkysimus.valikud:
            buf += '<gapText'
            buf += ' identifier="%s"' % _identifier(valik.kood)
            if valik.min_vastus is not None:
                buf += ' matchMin="%s"' % valik.min_vastus
            if valik.max_vastus is not None:
                buf += ' matchMax="%s"' % valik.max_vastus
            buf += '>'
            nimi = valik.tran(self.lang).nimi
            if bkysimus.rtf:
                buf += nimi
            else:
                buf += html.escape(nimi)
            buf += '</gapText>'

        buf += self._export_gap()
        return buf

    def _export_gap(self):
        # asendada sisus <select> -> <gap identifier=".."/>
        tree = etree.XML(self.plokk.tran(self.lang).sisu)
        li = tree.iterdescendants('input')
        for e in li:
            buf = '<gap'
            if e.get('value'):
                buf += ' identifier="%s"' % e.get('value')
            buf += '/>'
            new_e = etree.XML(buf)
            new_e.tail = e.tail
            e.getparent().replace(e, new_e)

        #log.info(outer_xml(tree))
        return outer_xml(tree)

class _textEntryInteraction(QtiExportInteraction):
    def export(self):
        return self.export_tag(expectedLength=True, mask=True)

    def export_tag_contents(self):
        return ''

class _extendedTextInteraction(QtiExportInteraction):
    def export(self):
        return self.export_tag()

    def export_tag(self):
        """Eksport-XML-i juure elemendi koostamine
        """
        buf = '<%s' % self.tag
        kysimus = self.plokk.kysimus
        # maxStrings, minStrings, expectedLines, 
        # format (plain/preFormatted/xhtml)
        buf += ' responseIdentifier="%s"' % (_identifier(kysimus.kood) or 'RESPONSE')
        buf += ' minStrings="%s"' % (kysimus.min_vastus or 1)
        buf += ' maxStrings="%s"' % (kysimus.max_vastus or 1)        
        if kysimus.ridu:
            buf += ' expectedLines="%s"' % (kysimus.ridu)
        if kysimus.vorming_kood:
            buf += ' format="%s"' % (_identifier(kysimus.vorming_kood))
        buf += '>'
        buf += self.export_prompt()
        buf += '</%s>' % self.tag
        return buf
        
    def export_tag_contents(self):
        return ''

class _mathInteraction(QtiExportInteraction):
    tag = 'customInteraction'
    def export(self):
        return self.export_tag(eistype='math')

    def export_tag_contents(self):
        buf = ''
        sisu = self.plokk.tran(self.lang).sisu
        if sisu:
            buf += '<contents>' + sisu + '</contents>'
        return buf

class _sliderInteraction(QtiExportInteraction):
    def export(self):
        kysimus = self.plokk.kysimus
        kyslisa = kysimus.kyslisa
        return self.export_tag(lowerBound=kyslisa.min_vaartus,
                               upperBound=kyslisa.max_vaartus,
                               step=kyslisa.samm,
                               stepLabel=_sbool(kyslisa.samm_nimi),
                               orientation=kyslisa.vertikaalne and 'vertical' or 'horizontal')

    def export_tag_contents(self):
        return ''


#########################################################
# Piltküsimused

class _positionObjectInteraction(QtiExportImageInteraction):
    def export(self):
        buf = ''
        buf += '<positionObjectStage>'
        buf += self.export_obj(self.plokk.taustobjekt)
        buf += self.export_position_obj()
        buf += '</positionObjectStage>'
        return buf

    def export_position_obj(self):
        buf = ''
        prompt = True
        for obj in self.plokk.piltobjektid:
            buf += '<positionObjectInteraction'
            buf += ' responseIdentifier="%s"' % (_identifier(obj.kood) or 'RESPONSE')
            buf += ' minChoices="%s"' % (obj.min_vastus or 1)
            buf += ' maxChoices="%s"' % (obj.max_vastus or 1)
            buf += '>'
            if prompt:
                # prompti paneme esimese pildi juurde
                buf += self.export_prompt()
                prompt = False
            buf += self.export_obj(obj)
            buf += '</positionObjectInteraction>'
        return buf

class _positionTextInteraction(_positionObjectInteraction):
    pass

class _drawingInteraction(QtiExportImageInteraction):
    def export(self):
        buf = self.export_tag()
        return buf

    def export_tag_contents(self):
        buf = self.export_obj(self.plokk.taustobjekt)
        return buf

class _graphicGapMatchInteraction(QtiExportImageInteraction):
    def export(self):
        buf = self.export_tag()
        return buf
    
    def export_tag_contents(self):
        buf = self.export_obj(self.plokk.taustobjekt)
        for obj in self.plokk.piltobjektid:
            buf += '<gapImg identifier="%s"' % _identifier(obj.kood)
            if obj.min_vastus is not None:
                buf += ' matchMin="%s"' % obj.min_vastus
            if obj.max_vastus is not None:
                buf += ' matchMax="%s"' % obj.max_vastus
            buf += '>'
            buf += self.export_obj(obj)        
            buf += '</gapImg>'
        buf += self.export_hotspots('associableHotspot')
        return buf

class _hotspotInteraction(QtiExportImageInteraction):
    def export(self):
        buf = self.export_tag(minChoices=True, maxChoices=True)
        return buf

    def export_tag_contents(self):
        buf = self.export_obj(self.plokk.taustobjekt)
        buf += self.export_hotspots('hotspotChoice')
        return buf

class _graphicOrderInteraction(QtiExportImageInteraction):
    def export(self):
        buf = self.export_tag()
        return buf

    def export_tag_contents(self):
        buf = self.export_hotspots('hotspotChoice')
        buf += self.export_obj(self.plokk.taustobjekt)        
        return buf

class _selectPointInteraction(QtiExportImageInteraction):
    def export(self):
        buf = self.export_tag(minChoices=True, maxChoices=True)
        return buf

    def export_tag_contents(self):
        buf = self.export_obj(self.plokk.taustobjekt)
        return buf

class _graphicAssociateInteraction(QtiExportImageInteraction):
    def export(self):
        buf =  self.export_tag()
        return buf
    
    def export_tag_contents(self):
        buf = self.export_hotspots('associableHotspot')
        buf += self.export_obj(self.plokk.taustobjekt)        
        return buf
        
#########################################################
# Faili laadimine

class _audioInteraction(QtiExportInteraction):
    tag = 'customInteraction'
    def export(self):
        return self.export_tag(eistype='audio')

    def export_tag_contents(self):
        return ''

class _uploadInteraction(QtiExportInteraction):
    def export(self):
        return self.export_tag()

    def export_tag_contents(self):
        return ''


#########################################################
# Abifunktsioonid

def _identifier(kood):
    """Lubame EISis kasutada koodi algusena numbrit. 
    QTI ei luba. Vajadusel paneme siis alakriipsu ette.
    """
    if not kood:
        return kood
    if not re.compile(r"^[A-Za-z_]").match(kood):
        kood = '_' + kood
    #regexp = re.compile(r"^[A-Za-z_][A-Za-z0-9\.\-\_]*$")
    return kood
        
def _sbool(b):
    return b is None and None or b is True and 'true' or 'false'

def _coords(koordinaadid, kujund):
    # koordinaadid on EISis kujul "[[x1,y1],[x2,y2]]"
    # viime need QTI kujule:
    
    # rect: left-x, top-y, right-x, bottom-y.

    # circle: center-x, center-y, radius. 
    # Note. When the radius value is a percentage value, 
    # user agents should calculate the final radius value 
    # based on the associated object's width and height. 
    # The radius should be the smaller value of the two.

    # poly: x1, y1, x2, y2, ..., xN, yN. 
    # The first x and y coordinate pair and the last should be the same 
    # to close the polygon. When these coordinate values are not the same, 
    # user agents should infer an additional coordinate pair 
    # to close the polygon.

    # ellipse: center-x, center-y, h-radius, v-radius. 
    # Note that the ellipse shape is deprecated as it is not defined by [XHTML].

    # default: no coordinates should be given.
    coords = ''
    if kujund == const.SHAPE_POLY:
        coords = koordinaadid.replace('[','').replace(']','')
        # lisame alguspunkti lõppu
        numbers = coords.split(',')
        if numbers[0] != numbers[-2] or numbers[1] != numbers[-1]:
            coords += ',%s,%s' % (numbers[0], numbers[1])
    else:
        p = re.compile(r'\[\[([0-9]+),([0-9]+)\],\[([0-9]+),([0-9]+)\]\]')
        m = p.match(koordinaadid)
        if m:
            numbers = [int(n) for n in m.groups()]
            (x1, y1, x2, y2) = numbers
            if kujund == const.SHAPE_RECT:
                coords = "%s,%s,%s,%s" % (x1, y1, x2, y2)
            elif kujund == const.SHAPE_CIRCLE:
                r = int(min(x2-x1,y2-y1)/2)
                cx = int(x1 + r)
                cy = int(y1 + r)
                coords = "%s,%s,%s" % (cx, cy, r)
            elif kujund == const.SHAPE_ELLIPSE:
                hr = int((x2-x1)/2)
                vr = int((y2-y1)/2)
                cx = int(x1 + hr)
                cy = int(y1 + vr)
                coords = "%s,%s,%s,%s" % (cx, cy, hr, vr)

    return coords

def _unique_fn(fn, n):
    p = fn.rfind('.')
    extra = '-%s' % n
    if p == -1:
        fn_new = fn + extra
    else:
        fn_new = fn[:p-1] + extra + fn[p:]
    return fn_new

def _write_file(fn, data):
    try:
        dirname = os.path.dirname(fn)
        os.makedirs(dirname)
    except OSError:
        pass

    if isinstance(fn, str):
        fn = fn.encode('utf-8')
    f = open(fn, 'wb')
    f.write(data)
    f.close()
