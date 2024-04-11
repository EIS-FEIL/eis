"""
Base class of a X-road SOAP client
Author: Ahti Kelder
"""

import string
from random import Random
import os
import httplib2
import socket
from datetime import datetime
import re
import stat
from lxml import etree
from lxml.builder import ElementMaker

import logging
log = logging.getLogger(__name__)

from .xutils import (
    NS,
    E,
    SoapFault,
    get_text,
    get_int,
    get_boolean,
    outer_xml,
    tree_to_xresult,
    make_log_day_path,
    )

from . import attachment

# X-road protocol version
XVER4 = 4

class XroadClient(object):
    security_server = None # security server IP (may be with :port)
    security_server_uri = '/cgi-bin/consumer_proxy' 
    userId = None # user ID value in SOAP header
    handler = None # view handler
    producer = None # data provider ID (used in configuration)
    namespace = None # data provider's namespace
    settings = {} # configuration settings
    xver = XVER4 # X-road protocol version

    _consumer = None # X-road 3.1 <consumer> header value
    _producer = None # X-road 3.1 <producer> header value
    _caller = {} # X-road 4.0 <client> header values
    _service = {} # X-road 4.0 <service> header values
    xml_response = None # response XML
    
    def __init__(self, handler=None, security_server=None, userId=None, settings=None):
        """
        Parameters:
        handler - view handler (to obtain settings from)
        security_server - HOST or HOST:PORT
        userId - user ID with country prefix (ISO2)
        settings - config settings dict; if missing, will be obtained from handler
        """
        if handler:
            self.handler = handler
            if not settings:
                settings = handler.request.registry.settings
            
        if settings:
            self.settings = settings

            db = self.producer

            self._caller = self._get_client_data(db)
            self._service = self._get_server_data(db)
            self._consumer = self._get_setting('consumer', db)
            self._producer = self._get_setting('producer', db) or db           
            
            self.security_server = self._get_setting('security_server', db)
            self.security_server_uri = self._get_setting('security_server_uri', db) or \
                                       self.security_server_uri

            self.key = self._get_setting('key', db)
            self.cert = self._get_setting('cert', db)
            self.http_proxy = self._get_setting('http_proxy', db) or None
            self.log_dir = self._get_setting('log_dir', db)
        else:
            self.security_server = security_server
        self.userId = userId

    def _get_client_data(self, db):
        # consumer's data in header
        value = self._get_setting('client', db)
        try:
            xRoadInstance, memberClass, memberCode, subsystemCode = value.split('/')
        except:
            log.error('conf error client %s' % db)
            raise
        else:
            return dict(
                xRoadInstance = xRoadInstance,
                memberClass = memberClass,
                memberCode = memberCode,
                subsystemCode = subsystemCode
                )
    
    def _get_server_data(self, db):
        # provider's data in header
        value = self._get_setting('server', db)
        try:
            xRoadInstance, memberClass, memberCode, subsystemCode = value.split('/')
        except:
            log.error('conf error server %s' % db)
            raise
        else:
            return dict(
                xRoadInstance = xRoadInstance,
                memberClass = memberClass,
                memberCode = memberCode,
                subsystemCode = subsystemCode
                )
        
    def _get_db_setting(self, key, db):
        return self.settings.get('xroad.%s.%s' % (key, db))

    def _get_setting(self, key, db):
        value = self._get_db_setting(key, db)
        if not value:
            value = self.settings.get('xroad.%s' % key)
        return value

    def allowedMethods(self):
        "Ask list of permitted services"
        list_path = ['/service']
        res = self.call('allowedMethods.v1', E.allowedMethods(), list_path)
        items = res and res.service or []
        return items

    def listMethods(self):
        "Ask list of services"
        list_path = ['/service']
        res = self.call('listMethods.v1', E.listMethods(), list_path)
        items = res and res.service or []
        return items

    def getWsdl(self, service, version):
        "Get WSDL (not yet implemented)"
        params = E.getWsdl(E.serviceCode(service),
                           E.serviceVersion(version))
        res = self.call('getWsdl', params, [])
        return res
    
    def call(self, service_name, params, list_path, service_version=None, attachments=[], timeout=None):
        """
        Call X-road service
        - service_name - short name of service
        - params - input parameters as XML object
        """

        self.xml_response = ''
        self.response_attachments = []        
        try:
            service_name, version = service_name.split('.')
        except:
            version = service_version or 'v1'

        if service_name in ('allowedMethods','listMethods','getWsdl'):
            # meta service belongs to X-road namespace
            ns = NS.XROAD4
        else:
            # data service belongs to data provider's own namespace
            ns = self.namespace
            if not ns:
                raise Exception("Namespace not defined ({s})".format(s=self.producer))
            
        # generate SOAP envelope
        xml_request = self._gen_envelope(service_name, params, version, ns)
        try:
            # execute call
            xml_response = self.send_xml(service_name, xml_request, attachments, ns, timeout)
            return self.parse_response(xml_response, list_path)
        except Exception as e:
            return self.on_fault(e, service_name)

    def fault_text(self, e, service_name):
        buf = f'X-road error: {e} ({self.producer}, {service_name})'
        if isinstance(e, SoapFault):
            buf += '\n' + e.faultstring
        buf += '\nSecurity server: %s' % (self.security_server) +\
              '\n\n' + self.xml_response +\
              '\n\nInput:\n' + self.xml_request
        return buf
    
    def on_fault(self, e, service_name):
        buf = self.fault_text(e, service_name)
        log.error(buf)
        #print(self.xml_response)
        err = 'X-tee päring ei toimi (%s: %s)' % (self.producer, e.faultstring)
        raise SoapFault(None, err)

    def parse_response(self, xml_response, list_path):
        """Parse XML response and
        return contents of the Body as Xresult object
        or raise SoapFault
        """
        # create XML object for response envelope and find Body element
        root = etree.fromstring(xml_response.encode('utf-8')) 
        body = root.find(NS._SOAPENV+'Body')
        if body is not None:
            # detect SOAP fault message
            response = body.find('*')
            if response.tag == NS._SOAPENV+'Fault':
                try:
                    detail = response.find('detail').find('message').text
                except:
                    detail = None
                raise SoapFault(response.find('faultcode').text,
                                response.find('faultstring').text,
                                detail)

            if response is not None:
                # convert XML to dict
                return tree_to_xresult(response, '', list_path)

    def send_xml(self, service_name, xml, attachments=[], namespace=None, timeout=None):
        "Send input message to security server and receive output message"

        args = {}
        prot = 'http'

        # SOAP server URL (at security server)
        url = '%s://%s%s' % (prot, self.security_server, self.security_server_uri)
        
        self.xml_request = xml
        self._trace_msg(service_name, 'in', xml)

        # compose HTTP message
        payload, headers, body = attachment.encode_soap(self.xml_request, attachments)

        call_started = datetime.now()
        # send message
        response = self._send_http(url, body, headers, timeout)
        duration = (datetime.now() - call_started).total_seconds()

        # decode envelope and attachments
        self.xml_response, self.response_attachments = attachment.decode(response)
        self._trace_msg(service_name, 'out', self.xml_response, duration)
        log.debug('REQUEST:\n%s\nRESPONSE:\n%s\n' % (self.xml_request, self.xml_response))

        return self.xml_response

    def _send_http(self, url, xml, headers, timeout=None):
        "Send message over HTTP"
        args = {}
        if self.http_proxy:
            m = re.match(r'.*/(.+):(\d+)$', self.http_proxy)
            proxy_host, proxy_port = m.groups()
            proxy_port = int(proxy_port)
            args['proxy_info'] = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_HTTP, proxy_host, proxy_port)
        if timeout:
            args['timeout'] = timeout
        http = httplib2.Http(**args)
        response, response_body = http.request(url, "POST", body=xml, headers=headers)

        # reconstruct whole message for MIME parsing later
        buf = ''
        for key, value in response.items():
            buf += '%s: %s\r\n' % (key, value)

        response = buf.encode('utf-8') + b'\r\n' + response_body
        return response

    def _gen_envelope(self, service_name, params, service_version, namespace):
        "Compose SOAP envelope"
        # params is SOAP doc/literal wrapper element and must be named by name of the service
        params.tag = '{%s}%s' % (namespace, service_name) 
        if service_name == 'getWsdl':
            # add namespace for all descendants
            for node in params.iterdescendants():
                node.tag = '{%s}%s' % (namespace, node.tag)
        nsmap = {'soap': NS.SOAP11,
                 'soapenc': NS.SOAPENC,
                 'xsi': NS.XSI,
                 'xsd': NS.XSD,
                 'a': namespace
                 }
        nsmap['xrd'] = NS.XROAD4
        nsmap['id'] = NS.XROAD4ID
            
        e = ElementMaker(namespace=NS.SOAP11, nsmap=nsmap)
        header = self._gen_header(service_name, service_version)
        envelope = e.Envelope(header, e.Body(params))
        return outer_xml(envelope, True)

    def _gen_header(self, service_name, service_version): 
        "Compose SOAP header"
        soap = ElementMaker(namespace=NS.SOAP11)
        xrd = ElementMaker(namespace=NS.XROAD4)
        xid = ElementMaker(namespace=NS.XROAD4ID)

        c = self._caller
        client = xrd.client(xid.xRoadInstance(c['xRoadInstance']),
                            xid.memberClass(c['memberClass']),
                            xid.memberCode(c['memberCode']),
                            xid.subsystemCode(c['subsystemCode']))
        client.set('{%s}objectType' % NS.XROAD4ID, 'SUBSYSTEM')

        s = self._service
        service = xrd.service(xid.xRoadInstance(s['xRoadInstance']),
                              xid.memberClass(s['memberClass']),
                              xid.memberCode(s['memberCode']),
                              xid.subsystemCode(s['subsystemCode']),
                              xid.serviceCode(service_name),
                              xid.serviceVersion(service_version))
        service.set('{%s}objectType' % NS.XROAD4ID, 'SERVICE')

        header = soap.Header(client, service)
        if self.userId:
            header.append(xrd.userId(self.userId))
        header.append(xrd.id(self._gen_nonce()))
        header.append(xrd.protocolVersion('4.0'))

        return header
        
    def _gen_nonce(self):
        "Generate unique id for service call"
        return ''.join(Random().sample(string.ascii_letters+string.digits, 32))
   
    def _trace_msg(self, method, ext, data, duration=None):
        "Log input and output messages"
        if self.log_dir:
            prefix = make_log_day_path(self.log_dir)
            fn = '%s.%s.%s.%s.xml' % (prefix, self.producer, method, ext)
            with open(fn, 'w') as file:
                file.write(data)
            os.chmod(fn, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

