${h.form_save(None, h.url('admin_koht_ruumid', koht_id=c.koht.id))}

<div class="form-group row">
  ${h.flb3(_("Ruumide arv"), 'f_ruumidearv')}
  <div class="col">
    ${h.int5('f_ruumidearv', c.koht.ruumidearv)}
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Tavatesti kohtade arv"), 'f_ptestikohti')}
  <div class="col">
    ${h.int5('f_ptestikohti', c.koht.ptestikohti)}
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("E-testi kohtade arv"), 'f_etestikohti')}
  <div class="col">
    ${h.int5('f_etestikohti', c.koht.etestikohti)}
  </div>
</div>

<h3>${_("Ruumide andmed")}</h3>

${h.rqexp()}
<% prefix = 'r' %>
<table class="table table-borderless table-striped tablesorter tablesorter-update" id="choicetbl_${prefix}">
  <thead>
    <tr>
      ${h.th(_("Ruumi tähis"), nowrap=True, rq=True, sorter=c.is_edit and 'inputs' or 'text')}
      ${h.th(_("Kohtade arv"), nowrap=True, sorter=c.is_edit and 'inputs-numeric' or 'digit')}
      ${h.th(_("E-kohtade arv"), nowrap=True, sorter=c.is_edit and 'inputs-numeric' or 'digit')}
      ${h.th(_("Kehtiv"), sorter=c.is_edit and 'checkbox' or 'text')}
      ${h.th(_("Varustus"))}
      ${h.th('', sorter="false", width="20px")}
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.ruum(c.new_item(),prefix,'-%s' % cnt)}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(c.koht.ruumid):
        ${self.ruum(item,prefix,'-%s' % cnt)}
  %   endfor
  % endif
  </tbody>
</table>
% if c.can_edit:
<div id="sample_choicetbl_${prefix}" class="invisible">
<!--
   ${self.ruum(c.new_item(kood='__kood__'),prefix, '__cnt__')}
-->
</div>
% endif

<%def name="ruum(item, baseprefix, cnt)">
## Ühe ruumi rida tabelis
    <% prefix = '%s%s' % (baseprefix, cnt) %>
    <tr>
      <td>${h.text('%s.tahis' % (prefix), item.tahis, size=20, maxlength=20)}</td>
      <td>${h.int5('%s.ptestikohti' % (prefix), item.ptestikohti)}</td>
      <td>${h.int5('%s.etestikohti' % (prefix), item.etestikohti)}</td>
      <td>${h.checkbox1('%s.staatus' % prefix, checked=not(item.staatus == False))}</td>
      <td>${h.text('%s.varustus' % (prefix), item.varustus)}</td>      
      <td>
        % if c.is_edit and not item.in_use:
        ${h.grid_remove()}
        % endif
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
    </tr>
</%def>

<div class="d-flex flex-wrap">
% if c.can_edit:
${h.button(_("Lisa"), onclick=f"grid_addrow('choicetbl_{prefix}');", level=2, mdicls='mdi-plus')}
% endif
<div class="flex-grow-1 text-right">
% if c.is_edit:
${h.submit()}
% elif c.can_edit:
${h.btn_to(_("Muuda"), h.url('admin_koht_new_ruum', koht_id=c.koht.id), method='get')}
% endif
</div>
</div>

${h.end_form()}
