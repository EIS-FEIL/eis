<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Materjalide väljastus"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['before_subtabs'] = True
%>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="draw_before_subtabs()">
<% c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.test) %>
<div>
  <h2 class="float-left nowrap mb-2">${_("Testi korraldamiseks vajalike dokumentide loomine ja väljastus")}</h2>
  % if request.is_ext():
  <div class="float-right">
    ${h.link_to(_("Eritingimused"), h.url('muud_erivajadused',
    toimumisaeg_id=c.toimumisaeg.id), target='_blank')}
  </div>
  % endif
</div>
<div style="clear:both"></div>
<div class="container">
<div class="row">
  <div class="col-12 col-md-6 col-lg-4">
    ${self.action_table()}
  </div>
  <div class="col-12 col-md-6 col-lg-8">
    ${self.total_table()}
  </div>
</div>
</div>

% if c.kontroll_err or c.kontroll_ok:
<div class="my-1">
  % if c.kontroll_err:
${h.alert_error(c.kontroll_err)}
  % else:
${h.alert_notice(c.kontroll_ok)}
  % endif
</div>
% endif
</%def>

<%def name="draw_subtabs()">
<div id="subtabs_pos"></div>
<%namespace name="tab" file='/common/tab.mako'/>
% if c.toimumisaeg.on_hindamisprotokollid:
<% current_tab = c.subtab %>
% if c.toimumisaeg.on_ymbrikud:
${tab.subdraw('valjastusymbrikud', h.url('korraldamine_valjastus_valjastusymbrikud', toimumisaeg_id=c.toimumisaeg.id), _("Väljastusümbrikud"), current_tab)}
${tab.subdraw('tagastusymbrikud', h.url('korraldamine_valjastus_tagastusymbrikud', toimumisaeg_id=c.toimumisaeg.id), _("Tagastusümbrikud"), current_tab)}
% endif
${tab.subdraw('protokollid', h.url('korraldamine_valjastus_protokollid', toimumisaeg_id=c.toimumisaeg.id), _("Protokollid ja nimekirjad"), current_tab)}
% if c.toimumisaeg.on_ymbrikud:
${tab.subdraw('turvakotikleebised', h.url('korraldamine_valjastus_turvakotikleebised', toimumisaeg_id=c.toimumisaeg.id), _("Turvakottide kleebised"), current_tab)}
${tab.subdraw('turvakotiaktid', h.url('korraldamine_valjastus_turvakotiaktid', toimumisaeg_id=c.toimumisaeg.id), _("Turvakottide aktid"), current_tab)}
% endif
${tab.subdraw('lisatingimused', h.url('korraldamine_valjastus_lisatingimused', toimumisaeg_id=c.toimumisaeg.id), _("Lisatingimused"), current_tab)}
% endif
</%def>


% if c.toimumisaeg.on_hindamisprotokollid:
<%include file="valjastus_pdf.mako"/>
% endif

<%def name="action_table()">
  <table class="table">
    <tr>
      <td>
        % if c.can_update:
        ${h.form(h.url('korraldamine_valjastus', toimumisaeg_id=c.toimumisaeg.id), method='post')}
        ${h.hidden('sub', 'kogused')}
        ${h.submit(_("Arvuta kogused"))}
        <br/>
        ${h.checkbox('sailitakoodid', 1, checked=c.sailitakoodid, label=_("Säilita olemasolevad koodid"))}
        <br/>
        ${h.checkbox('sordi', 1, checked=c.sordi, label=_("Järjesta sooritajad nime järgi"))}            
        <script>
          $(function(){
          $('input#sailitakoodid').click(function(){ $('input#sordi').prop('checked', false);});
          $('input#sordi').click(function(){ $('input#sailitakoodid').prop('checked', false);});              
          });
        </script>
        ${h.end_form()}
        % else:
        ${h.flb(_("Koguste arvutamine"),'kogustearvutus')}
        % endif
      </td>
      <td id="kogustearvutus">
        ${c.toimumisaeg.on_kogused and _("tehtud") or _("tegemata")}
      </td>
    </tr>
    <tr>
      <td>
        ${h.btn_to(_("Loo hindamiskirjed"), h.url('korraldamine_valjastus',
        toimumisaeg_id=c.toimumisaeg.id, sub='hindamisprotokollid'), method='post',
        disabled=not c.toimumisaeg.on_kogused)}
      </td>
      <td class="raam">
        ${c.toimumisaeg.on_hindamisprotokollid and _("tehtud") or _("tegemata")}
      </td>
    </tr>
    % if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
    <tr>
      <td>
        ${h.btn_to(_("Loo ümbrikud ja turvakotid"), h.url('korraldamine_valjastus',
        toimumisaeg_id=c.toimumisaeg.id, sub='ymbrikud'), method='post',
        disabled=not c.toimumisaeg.on_hindamisprotokollid)}
      </td>
      <td>
        ${c.toimumisaeg.on_ymbrikud and _("tehtud") or _("tegemata")}
      </td>
    </tr>
    % endif
    <tr>
      <td colspan="2">
        ${h.btn_to(_("Kontrolli"), h.url('korraldamine_valjastus',
        toimumisaeg_id=c.toimumisaeg.id, op='kontrolli'), method='get')}
      </td>
    </tr>
  </table>
