## -*- coding: utf-8 -*- 
<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.item.nimi} | ${_("Kasutamise ajalugu")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Minu töölaud"), h.url('tookogumikud'))}
${h.crumb(c.item.nimi or c.item.id, h.url('ylesanne', id=c.item.id))} 
${h.crumb(_("Kasutamise ajalugu"))}
</%def>

<div class="listdiv">
<%include file="testid_list.mako"/>
</div>
