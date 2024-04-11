<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'struktuur' %>
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Struktuur")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Struktuur"))}
</%def>
<%def name="require()">
<%
c.includes['ckeditor'] = True
c.includes['sortablejs'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>
<%def name="page_headers()">
<style>
  tr.tr-border-sortable>td {
    border-top: 1px #B22F16 dashed;
    border-bottom: 1px #B22F16 dashed;
  }
  tr.tr-border-sortable>td:first-child {
    border-left: 1px #B22F16 dashed;
  }
  tr.tr-border-sortable>td:last-child {
    border-right: 1px #B22F16 dashed;
  }
</style>
</%def>
<%include file="translating.mako"/>
<%
  if not c.item:
    if len(c.test.testiosad):
      c.item = c.test.testiosad[0]
  c.testiosa = c.item
  c.has_perm_t = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test)
  c.can_update = c.has_perm_t and c.test.staatus == const.T_STAATUS_KOOSTAMISEL  
  c.can_np = c.can_update # kas võib ylesandegruppe ja normipunkte muuta
  if c.item and c.test.diagnoosiv:
     for kv in c.item.komplektivalikud:
         for k in kv.komplektid:
             c.komplekt = k
             break
         break
%>

% if c.item and c.item.id:
${h.form_save(c.item.id, h.url('test_struktuur1', test_id=c.test.id, id=c.item.id))}
% else:
${h.form_save('')}
% endif

<div>
  ## testi nimetuse ja keelevaliku rida
      <div class="floatleft">
        ${h.lang_orig(c.test.nimi, c.test.lang)}<br/>
        % if c.lang:
           ${h.lang_tag()}
           ${c.test.tran(c.lang).nimi}
        % endif
      </div>

      % if not c.test.diagnoosiv:
      <div align="right" width="100%" class="brown">
              % if len(c.test.keeled) == 1:
              ${model.Klrida.get_str('SOORKEEL', c.test.lang)}
              % else:
                 % for lang in c.test.keeled:
                    % if lang == c.test.lang:
                     ${h.radio('lang', '', checked=not(c.lang), ronly=False, class_="nosave", label='%s (%s)' % (c.test.lang_nimi, _("põhikeel")))}
                    % else:
                    ${h.radio('lang', lang, checkedif=c.lang, ronly=False, class_="nosave",
                    label=model.Klrida.get_str('SOORKEEL', lang))}
                    % endif
                 % endfor
              <script>
                $(function(){
                 $('input[name=lang]').click(function(){
                 var lang = $(this).val();
                 var url = "${h.url('test_struktuur', test_id=c.test.id, lang='__LANG__')}".replace("__LANG__", lang);
                 window.location.replace(url);
                 });
                });
              </script>
              % endif
      </div>
      % endif
</div>

<div class="row mb-3">
  % if not c.test.diagnoosiv or len(c.test.testiosad) != 1:
  <div class="col-12 col-md-4 col-lg-2 bg-gray-50">
    ${self.list_testiosad()}
  </div>
  <div class="col-12 col-md-8 col-lg-10">
  % else:
  <div class="col-12">
  % endif
  % if c.item and c.item.id:
  % if c.test.diagnoosiv:
      % if c.can_update or c.is_tr:
      ${h.btn_to_dlg(_("Testiosa andmed"), h.url('test_edit_testiosa', test_id=c.test.id,
      id=c.item.id, lang=c.lang, partial=True, is_tr=c.is_tr), title=_("Testiosa andmed"), size='lg')}
      % else:
      ${h.btn_to_dlg(_("Testiosa andmed"), h.url('test_testiosa', test_id=c.test.id,
      id=c.item.id, lang=c.lang, partial=True, is_tr=c.is_tr), title=_("Testiosa andmed"), size='lg')}
      % endif
  % else:
      <% is_edit, c.is_edit, is_tr, c.is_tr = c.is_edit, False, c.is_tr, False %>
      <%include file="testiosa.sisu.mako"/>
      <% c.is_edit, c.is_tr = is_edit, is_tr %>
      ##<%include file="testiosa.show.mako"/>
      
      % if c.can_update or c.is_tr:
      ${h.btn_to_dlg(_("Muuda"), h.url('test_edit_testiosa', test_id=c.test.id,
      id=c.item.id, lang=c.lang, partial=True, is_tr=c.is_tr),
      title=_("Muuda testiosa andmeid"),
      dlgtitle=_("Testiosa andmed"), size='lg')}
      % endif

      % if c.can_update:
      ${h.btn_to(_("Eemalda"), h.url('test_delete_testiosa', test_id=c.test.id,
      id=c.item.id), method='delete')}      
      % endif
  % endif
  % endif
  </div>
