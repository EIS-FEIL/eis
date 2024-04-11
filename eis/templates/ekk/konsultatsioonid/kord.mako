<%inherit file="korrad.mako"/>
<%def name="require()">
<%
c.includes[ 'jstree'] = True
%>
</%def>
<% c.toimumisaeg = c.item.id and c.item.toimumisajad[0] or c.new_item() %>
${h.form_save(c.item.id)}
<h2>${_("Konsultatsiooni toimumiskorra andmed")}</h2>
${h.rqexp()}
<% ch = h.colHelper('col-md-4','col-md-8') %>
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${ch.flb(_("Konsultatsiooni toimumiskorra tähis"), rq=True)}
    <div class="col-md-4">
      ${h.text('f_tahis', c.item.tahis, maxlength=10, size=11, pattern='[0-9a-zA-Z]*')}
    </div>
    <div class="col text-right">
      ${h.link_to(_('Korraldamine'), h.url('korraldamine_soorituskohad',
      toimumisaeg_id=c.toimumisaeg.id))}
    </div>
  </div>

  <h3>${_("Ajad")}</h3>
  <div class="p-2 mb-3 border border-base-radius">  
    <div class="form-group row">
      ${ch.flb(_("Testisessioon"))}
      <div class="col">
        ${h.select('f_testsessioon_id', c.item.testsessioon_id,
        model.Testsessioon.get_opt(c.test.testiliik_kood), empty=True)}
      </div>
    </div>
    
    <div class="form-group row">
      <div class="col-12">
        ${self.toimumispaevad(c.toimumisaeg.toimumispaevad, 'tpv')}
      </div>
    </div>
  </div>

  % if c.item.id:
  <h3>${_("Lisavalikud")}</h3>
  <div class="p-2 mb-3 border border-base-radius">
    <div class="form-group row">
      ${ch.flb(_("Soorituspiirkonnad"))}
      <div class="col">
        ${', '.join(rcd.nimi for rcd in c.item.piirkonnad)}
        % if c.can_update:
        ${h.btn_to_dlg(_('Muuda'), h.url('konsultatsioon_edit_kord', test_id=c.test.id,
        id=c.item.id, sub='prk', partial=True), title=_('Piirkonnad'))}
        % endif
      </div>
    </div>
    <div class="form-group row">
      ${ch.flb(_("Testid"))}
      <div class="col">
        <table class="table" >      
          <col width="80"/>
          <col/>
          % for r in c.item.eksamikorrad:
          <tr>
            <td>
              <% tkord = r.eksam_testimiskord %>
              ${h.link_to(tkord.tahised, h.url('test_edit_kord', test_id=tkord.test_id, id=tkord.id))}
            </td>
            <td>${tkord.test.nimi}</td>
          </tr>
          % endfor
        </table>
        % if c.can_update:
        ${h.btn_to_dlg(_('Muuda'), h.url('konsultatsioon_edit_kord', test_id=c.test.id,
        id=c.item.id, sub='eksam', partial=True), title=_('Testid'), width=500)}
        % endif
      </div>
    </div>
  </div>
  % endif

  <h3>${_("Läbiviijad")}</h3>  
  <div class="p-2 mb-3 border border-base-radius">
    <div class="form-group row">
      ${ch.flb(_("Konsultandi koolituse varaseim lubatud kuupäev"))}
      <div class="col">
        ${h.date_field('ta_konsultant_koolituskp', c.toimumisaeg.konsultant_koolituskp, wide=False)}
      </div>
    </div>
  </div>

  <h3>${_("Töötasud")}</h3>
  <div class="p-2 mb-3 border border-base-radius">  
    <div class="form-group row">
      ${ch.flb(_("Konsultandi tasu"))}
      <div class="col">
        ${h.money('ta_konsultant_tasu', c.toimumisaeg.konsultant_tasu)} €
      </div>
    </div>
  </div>

  % if c.item.on_mall or c.is_edit:
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('f_on_mall', 1, checked=c.item.on_mall, label=_("Kasutusel toimumiskordade loomise mallina"))}
    </div>
  </div>
  <div class="form-group row trmall">
    ${ch.flb(_("Malli nimetus"))}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi, max=256)}
    </div>
  </div>
</div>
<script>
  $('#f_on_mall').click(function(){
  $('.trmall').toggle($('#f_on_mall').prop('checked'));
  });
  $('.trmall').toggle($('#f_on_mall').prop('checked'));
</script>

% endif

${h.end_form()}

<%def name="buttons()">
% if c.item and c.item.id:
% if c.user.has_permission('konsultatsioonid', const.BT_UPDATE):
${h.btn_to(_("Kopeeri"), h.url('konsultatsioon_new_kord', test_id=c.test.id,
id=c.item.id), level=2)}
% endif
% endif

% if c.can_update:
% if c.is_edit:
${h.submit(out_form=True)}
% elif c.item.id:
${h.btn_to(_('Muuda'), h.url('konsultatsioon_edit_kord', test_id=c.test.id,
id=c.item.id))}
% endif
% endif

</%def>


<%def name="row_toimumispaev(item, prefix)">
    <tr>
      <td>
        ${h.date_field('%s.kuupaev' % prefix, item.aeg, wide=False)}
      </td>
      <td>
        ${h.time('%s.kell' % prefix, item.aeg, default='10:00', wide=False)}
      </td>
      <td>
        % if c.can_update and c.is_edit:
        ${h.grid_remove()}
        % endif
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
    </tr>
</%def>

<%def name="toimumispaevad(choices, prefix)">
<table id="tbl_${prefix}" class="t1able" > 
  <thead>
    <tr>
      ${h.th(_("Toimumise kuupäev"), rq=True)}
      ${h.th(_("Alguse kellaaeg"))}
      <th>
      % if c.is_edit:
      ${h.button(_('Lisa'), onclick="grid_addrow('tbl_tpv')", class_="px-3")}
      % endif
      </th>
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or [0]:
        ${self.row_toimumispaev(c.new_item(),'%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
    <%
    if len(choices) == 0:
       ## alati peab vähemalt yks kuupäev olemas olema
       choices = [c.new_item()]
    %>
  %   for cnt,item in enumerate(choices):
        ${self.row_toimumispaev(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
</table>
% if c.is_edit:
<div id="sample_tbl_${prefix}" class="invisible">
<!--
   ${self.row_toimumispaev(c.new_item(),'%s__cnt__' % prefix)}
-->
</div>
% endif
</%def>
