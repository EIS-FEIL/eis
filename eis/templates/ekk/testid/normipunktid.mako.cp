## -*- coding: utf-8 -*- 
<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'normipunktid' %>
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${_(u"Test")}: ${c.test.nimi or ''} | ${c.test.testiliik_kood==const.TESTILIIK_DIAG2 and _(u"Feedback texts") or _(u"Profile page settings")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_(u"Tests"), h.url('testid'))} 
${h.crumb_sep()}
${h.crumb(c.test.nimi or _(u"Test"))} 
${h.crumb_sep()}
${h.crumb(c.test.testiliik_kood==const.TESTILIIK_DIAG2 and _(u"Feedback texts") or _(u"Profile page settings"))}
</%def>
<%def name="require()">
<%
c.includes['ckeditor'] = True
%>
</%def>

<%include file="translating.mako"/>
<% c.is_edit = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test) %>
${h.form_save(None)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)} 

<%
  c.opt_alatestid = [(r.id, '%s %s' % (r.seq, r.nimi)) for r in c.testiosa.alatestid]
  c.opt_ty = [(r.id, r.tahis, r.alatest_id) for r in c.testiosa.testiylesanded]
  c.on_grupid = c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH or len(c.testiosa.alatestigrupid)
  if c.test.testiliik_kood == const.TESTILIIK_DIAG2:
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
% if c.test.testiliik_kood == const.TESTILIIK_DIAG2:
${self.diag2_kokkuvotted()}
% endif

% if c.test.testiliik_kood == const.TESTILIIK_DIAG2:
<table style="margin:5px;width:100%;max-width:1000px;">
  <caption>${_(u"Feedback by task groups")}</caption>
</table>
% else:
${_(u"Profile fields")}
% endif

