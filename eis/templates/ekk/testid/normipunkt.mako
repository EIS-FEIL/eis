<div ${not c.is_edit and 'container_sel="#drnp%s"' % c.normipunkt.id or ''}>
</div>
<%include file="/common/message.mako"/>
<%
  if c.is_edit and c.lang:
     c.is_tr = True
  if c.is_tr:
     c.is_edit = False
%>
% if c.is_edit or c.is_tr:
${h.form_save(c.normipunkt.id)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)} 
${h.hidden('np_alatestigrupp_id', c.normipunkt.alatestigrupp_id)}
% endif
<%
  c.opt_alatestid = [(r.id, '%s %s' % (r.tahis or '', r.nimi)) for r in c.testiosa.alatestid]
  c.opt_ylesandegrupid = [(r.id, '%s (%sp)' % (h.utils.html2plain(r.nimi), h.fstr(r.max_pallid) or 0)) for r in c.testiosa.ylesandegrupid]  
  if c.test.diagnoosiv:
     c.opt_ty = []
     c.opt_jatkyl = []
     for ty in c.testiosa.testiylesanded:
        for vy in ty.valitudylesanded:
           yl = vy.ylesanne
           if yl:
             buf = '%s - %s (%sp)' % (vy.ylesanne_id, yl.nimi, h.fstr(ty.max_pallid) or 0)
             if ty.on_jatk:
                c.opt_jatkyl.append((ty.id, buf))
             c.opt_ty.append((ty.id, buf, ty.alatest_id))
  else:
     c.opt_ty = [(r.id, r.tahis, r.alatest_id) for r in c.testiosa.testiylesanded if r.tahis] 
  c.opt_tehe = model.Nptagasiside.opt_tehe()
  c.opt_atg = [(r.id, r.nimi) for r in c.testiosa.alatestigrupid]  
%>
${self.normipunkt_tbl(c.normipunkt)}

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
% if c.normipunkt.id and c.is_edit:
${h.btn_remove(confirm=_("Kas oled kindel, et soovid kustutada?"))}
% endif

% if c.is_edit:
<%
  grid_npts = 'tbl_npts'
  onclick = f"grid_addrow('{grid_npts}',null,null,false,null,'npts');on_addrow_npts('{grid_npts}');"
%>
${h.button(_("Lisa tingimus"), onclick=onclick)}
% endif
  </div>
  <div>
% if c.normipunkt.id and c.is_edit:
    <script>
      <% url = h.url_current('new', copy_id=c.normipunkt.id) %>
      function copynp(){ dialog_load("${url}", null, 'GET', $('.modal-body')); }
    </script>
    ${h.button(_("Kopeeri"), id="copy", level=2, onclick="copynp()")}
% endif
% if c.is_edit or c.is_tr:
${h.submit_dlg()}
% endif
  </div>
</div>

% if c.is_edit or c.is_tr:
${h.end_form()}
<script>
  <%include file="normipunkt.js"/>
</script>
<div style="height:0">
<div id="np_ckeditor_top" class="ckeditor-top-float"></div>
</div>
% endif

<%def name="normipunkt_tbl(item)">
<%
  opt_normityyp = c.opt.normityyp
  errprefix = 'np%s' % item.id
  opt_lang = [('', _("Kõik keeled"))] + c.test.opt_keeled  
