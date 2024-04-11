<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eksamitunnistused")} | ${c.item.rveksam.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Eksamitunnistused'), h.url('tunnistused'))}
${h.crumb_sep()}
${h.crumb(c.item.rveksam.nimi, h.url('tunnistused_rvtunnistus', id=c.item.id))}
</%def>

<%include file="/ekk/otsingud/rvtunnistus.sisu.mako"/>

${h.btn_to(_('Tagasi'), h.url('tunnistused'))}