</div>

% if c.item and c.item.id:
<div>
      % if c.test.is_encrypted:
      ${h.alert_notice(_("Test on krüptitud"))}
      % else:
    
        <% on_kursusi = False %>
        % for r in c.test.testikursused:
        % if r.kursus_kood:
        ${self.tbl_kursus(r.kursus_kood, r.kursus_nimi)}
        <br/>
        <% on_kursusi = True %>
        % endif
        % endfor

        % if on_kursusi:
        ${self.struktuurinupud()}
        % else:
        ${self.tbl_kursus(None, None)}
        % endif

        % if c.test.diagnoosiv:
        <div class="grupid-list" style="padding:5px 0">
          <%include file="ylesandegrupid_list.mako"/>
        </div>
        % endif

        % endif
</div>
% endif

${h.hidden('order', '')}
${h.end_form()}

% if c.dialog_testiosa:
  ${self.open_dialog('testiosa', '/ekk/testid/testiosa.mako', _("Testiosa andmed"), 'lg')}

% elif c.dialog_alatest:
  <% c.item = c.alatest %>
  ${self.open_dialog('alatest', '/ekk/testid/alatest.mako', _("Alatest"), 'lg')}

% elif c.dialog_testiplokk:
  <% c.item = c.testiplokk %>
  ${self.open_dialog('testiplokk', '/ekk/testid/testiplokk.mako', _("Testiplokk"), 'lg')}

% elif c.dialog_testiylesanne:
  <% c.item = c.testiylesanne %>
  ${self.open_dialog('testiylesanne', '/ekk/testid/testiylesanne.mako', _("Testiülesanne {s}").format(s=c.item.tahis), 'lg')}

% elif c.dialog_kinnita:
  ${self.open_dialog('kinnita', '/ekk/testid/kontroll.mako', _("Struktuuri kinnitamine"), 'lg')}

% endif

<%def name="list_testiosad()">
      <table width="100%" class="table table-borderless table-striped">
        <caption>${_("Testiosad")}</caption>
        <tbody>
        % if len(c.test.testiosad) == 0:
        <tr>
          <td style="color:#000000">${_("Testiosi pole kirjeldatud")}</td>
        </tr>
        % else:
          % for item in c.test.testiosad:
            % if c.item and item.id == c.item.id:
        <tr class="active">
            % else:
        <tr>
            % endif
          <td>${item.tahis}</td>
            <td>
              ${h.link_to(item.nimi, h.url('test_struktuur1',
              test_id=c.test.id, id=item.id, lang=c.lang))}
            </td>
        </tr>
          % endfor
        % endif
        </tbody>
      % if c.can_update:
        <tfoot>
          <tr>
            <td colspan="2" class="field_body">
          ${h.btn_to_dlg(_("Lisa testiosa"), h.url('test_new_testiosa',
          test_id=c.test.id, partial=True), title=_("Testiosa andmed"), size='lg')}
            </td>
          </tr>
        </tfoot>
      % endif
      </table>
</%def>