%>
<div class="form nptable">
  ######################################################
  ## kuidas tunnusele viidatakse?
  ## õpip
  <div class="form-group row">
    ${h.flb3(_("Nimetus"))}
    <div class="col">
    % if c.is_edit or item.nimi:
      % if c.lang:
      ${h.lang_orig(item.nimi)}<br/>
      ${h.lang_tag()}
      ${h.textarea('np.nimi', item.tran(c.lang).nimi, placeholder=item.default_nimi,
      maxlength=330, ronly=not c.is_tr)}      
      % else:
      ${h.textarea('np.nimi', item.nimi, placeholder=item.default_nimi, maxlength=330)}
      % endif
    % else:
      ## psyh
      ${item.default_nimi}
    % endif
    </div>
  </div>

  ## õpip
  % if c.is_edit or item.kood:
  <div class="form-group row">
    ${h.flb3(_("Kood"))}
    <div class="col">
      ${h.text('np.kood', item.kood, maxlength=50)}
    </div>
  </div>
  % endif
  
  ######################################################
  ## milliste sooritajate korral arvutatakse?
  ## õpip
  <div class="form-group row">
    % if c.is_edit or item.lang:
    ${h.flb3(_("Soorituskeel"))}
    <div class="col-md-2">
      ${h.select('np.lang', item.lang, opt_lang, wide=False)}
    </div>
    % else:
    <div class="col-md-2"></div>
    % endif
    <div class="col">
        % if c.is_edit:
        ${h.checkbox('np.on_opilane', 1, checked=item.on_opilane!=False, label=_("Õpilase profiilileht"))}
        ${h.checkbox('np.on_grupp', 1, checked=item.on_grupp!=False, label=_("Grupi profiilileht"))}
        % elif item.on_opilane and not item.on_grupp:
        ${_("Õpilase profiilileht")}
        % elif item.on_grupp and not item.on_opilane:
        ${_("Grupi profiilileht")}
      % elif item.on_opilane and item.on_grupp:
        ${_("Õpilase ja grupi profiilileht")}
        % elif not item.on_grupp and not item.on_opilane:
        ${_("Profiililehel ei kuvata")}
        % endif
    </div>
  </div>
  % if c.is_edit and c.opt_atg or item.alatestigrupp_id:
  <div class="form-group row">
    ${h.flb3(_("Tunnuste grupp"))}
    <div class="col">
      ${h.select('np.alatestigrupp_id', item.alatestigrupp_id, c.opt_atg, wide=False)}
    </div>
  </div>
  % endif
% if not c.lang:  
  <div class="form-group row">
    ${h.flb3(_("Liik"))}
    <div class="col">
      ${h.select('np.normityyp', item.normityyp, opt_normityyp, class_="normityyp", wide=False)}
      ${self.errpos(errprefix + '.normityyp')}      
    </div>
  </div>

  #######################################################
  ## mille põhjal arvutatakse?
  <div class="form-group row">
    <div class="col">
      ${h.flb(_("Mille põhjal tunnuse väärtus arvutatakse"))}
    </div>
  </div>
  % if c.is_edit and c.opt_ylesandegrupid or item.ylesandegrupp_id:
  ## diag
  <div class="form-group row">
    ${h.flb3(_("Ülesandegrupp"))}
    <div class="col">
      ${h.select('np.ylesandegrupp_id', item.ylesandegrupp_id, c.opt_ylesandegrupid, wide=False, names=True, empty=True, class_='diag-grupp_id')}
    </div>
  </div>
  % endif

  ## psyh
  % if c.testiosa.on_alatestid and (c.is_edit or item.alatest_id):
  <div class="form-group row">
    ${h.flb3(_("Alatest"))}
    <div class="col">
      ${h.select('np.alatest_id', item.alatest_id, c.opt_alatestid, empty=True, wide=False, class_="alatest_id")}
    </div>
  </div>
  % endif
  % if c.is_edit or item.testiylesanne_id:
   <div class="form-group row ${not c.test.diagnoosiv and 'trpolevalem' or ''}">
     ${h.flb3(_("Ülesanne"))}
     <div class="col">
       ${h.select('np.testiylesanne_id', item.testiylesanne_id, c.opt_ty, wide=False, names=True, empty=True, class_='testiylesanne_id')}
       ${self.errpos(errprefix + '.testiylesanne_id')}      
     </div>
   </div>
   % endif
   <% on_valem = item.normityyp == const.NORMITYYP_VALEM %>
   % if c.is_edit or item.kysimus_kood:
  <div class="form-group row">
    <label class="font-weight-bold col-md-3">
    % if c.is_edit or not on_valem:
      <div class="trpolevalem">
        ${_("Küsimuse kood")}
      </div>
      % endif
      % if c.is_edit or on_valem:
      <div class="trvalem">
        ${_("Valem")}
      </div>
      % endif
    </label>
    <div class="col">
      <%
        opt_kood, c.valikud = request.handler._get_opt_k_valik(item.testiylesanne_id, item.alatest_id)
        k_kood = None
        if item.kysimus_kood in [r[0] for r in opt_kood]:
           k_kood = item.kysimus_kood
      %>
      <script>
        var choices = ${model.json.dumps(c.valikud)};
      </script>
      ## diag
      % if c.is_edit or item.testiylesanne_id and not on_valem:
      <div class="tronyl-polevalem">
      ${h.select('np.kysimus_kood1', k_kood, opt_kood, class_='kkood1', empty=True, wide=False)}
      ${self.errpos(errprefix + '.kysimus_kood1')}      
      </div>
      % endif
      % if c.is_edit or on_valem or not item.testiylesanne_id:
      <div class="trpoleyl" style="overflow-wrap:anywhere">
      ${h.textarea('np.kysimus_kood', item.kysimus_kood, maxlength=2000, style="width:98%", rows=2, class_='kkood')}
      ${self.errpos(errprefix + '.kysimus_kood')}
      </div>
      % endif
    </div>
  </div>
  % endif

  % if not c.is_edit and not item.kysimus_kood and not item.testiylesanne_id and not item.ylesandegrupp_id and not item.alatest_id:
  <div class="form-group row">
    <div class="col">
      ${_("Väärtus arvutatakse kogu testiosa põhjal")}
    </div>
  </div>
  % endif
