<% c.is_edit = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test) %>
% if c.is_edit:
${h.form_save(None)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)} 
<div id="dia_ckeditor_top" class="ckeditor-top-float"></div>
% endif


<%
  c.opt_alatestid = [(r.id, '%s %s' % (r.seq, r.nimi)) for r in c.testiosa.alatestid]
  c.opt_ty = [(r.id, r.tahis, r.alatest_id) for r in c.testiosa.testiylesanded]
  c.on_grupid = c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH or len(c.testiosa.alatestigrupid)
  if c.test.diagnoosiv:
     c.opt_ylesandegrupid = [(r.id, '%s (%sp)' % (r.nimi, h.fstr(r.max_pallid) or 0)) for r in c.testiosa.ylesandegrupid]  
     c.opt_testiylesanded = []
     for ty in c.testiosa.testiylesanded:
        for vy in ty.valitudylesanded:
           yl = vy.ylesanne
           if yl:
               buf = '%s - %s (%sp)' % (vy.ylesanne_id, yl.nimi, h.fstr(ty.max_pallid) or 0)
               c.opt_testiylesanded.append((ty.id, buf))
     c.opt_tehe = model.Nptagasiside.opt_tehe()
%>

% if c.is_edit:
<script>
<%include file="normipunkt.js"/>
</script>
% endif

% if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
${self.normipunkt_psyh(c.normipunkt)}
% elif c.test.diagnoosiv:
${self.normipunkt_diag(c.normipunkt)}
% else:
${self.normipunkt_opip(c.normipunkt)}
% endif

<%def name="normipunkt_opip(item, prefix)">
<%
  opt_normityyp = c.opt.normityyp_opip
%>
  <col width="100"/>
  <col width="200"/>
  <col/>
  <col width="200"/>
  <col/>
  <col width="200"/>
  <col width="20"/>
  <tr>
    <td class="fh">
      ${_("Nimetus")}
    </td>
    <td colspan="3">
      ${h.text('%s.nimi' % prefix, item.nimi, maxlength=75)}
    </td>
    <td class="frh">
      ${_("Liik")}
    </td>
    <td>
      ${h.select('%s.normityyp' % prefix, item.normityyp, opt_normityyp,
      onchange="change_normityyp(this)")}
    </td>
    <td rowspan="3" valign="middle">
      <span style="float:right">${h.grid_s_remove("table", confirm=True)}</span>
    </td>
  </tr>
  <tr>
    <td colspan="2">
    </td>
    <td class="fh">
      ${_("Kood")}
    </td>
    <td colspan="1">
      ${h.text('%s.kood' % prefix, item.kood, maxlength=50)}
    </td>
    <td colspan="2">
      <table width="100%">
        <tr>
          <td class="frh">Min</td>
          <td>${h.int5('%s.min_vaartus' % prefix, item.min_vaartus)}</td>
          <td class="frh">Max</td>
          <td>${h.int5('%s.max_vaartus' % prefix, item.max_vaartus)}</td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td class="fh">
      ${_("Avaldis")}
    </td>
    <td colspan="5">
      ${h.textarea('%s.avaldis' % prefix, item.kysimus_kood, maxlength=1024, style="width:98%", rows=1, class_='kkood')}
    </td>
  </tr>

</%def>

<%def name="row_normipunkt_psyh(item, prefix)">
<%
  opt_normityyp = c.opt.normityyp_psyh