<%def name="tbl_kursus(kursus_kood, kursus_nimi)">
      <table class="table table-bordered ${c.test.diagnoosiv and 'multipleselect' or ''}">
         % if kursus_nimi:
        <caption>${kursus_nimi}</caption>
         % endif
        % if len(c.item.alatestid) == 0 and len(c.item.testiylesanded) == 0:
        <tr>
          <td>${_("Alateste, plokke ja testiülesandeid ei ole lisatud")}</td>
        </tr>

        % else:
        <thead>
        <tr>
          % if c.test.diagnoosiv:
          <th colspan="2">
            % if c.can_np:
            ${h.checkbox1('vy_all_id', 1, title=_("Vali kõik"))}
            % endif
          </th>
          <th>
            ${_("Jrk")}
          </th>
          <th>${_("ID")}</th>
          <th>${_("Nimetus")}</th>
          <th>${_("Teema")}</th>
          <th>${_("Ülesandetüüp")}</th>
          <th>${_("Märksõnad")}</th>
          <th>${_("Punktid")}</th>
          <th>${_("Koostaja")}</th>
          <th></th>
          % else:
          <th colspan="3">${_("Jrk")}</th>
          <th colspan="4">${_("Nimetus")}</th>
          <th style="white-space:nowrap">${_("Ül arv")}</th>
          <th nowrap>${_("Piiraeg")}</th>
          <th>${_("Punktid")}</th>
          <th></th>
          % endif
        </tr>
        </thead>
        <tbody class="sortables">
        <% c.row_cnt = -1 %>
        % if len(c.item.alatestid):
          % for alatest in c.item.alatestid:
          % if alatest.kursus_kood==kursus_kood:
          ${self.row_alatest(alatest)}
          % endif
          % endfor
        % else:
        ## otse testiosa all olevad ülesanded
          % for testiylesanne in c.item.testiylesanded:
             ${self.row_testiylesanne(testiylesanne)}
          % endfor
        % endif
        </tbody>
        % endif

% if c.can_update:
         <tfoot>
           <tr>
             <td class="field_body" colspan="11">
${h.btn_to_dlg(_("Lisa alatest"), h.url('test_testiosa_new_alatest',
test_id=c.test.id, testiosa_id=c.item.id, kursus_kood=kursus_kood, partial=True), title=_("Alatest"), size='lg')}

% if not c.item.on_alatestid and not kursus_kood:
## kui on alatestid, siis lisatakse ülesanded alatesti testiploki alla, mitte otse
## testiosa alla
% if c.test.diagnoosiv:
      ${h.btn_to_dlg(_("Lisa ülesandeid"), h.url('test_testiosa_otsiylesanded', 
      test_id=c.test.id, testiosa_id=c.item.id),
      title=_("Ülesanded"), size='lg')}
% else:
      ${h.btn_to_dlg(_("Lisa testiülesanne"), h.url('test_testiosa_new_testiylesanne',
      test_id=c.test.id, testiosa_id=c.item.id, partial=True),
      title=_("Ülesanne"), size='lg')}
% endif
% endif

    % if not kursus_kood:
    ${self.struktuurinupud()}
    % endif
             </td>
           </tr>
       </tfoot>
% endif       
      </table>
</%def>