% endif
  
  
% if c.is_edit or c.is_tr or c.ting:
  ######################################################
  ## tagasiside
  <div class="form-group row">
    <div class="col">
      ${h.flb(_("Tagasiside tingimused"))}
    </div>
  </div>
% if not c.lang:
  ## õpip
  % if c.is_edit or item.min_max or item.min_vaartus is not None or item.max_vaartus is not None:
  % if c.test.tagasiside_mall == const.TSMALL_OPIP:
  <div class="form-group row">
    ${h.flb3(_("Min-max"))}
    <div class="col">
      ${h.text('np.min_max', item.min_max, class_="minmax")}
    </div>
  </div>
  % else:
  <div class="form-group row">
    ${h.flb3(_("Min"), 'np.min_vaartus')}
    <div class="col-md-3">
      ${h.float10('np.min_vaartus', item.min_vaartus, size=8)}
    </div>
    ${h.flb3(_("Max"), 'np.max_vaartus', 'text-right')}
    <div class="col-md-3">
      ${h.posfloat('np.max_vaartus', item.max_vaartus, size=8)}
    </div>
  </div>
  % endif
  % endif
  % if c.test.tagasiside_mall == const.TSMALL_OPIP:  
  % if c.is_edit or c.is_tr or len(item.sooritusryhmad):
  <div class="form-group row">
    ## opip
    ${h.flb3(_("Sooritusrühm"))}
    <div class="col-md-3">
      ${self.opip_sooritusryhmad(item)}
      ${h.hidden('err_sryhmad','')}
    </div>
    <div class="col">
    % if c.is_edit:
      ${h.checkbox('np.pooratud_varv', 1, checked=item.pooratud_varv,
      label=_("Värvid pööratud järjekorras"))}<br/>
      ${h.checkbox('np.varv2_mk', 1, checked=item.varv2_mk,
      label=_("Kahe rühma kattumisel äärmise rühma värv"))}<br/>
      % else:
      % if item.pooratud_varv:
      ${_("Värvid pööratud järjekorras")}<br/>
      % endif
      % if item.varv2_mk:
      ${_("Kahe rühma kattumisel äärmise rühma värv")}<br/>
      % endif
      % endif
    </div>
  </div>
  % endif
  % endif
  
  % if (c.is_edit or len(item.normiprotsentiilid)) and c.test.tagasiside_mall == const.TSMALL_PSYH:
  ## psyh
  <div class="form-group row">
    ${h.flb3(_("Protsentiilid"))}
    <div class="col-md-3">
      ${self.psyh_protsentiilid(item)}
    </div>
    <div class="col">
      % if c.is_edit:
      ${h.checkbox('np.on_oigedvaled', 1, checked=item.on_oigedvaled, label=_("Kuva õigete ja valede vastuste arv"))}
      % elif item.on_oigedvaled:
      ${_("Kuva õigete ja valede vastuste arv")}
      % endif
    </div>
  </div>
  % endif
