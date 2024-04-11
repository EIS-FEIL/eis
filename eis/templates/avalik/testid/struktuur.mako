<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'struktuur' %>
<%include file="tabs.mako"/>
</%def>
<%def name="page_title()">
% if c.item.on_jagatudtoo:
${c.item.nimi or ''} | ${_("Töö sisu")}
% else:
${c.item.nimi or ''} | ${_("Testi sisu")}
% endif
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))} 
${h.crumb(c.item.nimi or _('Test'))} 
% if c.item.on_jagatudtoo:
${h.crumb(_('Töö sisu'))}
% else:
${h.crumb(_('Testi sisu'))}
% endif
</%def>
<%def name="require()">
<%
c.includes['ckeditor'] = True
c.includes['fancybox'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<%def name="page_headers()">
<style>
div.yk {
  margin: 3px 0px;
}
div.yk-title {
  border-radius: 3px;
  background-color: #efefef;
  padding: 3px;
  cursor: pointer;
}
div.yk-title .glyphicon {
    color: #e4882a;
    padding-right:2px;
}

div.ykg {
  margin: 3px 0px;
  padding-left: 5px;

}
div.ykg-title {
  border-radius: 3px;
  background-color: #fff;
  padding: 3px;
  cursor: pointer;
}
div.ykg-title .glyphicon {
  color: #e4882a;
  padding-right:2px;
}
div.ykg-items {
  display: none;
  padding-left: 6px;
}
</style>
</%def>

<% 
   kv = c.testiosa.give_komplektivalik()
   hkogum = kv.get_default_hindamiskogum()
   c.can_edit = c.user.has_permission('testid', const.BT_UPDATE, c.item)
%>

<% c.testiosavalik_action = h.url_current('show') %>
<%include file="testiosavalik.mako"/>

${h.form_save(c.item.id)}

<div class="p-3">
  <div class="row">
    ${h.flb3(_("Hindepallide arv"), 'max_pallid')}
    <div class="col-md-3">
      <div style="width:100px">${h.roxt(h.fstr(c.testiosa.max_pallid))}</div>
    </div>
    % if hkogum and hkogum.arvutihinnatav:
    <div class="col">
      ${_("Üleni arvutihinnatav test")}
    </div>
    % endif
  </div>
  <div class="row">
    ${h.flb3(_("Juhised sooritajale"),'f_sooritajajuhend')}
    <div class="col-md-9">
    % if c.is_edit:
      ${h.textarea('f_sooritajajuhend', c.testiosa.sooritajajuhend, class_="editable")}
    <script>
$(function(){
    var inputs = $('#f_sooritajajuhend.editable');
    init_ckeditor(inputs, 'osa_ckeditor_top', '${request.localizer.locale_name}', 'basic', null, 50);
});
    </script>
    <div style="height:0">
      <div id="osa_ckeditor_top" class="ckeditor-top-float"></div>
    </div>
      % else:
    <div class="readonly">${c.testiosa.sooritajajuhend}</div>
     % endif
    </div>
  </div>
  % if c.is_edit or c.testiosa.yhesuunaline:
  <div class="row">
    <div class="col">
      ${h.checkbox('f_yhesuunaline', 1, checked=c.testiosa.yhesuunaline,
      label=_("Ühesuunaline lahendamine"))}
    </div>
  </div>
  % endif
  % if c.is_edit or c.testiosa.yl_segamini:
  <div class="row">
    <div class="col">
      ${h.checkbox('f_yl_segamini', 1, checked=c.testiosa.yl_segamini,
      label=_("Ülesannete segamine"))}
    </div>
  </div>
  % endif
</div>


<% on_jatk = False %>
<table class="table" >
  <caption>${_("Ülesanded")}</caption>
  % if len(c.testiosa.testiylesanded) == 0:
  <tr>
    <td>${_("Ülesandeid ei ole lisatud")}</td>
  </tr>
  % else:
  <thead>
    <tr>
      <th nowrap>${_("Jrk")}</th>
      <th>${_("Nimetus")}</th>
      <th>${_("Hindepalle")}</th>
      <th>${_("Arvutiga hinnatav")}</th>
      <th>${_("Soorituskeel")}</th>
      <th></th>
    </tr>
  </thead>
  <tbody id="sortables">
    <%
      kv_komplekt = {}
      for kv in c.testiosa.komplektivalikud:
          for k in kv.komplektid:
              if k.staatus == const.K_STAATUS_KINNITATUD:
                 kv_komplekt[kv.id] = k
                 break
      c.row_cnt = -1
    %>
    % if c.testiosa.on_alatestid:
    % for alatest in c.testiosa.alatestid:
    <% komplekt = kv_komplekt.get(alatest.komplektivalik_id) %>
    % for testiylesanne in alatest.testiylesanded:
    <% if testiylesanne.on_jatk: on_jatk = True %>
    ${self.row_testiylesanne(testiylesanne, komplekt)}
    % endfor
    % endfor
    % else:
    <% komplekt = kv_komplekt and list(kv_komplekt.values())[0] or None %>
    % for testiylesanne in c.testiosa.testiylesanded:
    <% if testiylesanne.on_jatk: on_jatk = True %>
    ${self.row_testiylesanne(testiylesanne, komplekt)}
    % endfor
    % endif
  </tbody>
  % endif
</table>
% if on_jatk and c.test.diagnoosiv:
<div style="padding:2px">
  ${_("*Õpilasele kuvatakse ülesanne sõltuvalt eelnevale ülesandele antud vastusest")}
</div>
% endif

<div class="mt-3 d-flex flex-wrap">
  % if c.can_edit:
  ${h.btn_to_dlg(_('Lisa ülesanne'), h.url('test_ylesanded', test_id=c.item.id, testiruum_id=c.testiruum_id),
  title=_('Ülesannete valimine'), size='lg', mdicls='mdi-plus')}
  % endif

  <div class="text-right flex-grow-1">
  % if not c.is_edit:
  % if c.can_edit:
  ${h.btn_to(_('Muuda'), h.url_current('edit'), method='get')}
  % endif
  % else:
  ${h.btn_to(_('Vaata'), h.url_current('show'), method='get', level=2)}
  ${h.submit()}
  % endif
  </div>
</div>
${h.hidden('order', '')}
${h.end_form()}

% if c.dialog_ylesanne:
  ${self.open_dialog('ylesanded', 'ylesanded.mako', _('Ülesannete valimine'))}
% endif

</p>

<%def name="row_testiylesanne(testiylesanne, komplekt)">
        <% 
           c.row_cnt += 1 
           prefix = 'ty-%d' % c.row_cnt
           vy = komplekt and testiylesanne.get_valitudylesanne(komplekt) or None
           ylesanne = vy and vy.ylesanne or None
        %>
  % if not c.is_edit:
        <tr id="testiylesanne_${testiylesanne.id}">
  % else:
        <tr class="sortable" id="testiylesanne_${testiylesanne.id}">
  % endif
  
           <td>
             % if testiylesanne.on_jatk:
             <span title=_("Õpilasele kuvatakse ülesanne sõltuvalt eelnevale ülesandele antud vastusest")>${testiylesanne.seq}*</span>
             % else:
             ${testiylesanne.seq}
             % endif
           </td>
  % if not c.is_edit:
          <td>
  % else:
          <td class="border-sortable">
            ${h.mdi_icon('mdi-drag-vertical', title=_("Lohista järjekorra muutmiseks"))}            
  % endif
  % if ylesanne and c.user.has_permission('avylesanded', const.BT_SHOW, obj=ylesanne):
           ${h.link_to(ylesanne.nimi, h.url('ylesanded_lahendamine', id=ylesanne.id), target='_blank')}
  % elif ylesanne and c.user.has_permission('lahendamine', const.BT_VIEW, obj=ylesanne):
            ${h.link_to(ylesanne.nimi, h.url('lahendamine1', id=ylesanne.id), target='_blank')}  
  % elif ylesanne:
            ${ylesanne.nimi}
  % else:
            <i>${_("Ülesanne puudub")}</i>
  % endif
          </td>
          <td>
            % if c.item.on_jagatudtoo and ylesanne and ylesanne.on_tagasiside and ylesanne.on_pallid == False:
            ${_("Tulemus protsentides")}
            % elif ylesanne and ylesanne.pallemaara:
            ${h.float5('%s.max_pallid' % prefix, testiylesanne.max_pallid)}
            ${h.hidden('%s.id' % prefix, testiylesanne.id)}
            % else:
            ${h.fstr(testiylesanne.max_pallid)}
            % endif
          </td>
          <td>
  % if ylesanne:
            ${h.sbool(ylesanne.arvutihinnatav)}
  % endif
          </td>
          <td>
            % if ylesanne and ylesanne.skeeled:
            % for lang in sorted(ylesanne.keeled, key=lambda l: l not in const.LANG_ORDER and l or const.LANG_ORDER.index(l)):
            ${model.Klrida.get_lang_nimi(lang)}
            % endfor
            % endif
          </td>
          <td nowrap>
  % if c.can_edit:
            ${h.remove(h.url('test_delete_ylesanne', test_id=c.item.id, testiruum_id=c.testiruum_id, id=testiylesanne.id))}
  % endif
          </td>
        </tr>
</%def>

% if c.is_edit:
<script>
  $(function(){
    $("#sortables").sortable({
         containment: 'parent',
         axis: 'y',
         update: function(event, ui){
            $('input[name=order]')[0].value = $("#sortables").sortable("toArray");
          }
     });
    ##$("#sortables").disableSelection();
  })
</script>
% endif
