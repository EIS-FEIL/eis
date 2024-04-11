## Valitud nimekirja andmed

<%inherit file="/common/page.mako"/>
<%namespace name="tab" file='/common/tab.mako'/>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="page_title()">
${_("Registreerimisnimekiri")}. ${c.test.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi sooritajate määramine"), h.url('nimekirjad_testimiskorrad'))} 
${h.crumb('%s %s' % (c.test.nimi, c.testimiskord.tahised), h.url('nimekirjad_testimiskord_korrasooritajad',testimiskord_id=c.testimiskord.id))} 
</%def>

<h1>${_("Testi sooritajate määramine")}</h1>

<% 
   c.can_update = c.user.has_permission('nimekirjad', const.BT_UPDATE, c.testimiskord)
%>
<%include file="nimekirjad.testimiskord.mako"/>

% if c.on_vvkoht:
${h.form_search(None)}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-6 col-lg-5">
      <div class="form-group">    
        ${h.radio('kand', '0', checked=c.kand!='1',
        label=_('Minu kooli õpilased'))}
        ${h.radio('kand', '1', checked=c.kand=='1',
        label=_('Minu kooli kandideerivad'))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">    
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("CSV"), id="csv", level=2)}        
      </div>
    </div>
  </div>
</div>
${h.end_form()}
% endif

<div class="listdiv" width="100%">
  <%include file="sooritajad_list.mako"/>
</div>

% if c.can_update and c.kand != '1' and not c.testimiskord.reg_kohavalik:

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${_("Lisa sooritajad")}:
    ${h.btn_to_dlg(_("Isikukoodiga"),
    h.url('nimekiri_isikud', testimiskord_id=c.testimiskord_id, sub='ik'), title=_("Sooritaja lisamine"), width=700, level=1, mdicls='mdi-plus')}
    % if c.user.koht_id and c.user.has_permission('klass', const.BT_UPDATE, obj=c.user.koht):
    ${h.btn_to_dlg(request.is_ext() and _("EHISest") or _("klassi järgi"), h.url('nimekiri_isikud',
    testimiskord_id=c.testimiskord_id, sub='ehis'), title=_("Sooritaja lisamine"),
    width=700, level=1, mdicls='mdi-import')}
    % endif
    ${h.btn_to_dlg(_("Failist"), h.url('nimekiri_isikud',
    testimiskord_id=c.testimiskord_id, sub='fail'), title=_("Sooritaja lisamine"), width=700, level=1, mdicls='mdi-file-import')}
  </div>
</div>
% endif