<%def name="struktuurinupud()">
% if c.can_update:
  % if c.test.diagnoosiv:
     ${h.btn_to_dlg(_("Uus ülesandegrupp"), h.url('test_testiosa_new_ylesandegrupp',
      test_id=c.test.id, testiosa_id=c.item.id),
      title=_("Uus ülesandegrupp"), class_="addgrp d-none")}
     ${h.hidden('deltasks', '')}
     ${h.button(_("Eemalda ülesanded"), class_='button1 d-none deltasks',
         onclick="confirm_dialog('%s', function(){$('#deltasks').val('1'); $('form#form_save').submit();})" % _("Kas oled kindel, et soovid kustutada?"))}
  % endif
  % if c.is_debug and c.is_devel:
     ${h.hidden('deltasks2', '')}
     ${h.button(_("Kustuta ülesanded"), class_='button1',
     onclick="confirm_dialog('%s', function(){$('#deltasks2').val('1'); $('form#form_save').submit();})" % _("Kas oled kindel, et soovid kustutada?"))}
  % endif
  ${h.submit(_("Salvesta järjekord"), class_='button1 d-none', id='save_order')}
  ${h.btn_to_dlg(_("Kontrolli ja arvuta"), h.url('test_edit_struktuur1',
    test_id=c.test.id, id=c.item.id, sub='kontroll', partial=True),
    title=_("Kontrolli"))}
  ${h.btn_to(_("Kinnita struktuur"), h.url('test_edit_struktuur1',
      test_id=c.test.id, id=c.item.id, sub='kinnita', partial=True))}
% endif
</%def>

<%def name="row_alatest(alatest)">
        <% c.row_cnt += 1 %>
        <tr class="notselectable sortable ${c.can_update and 'tr-border-sortable' or ''}" id="alatest_${alatest.id}">
          <td nowrap>
            % if c.can_update:
            ${h.mdi_icon('mdi-drag-vertical', title=_("Lohista järjekorra muutmiseks"))}            
            % endif
            ${alatest.tahis}
          </td>
          <td colspan="2"></td>
          % if c.test.diagnoosiv:
          <td></td>
          % endif
          <td colspan="4">
            <b>${_("Alatest")}: 
              ${alatest.tran(c.lang).nimi}
            </b>
            % if alatest.alatest_kood:
              (${alatest.alatest_nimi})
            % endif
            % if alatest.testivaline:
            (${_("Küsimustik")})
            % endif
            <% rvosaoskus = alatest.rvosaoskus %>
            % if rvosaoskus:
            <br/>${_("osaoskus tunnistusel")}:
            % if rvosaoskus.rveksam_id == c.test.rveksam_id:
            ${rvosaoskus.nimi}
            % else:
            <div class="error">${_("puudub")}</div>
            % endif
            % endif
            (${alatest.ylesannete_arv})
          </td>
          % if not c.test.diagnoosiv:
          <td>${alatest.ylesannete_arv}</td>
          <td style="white-space:nowrap">
            % if alatest.piiraeg:
            max ${h.str_from_time_sec(alatest.piiraeg)}
            % endif
          </td>
          % endif
          <td>${h.fstr(alatest.max_pallid)}</td>
          % if c.test.diagnoosiv:
          <td></td>
          % endif
          <td nowrap>
         % if c.can_update or c.is_tr:

            ${h.btn_to_dlg('', h.url('test_testiosa_edit_alatest',
            test_id=c.test.id, testiosa_id=c.item.id, id=alatest.id, lang=c.lang,
            partial=True, is_tr=c.is_tr),
            title=_("Muuda"), dlgtitle=_("Alatest"), size='lg', level=0, mdicls='mdi-file-edit')}
         % else:
            ${h.btn_to_dlg(_("Vaata"), h.url('test_testiosa_alatest',
            test_id=c.test.id, testiosa_id=c.item.id, id=alatest.id, lang=c.lang,
            partial=True, is_tr=c.is_tr), title=_("Alatest"), size='lg', level=2)}         
         % endif

         % if c.can_update:
         % if not c.test.diagnoosiv:
            ${h.btn_to_dlg(_("Lisa testiplokk"), h.url('test_testiosa_new_testiplokk',
            test_id=c.test.id, testiosa_id=c.item.id, alatest_id=alatest.id,
            partial=True), title=_("Testiplokk"), size='lg', level=2)}
         % endif
         % if len(alatest.testiplokid) == 0:
         % if c.test.diagnoosiv:
         ${h.btn_to_dlg(_("Lisa ülesandeid"), h.url('test_testiosa_otsiylesanded', 
         test_id=c.test.id, testiosa_id=c.item.id, alatest_id=alatest.id),
         title=_("Ülesanded"), size='lg', level=2)}
         % else:
         ${h.btn_to_dlg(_("Lisa testiülesanne"), h.url('test_testiosa_new_testiylesanne',
         test_id=c.test.id, testiosa_id=c.item.id, alatest_id=alatest.id, partial=True),
         title=_("Ülesanne"), size='lg', level=2)}
         % endif
         % endif
            ${h.remove(h.url('test_testiosa_delete_alatest', test_id=c.test.id,
            testiosa_id=c.item.id, id=alatest.id))}
         % endif

            ${h.hidden('s-%s.id' % c.row_cnt, alatest.id, id="id")}
            ${h.hidden('s-%s.type' % c.row_cnt, 'alatest', id="type")}
          </td>
        </tr>

        % if len(alatest.testiplokid):
          % for testiplokk in alatest.testiplokid:
              ${self.row_testiplokk(testiplokk, alatest)}
          % endfor
        % else:
        ## otse testiosa all olevad ülesanded
          % for testiylesanne in alatest.testiylesanded:
              ${self.row_testiylesanne(testiylesanne)}
          % endfor
        % endif
