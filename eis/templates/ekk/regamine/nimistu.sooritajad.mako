## -*- coding: utf-8 -*- 
<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'sooritajad' %>
<%include file="nimistu.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))} 
${h.crumb(_("Registreerimise taotluse sisestamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

## enne faili yleslaadimist
${h.form_save(None, h.url('regamine_nimistu_create_sooritajad', korrad_id=c.korrad_id), multipart=True)}
${h.hidden('testiliik', c.testiliik)}
${h.hidden('debug', c.debug)}
<div class="p-2">
  <div class="form-group row">
    ${h.flb3(_("Faili veerud"))}
    <div class="col-md-9">
      ${h.checkbox('col', 'isikukood', checked=True, disabled=True, label=_("isikukood"))}
      ${h.checkbox('col', 'epost', label=_("e-posti aadress"))}
      ${h.checkbox('col', 'aadress', label=_("aadress"))}
      ${h.checkbox('col', 'test_id', label=_("testi ID"))}      
      ${h.checkbox('col', 'lang', label=_("soorituskeel"))}      
      <script>$('input[name="col"][value="isikukood"]').prop('checked', true);</script>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Sooritajate fail"))}
    <div class="col-md-9">
      ${h.file('ik_fail', value=_("Fail"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      ${h.radio('tyhistada', '', checked=not c.tyhistada, label=_("Registreerida sooritajad"))}
      ${h.radio('tyhistada', 1, label=_("Tühistada sooritajate registreeringud"))}
    </div>
  </div>
  <div class="form-group row regamine">
    <div class="col">
  % if c.testiliik != const.TESTILIIK_KUTSE:
      ${h.checkbox('muutmatu', 1, label=_("Kool ei või registreeringuid muuta ega tühistada"))}
      <br/>
      ${h.checkbox('tyhistamatu', 1, label=_("Kool ei või registreeringuid tühistada"))}
      <br/>
      ${h.checkbox('valimis', 1, label=_("Testimiskorrasisese valimi sooritajad"))}
      <br/>      
  % endif
    </div> 
  </div>
  <div class="form-group row tyhistamine" style="display:none">
    ${h.flb3(_("Tühistamise põhjus"))}
    <div class="col-md-9">
      ${h.textarea('pohjus', '')}      
    </div>
  </div>
</div>

<table class="table">
  <thead>
    <tr>
      ${h.th(_("Toimumisaeg"))}
      ${h.th(_("Toimumispäev"))}
      ##, class_="fixtp", style="display:none")}
      ${h.th(_("Soorituskoht"))}
      ${h.th(_("Algus"))}
    </tr>
  </thead>
  <tbody>
    <% ind = 0 %>
    % for n_kord, kord in enumerate(c.korrad):
    % for ta in kord.toimumisajad:
    <tr>
      <td>
        ${ta.tahised}
        <%
          prefix = 'tadata-%d' % ind
          ind += 1
        %>
        ${h.hidden(prefix + '.ta_id', ta.id)}
      </td>
      <td>
                <%
                  opt_tp = ta.get_toimumispaevad_opt()
                %>
                % if opt_tp:
                ${h.select(prefix + '.toimumispaev_id', '', opt_tp, empty=_("Määratakse hiljem"), wide=False)}
                % else:
                <i>${_("Toimumispäevi pole veel määratud")}</i>
                % endif
      </td>
      <td>
                <%
                  opt_tk = ta.get_testikohad_opt()
                  testikoht_id = len(opt_tk) == 1 and opt_tk[0][0] or None
                  
                %>
                % if opt_tk:
                ${h.select(prefix + '.testikoht_id', testikoht_id, opt_tk, empty=_("Määratakse hiljem"), class_="testikoht", wide=False)}
                % else:
                <i>${_("Soorituskohti pole veel määratud")}</i>
                % endif
      </td>
      <td>
                % if opt_tk:
                <span class="testikell" class="invisible">
                  ${h.time(prefix + '.kell', '', wide=False)}
                </span>
                % endif
      </td>
    </tr>
    % endfor
    % endfor
  </tbody>
</table>
<script>
        $('select.testikoht').change(function(){
           $(this).closest('tr').find('.testikell').toggleClass('invisible', !$(this).val());
        });
        $('select.testikoht').each(function(){
           $(this).closest('tr').find('.testikell').toggleClass('invisible', !$(this).val());
        });
</script>

<div class="d-flex flex-wrap mb-3">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('regamine_nimistu_edit_yksikasjad', korrad_id=c.korrad_id, testiliik=c.testiliik, lang=c.lang),
    level=2, mdicls='mdi-arrow-left-circle')}
  </div>
  <div>
    % if c.arvutusprotsessid:
    ${h.submit(_("Laadi veel üks fail"), mdicls2='mdi-arrow-right-circle')}
    % else:
    ${h.submit(_("Laadi fail"), mdicls2='mdi-arrow-right-circle')}
    % endif
  </div>
</div>
${h.end_form()}

<%
  c.url_refresh = h.url('regamine_nimistu_sooritajad_protsessid', korrad_id=c.korrad_id, testiliik=c.testiliik, sub='progress')
  c.protsessid_next = lambda protsess_id: h.url('regamine_nimistu_edit_lisavalikud', korrad_id=c.korrad_id, protsess_id=protsess_id)
  c.protsessid_caption = _("Registreerimisnimekirja laadimine")
  c.protsessid_no_pager = True
%>
<%include file="/common/arvutusprotsessid.mako"/>

<script>
  function toggle_t(){
    var t = $('input[name="tyhistada"][value="1"]').prop('checked');
    $('.regamine').toggle(!t);
    $('.tyhistamine').toggle(t);
  }
  $(function(){
    $('input[name="tyhistada"]').click(toggle_t);
    toggle_t();
  });
</script>
