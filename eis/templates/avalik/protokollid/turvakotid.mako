## -*- coding: utf-8 -*- 
<%inherit file="/common/formpage.mako"/>

<%def name="page_title()">
${_("Testi toimumise protokollimine")} | ${c.toimumisprotokoll.tahistus}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Testi toimumise protokolli koostamine'), h.url('protokollid'))}
${h.crumb(c.toimumisprotokoll.tahistus, h.url('protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id))}
${h.crumb(_('Turvakotid'))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="/avalik/protokollid/before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="/avalik/protokollid/tabs.mako"/>
</%def>

${h.form_save(None)}

<table class="table table-borderless table-striped tablesorter" width="100%">
  <caption>${_("Testitööde eksamikeskusse saatmise turvakottide numbrid")}</caption>
  <tr>
    <th width="100px">${_("Tagastamine")}</th>
    ${h.th(_('Koti nr'))}
  </tr>
  <% n = 0 %>
  % for pakett in c.toimumisprotokoll.testipaketid:
  % for rcd in pakett.tagastuskotid:
  <tr>
    <td>
      % if rcd.staatus != const.M_STAATUS_TAGASTATUD:
      ${h.checkbox('tk-%d.turvakott_id' % n, rcd.id, checked=rcd.staatus==const.M_STAATUS_TAGASTAMISEL)}
      % endif
    </td>
    <td>
      ${rcd.kotinr}
    </td>
  </tr>
  <% n += 1 %>
  % endfor
  % endfor
</table>
<br/>
% if c.is_edit:
${h.button(_('Vali kõik'),
onclick="$('input[name$=id]').prop('checked',true)")}
${h.submit()}
% endif
${h.end_form()}