</%def>

<%def name="row_testiplokk(testiplokk, alatest)">
        <% c.row_cnt += 1 %>
        <tr class="notselectable sortable ${c.can_update and 'tr-border-sortable' or ''}" id="testiplokk_${testiplokk.id}">
          <td>
            % if c.can_update:
            ${h.mdi_icon('mdi-drag-vertical', title=_("Lohista järjekorra muutmiseks"))}            
            % endif
          </td>
          <td>${testiplokk.seq}</td>
          <td></td>
          % if c.test.diagnoosiv:
          <td></td>
          % endif
          <td style="padding-left:20px" colspan="5">
            <b>${_("Plokk")}: 
              ${testiplokk.tran(c.lang).nimi}</b>
            (${testiplokk.ylesannete_arv})
          </td>
          <td>${h.fstr(testiplokk.max_pallid)}</td>
          <td></td>
          <td nowrap>
          % if c.can_update or c.is_tr:

            ${h.btn_to_dlg('', h.url('test_testiosa_edit_testiplokk',
            test_id=c.test.id, testiosa_id=c.item.id, alatest_id=testiplokk.alatest_id, lang=c.lang,
          id=testiplokk.id, partial=True, is_tr=c.is_tr),
          title=_("Muuda"), mdicls='mdi-file-edit',
          dlgtitle=_("Testiplokk"), size='lg', level=0)}
          % endif

          % if c.can_update:
          % if c.test.diagnoosiv:
          ${h.btn_to_dlg(_("Lisa ülesandeid"), h.url('test_testiosa_otsiylesanded', 
          test_id=c.test.id, testiosa_id=c.item.id, alatest_id=alatest.id, testiplokk_id=testiplokk.id),
          title=_("Ülesanded"), size='lg', level=2)}
          % else:
          ${h.btn_to_dlg(_("Lisa testiülesanne"), h.url('test_testiosa_new_testiylesanne',
          test_id=c.test.id, testiosa_id=c.item.id, alatest_id=alatest.id, testiplokk_id=testiplokk.id,partial=True),
          title=_("Ülesanne"), size='lg', level=2)}
          % endif
          % endif

            ${h.hidden('s-%s.id' % c.row_cnt, testiplokk.id, id="id")}
            ##${h.hidden('s-%s.seq' % c.row_cnt, testiplokk.seq, id="seq")}
            ${h.hidden('s-%s.type' % c.row_cnt, 'testiplokk', id="type")}
            ${h.hidden('s-%s.alatest_id' % c.row_cnt, testiplokk.alatest_id,
            id="alatest_id")}

          % if c.can_update:
            ${h.remove(h.url('test_testiosa_delete_testiplokk', test_id=c.test.id,
            testiosa_id=c.item.id, id=testiplokk.id))}
          % endif
          </td>
        </tr>
          % for testiylesanne in testiplokk.testiylesanded:
              ${self.row_testiylesanne(testiylesanne)}
          % endfor
