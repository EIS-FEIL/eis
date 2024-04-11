# # ei ole kasutusel, ei ole testitud
# from datetime import datetime, date
# from eis.lib.xtee.xroad import *

# import logging
# log = logging.getLogger(__name__)

# from io import StringIO
# import mimetypes

# log = logging.getLogger(__name__)

# class Dhl(XroadClientEIS):
#     "DVK liides"
#     producer = 'dhl'

#     def sendDocuments_vaie(self, file_data, fn):
#         saatja = {'regnr': self.asutus,
#                   #'asutuse_nimi': 'Eksami- ja Kvalifikatsioonikeskus',
#                   'nimi': 'Eksamikeskus',
#                   }
        
#         if self.handler:
#             settings = self.handler.request.registry.settings
#             saaja_regnr = settings.get('vaie.saaja.regnr')
#             saaja_asutuse_nimi = settings.get('vaie.saaja.nimi') or 'HTM'            

#             saaja = {'regnr': saaja_regnr,
#                      'nimi': saaja_asutuse_nimi,
#                      }
#         else:
#             # testimine
#             saaja = saatja

#         return self.sendDocuments(saatja, saaja, file_data, fn)

#     def sendDocuments(self, saatja, saaja, file_data, fn):
#         doc = self._gen_dokument(saatja, saaja, file_data, fn)
#         doc_attachment = attachment.Attachment(doc)
#         content_id = doc_attachment.gen_content_id()
#         attachments = [doc_attachment]
#         request = E.request(E.dokumendid(href='cid:%s' % content_id))
#         try:
#             res = self.call('sendDocuments', request, [], attachments=attachments)
#             response = res.get('response')
#             return None, response
#         except SoapFault as e:
#             return e.faultstring, []
#         return None, []

#     def _gen_dokument(self, saatja, saaja, file_data, fn):
#         #buf = '<dokument xmlns:dhl="http://www.riik.ee/schemas/dhl/2010/2">'
#         buf = '<?xml version="1.0" encoding="UTF-8"?>\n'
#         buf += '<dhl:dokument xmlns:dhl="http://www.riik.ee/schemas/dhl">' +\
#               self._gen_metainfo() +\
#               self._gen_transport(saatja, saaja) +\
#               '<dhl:ajalugu/>' +\
#               self._gen_metaxml(saatja, saaja) +\
#               self._gen_failid(file_data, fn) +\
#               '</dhl:dokument>'

#         # f = open('test.dokument.xml', 'w')
#         # f.write(doc)
#         # f.close()
#         # log.debug(doc)
#         #f = open('test.dokument.xml', 'r')
#         #buf = f.read()
#         #f.close()
#         log.debug(buf)
#         return buf

#     def _gen_metainfo(self):
#         buf = '<dhl:metainfo xmlns:ma="http://www.riik.ee/schemas/dhl-meta-automatic"/>'
#         return buf

#     def _gen_metaxml(self, saatja, saaja):
#         #return '<dhl:metaxml/>'
#         buf = '<dhl:metaxml xmlns="http://www.riik.ee/schemas/dhl/rkel_letter">'

#         nimi = saaja.get('nimi') or ''
#         try:
#             eesnimi, perenimi = nimi.rsplit(' ', 1)
#         except:
#             eesnimi = ''
#             perenimi = nimi
#         buf += '<Addressees>'
#         buf += '<Addressee>'
#         buf += '<Organisation>'
#         buf += '<organisationName>%s</organisationName>' % (saaja.get('asutuse_nimi') or '')
#         buf += '<departmentName>%s</departmentName>' % (saaja.get('osakonna_nimi') or '')
#         buf += '</Organisation>'
#         buf += '<Person>'
#         buf += '<Firstname>%s</Firstname>' % (eesnimi)
#         buf += '<Surname>%s</Surname>' % (perenimi)
#         buf += '<JobTitle>%s</JobTitle>' % (saaja.get('ametikoha_nimetus') or '')
#         buf += '<Email>%s</Email>' % (saaja.get('epost') or '')
#         buf += '<Telephone>%s</Telephone>' % (saaja.get('telefon') or '')
#         buf += '</Person>'
#         buf += '</Addressee>'
#         buf += '</Addressees>'

