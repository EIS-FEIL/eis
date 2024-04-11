% if not c.ylesanne.arvutihinnatav:
${h.alert_error(_("Ülesanne ei ole arvutihinnatav."))}
% endif

% if c.is_edit or c.is_tr:
${h.form_save(None)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)} 
% endif
<%
  c.opt_tehe = model.Nptagasiside.opt_tehe()
  np = c.new_item()
  for np in c.ylesanne.normipunktid:
      break
  prefix = 'np'
  grid_npts = 'tbl_%s_npts' % prefix  
%>

<table width="100%"  class="table">
${self.normipunkt_diag(np, prefix)}
</table>

<br/>

${_("Ülesande kommentaar")}
<table width="100%"  class="table">
  <tr>
    <td style="position:relative">     
      ${self.tran_editable('yl_tagasiside', c.ylesanne, 'f_')}
    </td>
  </tr>
</table>

% if c.is_edit or c.is_tr:
% if c.is_edit:
${h.button(_("Lisa"), class_="addnpts", 
onclick=f"grid_addrow('{grid_npts}',null,null,false,null,'npts');on_addrow_npts('{grid_npts}');", level=2, mdicls='mdi-plus')}
${h.button(_("Genereeri vahemikud..."), id='op_gen',
      onclick="dialog_el($('#gendlg'), '%s', 300);" % (_("Genereeri vahemikud...")), level=2)}
% endif
${h.submit()}

<div id="gendlg" style="display:none">
  <table class="table">
    <col width="80"/>
    <tr>
      <td class="frh">${_("Samm")}</td>
      <td>${h.posfloat('d_step', '')}</td>
    </tr>
    <tr>
      <td class="frh">${_("Tehe")}</td>
      <td>
        ${h.select('d_tehe', c.opt_tehe[0], c.opt_tehe)}
      </td>
    </tr>
  </table>
  <br/>
  ${h.button(_("Genereeri"), onclick="gen_ranges(this)", level=2)}
</div>
##${h.hidden('g_tehe', '')}
##${h.hidden('g_step', '')}
${h.end_form()}
<script>
<%include file="tagasiside.js"/>
</script>
<div style="height:0">
<div id="np_ckeditor_top" class="ckeditor-top-float"></div>
</div>
% endif

<%def name="normipunkt_diag(item, prefix)">
<%
  opt_normityyp = c.opt.normityyp_diag2
  errprefix = 'np%s' % item.id
%>
  <col width="120"/>
  <col/>
  <tr>
    <td class="frh">${_("Võrreldav väärtus")}</td>
    <td>
      <%
        #opt_kood, c.valikud = request.handler._get_valik(item.testiylesanne_id)
        opt_normikood = [(const.NORMITYYP_PROTSENT, _("Punktid protsentides")),
                         (const.NORMITYYP_PALLID, _("Punktid"))]# + opt_kood
        if item.normityyp in (const.NORMITYYP_PROTSENT, const.NORMITYYP_PALLID):
           normikood = item.normityyp
        #elif item.kysimus_kood:
        #   normikood = item.kysimus_kood
        else:
           normikood = None
      %>
##      % if c.is_edit:
##      <script>
##        var choices = ${model.json.dumps(c.valikud)};
##      </script>
##      % endif
      ${h.select('%s.normikood' % prefix, normikood, opt_normikood, class_='normikood', wide=False)}
      % if c.is_tr:
      ${h.hidden('%s.normikood' % prefix, normikood)}
      % endif
      <%
        prefix_npts = '%s.npts' % prefix
        grid_npts = 'tbl_%s_npts' % prefix
      %>
      ${self.errpos(errprefix + '.normikood')}      
    </td>
    <td>
      ${h.checkbox('kuva_tulemus', 1, checked=c.ylesanne.kuva_tulemus != False,
      label=_("Kuva ülesande tulemus"))}
    </td>
  </tr>
  <tr>
    <td colspan="3" valign="top">
      ${self.errpos(errprefix + '.id')}
      ${self.nptagasisided(item, prefix_npts, grid_npts)}
##      % if c.is_edit:
##      ${h.checkbox('set_default_range', 1, label=_("Kasuta samu vahemikke edaspidi vaikimisi vahemikena"))}
##      % endif
    </td>
  </tr>
</%def>              

<%def name="nptagasisided(normipunkt, prefix, grid_id)">
<%
  rows = list(normipunkt.nptagasisided)