</%def>

<%def name="row_testiylesanne(testiylesanne)">
<% c.row_cnt += 1 %>
% if c.test.diagnoosiv:
${self.row_testiylesanne_y(testiylesanne)}
% else:
${self.row_testiylesanne_ty(testiylesanne)}
% endif
</%def>

<%def name="row_testiylesanne_ty(testiylesanne)">
## mitme komplektiga tavalise testi korral
<tr class="sortable ${c.can_update and 'tr-border-sortable' or ''}" id="testiylesanne_${testiylesanne.id}">
  <td colspan="2">
    <!--${testiylesanne.alatest_seq}-->
    % if c.can_update:
    ${h.mdi_icon('mdi-drag-vertical', title=_("Lohista järjekorra muutmiseks"))}            
    % endif
  </td>
          <td>
            % if c.is_debug and c.is_devel:
            ${h.checkbox('ty_id', testiylesanne.id, checked=False, ronly=False, title=_("Vali rida"))}
            % endif
            ${testiylesanne.tahis}
          </td>
          <td style="padding-left:40px" colspan="5">
            ${testiylesanne.liik_nimi}
            ${testiylesanne.tran(c.lang).nimi}
            % if testiylesanne.yhisosa_kood:
            [${testiylesanne.yhisosa_kood}]
            % endif
            % if testiylesanne.valikute_arv > 1:
            (${testiylesanne.valikute_arv})
            % endif
            <br/>
            ${testiylesanne.hindamine_nimi or ''}
            % if testiylesanne.arvutihinnatav:
            (${_("arvutiga hinnatav")})
            % endif
            ${testiylesanne.aste_nimi or ''}
            ${testiylesanne.teema_nimi or ''}
            ${testiylesanne.alateema_nimi or ''}
            ${testiylesanne.mote_nimi or ''}

            ${testiylesanne.tyyp_nimi or ''}

            % if testiylesanne.kasutusmaar is not None:
            ${_("Kasutusmäär")}: ${h.fstr(testiylesanne.kasutusmaar) or ''}
            % endif
          </td>
          <td style="white-space:nowrap">
            % if testiylesanne.piiraeg:
            <div>max
              ${h.str_from_time_sec(testiylesanne.piiraeg)}
              ##${h.str2_from_timedelta(testiylesanne.piiraeg)}
            </div>
            % endif
            % if testiylesanne.min_aeg:
            <div>min
              ${h.str_from_time_sec(testiylesanne.min_aeg)}
              ##${h.str2_from_timedelta(testiylesanne.min_aeg)}
            </div>
            % endif
          </td>
          <td>${h.fstr(testiylesanne.max_pallid)}</td>
          <td nowrap>
            % if c.can_update:
            ${h.btn_to_dlg('', h.url('test_testiosa_edit_testiylesanne',
            test_id=c.test.id, testiosa_id=c.item.id, id=testiylesanne.id,
            lang=c.lang, is_tr=c.is_tr, partial=True),
            title=_("Muuda"), mdicls='mdi-file-edit',
            dlgtitle=_("Testiülesanne {s}").format(s=testiylesanne.tahis), size='lg', level=0)}
            % else:
            ${h.btn_to_dlg(_("Vaata"), h.url('test_testiosa_testiylesanne',
            test_id=c.test.id, testiosa_id=c.item.id, id=testiylesanne.id,
            lang=c.lang, is_tr=c.is_tr, partial=True), title=_("Testiülesanne {s}").format(s=testiylesanne.tahis), size='lg', level=2)}
            % endif
            ${self.del_row_testiylesanne(testiylesanne)}
          </td>
        </tr>