% endif
  
  % if c.is_edit or len(item.nptagasisided):
  <div class="form-group row">
    <div class="col">
      ${self.errpos(errprefix + '.id')}
      <%
        prefix_npts = 'np.npts'
        grid_npts = 'tbl_npts'
      %>
      ${self.nptagasisided(item, prefix_npts, grid_npts)}
      % if c.is_edit:
      ${h.checkbox('set_default_range', 1, label=_("Kasuta samu vahemikke edaspidi vaikimisi vahemikena"))}
      ${h.checkbox1('show_stat', 1, checked=c.show_stat, label=_("Tagasiside statistikas"))}      
      % endif
    </div>
  </div>
  % endif
% endif  
</div>
</%def>              

<%def name="nptagasisided(normipunkt, prefix, grid_id)">
<%
  rows = list(normipunkt.nptagasisided)
  on_ahel = c.test.diagnoosiv and (c.is_edit or len([r for r in rows if r.ahel_testiylesanne_id]))
  c.opt_nsgrupid = [(ng.id, h.utils.html2plain(ng.nimi)) for ng in c.testiosa.nsgrupid]
  on_nsgrupid = len(c.opt_nsgrupid) > 0
  c.show_stat = False
%>
% if c.is_edit or c.is_tr:
<table width="100%"  id="${grid_id}" class="table table-borderless table-striped nptagasisided">
% else:
<table width="100%"  class="table table-borderless table-striped">
% endif
  <col width="40px"/>
  % if c.is_edit:
  <col width="60px"/>
  <col width="80px"/>
  % if on_ahel:
  <col width="100px"/>
  % endif
  <col/>
  % if on_nsgrupid:
  <col width="100px"/>
  % endif
  <col width="30px"/>
  % else:
  <col width="20px"/>
  <col width="20px"/>  
  % if on_ahel:
  <col width="25%"/>
  <col width="65%"/>
  % else:
  <col width="85%"/>
  % if on_nsgrupid:
  <col/>
  % endif
  % endif
  % endif
  <thead>
    <tr>
      ${h.th(_("Jrk"))}
      ${h.th(_("Tingimus"), colspan=2)}
      % if on_ahel:
      ${h.th(_("Ahel"))}
      % endif
      ${h.th(_("Tagasiside"))}
      % if on_nsgrupid:
      ${h.th(_("Tagasiside grupp"))}
      % endif
      % if c.is_edit:
      <th></th>
      % endif
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_nptagasiside(c.new_item(), '%s-%s' % (prefix, cnt), normipunkt, on_ahel, on_nsgrupid)}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(rows):
        ${self.row_nptagasiside(item, '%s-%s' % (prefix, cnt), normipunkt, on_ahel, on_nsgrupid)}
  %   endfor
  <% min_rows = c.test.diagnoosiv and 1 or 0 %>
  %   for cnt in range(len(rows or []), min_rows):
        ${self.row_nptagasiside(c.new_item(), '%s-%s' % (prefix, cnt), normipunkt, on_ahel, on_nsgrupid)}
  %   endfor
  % endif
  </tbody>
% if c.is_edit:
  <tfoot id="sample_${grid_id}" class="invisible sample">
   ${self.row_nptagasiside(c.new_item(), '%s__cnt__' % prefix, normipunkt, on_ahel, on_nsgrupid)}
  </tfoot>
% endif
</table>
</%def>