</%def>

<%def name="total_table()">
<div class="row">
<table class="table table-borderless table-striped col-md-12">
        <thead>
          <tr>
            ${h.th(_("Kuupäev"))}
            ${h.th(_("Ruumide arv"))}
            ${h.th(_("Sooritajate arv"))}
          </tr>
        </thead>
        <tbody>
          % for (kpv,cnt, lang_cnt) in c.kpv_cnt:
          <tr>
            % if kpv:
            <td>${h.str_from_date(kpv)}</td>
            % else:
            <td>${_("Määramata")}</td>
            % endif
            <td>${cnt}</td>
            <td>
              % for lang_nimi, cnt in lang_cnt:
              <div>${lang_nimi}: ${cnt}</div>
              % endfor
            </td>
          </tr>
          % endfor
        </tbody>
  </table>


% if c.toimumisaeg.on_ymbrikud:
<% 
   v_liigid = [liik.tahis for liik in c.toimumisaeg.valjastusymbrikuliigid] 
   t_liigid = [liik.tahis for liik in c.toimumisaeg.tagastusymbrikuliigid]
   test = c.toimumisaeg.testiosa.test
%>
      <table class="table table-borderless table-striped col-md-12">
% if len(v_liigid) > 0:
          <tr>
            ${h.th(_("Keel"))}
            ${h.th(_("Kursus"))}
            ${h.th(_("Ümbriku liik"))}
            ${h.th(_("Väljastatavate ümbrike arv"))}
            ${h.th(_("Väljastatavate tööde arv"))}
          </tr>
          % for lang in c.toimumisaeg.testimiskord.get_keeled():
          % for kursus in test.get_kursused() or [None]:
          % for liik_tahis in v_liigid:
          <% kogused = c.v_kogused.get((lang,kursus,liik_tahis)) or (0,0) %>
          <tr>
            <td nowrap>${model.Klrida.get_lang_nimi(lang)}</td>
            <td nowrap>${model.Klrida.get_str('KURSUS', kursus, ylem_kood=test.aine_kood)}</td>
            <td>${liik_tahis}</td>
            <td>${kogused[0]}</td>
            <td>${kogused[1]}</td>
          </tr>
          % endfor
          % endfor
          % endfor
% else:
          <tr>
            <td colspan="4">${_("Väljastusümbrikuliike pole kirjeldatud")}</td>
          </tr>
% endif

% if len(t_liigid) > 0:
          <tr>
            ${h.th(_("Keel"))}
            ${h.th(_("Kursus"))}
            ${h.th(_("Ümbriku liik"))}
            ${h.th(_("Tagastatavate ümbrike arv"))}
            ${h.th(_("Sooritajate arv"))}
          </tr>

          % for lang in c.toimumisaeg.testimiskord.get_keeled():
          % for kursus in test.get_kursused() or [None]:
          % for liik_tahis in t_liigid:
          <% kogused = c.t_kogused.get((lang,liik_tahis)) or (0,0) %>
          <tr>
            <td nowrap>${model.Klrida.get_lang_nimi(lang)}</td>
            <td nowrap>${model.Klrida.get_str('KURSUS', kursus, ylem_kood=test.aine_kood)}</td>
            <td>${liik_tahis}</td>
            <td>${kogused[0]}</td>
            <td>${kogused[1]}</td>
          </tr>
          % endfor
          % endfor
          % endfor
% else:
          <tr>
            <td colspan="4">${_("Tagastusümbrikuliike pole kirjeldatud")}</td>
          </tr>
% endif
      </table>


      <table class="table table-borderless table-striped col-md-12">
        <thead>
          <tr>
            ${h.th(_("Keel"))}
            ${h.th(_("Väljastatavate turvakottide arv"))}
            ${h.th(_("Tagastatavate turvakottide arv"))}
          </tr>
        </thead>
        <tbody>
          % for lang in c.toimumisaeg.testimiskord.get_keeled():
          <% kogused = c.kogused.get(lang) or (0,0) %>
          <tr>
            <td nowrap>${model.Klrida.get_lang_nimi(lang)}</td>
            <td>${kogused[0]}</td>
            <td>${kogused[1]}</td>
          </tr>
          % endfor
        </tbody>
      </table>
</div>

      % if request.is_ext():
      % if c.sisestamata_valjastuskotid:
      <div class="alert alert-danger alert-dismissable fade show">
      ${h.link_to(_("{n} väljastuskoti numbrid on sisestamata").format(n=c.sisestamata_valjastuskotid),
        h.url('sisestamine_turvakotinumbrid', toimumisaeg_id=c.toimumisaeg.id, suund=const.SUUND_VALJA), target='_blank')}.
      </div>
      % endif

      % if c.sisestamata_tagastuskotid:
      <div class="alert alert-danger alert-dismissable fade show">
        ${h.link_to(_("{n} tagastuskoti numbrid on sisestamata").format(n=c.sisestamata_tagastuskotid),
        h.url('sisestamine_turvakotinumbrid', toimumisaeg_id=c.toimumisaeg.id, suund=const.SUUND_TAGASI), target='_blank')}.
      </div>
      % endif
      % endif

% endif
</%def>
