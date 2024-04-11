<%inherit file="/common/page.mako"/>
<%def name="require()">
<% c.includes['ckeditor'] = True %>
</%def>
<%def name="page_title()">
${_("Klassifikaatorid")} | ${c.item.nimi}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Klassifikaatorid"), h.url('admin_klassifikaatorid', lang=c.lang))} 
${h.crumb(c.item.nimi, h.url('admin_edit_klassifikaator', id=c.item.kood))}
${h.crumb(_("Klassifikaatorite vastavus"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${c.item.nimi}</h1>

${h.form_save(c.item.kood)}

<%
  if c.kl2 == 'OPIAINE':
     c.opt_vaste = c.opt.klread_id('OPIAINE')
  elif c.kl2 == 'EHIS_AINE':
     c.opt_vaste = c.opt.klread_id('EHIS_AINE')
  else:
     c.opt_vaste = []
%>
<table class="table table-striped tablesorter"  width="100%">
  <thead>
    <tr>
      ${h.th(_("EISi klassifikaator"))}
      % if c.kl2 == 'OPIAINE':
      ${h.th(_("oppekava.edu.ee vaste"))}
      % elif c.kl2 == 'EHIS_AINE':
      ${h.th(_("EHISe vaste"))}
      % endif
    </tr>
  </thead>
  <tbody>
    % for ind, klv in enumerate(c.items):
    <tr>
      <td>${klv.nimi}</td>
      <td>
        <%
          prefix = 'klv-%d' % ind
          selected_id = [v.ehis_klrida_id for v in klv.eis_klvastavused if v.ehis_kl == c.kl2]
        %>
        ${h.select2(prefix + '.vaste_id', selected_id, c.opt_vaste, multiple=True)}
        ${h.hidden(prefix + '.id', klv.id)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>

% if c.is_edit:
${h.submit()}
% endif
${h.end_form()}
