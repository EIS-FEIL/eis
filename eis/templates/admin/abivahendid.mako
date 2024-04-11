<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Abivahendid")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Abivahendid"))}
</%def>
<%def name="require()">
<% c.includes['ckeditor'] = True %>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<div class="p-3 d-flex">
  <div class="flex-grow-1">
    <h1>${_("Ülesande lahendamise abivahendid")}</h1>
    
  </div>
  <div class="text-right">
    ${h.btn_to_dlg(_("Lisa"), h.url('admin_new_abivahend'), level=1, title=_("Uus abivahend"), mdicls='mdi-plus', size='lg')}
  </div>
</div>

${h.form_search()}
<div class="p-2" style="text-align:right">
${_("Tõlkekeel")}: ${h.select('lang', c.lang, c.opt.SOORKEEL, empty=True, style="width:190px", onchange="this.form.submit()")}
</div>
${h.end_form()}
  
<div class="listdiv">
  <%include file="abivahendid_list.mako"/>
</div>