%>
% if c.is_edit or c.is_tr:
<table width="100%"  id="${grid_id}" class="table table-borderless table-striped nptagasisided">
% else:
<table width="100%"  class="table table-borderless table-striped">
% endif
  <col width="60px"/>
  <col width="80px"/>
  <col/>
  <col width="30px"/>
  <thead>
    <tr>
      ${h.th(_("Tingimus"), colspan=2)}
      ${h.th(_("Tagasiside"))}
      % if c.is_edit:
      <th></th>
      % endif
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_nptagasiside(c.new_item(), '%s-%s' % (prefix, cnt), normipunkt)}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(rows):
        ${self.row_nptagasiside(item, '%s-%s' % (prefix, cnt), normipunkt)}
  %   endfor
  %   for cnt in range(len(rows or []), 1):
        ${self.row_nptagasiside(c.new_item(), '%s-%s' % (prefix, cnt), normipunkt)}
  %   endfor
  % endif
  </tbody>
% if c.is_edit:
  <tfoot id="sample_${grid_id}" class="invisible sample">
   ${self.row_nptagasiside(c.new_item(), '%s__cnt__' % prefix, normipunkt)}
  </tfoot>
% endif
</table>
</%def>

<%def name="row_nptagasiside(item, prefix, normipunkt)">
<% errprefix = 'np%s.ns%s' % (normipunkt.id, item.id) %>
<tr>
  % if c.is_edit:
  <td>
    ${h.select('%s.tingimus_tehe' % prefix, item.tingimus_tehe, c.opt_tehe, class_='tingimus_tehe')}
  </td>
  <td>
##    <% opt_valik = c.valikud.get(normipunkt.kysimus_kood) or [] %>
##    ${h.select('%s.tingimus_valik' % prefix, item.tingimus_valik, opt_valik, class_='tingimus_valik')}
    ${h.posfloat('%s.tingimus_vaartus' % prefix, item.tingimus_vaartus, class_='tingimus_vaartus')}
    ${self.errpos(errprefix + '.tingimus_vaartus')}
  </td>
  % else:
  <td colspan="2" class="nowrap">
    ${normipunkt.kysimus_kood or _("Tulemus")}
    ${item.tingimus_tehe_ch}
    % if item.tingimus_valik:
    ${item.tingimus_valik}
    % else:
    ${h.fstr(item.tingimus_vaartus)}
    % if normipunkt.normityyp == const.NORMITYYP_PROTSENT:
    ${'%'}
    % endif
    % endif
    ${self.errpos(errprefix + '.tagasiside')}
    % if c.is_tr:
    ${h.hidden('%s.tingimus_tehe' % prefix, item.tingimus_tehe)}
    ${h.hidden('%s.tingimus_vaartus' % prefix, item.tingimus_vaartus)}    
    % endif
  </td>
  % endif
  <td>
      % if c.is_edit or c.is_tr:
      <div class="cke_top_pos" name="${prefix}.tagasiside"></div>
      <div class="cke_top_pos" name="${prefix}.op_tagasiside"></div>
      % endif
      <div>
      <div class="row">
      <div class="col-sm-6">
      % if c.is_edit or c.is_tr or item.tagasiside:
        ${_("Tagasiside õpilasele")}:
        ${self.tran_editable('tagasiside', item, prefix + '.')}
      % endif
      </div>
      <div class="col-sm-6">
      % if c.is_edit or c.is_tr or item.op_tagasiside:
        ${_("Tagasiside õpetajale")}:
        ${self.tran_editable('op_tagasiside', item, prefix + '.')}          
      % endif
      </div>
      </div>
      </div>
      % if c.is_edit:
      ${h.checkbox('%s.jatka' % prefix, 1, checked=item.jatka, label=_("Jätka sama ülesannet"))}
      % elif item.jatka:
      ${_("Jätka sama ülesannet")}
      % endif
      % if c.is_edit or c.is_tr:
      ${h.hidden('%s.id' % prefix, item.id)}
      % endif
  </td>
  % if c.is_edit:
  <td width="20px">
    ${h.grid_remove()}
    <span class="glyphicon glyphicon-chevron-up ts-up"></span>
    <span class="glyphicon glyphicon-chevron-down ts-down"></span>
  </td>
  % endif
</tr>
</%def>              

<%def name="errpos(pos)">
## kontrolli teated
<% msg = c.errors and c.errors.get(pos) %>
% if msg:
<div class="error">${msg}</div>
% endif
</%def>

<%def name="tran_editable(key, item, prefix)">
<%
  orig_val = item and item.__getattr__(key)
  if c.lang:
     tran = item and item.tran(c.lang, False)
     tran_val = tran and tran.__getattr__(key) or ''
%>
<div class="body16">
% if c.lang:
<div>
  ${h.lang_orig(h.literal(orig_val), c.ylesanne.lang)}
</div>
${h.lang_tag()}
% if c.is_tr:
${h.textarea(prefix + key, tran_val, ronly=False, class_="editable editable16")}
% else:
${tran_val}
% endif
% else:
% if c.is_edit:
${h.textarea(prefix + key, orig_val, ronly=False, class_="editable editable16")}
% else:
${orig_val}
% endif
% endif
</div>
</%def>