%>
  <col width="100"/>
  <col width="200"/>
  <col/>
  <col width="200"/>
  <col/>
  <col width="200"/>
  <col width="20"/>
  <tr>
    <td class="fh">
      ${_("Nimetus")}
    </td>
    <td colspan="3">
      ${h.text('%s.nimi' % prefix, item.nimi, placeholder=item.default_nimi, maxlength=75)}
      % if not c.is_edit and not item.nimi:
      ${item.default_nimi}
      % endif
    </td>
    <td class="frh">
      ${_("Protsentiili väärtus")}
    </td>
    <td>
      ${h.select('%s.normityyp' % prefix, item.normityyp, opt_normityyp,
      onchange="change_normityyp(this)")}
    </td>
    <td rowspan="3" valign="middle">
      <span style="float:right">${h.grid_s_remove("table", confirm=True)}</span>
    </td>
  </tr>
  <tr>
    <td colspan="2">
      <table width="100%">
        % if c.testiosa.on_alatestid:
        <tr>
          <td class="fh">
            ${_("Alatest")}
          </td>
          <td>
            ${h.select('%s.alatest_id' % prefix, item.alatest_id, c.opt_alatestid, empty=True)}
          </td>
        </tr>
        % endif
        <tr>
          <td class="fh">
            ${_("Ülesanne")}
          </td>
          <td>
            ${h.select('%s.testiylesanne_id' % prefix, item.testiylesanne_id, c.opt_ty, wide=False, empty=True)}
          </td>
        </tr>
      </table>

    </td>
    <td colspan="2">
      <table width="100%">
        <tr>
          <td class="frh">
            ${_("Küsimuse kood")}
          </td>
          <td>
            ${h.text('%s.kysimus_kood' % prefix, item.kysimus_kood, maxlength=100, 
            class_='kkood')}                        
          </td>
        </tr>
        <tr>
          <td colspan="2">
            ${h.checkbox('%s.on_oigedvaled' % prefix, 1, checked=item.on_oigedvaled, label=_("Kuva õigete ja valede vastuste arv"))}
          </td>
        </tr>
      </table>
    </td>
    <td colspan="2">
      ${self.protsentiilid(item, prefix)}
    </td>
  </tr>
</%def>              

<%def name="row_normipunkt_diag2(item, prefix)">
<%
  opt_normityyp = c.opt.normityyp_diag2
%>
  <col width="150"/>
  <col/>
  <col width="20"/>
  <tr>
    <td class="frh">${_("Ülesandegrupp")}</td>
    <td colspan="2">
      ${h.select('%s.ylesandegrupp_id' % prefix, item.ylesandegrupp_id, c.opt_ylesandegrupid, wide=False, names=True, empty=True, class_='diag-grupp_id')}
    </td>
    <td rowspan="3" valign="middle">
      <span style="float:right">${h.grid_s_remove("table", confirm=True)}</span>
    </td>
  </tr>
  <tr>
    <td class="frh">${_("Ülesanne")}</td>
    <td colspan="2">
      ${h.select('%s.testiylesanne_id' % prefix, item.testiylesanne_id, c.opt_testiylesanded, wide=False, names=True, empty=True, class_='diag-ty_id')}
    </td>
  </tr>
  <tr>
    <td valign="top" style="position:relative" id="npts_${item.id}">
      ${h.select('%s.normityyp' % prefix, item.normityyp, opt_normityyp)}

      <%
        prefix_npts = '%s.npts' % prefix
        grid_npts = 'tbl_%s_npts' % prefix
      %>
      ${h.button(_("Lisa"), style="position:absolute;bottom:5px;right:5px;",
      onclick=f"grid_addrow('{grid_npts}',null,null,false,null,'npts');on_addrow_npts('{grid_npts}');", level=2, mdicls='mdi-plus')}
    </td>
    <td colspan="2" valign="top">
      ${self.nptagasisided(item, prefix_npts, grid_npts)}
    </td>
  </tr>
</%def>              

