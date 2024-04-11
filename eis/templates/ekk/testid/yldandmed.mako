<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%
   c.can_update = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.item)
   eeltest = c.item.eeltest
   c.can_update_korduv = eeltest or c.user.has_permission('korduvsooritatavus', const.BT_UPDATE, c.item)    
%>
<%def name="page_title()">
${_("Test")}: ${c.item.nimi or ''} | ${_("Üldandmed")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))}
${h.crumb(c.item.nimi or _("Test"), h.url_current())}
</%def>
<%def name="require()">
<%
  c.includes['ckeditor'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

${h.form_save(c.item.id, multipart=True)}
<% ch = h.colHelper('col-md-2', 'col-md-4') %>
${h.rqexp()}
<div class="form-wrapper mb-2">
  <div style="height:0">
    <div id="ckt_ckeditor_top" class="ckeditor-top-float"></div>
  </div>

  <div class="form-group row">
  % if c.item.id:
    ${ch.flb(_("ID"), 'id')}
    <div class="col-md-4" id="id">
      ${c.item.id}
    </div>
  % endif
  % if c.item.eeltest_id:
    <div class="col-md-6 align-right">
      <%
        algtest = eeltest.algne_test
      %>
      ${_("Katsetamine")} /
      ${_("Eeltestitav test")}:
      <font style="text-decoration:underlined">
      ${h.link_to('%s (%s)' % (algtest.id, algtest.nimi), h.url('test_eeltest', test_id=algtest.id, id=eeltest.id))} 
      </font>
    </div>
  % endif
  </div>
  <div class="form-group row">
    ${ch.flb(_("Testi liik"), 'f_testiliik_kood', rq=True)}
    <div class="col-md-4">
        <%
          opt_testiliik = c.opt.testiliik
          dflt = const.TESTILIIK_EELTEST
          # jätame välja lubamatud testiliigid
          if not c.item.id:
              # enne esimest salvestamist saab valida nii avaliku kui ka EKK testi liike
              if not c.user.has_permission('ekk-testid', const.BT_CREATE, gtyyp=const.USER_TYPE_EKK):
                  opt_testiliik = [r for r in opt_testiliik if r[0] == const.TESTILIIK_AVALIK]
                  dflt = const.TESTILIIK_AVALIK
              elif not c.user.has_permission('ekk-testid', const.BT_CREATE, gtyyp=const.USER_TYPE_AV):
                  opt_testiliik = [r for r in opt_testiliik if r[0] != const.TESTILIIK_AVALIK]
                  dflt = const.TESTILIIK_EELTEST
          else:
              # peale esmast salvestamist ei saa muuta testityypi
              if  c.item.testityyp == const.TESTITYYP_AVALIK:
                  opt_testiliik = [r for r in opt_testiliik if r[0] == const.TESTILIIK_AVALIK]
                  dflt = const.TESTILIIK_AVALIK
              elif c.item.testityyp == const.TESTITYYP_EKK:
                  opt_testiliik = [r for r in opt_testiliik if r[0] != const.TESTILIIK_AVALIK]
                  dflt = const.TESTILIIK_EELTEST
        %>
        ${h.select('f_testiliik_kood', c.item.testiliik_kood or dflt, opt_testiliik)}
    </div>
    % if c.item.testiliik_kood == const.TESTILIIK_RV:
    ${ch.flb(_("Tunnistus"), 'f_rveksam_id', colextra='text-md-right')}
    <div class="col-md-4">
      ${h.select('f_rveksam_id', c.item.rveksam_id, c.opt.rveksamid(c.item.aine_kood), empty=True)}
    </div>
    % elif c.item.id and c.item.testiliik_kood == const.TESTILIIK_TKY:
      <% tky = c.item.opetaja_taustakysitlus %>
      % if tky:
      ${ch.flb(_("Õpilase test"), 'f_tky', colextra='text-md-right')}
      <div class="col-md-4">
        <%
          test2 = tky.opilase_test
          label = f'{test2.id} {test2.nimi}'
        %>
        ${h.link_to(label, h.url('test', id=test2.id))}
      </div>
      % else:
      <% tky = c.item.opilase_taustakysitlus %>
      ${ch.flb(_("Õpetaja test"), 'f_tky', colextra='text-md-right')}
      <div class="col-md-4" id="f_tky">
        % if tky:
        <%
          test2 = tky.opetaja_test
          label = f'{test2.id} {test2.nimi}'
        %>
        ${h.link_to(label, h.url('test', id=test2.id))}
        % endif
        ${h.btn_to_dlg(_("Vali test"), h.url_current('edit', id=c.item.id, sub='tky'), title=_("Õpetaja test"), level=2)}
      </div>
      % endif
    % endif
  </div>

  % if c.item.testityyp == const.TESTITYYP_EKK:
  <div class="form-group row">
    ${ch.flb(_("E-kogu"),'kogud_id')}
    <div class="col-md-10">
      <%
        kogud = [(r.id, r.nimi, r.aine_kood, r.aste_kood) for r in model.Ylesandekogu.query.order_by(model.Ylesandekogu.nimi).all()]
        kogu_opt = [(r[0], r[1]) for r in kogud]
        c.kogu_data = {r[0]: (r[2],r[3]) for r in kogud}
        selected_id = [r.ylesandekogu_id for r in c.item.kogutestid]
      %>
      ${h.select2('kogud_id', selected_id, kogu_opt, multiple=True)}
    </div>
  </div>
  % endif
  
  <div class="form-group row">
    ${ch.flb(_("Periood"),'f_periood_kood')}
    <div class="col-md-4">
      ${h.select('f_periood_kood', c.item.periood_kood,
      c.opt.klread_kood('PERIOOD', empty=True, vaikimisi=c.item.periood_kood), wide=False)}
    </div>
    ${ch.flb(_("Klass"), 'f_testiklass_kood', colextra='text-md-right')}
    <div class="col-md-4">
      ${h.select('f_testiklass_kood', c.item.testiklass_kood,
      c.opt.klread_kood('TESTIKLASS', empty=True), wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Kooliaste"),'aste_kood')}
    <div class="col-md-10">
      ${h.select_checkbox('aste_kood', c.item.kooliastmed, c.opt.astmed())}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Õppeaine"),'f_aine_kood', rq=True)}
    <div class="col-md-4">
      ${h.select('f_aine_kood', c.item.aine_kood, c.opt.klread_kood('AINE',
      empty=True, vaikimisi=c.item.aine_kood))}
    </div>
  </div>
  % if c.is_edit or c.item.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
  <div class="form-group row riigi">
    <div class="col-md-2"></div>
    <div class="col-md-10 d-flex flex-wrap align-content-end">
      <div class="flex-grow-1">
        ${self.testikursused()}
      </div>
      % if c.is_edit:
      <div>
        ${h.button(_("Lisa nimetus tunnistusel/kursus"), onclick="grid_addrow('tbl_testikursus',null,null,true); if($('.tunnaine').length==1) update_testikursus();toggle_kursus();", level=2)}
      </div>
      % endif
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${ch.flb(_("Nimetus"),'f_nimi', rq=True)}
    <div class="col-md-6">
      ${h.text('f_nimi', c.item.nimi)}
    </div>
    % if c.is_edit:
    <div class="col-md-4">
      ${h.button(_("Genereeri nimetus"), onclick="gen_title()", level=2)}
    </div>
    % endif
  </div>

  <div class="form-group row">
    ${self.testihinded()}      
    ${self.testitasemed()}
  </div>

  % if c.is_edit or c.item.diagnoosiv:
  <div class="form-group row">
    <div class="col-md-4"></div>
    <div class="col-md-10">
      ${h.checkbox('f_diagnoosiv', 1, checked=c.item.diagnoosiv, label=_("Diagnostiline test"), class_="diagnoosiv")}
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${ch.flb(_("Hindepallide arv"),'f_max_pallid')}
    <div class="col-md-2">
      ${h.float5('f_max_pallid', c.item.max_pallid or 0, ronly=True)}
      % if c.item.yhisosa_max_pallid:
      (${_("sh kursuste ühisosa")} ${h.fstr(c.item.yhisosa_max_pallid)})
      % endif
    </div>
    <div class="col-md-8">
      % if c.is_edit or not c.item.diagnoosiv:
      <div class="no-diag">
      <% if not c.item.id: c.item.ymardamine = True %>
      ${h.checkbox('f_ymardamine', 1, checked=c.item.ymardamine, label=_("Tulemus ümardatakse"))}
      <br/>
      ${h.checkbox('f_pallideta', 1, checked=c.item.pallideta, label=_("Tulemus pallideta"))}
      <br/>
      ${h.checkbox('f_protsendita', 1, checked=c.item.protsendita, label=_("Tulemust ei kuvata protsentides"))}
      </div>
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Vastuste näitamine"))}
    <div class="col-md-10">
      <div>
        ${h.checkbox1('f_osalemise_peitmine', 1, checked=c.item.osalemise_peitmine,
        label=_("Osalemine peidetakse sooritaja eest (testimiskorrata lahendamisel)"))}
      </div>
      <div>
        ${h.checkbox1('f_oige_naitamine', 1, checked=c.item.oige_naitamine,
        label=_("Õigete vastuste vaatamise võimalus oma tulemusi vaadates"))}
      </div>
      % if c.is_edit or not c.item.diagnoosiv:
      <div class="no-diag">
        ${h.checkbox1('f_arvutihinde_naitamine', 1, checked=c.item.arvutihinde_naitamine,
        label=_("Arvutihinnatav osa tulemusest näidatakse kohe peale sooritamist"))}
      </div>
      % endif
      <div>
        ${h.checkbox1('f_opetajale_peidus', 1, checked=c.item.opetajale_peidus,
        label=_("Õpetaja ei näe õpilase vastuseid (testimiskorrata lahendamisel)"))}
      </div>
      <div>
        ${h.checkbox1('f_vastus_tugiisikule', 1, checked=c.item.vastus_tugiisikule,
        label=_("Tugiisik võib näha sooritatud testi"))}
      </div>
      <div>
        ${h.checkbox1('f_tulemus_tugiisikule', 1, checked=c.item.tulemus_tugiisikule,
        label=_("Tugiisik võib näha tulemust"))}
      </div>
    </div>
  </div>
  
  % if c.test.avaldamistase in (const.AVALIK_POLE, const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD) and not eeltest:
  <div class="form-group row">
    ${ch.flb(_("Korduvalt sooritatavus"))}
    <div class="col-md-10">
      <div>
        ${h.checkbox('r_korduv_sooritamine', 1, checked=c.item.korduv_sooritamine,
        ronly=not c.is_edit or not c.can_update_korduv,
        label=_("Korduvalt sooritamise võimalus"))}
      </div>
      <div>
        ${h.checkbox('r_korduv_sailitamine', 1, checked=c.item.korduv_sailitamine,
        ronly=not c.is_edit or not c.can_update_korduv,
        label=_("Sooritaja varasemad sooritused säilitatakse (kui korduvalt sooritamine on lubatud)"))}
      </div>
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${ch.flb(_("Kvaliteedimärk"), 'ylkvaliteet')}
    <div class="col-md-10">
      % if c.user.has_permission('ylkvaliteet', const.BT_UPDATE, c.item):
      ${h.select2('kvaliteet_kood', c.item.kvaliteet_kood, c.opt.klread_kood('KVALITEET'), multiple=True, max_sel_length=1)}
      % else:
      ${c.item.kvaliteet_nimi}
      ${h.hidden('kvaliteet_kood', c.item.kvaliteet_kood)}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Autor"),'f_autor')}
    <div class="col-md-10">
      ${h.text('f_autor', c.item.autor, maxlength=128)}
    </div>
  </div>  

  <%
    c.lang_tm = True
    c.lang_ch = ch
  %>
  <%include file="/common/lang_div.mako" />

  <div class="form-group row">
    <div class="col-md-2"></div>
    <div class="col">
      ${h.checkbox1("f_ui_lang", 1, checked=c.item.ui_lang, label=_("Soorituskeelne kasutajaliides"))}
    </div>
  </div>

  <div class="form-group row">
    ${ch.flb(_("Märkused"),'f_markus')}
    <div class="col-md-10">
      ${h.ckeditor2('f_markus', c.item.markus, top_id='ckt_ckeditor_top')}      
    </div>
  </div>

  <div class="form-group row">
    ${ch.flb(_("Eristuskiri"),'ek_sisu')}
    <div class="col-md-10">
      <% ek = c.item.eristuskiri %>
      ${h.textarea('ek_sisu', ek and ek.sisu or '', rows=4)}
      <table>
        <tr>
      % if ek and ek.has_file:
      <td>${h.btn_to(_("Laadi alla"), h.url_current('download', format=ek.fileext, id=c.item.id))}</td>
      % endif
      % if c.is_edit:
      <td>${h.file('ek_filedata', value=_("Vali fail"))}</td>
      % endif
        </tr>
      </table>
    </div>
  </div>

% if c.item.on_tseis or c.item.aine_kood==const.AINE_ET2:

  <div class="form-group row">
    ${ch.flb(_("Tunnistuse väljastamise lävi"), 'f_lavi_pr')}
    <div class="col-md-2">
      ${h.posint5('f_lavi_pr', c.item.lavi_pr, maxvalue=100, maxlength=3)}%
    </div>
    <div class="col-lg-8 col-md-12 row">
      ${h.flb(_("Tulemuste protsendivahemikud"), 'tbl_vahemikud', col='col-md-4 text-md-right')}
      <div class="col-md-8">
        <table width="100%" id="tbl_vahemikud">
      <% 
           if not c.item.tulemuste_vahemikud_pr:
              c.item.tulemuste_vahemikud_pr = '1,50,60,76,91'
           values = c.item.tulemuste_vahemikud_pr.split(',') 
           algus = 0
           lopp = 100
        %>
        % for n in range(6):
        <tr>
          <td align="right">
            % if c.is_edit and n>0:
            ${h.posint('vahemikud-%d' % (n-1), algus, maxvalue=100, minvalue=1, maxlength=3, size=2)}
            % else:
            <span class="brown">${algus}</span>
            % endif
          </td>
          <td width="100">
            <% 
               if len(values) > n and values[n]: 
                  algus = int(values[n])
                  lopp = algus - 1 
               else:
                  if algus:
                     lopp = 100
                  algus = None
            %>
            -
            <span id="vahemikulopp" class="brown">${lopp}</span> %
          </td>
          <td>${const.VAHEMIK[n]}</td>
        </tr>
        % endfor
        </table>
      </div>
    </div>
  </div>
% endif

% if c.item.id:
  <div class="form-group row">
    ${ch.flb(_("Tähemärkide arv"))}
    <div class="col-md-10">
      % for lang in c.item.keeled:
      <% tr_item = lang == c.item.lang and c.item or c.item.tran(lang, False) %>
      % if tr_item and tr_item.tahemargid:
      <div>${model.Klrida.get_lang_nimi(lang)} <span class="brown">${_("{n} tähemärki").format(n=tr_item.tahemargid)}</span></div>
      % endif
      % endfor
    </div>
  </div>
% endif
</div>
${h.btn_back(url=h.url('testid'))}

% if c.item.id and c.can_update:
<%
  on_tk = model.SessionR.query(model.Testimiskord.id).filter_by(test_id=c.item.id).first()
  on_sj = model.SessionR.query(model.Sooritaja.id).filter_by(test_id=c.item.id).first()
%>
% if not (on_tk or on_sj):
${h.btn_remove()}
% elif eeltest:
${h.btn_to(_("Eemalda test"), h.url('delete_test', id=c.item.id, tkconfirmed=1), method='delete',confirm=_("Testil on testimiskordi või sooritajaid. Kas oled kindel, et soovid testi koos sooritustega kustutada?"), level=2)}
% endif

${h.btn_to(_("Kopeeri"), h.url('update_test',id=c.item.id, sub='kopeeri'), method='post', level=2)}
% if on_sj and eeltest:
${h.btn_to(_("Eemalda sooritajad"), h.url('delete_test', id=c.item.id, dsooritajad=1), method='delete', level=2)}
% endif
% endif

% if c.item.id and c.user.on_admin:
${h.btn_to(_("Ekspordi"), h.url_current('download', format='raw', id=c.item.id), level=2)}
% endif

% if c.is_edit:
${h.submit()}
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('test', id=c.item.id), method='get')}
%   endif
% elif c.can_update:
${h.btn_to(_("Muuda"), h.url('edit_test', id=c.item.id), method='get')}
% endif


${h.end_form()}

<script>
% if c.is_edit:
<%include file="yldandmed.js"/>
% endif
</script>

<%def name="testitasemed()">
% if c.is_edit or len(c.item.testitasemed):
<div class="col-12 col-lg-6 keeletase ${c.is_edit and 'd-none' or ''} row">
  ${h.flb(_("Keeleoskuse tase"), col="col-sm-12 col-md-2 col-lg-4 text-md-right")}
  <div class="col">
    <table width="100%">
        % if c.is_edit:
        <%
           testitasemed = list(c.item.testitasemed)
           if c.is_edit:
               while len(testitasemed) < 2:
                   testitasemed.append(c.new_item())
        %>
        % for n, r in enumerate(testitasemed):
        <% prefix = 't-%s' % n %>
        <tr>
          <td>
            ${h.select('%s.keeletase_kood' % prefix, r.keeletase_kood,
            c.opt.klread_kood('KEELETASE', c.item.aine_kood, empty=True,
            vaikimisi=r.keeletase_kood, ylem_required=True), wide=False, class_='keeletase')}
          </td>
          <td nowrap>
            % if c.is_edit or r.pallid is not None:
            ${_("kui tulemus vähemalt")}
            ${h.posint5('%s.pallid' % prefix, r.pallid)} %
            % endif
          </td>
        </tr>
        % endfor
        % else:
              % for n, r in enumerate(c.item.testitasemed):
              <tr>
                <td style="background:#fafafa">
                  ${r.keeletase_nimi}
                </td>
                <td nowrap>
                  % if r.pallid is not None:
                  ${_("kui tulemus vähemalt")} ${h.fstr(r.pallid)} %
                  % endif
                </td>
              </tr>
              % endfor       
        % endif
    </table>
  </div>
</div>
% endif
</%def>      

<%def name="testihinded()">
<div class="col-md-6 row m-0 p-0">
% if c.is_edit or len(c.item.testihinded):
<% ch = h.colHelper('col-md-4', 'col-md-8') %>
${ch.flb(_("Hinne"))}
<div class="col-md-8">
  <table width="100%">
              % if c.is_edit:
              % for n, hinne in enumerate(c.opt.HINNE):
              <%
                 prefix = 'h-%s' % n
                 r = c.item.get_testihinne(hinne) or c.new_item()
              %>
              <tr>
                <td class="px-3" style="background:#fafafa">
                  ${hinne}
                  ${h.hidden('%s.hinne' % prefix, hinne)}
                </td>
                <td nowrap>
                  % if c.is_edit or r.pallid is not None:
                  ${_("kui tulemus vähemalt")}
                  ${h.posint5('%s.pallid' % prefix, r.pallid)} %
                  % endif
                </td>
              </tr>
              % endfor
              % else:
              % for n, r in enumerate(c.item.testihinded):
              <tr>
                <td style="background:#fafafa">
                  ${r.hinne}
                </td>
                <td nowrap>
                  % if r.pallid is not None:
                  ${_("kui tulemus vähemalt")} ${h.fstr(r.pallid)} %
                  % endif
                </td>
              </tr>
              % endfor
              % endif
  </table>
</div>
% endif
</div>
</%def>      

<%def name="row_testikursus(item, prefix)">
      <tr>
        <td nowrap align="right" class="fr">
          ${_("Õppeaine nimetus tunnistusel")}
        </td>
        <td nowrap>
          ${h.select('%s.tunnaine_kood' % prefix, item.tunnaine_kood, 
            c.opt.klread_kood('TUNNAINE', c.item.aine_kood, empty=True,
            vaikimisi=item.tunnaine_kood, ylem_required=True), wide=False, class_='tunnaine')}
        </td>
        <%
           if c._arrayindexes != '':
              aine = request.params.get('f_aine_kood')
           else:
              aine = c.item.aine_kood
           opt_kursus = c.opt.klread_kood('KURSUS', aine,
                                          vaikimisi=item.kursus_kood, ylem_required=True)
           cls_kursus = len(opt_kursus) > 0 and 'kursus' or 'kursus d-none'
        %>
        <td align="right" class="fr ${cls_kursus}">
          ${_("Kursus")}
        </td>
        <td class="${cls_kursus}" nowrap>
            ${h.select('%s.kursus_kood' % prefix, item.kursus_kood,
            opt_kursus, wide=False, class_='kursus', onchange='toggle_kursus()')}
        </td>
        <td>
          % if item.max_pallid:
          ${h.fstr(item.max_pallid)}p
          % endif
        </td>
        <td>
          <%
             in_use = not c.is_edit
             if not in_use and item.kursus_kood:
                for testiosa in c.item.testiosad:
                   for alatest in testiosa.alatestid:
                      if alatest.kursus_kood == item.kursus_kood:
                         in_use = True
                         break
          %>
          % if not in_use:
          ${h.grid_remove()}
          % endif
          ${h.hidden('%s.id' % prefix, item.id)}         
        </td>
      </tr>
</%def>

<%def name="testikursused()">
      <table id="tbl_testikursus" class="table" border="0" > 
        <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get('testikursus') or []:
        ${self.row_testikursus(c.new_item(),'testikursus-%s' % (cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(c.item.testikursused):
        ${self.row_testikursus(item, 'testikursus-%s' % (cnt))}
  %   endfor
  % endif
        </tbody>
      </table>
      % if c.is_edit:
      <div id="sample_tbl_testikursus" class="d-none">
        <!--
            ${self.row_testikursus(c.new_item(),'testikursus__cnt__')}
          -->
      </div>
      % endif
</%def>