</%def>

<%def name="row_testiylesanne_y(testiylesanne)">
## yhe komplektiga lihtsa testi korral (diagnoosiv test)
<%
  vy = c.komplekt and c.komplekt.get_valitudylesanne(None, testiylesanne.id)
  ylesanne = vy and vy.ylesanne
  %>
<tr class="tr-ty ${c.can_update and 'sortable tr-border-sortable' or 'notselectable'}" id="testiylesanne_${testiylesanne.id}">
  <td colspan="2"><!--${testiylesanne.alatest_seq}-->
    % if c.can_update:
    ${h.mdi_icon('mdi-drag-vertical', title=_("Lohista järjekorra muutmiseks"))}            
    % endif
    % if vy:
    ${h.checkbox('vy_id', vy.id, ronly=not c.can_np, class_="selectrow nosave", label=_("Vali rida"))}
    % endif
  </td>
  <td>${testiylesanne.tahis}</td>
  % if ylesanne:
  <td>${ylesanne.id}
    % if testiylesanne.on_jatk:
    (${_("jätk")})
    % endif
  </td>
  <td>
    % if not c.user.has_permission('ylesanded', const.BT_SHOW, obj=ylesanne):
    ${ylesanne.nimi}
    % else:
    ${h.link_to(ylesanne.nimi, url=h.url('ylesanne', id=ylesanne.id))}
    % endif
  </td>
  <td>
    % for yaine in ylesanne.ylesandeained:
    ${'<br/>'.join(['%s | %s' % (r.teema_nimi or '', r.alateema_nimi or '') for r in yaine.ylesandeteemad])}
    % endfor
  </td>
  <td>
    ${'<br/>'.join(sorted(set([sp.tyyp_nimi for sp in ylesanne.sisuplokid if sp.is_interaction])))}
  </td>
  <td>${ylesanne.marksonad}</td>
  <td>${h.fstr(testiylesanne.max_pallid)}
    % if testiylesanne.max_pallid != ylesanne.max_pallid:
    (${h.fstr(ylesanne.max_pallid)})
    % endif
  </td>
  <td>${'<br/>'.join(ylesanne.koostaja_nimed)}</td>
  % else:
  <td colspan="7">${_("Ülesanne on valimata")}</td>
  % endif
  <td>
    % if c.can_update and not c.is_tr:
    ${h.btn_to_dlg('', h.url('test_testiosa_edit_testiylesanne',
    test_id=c.test.id, testiosa_id=c.item.id, id=testiylesanne.id,
    lang=c.lang, is_tr=c.is_tr, partial=True),
    title=_("Muuda"), mdicls='mdi-file-edit',
    dlgtitle=_("Testiülesanne {s}").format(s=testiylesanne.tahis or ''), size='lg', level=0)}
    % endif
    ${self.del_row_testiylesanne(testiylesanne)}
  </td>
</tr>
</%def>

<%def name="del_row_testiylesanne(testiylesanne)">
${h.hidden('s-%s.id' % c.row_cnt, testiylesanne.id, id="id")}
##${h.hidden('s-%s.seq' % c.row_cnt, testiylesanne.seq, id="seq")}
${h.hidden('s-%s.type' % c.row_cnt, 'testiylesanne', id="type")}
% if testiylesanne.testiplokk:
${h.hidden('s-%s.alatest_id' % c.row_cnt,
testiylesanne.testiplokk.alatest_id, id="alatest_id")}
${h.hidden('s-%s.testiplokk_id' %
c.row_cnt,testiylesanne.testiplokk_id, id="testiplokk_id")}
% endif
% if c.can_update:
${h.remove(h.url('test_testiosa_delete_testiylesanne', test_id=c.test.id,
testiosa_id=c.item.id, id=testiylesanne.id))}
% endif
</%def>

% if c.can_update:
<script>
  <%include file="struktuur.js"/>
</script>
% endif
