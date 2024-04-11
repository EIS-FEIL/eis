<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="skannid.tabs.mako"/>
</%def>
<%def name="page_title()">
${_("Taotluse esitamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Skannitud eksamitööd"), h.url('muud_skannid_taotlemised'))}
${h.crumb(_("Taotluse esitamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-md-4">
      ${h.flb(_("Testsessioon"), 'sessioon_id')}
      ${h.select('sessioon_id', c.sessioon_id, c.opt_sessioon)}
      <script>
        $('#sessioon_id').change(function(){ this.form.submit(); });
      </script>
    </div>
  </div>
</div>
${h.end_form()}

${h.form_save(None)}
${h.hidden('sessioon_id', c.sessioon_id)}
<div class="listdiv">
  <%include file="skannid.taotlemised_list.mako"/>
</div>
<br/>
<span class="add invisible">
##${h.btn_to_dlg(_("Muuda taotlemise ajavahemikku"), h.url('muud_skannid_new_taotlemine'), 
##title=_("Tööga tutvumise taotluste esitamise aeg"), width=450, form='$(this.form)', id='taotlemine')}
${h.btn_to_dlg(_("Muuda"), h.url('muud_skannid_new_taotlemine'), 
title=_("Tööga tutvumine"), width=800, form='$(this.form)', id='taotlemine')}
</span>
${h.end_form()}
