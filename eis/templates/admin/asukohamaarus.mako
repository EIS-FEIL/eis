<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Asukohamäärus")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_('Asukohamäärus'), h.url('admin_asukohamaarus'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%
c.can_update = c.user.has_permission('kohad', const.BT_UPDATE)
%>

<h1>${_("Tunnistusel kuvatava eksami sooritamise asukoha käänamine")}</h1>
${h.alert_notice(_('Nende asulate korral, mille nime lõppu tabelist ei leita, kasutatakse seesütlevat käänet (asula nimele lisatakse täht "s").'), False)}

${h.form_save(None, h.url('admin_create_asukohamaarus'))}
<table class="table" id="choicetbl_r">
  <thead>
    <tr>
      <th>${_("Mis (asula nime lõpp)?")}</th>
      <th>${_("Kus?")}</th>
      <th width="20px"></th>
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get('r') or []:
        ${self.row('r-%s' % cnt, c.new_item())}
  %   endfor
  % else:
## tavaline kuva
    % for n,r in enumerate(c.items):
    ${self.row('r-%d' % n, r)}
    % endfor
  % endif
  </tbody>
  % if c.is_edit:
  <tfoot>
    <tr>
      <td colspan="3">
      <div id="sample_choicetbl_r" class="invisible">
        <!--
            ${self.row('r__cnt__', c.new_item())}
          -->
      </div>
      </td>
    </tr>
  </tfoot>
  % endif
</table>

% if c.is_edit:
<div class="d-flex flex-wrap">
  ${h.button(_("Lisa"), onclick="grid_addrow('choicetbl_r');", level=2, mdicls='mdi-plus')}
  <div class="flex-grow-1 text-right">
    ${h.submit()}
  </div>
</div>
% endif

${h.end_form()}

<%def name="row(prefix, r)">
    <tr>
      <td>
        ${h.text('%s.nimetav' % prefix, r.nimetav, maxlength=30)}
      </td>
      <td>${h.text('%s.kohamaarus' % prefix, r.kohamaarus, maxlength=30)}</td>
      <td>
        ${h.grid_remove()}
        ${h.hidden('%s.id' % prefix, r.id)}
      </td>
    </tr>
</%def>