<div class="profiiliseaded" style="max-width:1000px">
  ## grupita normipunktid
  <%
    c.n_norm = c.grupp_index = 0
    normipunktid = [r for r in c.testiosa.normipunktid if not r.alatestigrupp_id]
  %>
  ${self.normipunktid(normipunktid, '')}

  % if c.on_grupid:
  ## grupid - koolipsühholoogi testi korral
  <%
    prefix = 'atg'
    grid_id = 'grid_atg'
  %>
  <div id="${grid_id}" class="grupid ${c.is_edit and 'sortables' or ''}">
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
         <%
           # leiame indeksid selles järjekorras, milles vastati
           indexes = []
           for key, value in request.params.items():
              m = model.re.match(r'atg-(\d+).id', key)
              if m:
                 indexes.append(m.groups(0)[0])
         %>
  ${indexes}
  %   for cnt in indexes:
        ${self.row_grupp(c.new_item(), '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(c.testiosa.alatestigrupid):
        ${self.row_grupp(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </div>
  % endif
</div>
% if c.is_edit:
% if c.on_grupid:
${h.button(_(u"Add group"), class_="button1", onclick="grid_addrow('%s', null, null, null, null, '%s');set_grupp_seq();" % (grid_id, prefix))}
<div id="sample_${grid_id}" class="invisible sample">
  ${self.row_grupp(c.new_item(), '%s__cnt__' % (prefix))}
</div>
% endif
##${h.submit_dlg()}
${h.submit()}
% if c.test.testiliik_kood == const.TESTILIIK_DIAG2:
${h.submit(_(u"Check"), id="kontroll")}
% endif
% endif

##${h.button(_(u"Cancel"), onclick="close_dialog()")}
${h.end_form()}

% if c.is_edit:
<div id="dia_ckeditor_top" class="ckeditor-top-float"></div>
<script>
<%include file="normipunktid.js"/>
</script>
% endif

<%def name="row_grupp(item, prefix)">
<div ${c.is_edit and 'class="sortable grupp"' or ''} style="padding: 5px 0px;">
  <div ${c.is_edit and 'class="border-sortable"' or ''}>
##INDEX ${prefix}
    <table width="100%">
      <col width="100"/>
      <col/>
      <col width="20px"/>
      <tr>
        <td class="fh">
          ${_(u"Group title")}
        </td>
        <td>
          ${h.text('%s.nimi' % prefix, item.nimi, maxlength=75)}
        </td>
        % if c.is_edit:
        <td>
          ${h.grid_s_remove('div.grupp', confirm=True)}
          ${h.hidden('%s.id' % prefix, item.id, class_='grp_id')}
          ${h.hidden('%s.seq' % prefix, item.seq, class_='grp_seq')}          
          ${h.hidden('%s.prefix' % prefix, prefix)}              
        </td>
        % endif
      </tr>
    </table>
    ${self.normipunktid(item.normipunktid or [], prefix)}
  </div>
</div>
</%def>

<%def name="normipunktid(normipunktid, grupp_prefix)">
<%
  prefix = 'normid'
  c.grupp_index += 1
  grid_id = 'grid_norm%d' % c.grupp_index
%>
    <div id="${grid_id}" data-grupp-prefix="${grupp_prefix}"
         % if c.is_edit:
         class="grupinormid sortables" style="min-height:30px">
         % else:
         class="grupinormid">
         % endif
      % if c._arrayindexes != '' and not c.is_tr:
         ## valideerimisvigade korral
         <%
           indexes = []
           for key, value in request.params.items():
              m = model.re.match(r'normid-(\d+).grupp_prefix', key)
              if m and value == grupp_prefix:
                 indexes.append(m.groups(0)[0])
         %>
      %   for cnt in indexes:
         ${self.row_normipunkt(c.new_item(), '%s-%s' % (prefix, cnt), grupp_prefix)}
      %   endfor
      % else:
      ## tavaline kuva
      %   for cnt,item in enumerate(normipunktid):
         ${self.row_normipunkt(item, '%s-%s' % (prefix, c.n_norm), grupp_prefix)}
         <% c.n_norm += 1 %>         
      %   endfor
      % endif
    </div>
    % if c.is_edit:
    <%
      label = not c.on_grupid and _(u"Add") or \
         grupp_prefix and _(u"Add field to the group") or \
         _(u"Add field without group")
      onclick = "var r=grid_addrow('%s',null,null,null,null,'normid',$('.profiiliseaded'));" % (grid_id)
      if c.test.testiliik_kood == const.TESTILIIK_DIAG2:
         onclick += "on_addrow_np(r);"
    %>
    ${h.button(label, class_="button1", onclick=onclick)}
    <div id="sample_${grid_id}" class="invisible sample">
      ${self.row_normipunkt(c.new_item(), '%s__cnt__' % (prefix), grupp_prefix)}
    </div>
    % endif
</%def>


<%def name="row_normipunkt(item, prefix, grupp_prefix)">
<table class="norm ${c.is_edit and 'border-sortable sortable' or ''}" style="margin:3px;background-color:#fff;" width="100%">
  % if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
  ${self.row_normipunkt_psyh(item, prefix)}
  % elif c.test.testiliik_kood == const.TESTILIIK_DIAG2:
  ${self.row_normipunkt_diag2(item, prefix)}  
  % else:
  ${self.row_normipunkt_opip(item, prefix)}
  % endif
  <tr>
    <td>
      ${h.hidden('%s.id' % prefix, item.id or '')}
      ${h.hidden('%s.grupp_prefix' % prefix, grupp_prefix)}
##INDEX ${prefix} / ${grupp_prefix}
    </td>
  </tr>
</table>
</%def>

<%def name="row_normipunkt_opip(item, prefix)">
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
      ${_(u"Title")}
    </td>
    <td colspan="3">
      ${h.text('%s.nimi' % prefix, item.nimi, maxlength=75)}
    </td>
    <td class="frh">
      ${_(u"Type")}
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
      ${_(u"Code")}
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
      ${_(u"Expression")}
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
      ${_(u"Title")}
    </td>
    <td colspan="3">
      ${h.text('%s.nimi' % prefix, item.nimi, placeholder=item.default_nimi, maxlength=75)}
      % if not c.is_edit and not item.nimi:
      ${item.default_nimi}
      % endif
    </td>
    <td class="frh">
      ${_(u"Percentile value")}
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
            ${_(u"Subtest")}
          </td>
          <td>
            ${h.select('%s.alatest_id' % prefix, item.alatest_id, c.opt_alatestid, empty=True)}
          </td>
        </tr>
        % endif
        <tr>
          <td class="fh">
            ${_(u"Task")}
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
            ${_(u"Item code")}
          </td>
          <td>
            ${h.text('%s.kysimus_kood' % prefix, item.kysimus_kood, maxlength=100, 
            class_='kkood')}                        
          </td>
        </tr>
        <tr>
          <td colspan="2">
            ${h.checkbox('%s.on_oigedvaled' % prefix, 1, checked=item.on_oigedvaled, label=_(u"Show number of correct and incorrect responses"))}
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
    <td class="frh">${_(u"Task group")}</td>
    <td colspan="2">
      ${h.select('%s.ylesandegrupp_id' % prefix, item.ylesandegrupp_id, c.opt_ylesandegrupid, wide=False, names=True, empty=True, class_='diag-grupp_id')}
    </td>
    <td rowspan="3" valign="middle">
      <span style="float:right">${h.grid_s_remove("table", confirm=True)}</span>
    </td>
  </tr>
  <tr>
    <td class="frh">${_(u"Task")}</td>
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
      <input type="button" class="button1" value="${_(u"Add")}"
             style="position:absolute;bottom:5px;right:5px;"
             onclick="grid_addrow('${grid_npts}',null,null,false,null,'npts');on_addrow_npts('${grid_npts}');"/>
    </td>
    <td colspan="2" valign="top">
      ${self.nptagasisided(item, prefix_npts, grid_npts)}
    </td>
  </tr>
</%def>              

<%def name="nptagasisided(item, prefix, grid_id)">
<table id="${grid_id}" width="100%" cellspacing="1" cellpadding="4" class="list nptagasisided">
  <col width="60px"/>
  <col width="80px"/>
  <col/>
  % if c.is_edit:
  <col width="30px"/>
  % endif
  <thead>
    <tr>
      ${h.th(_(u"Condition"), colspan=2)}
      ${h.th(_(u"Feedback"))}
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
        <td align="right" style="white-space:nowrap;padding-right:3px">${_(u"Feedback text")}</td>
        <td>
          ${h.textarea('%s.tagasiside' % prefix, item.tagasiside, class_='diag-txt editable', rows=3)}
        </td>
      </tr>
      <tr>
        <td align="right" style="white-space:nowrap;padding-right:3px;">${_(u"Next task")} </td>
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
    <th>${_(u"Turned")}</th>
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

<%def name="diag2_kokkuvotted()">
<%
  tts = c.test.testitagasiside
%>
<table class="border" style="margin:5px;width:100%;max-width:1000px;">
  <caption>${_(u"Feedback for the student")}</caption>
  <tr>
    <td>
      ${_(u"Introduction")}
       ## % if c.lang:
       ##    ${h.lang_orig(h.literal(c.item.get_juhis()), c.item.lang)}<br/>
       ##    ${h.lang_tag()}
       ##    ${h.ckeditor('j_juhis', c.item.get_juhis(c.lang), ronly=not c.is_tr, height=150)}
       ## % else:
      ${h.textarea('s_sissejuhatus_opilasele', tts and tts.sissejuhatus_opilasele, ronly=not c.is_tr and not c.is_edit, class_="editable editable70")}
       ## % endif
    </td>
  </tr>
  <tr>
    <td>
      ${_(u"Resume")}
      ${h.textarea('s_kokkuvote_opilasele', tts and tts.kokkuvote_opilasele, ronly=not c.is_tr and not c.is_edit, class_="editable editable70")}      
    </td>
  </tr>
</table>
<table class="border" style="margin:5px;width:100%;max-width:1000px;">
  <caption>${_(u"Feedback for the teacher")}</caption>
  <tr>
    <td>
      ${_(u"Introduction")}
      ${h.textarea('s_sissejuhatus_opetajale', tts and tts.sissejuhatus_opetajale, ronly=not c.is_tr and not c.is_edit, class_="editable editable70")}
    </td>
  </tr>
  <tr>
    <td>
      ${_(u"Resume")}
      ${h.textarea('s_kokkuvote_opetajale', tts and tts.kokkuvote_opetajale, ronly=not c.is_tr and not c.is_edit, class_="editable editable70")}      
    </td>
  </tr>
</table>
</%def>
