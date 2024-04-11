## AJUTINE VORM
<%inherit file="/common/page.mako"/>
##<%include file="tabs.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.item.testimiskord.test.nimi} ${h.str_from_date(c.item.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.link_to(u'Korraldamine', h.url('korraldamised'))} 
${h.crumb_sep()}
${c.item.testimiskord.test.nimi} ${h.str_from_date(c.item.alates)} 
</%def>
${h.form_save(c.item.id)}
<div width="100%" class="lightback">
<table width="100%">
<caption>See on ajutine lihtsustatud vorm testide toimumisaegade sidumiseks soorituskohtadega</caption>
  <%
    c.kohad_id = [rcd.koht_id for rcd in c.item.testikohad]
    found = False
  %>
  % for rcd in model.Koht.query.all():
    <% 
       found = True 
     
       testikoht = None
       for rcd2 in c.item.testikohad:
          if rcd2.koht_id == rcd.id:
              testikoht = rcd2
    %>
  <tr>
    <td>${h.checkbox('koht_id', value=rcd.id, checked=testikoht is not None)}</td>
    <td>${rcd.nimi}</td>
    <td>
      % if testikoht:
         ${h.link_to(_("Sooritajad") + ' (%s)' % len(testikoht.sooritused), 
                     h.url('korraldamine_sooritaja', id=testikoht.id))}
      % endif
    </td>
  </tr>
  % endfor
</table>
  % if not found:
${_("Pole sisestatud ühtki soorituskohta")}
  % endif
</div>

% if c.is_edit:
${h.submit()}
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('korraldamine', id=c.item.id), method='get')}
%   endif
% elif c.user.has_permission('ekk-testid', const.BT_UPDATE):
${h.btn_to(_("Muuda"), h.url('edit_korraldamine', id=c.item.id), method='get')}
% endif
${h.btn_back(url=h.url('korraldamised'))}

${h.end_form()}