<%def name="row_nptagasiside(item, prefix, normipunkt, on_ahel, on_nsgrupid)">
<% errprefix = 'np%s.ns%s' % (normipunkt.id, item.id) %>
<tr>
  <td>${item.seq}</td>
  % if c.is_edit:
  <td>
    ${h.select('%s.tingimus_tehe' % prefix, item.tingimus_tehe, c.opt_tehe, class_='tingimus_tehe')}
  </td>
  <td>
    <% opt_valik = c.valikud.get(normipunkt.kysimus_kood) or [] %>
    ${h.select('%s.tingimus_valik' % prefix, item.tingimus_valik, opt_valik, class_='tingimus_valik')}
    ${h.posfloat('%s.tingimus_vaartus' % prefix, item.tingimus_vaartus, class_='tingimus_vaartus')}
    ${self.errpos(errprefix + '.tingimus_vaartus')}
  </td>
  % else:
  <td colspan="2" class="nowrap">
    % if normipunkt.kysimus_kood and normipunkt.normityyp == const.NORMITYYP_VASTUS:
    ##% if normipunkt.kysimus_kood and len(normipunkt.kysimus_kood) < 20:
    ${normipunkt.kysimus_kood}
    % else:
    ${_("Tulemus")}
    % endif                                                                
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
  </td>
  % endif
  % if on_ahel:
  <td>
    ${h.select('%s.ahel_testiylesanne_id' % prefix, item.ahel_testiylesanne_id,
    c.opt_ty, wide=True, names=True, empty=True, class_="diag-ahel")}
  </td>
  % endif
  <td>
      % if c.test.diagnoosiv and (c.is_edit or item.uus_testiylesanne_id):
      <div>
        ${_("Järgmine ülesanne")}:
        ${h.select('%s.uus_testiylesanne_id' % prefix, item.uus_testiylesanne_id,
        c.opt_jatkyl, wide=False, names=True, empty=True, class_='diag-yl')}
      </div>
      % endif
      % if c.is_edit or c.is_tr:
      <div class="cke_top_pos" name="${prefix}.tagasiside"></div>
      <div class="cke_top_pos" name="${prefix}.op_tagasiside"></div>
      <div class="cke_top_pos" name="${prefix}.stat_tagasiside"></div>      
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
      <div class="col-sm-6 stat">
      % if c.is_edit or c.is_tr or item.stat_tagasiside:
        ${_("Tagasiside statistikas")}:
        ${h.text(prefix + '.stat_tagasiside', item.stat_tagasiside)}
        <% if item.stat_tagasiside: c.show_stat = True %>
      % endif
      </div>
      </div>
      </div>
      % if c.is_edit or c.is_tr:
      ${h.hidden('%s.id' % prefix, item.id)}
      % endif
  </td>
  % if on_nsgrupid:
  <td>
    ${h.select('%s.nsgrupp_id' % prefix, item.nsgrupp_id, c.opt_nsgrupid)}
  </td>
  % endif
  % if c.is_edit:
  <td width="20px">
    ${h.grid_remove()}
    <span class="glyphicon glyphicon-chevron-up ts-up"></span>
    <span class="glyphicon glyphicon-chevron-down ts-down"></span>
  </td>
  % endif
</tr>
</%def>              

<%def name="psyh_protsentiilid(item)">
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
      ${h.checkbox('np.pooratud', 1, checked=item.pooratud)}
    </td>
    % for p_ind, protsent in enumerate((10,25,50,75,90)):
    <%
      pprefix = 'np.protsentiilid-%d' % (p_ind)
      norm = protsentiilid.get(protsent) or None
    %>
    <td>
      ${h.posfloat('%s.protsentiil' % pprefix, norm and norm.protsentiil, size=3)}
      % if c.is_edit or c.is_tr:
      ${h.hidden('%s.id' % pprefix, norm and norm.id or '')}
      ${h.hidden('%s.protsent' % pprefix, protsent)}
      % endif
    </td>
    % endfor
  </tr>
</table>
</%def>

<%def name="opip_sooritusryhmad(item)">
<%
  ryhmad = {}
  for r in item.sooritusryhmad:
     ryhmad[r.ryhm] = r
  ryhmad_id = (model.Sooritusryhm.OPIP_MADAL,
               model.Sooritusryhm.OPIP_KESK,
               model.Sooritusryhm.OPIP_KORGE)
%>
<table>
  <tr>
    <th>Madal</th>
    <th>Keskmine</th>
    <th>Kõrge</th>
  </tr>
  <tr>
    % for p_ind, ryhm in enumerate(ryhmad_id):
    <%
      pprefix = 'np.sryhmad-%d' % (p_ind)
      norm = ryhmad.get(ryhm) or None     
    %>
    <td>
      % if p_ind == 0:
      ${_("vähemalt")} <span class="sryhm0">${h.fstr(item.min_vaartus) or 0}</span>
      ${h.hidden('%s.lavi' % pprefix, 0)}
      % else:
      ${_("vähemalt")} ${h.float5('%s.lavi' % pprefix, norm and norm.lavi, size=3)}
      % endif
      % if c.is_edit or c.is_tr:
      ${h.hidden('%s.id' % pprefix, norm and norm.id or '')}
      ${h.hidden('%s.ryhm' % pprefix, ryhm)}
      % endif
    </td>
    % endfor
  </tr>
</table>
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
  ${h.lang_orig(h.literal(orig_val), c.test.lang)}
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