<%def name="nptagasisided(item, prefix, grid_id)">
<table id="${grid_id}" width="100%"  class="table table-borderless table-striped nptagasisided">
  <col width="60px"/>
  <col width="80px"/>
  <col/>
  % if c.is_edit:
  <col width="30px"/>
  % endif
  <thead>
    <tr>
      ${h.th(_("Jrk"))}
      ${h.th(_("Tingimus"), colspan=2)}
      ${h.th(_("Tagasiside"))}
      % if c.is_edit:
      <th></th>
      % endif
    </tr>
  </thead>
  <tbody>
  <% rows = list(item.nptagasisided) %>
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_nptagasiside(c.new_item(), '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(rows):
        ${self.row_nptagasiside(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  %   for cnt in range(len(rows or []), 1):
        ${self.row_nptagasiside(c.new_item(), '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
% if 0:
  <tfoot>
% if c.is_edit:
   <tr style="display:none">
     <td colspan="4">
       <div id="sample_${grid_id}" class="invisible sample">
<!--
   ${self.row_nptagasiside(c.new_item(), '%s__cnt__' % prefix)}
-->
       </div>
     </td>
   </tr>
% endif
  </tfoot>
% endif
% if c.is_edit:
  <tfoot id="sample_${grid_id}" class="invisible sample">
   ${self.row_nptagasiside(c.new_item(), '%s__cnt__' % prefix)}
  </tfoot>
% endif
</table>
</%def>

<%def name="row_nptagasiside(item, prefix)">
<tr>
  <td>${item.seq}</td>
  <td>
    ${h.select('%s.tingimus_kood' % prefix, item.tingimus_kood, c.opt_kood, onchange="ch_diag_kood(this, true)", class_='diag-code')}
  </td>
  <td>
    ${h.select('%s.tingimus_tehe' % prefix, item.tingimus_tehe, c.opt_tehe, class_='diag-op')}
  </td>
  <td>
    ${h.select('%s.tingimus_valik' % prefix, item.tingimus_valik, c.valikud.get(item.tingimus_kood) or [],
    class_='diag-choice')}
    ${h.posfloat('%s.tingimus_vaartus' % prefix, item.tingimus_vaartus, class_='diag-value')}
  </td>
  <td>
    <table width="100%" cellspacing="0" colspacing="0" cellpadding="0">
      <col width="100"/>
      <tr>
        <td align="right" style="white-space:nowrap;padding-right:3px">${_("Tagasiside tekst")}</td>
        <td>
          ${h.textarea('%s.tagasiside' % prefix, item.tagasiside, class_='diag-txt editable', rows=3)}
        </td>
      </tr>
      <tr>
        <td align="right" style="white-space:nowrap;padding-right:3px;">${_("Järgmine ülesanne")} </td>
        <td>
          ${h.select('%s.uus_testiylesanne_id' % prefix, item.uus_testiylesanne_id, c.opt_testiylesanded,
          wide=False, names=True, empty=True, class_='diag-yl')}
        </td>
      </tr>
    </table>

  </td>
  % if c.is_edit:
  <td width="20px">
    ${h.grid_remove()}
    ${h.hidden('%s.id' % prefix)}
  </td>
  % endif
</tr>
</%def>              

<%def name="protsentiilid(item, prefix)">
<%
  protsentiilid = {}
  for r in item.normiprotsentiilid:
     protsentiilid[r.protsent] = r
%>
<table>
  <tr>
    <th>${_("Pööratud")}</th>
    <th>10%</th>
    <th>25%</th>
    <th>50%</th>
    <th>75%</th>
    <th>90%</th>
  </tr>
  <tr>
    <td>
      ${h.checkbox('%s.pooratud' % prefix, 1, checked=item.pooratud)}
    </td>
    % for p_ind, protsent in enumerate((10,25,50,75,90)):
    <%
      pprefix = '%s.protsentiilid-%d' % (prefix, p_ind)
      norm = protsentiilid.get(protsent) or None
    %>
    <td>
      ${h.posfloat('%s.protsentiil' % pprefix, norm and norm.protsentiil, size=3)}
      ${h.hidden('%s.id' % pprefix, norm and norm.id or '')}
      ${h.hidden('%s.protsent' % pprefix, protsent)}                  
    </td>
    % endfor
  </tr>
</table>
</%def>
