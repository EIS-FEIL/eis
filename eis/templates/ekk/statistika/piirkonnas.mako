<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Piirkondade tulemused")} | ${c.test.nimi}
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Piirkondade tulemused"), h.url('statistika_piirkonnatulemused'))}
${h.crumb(c.test.nimi, h.url_current())}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>

<%include file="piirkonnas.pais.mako"/>
<% c.is_edit = True %>

${h.form_search(url=h.url_current())}
<%include file="piirkonnas.filter.mako"/>
${h.end_form()}

<div class="listdiv">
<%include file="piirkonnas_list.mako"/>
</div>