#         nimi = saaja.get('nimi') or ''
#         try:
#             eesnimi, perenimi = nimi.rsplit(' ', 1)
#         except:
#             eesnimi = ''
#             perenimi = nimi

#         buf += '<Author>'
#         buf += '<Organisation>'
#         buf += '<organisationName>%s</organisationName>' % (saatja.get('asutuse_nimi') or '')
#         buf += '<departmentName>%s</departmentName>' % (saatja.get('osakonna_nimi') or '')
#         buf += '</Organisation>'
#         buf += '<Person>'
#         buf += '<Firstname>%s</Firstname>' % (eesnimi)
#         buf += '<Surname>%s</Surname>' % (perenimi)
#         buf += '<JobTitle>%s</JobTitle>' % (saatja.get('amet') or '')
#         buf += '<Email>%s</Email>' % (saatja.get('epost') or '')
#         buf += '<Telephone>%s</Telephone>' % (saatja.get('telefon') or '')
#         buf += '</Person>'
#         buf += '</Author>'

#         # buf += '<Signatures>'
#         # for (aeg, perenimi, eesnimi, isikukood, ametnik) in allkirjad:
#         #     buf += '<Signature>'
#         #     buf += '<Person>'
#         #     buf += '<Firstname>%s</Firstname>' % (eesnimi)
#         #     buf += '<Surname>%s</Surname>' % (perenimi)
#         #     buf += '<JobTitle>%s</JobTitle>' % (ametnik and ametnik.ametinimetus or '')
#         #     buf += '<Email>%s</Email>' % (ametnik and ametnik.epost or '')
#         #     buf += '<Telephone>%s</Telephone>' % (ametnik and ametnik.telefon or '')
#         #     buf += '</Person>'
#         #     if aeg:
#         #         kpv, kell = aeg.split('T', 1)
#         #         buf += '<SignatureData>'
#         #         buf += '<SignatureDate>%s</SignatureDate>' % (kpv)
#         #         buf += '<SignatureTime>%s</SignatureTime>' % (kell)
#         #         buf += '</SignatureData>'
#         #     buf += '</Signature>'
#         # buf += '</Signatures>'

#         buf += '<Compilators>'
#         buf += '<Compilator>'
#         buf += '<Firstname>%s</Firstname>' % (eesnimi)
#         buf += '<Surname>%s</Surname>' % (perenimi)
#         buf += '<JobTitle>%s</JobTitle>' % (saatja.get('amet') or '')
#         buf += '<Email>%s</Email>' % (saatja.get('epost') or '')
#         buf += '<Telephone>%s</Telephone>' % (saatja.get('telefon') or '')
#         buf += '</Compilator>'
#         buf += '</Compilators>'
                    
#         buf += '<LetterMetaData>'
#         buf += '<SignDate>%s</SignDate>' % (_xsdate(date.today()))
#         #buf += '<SenderIdentifier>%s</SenderIdentifier>' % (dokument.reg_nr)
#         buf += '<Type>%s</Type>' % ('vaideavaldus')
#         buf += '<Language>eesti</Language>'
#         buf += '<Title>Vaideavaldus</Title>'

#         buf += '<Enclosures>'
#         buf += '<EnclosureTitle>vaideavaldus</EnclosureTitle>'
#         buf += '</Enclosures>'
            
#         # if dokument.juurdepaas_kood == Dokument.Juurdepaas.ASUTUS:
#         #     buf += '<AccessRights>'
#         #     buf += '<Restriction>%s</Restriction>' % (dokument.juurdepaas_nimi)
#         #     buf += '<BeginDate>%s</BeginDate>' % (_xsdate(dokument.kuupaev))
#         #     buf += '<EndDate>%s</EndDate>' % (_xsdate(dokument.piirangulopp))
#         #     alused = [r.piirangualus_nimi for r in dokument.piirangualused]
#         #     buf += '<Reason>%s</Reason>' % (', '.join(alused))
#         #     buf += '</AccessRights>'

