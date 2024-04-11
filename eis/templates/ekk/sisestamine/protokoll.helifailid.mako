<%inherit file="/common/formpage.mako"/>

<%def name="page_title()">
${_("Testi toimumise protokollimine")} | ${c.toimumisprotokoll.tahistus}
</%def>      
<%def name="breadcrumbs()">
<%
   if c.toimumisprotokoll.testikoht:
      toimumisaeg_id = c.toimumisprotokoll.testikoht.toimumisaeg_id
   else:
      toimumisaeg_id = None
%>
${h.crumb(_('Testi toimumise protokolli sisestamine'),h.url('sisestamine_protokollid', toimumisaeg_id=toimumisaeg_id, testimiskord_id=c.toimumisprotokoll.testimiskord_id))}
${h.crumb(c.toimumisprotokoll.tahistus, h.url('sisestamine_protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id))}
${h.crumb(_('Helifailid'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>


<%def name="draw_before_tabs()">
<%include file="/ekk/sisestamine/tprotokoll.before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="/ekk/sisestamine/tprotokoll.tabs.mako"/>
</%def>

##${h.form_save(None)}

<table class="table table-borderless table-striped tablesorter" width="100%">
  <caption>${_("Testisoorituste helifailid")}</caption>
  <tr>
    ${h.th(_('Helifail'))}
    ${h.th(_('Sooritajad'))}
    <th>${_("Muuda")}</th>
    <th>${_("Kustuta")}</th>
  </tr>
  % for n, rcd in enumerate(c.items):
  <tr>
    <td>
      ${h.link_to(rcd.filename, h.url('sisestamine_protokoll_helifail',
      toimumisprotokoll_id=c.toimumisprotokoll.id, id='%s.%s' % (rcd.id, rcd.fileext or 'file')))}
    </td>
    <td>
      % for hv in rcd.helivastused:
      ${hv.sooritus.tahis} ${hv.sooritus.sooritaja.kasutaja.nimi}
        % if hv.testiylesanne_id:
          (ül ${hv.testiylesanne.tahis})
        % endif
      <br/>
      % endfor
    </td>
    <td>
      % if c.is_edit:
      ${h.dlg_edit(h.url('sisestamine_protokoll_edit_helifail',
      toimumisprotokoll_id=c.toimumisprotokoll.id, id=rcd.id, partial=True),
      title=_('Faili muutmine'), width=500)}
      % endif
    </td>
    <td>
      % if c.is_edit:
      ${h.remove(h.url('sisestamine_protokoll_delete_helifail', toimumisprotokoll_id=c.toimumisprotokoll.id, id=rcd.id))}
      % endif
    </td>
  </tr>
  % endfor
</table>
<br/>
% if c.is_edit:
${h.btn_to_dlg('Lisa', h.url('sisestamine_protokoll_new_helifail', toimumisprotokoll_id=c.toimumisprotokoll.id, partial=True),
title=_('Faili lisamine'), width=500)}

% endif
