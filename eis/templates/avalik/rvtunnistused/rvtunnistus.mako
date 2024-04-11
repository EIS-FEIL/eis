## -*- coding: utf-8 -*- 
## $Id: rvtunnistus.mako 9 2015-06-30 06:34:46Z ahti $         
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Rahvusvahelise eksami tunnistus")} | ${c.item.tunnistus.kasutaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Rahvusvaheliste eksamite tunnistused'), h.url('otsing_rvtunnistused'))}
${h.crumb_sep()}
${h.crumb(c.item.tunnistus.kasutaja.nimi, h.url('otsing_rvtunnistus', id=c.item.id))}
</%def>

<%include file="/ekk/otsingud/rvtunnistus.sisu.mako"/>

${h.btn_to(_('Tagasi'), h.url('otsing_rvtunnistused'))}