#         arhiivis = 'false'
#         buf += '<SenderVitalRecordIndicator>%s</SenderVitalRecordIndicator>' % (arhiivis)
#         buf += '</LetterMetaData>'
#         buf += '</dhl:metaxml>'
#         return buf
    
#     def _gen_transport(self, saatja, saaja):
#         buf = '<dhl:transport>'
#         aadress_keys = ('regnr',
#                         'isikukood',
#                         'ametikoha_kood',
#                         'ametikoha_nimetus',
#                         'allyksuse_kood',
#                         'allyksuse_nimetus',
#                         'epost',
#                         'nimi',
#                         'asutuse_nimi',
#                         'osakonna_kood',
#                         'osakonna_nimi')

#         buf += '<dhl:saatja>'
#         for key in aadress_keys:
#             if key in saatja:
#                 buf += '<dhl:%s>%s</dhl:%s>' % (key, saatja[key], key)
#         buf += '</dhl:saatja>'

#         buf += '<dhl:saaja>'
#         for key in aadress_keys:
#             if key in saaja:
#                 buf += '<dhl:%s>%s</dhl:%s>' % (key, saaja[key], key)        
#         buf += '</dhl:saaja>'

#         buf += '</dhl:transport>'
#         return buf

#     def _gen_failid(self, file_data, fn):
#         # DVK-s kasutatakse failide jaoks DIGIDOC konteinerit (<SignedDoc>),
#         # aga isegi kui meie fail juba on ise DIGIDOC konteiner, siis tuleb
#         # selle ümber luua ikkagi veel teine konteiner, kuna DVK ei suuda
#         # reavahetusi säilitada ja muudab sellega konteineris olevad allkirjad kehtetuks

#         # # Loome digidociga tegeleva objekti
#         # ddoc = Ddoc(self.settings or {})
#         # # koostame DVK jaoks eraldi DDOCi
#         # fn_dvk_ddoc = ddoc.create(file_data, fn, mime_type='application/octet-stream')
#         # dvk_data = ddoc.read_output(fn_dvk_ddoc)
#         # ddoc.clean()

#         # # eemaldame XML-faili algusest XML deklaratsiooni
#         # dvk_data = dvk_data[dvk_data.find('?>')+2:]
#         # return dvk_data
    
#         buf = '<SignedDoc format="DIGIDOC-XML" version="1.3" xmlns="http://www.sk.ee/DigiDoc/v1.3.0#">'
#         filesize = len(file_data)
#         filetype = 'application/octet-stream'
#         buf += '<DataFile ContentType="EMBEDDED_BASE64" Filename="%s" Id="D%d" MimeType="%s" Size="%d">' %\
#                (fn, 0, filetype, filesize)
#         buf += file_data.encode('base64')
#         buf += '</DataFile>'
#         buf += '</SignedDoc>'
#         return buf

# def _xsdate(value):
#     return value and value.strftime('%Y-%m-%d') or ''

# def _xstime(value):
#     return value and value.strftime('%H:%M:%S') or ''

# if __name__ == '__main__':
#     import logging
#     logging.basicConfig(level=logging.DEBUG)
#     from eis.scripts.scriptuser import *
#     reg = Dhl(settings=registry.settings, userId='EE30101010007')
#     try:
#         soap_li = reg.allowedMethods()
#         #fn = 'test.ddoc'
#         #f = open(fn, 'r')
#         #file_data = f.read()
#         #f.close()
#         #res = reg.sendDocuments_vaie(file_data, fn)
#     except SoapFault as e:
#         print(e.faultstring)
#     else:
#         li = [str(item) for item in list(soap_li)]
#         #li.sort()
#         for item in li:
#             print(item)
            
