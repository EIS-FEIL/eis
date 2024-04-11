<%inherit file="/common/page.mako"/>
<%def name="require()">
<% c.includes['ckeditor'] = True %>
</%def>
<%def name="page_title()">
${_("Klassifikaatorid")} | ${c.item.nimi}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Klassifikaatorid"), h.url('admin_klassifikaatorid', lang=c.lang))} 
${h.crumb(c.item.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%
  if c.item.kood in ('OPITULEMUS','OPIAINE'):
     c.is_edit = False
  ch = h.colHelper('col-md-3 text-md-right', 'col-md-9')
%>
${h.form_save(c.item.kood)}
<div class="form-wrapper-lineborder">
  <div class="form-group row">
    ${ch.flb(_("Kood"), 'kood')}
    <div class="col-md-9" id="kood">
      ${c.item.kood}

      % if c.item.kood == 'AINE':
      <div class="float-right">
        ${h.btn_to(_("Klassifikaatorite vastavus (oppekava.edu.ee)"), h.url('admin_edit_ainevastavus', kl2='OPIAINE', id='AINE'))}
        ${h.btn_to(_("Klassifikaatorite vastavus (EHIS)"), h.url('admin_edit_ainevastavus', kl2='EHIS_AINE', id='AINE'))}        
      </div>
      % elif c.item.kood == 'OPIAINE':
      <div class="float-right">
        ${h.btn_to(_("Klassifikaatorite vastavus"), h.url('admin_edit_ainevastavus', kl2='OPIAINE', id='AINE'))}
      </div>
      % elif c.item.kood == 'EHIS_AINE':
      <div class="float-right">
        ${h.btn_to(_("Klassifikaatorite vastavus"), h.url('admin_edit_ainevastavus', kl2='EHIS_AINE', id='AINE'))}
      </div>
      % endif      
    </div>
  </div>

  <div class="form-group row">
    ${ch.flb(_("Nimi"), 'f_nimi')}
    <div class="col-md-9">
      % if c.lang == const.LANG_XX or not c.lang:
      ${h.text('f_nimi', c.item.nimi)}
      % else:
        ${c.item.nimi}
        <br/>
        <% tran = c.item.tran(c.lang, False) %>
        ${h.text('f_nimi', tran and tran.nimi or '')}
      % endif
    </div>
  </div>

  <div class="form-group row">
    <div class="col-md-3"></div>
    <div class="col-md-9">
      ${h.checkbox('f_kehtib', value=1, checked=c.item.kehtib, label=_("Kehtiv"))}
    </div>
  </div>

% if c.item.ylem_kood:
  ${self.filter1(ch, c.item)}
% elif c.item.kood == 'ERIVAJADUS':
  ${self.filter_erivajadus(ch, c.item)}    
% elif c.item.kood == 'OPITULEMUS':
  ${self.filter_opitulemus(ch, c.item)}
% endif

    % if c.item.kood == 'HTUNNUS':
  <div class="form-group row">
    ${ch.flb(_("Klass"), 'testiklass')}
    <div class="col-md-9">
      ${h.select('testiklass', c.testiklass, c.opt.klread_kood('TESTIKLASS'))}
    </div>
  </div>
    % elif c.item.kood == 'NULLIPOHJ':
  <div class="form-group row">
    ${ch.flb(_("Õppeained, mille korral on nulli põhjus e-testi hindamisel kasutusel"), 'nullipaine')}
    <div class="col-md-9">
      ${h.select2('nullipaine', c.opt.nullipained, c.opt.klread_kood('AINE'), multiple=True)}
    </div>
  </div>
    % endif
</div>

<%def name="filter2(ch, item, target_kood)">
## vanavanema filter, valiku tegemisel täidetakse vanem filtri select-väli
  <div class="form-group row">
    ${ch.flb(item.ylem.nimi, 'ylem_id2')}
    <div class="col-md-9">
      ${h.select('ylem_id2', c.ylem_id2, 
                 c.opt.klread_id(item.ylem_kood, empty=True), 
                 class_='nosave', 
                 ronly=False)}
  <script>
$(document).ready(function(){
  $('select#ylem_id2').change(function(){
    $('#griddiv').html('');
  }).change(
    callback_select("${h.url('pub_formatted_valikud', kood=target_kood, format='json')}", 
                   'ylem_id', 
                   $('select#ylem_id'), 
                   {'byid':1})
  );
});
  </script>
    </div>
  </div>
</%def>

<%def name="filter1(ch, item)">
## vanema filter, valiku tegemisel kuvatakse tabel klassifikaatoriridadest
  % if item.ylem.ylem_kood:
    ## kaks vanemate taset

    ## esmalt kuvame vanavanema
    ${self.filter2(ch, item.ylem, item.ylem_kood)}
    &nbsp;
    
    ## siis kuvame vanema
  <div class="form-group row">
    <%
      if c.lang == const.LANG_XX:
         label = item.ylem.nimi
      else:
         tran = item.ylem.tran(c.lang, False) 
         label = tran and tran.nimi or ''
    %>
    ${ch.flb(label, 'ylem_id')}
    <div class="col-md-9">
    % if c.ylem_id2:
       ## kui vanavanem on valitud
       ${h.select('ylem_id', c.ylem_id, 
                  c.opt.klread_id(item.ylem_kood, ylem_id=c.ylem_id2, empty=True),
                  class_='nosave', ronly=False)}
    % else:
       ## kui vanavanemat pole valitud
       ${h.select('ylem_id', c.ylem_id, [], class_='nosave', ronly=False)}

    % endif
    </div>
  </div>

  % else:
    ## ainult yks vanema tase
  <div class="form-group row">
    <%
      if c.lang == const.LANG_XX:    
         label = item.ylem.nimi
      else:
         tran = item.ylem.tran(c.lang, False)
         label = tran and tran.nimi or ''
    %>
    ${ch.flb(label, 'ylem_id')}
    <div class="col-md-9">
    <%
       opt_ylem = c.opt.klread_id(item.ylem_kood)
    %>
    ${h.select('ylem_id', c.ylem_id, opt_ylem, empty=True, class_='nosave', ronly=False)}
    </div>
  </div>
  % endif

<script>
$(document).ready(function(){
  $('select#ylem_id,select#testiklass').change(refresh_klread);
});

function refresh_klread(){
   var fld = $('select#ylem_id');
% if item.kood == 'KEELETASE':
   if(true)
% else:
   if(fld.val())
% endif
   {
% if c.is_edit:
     var url="${h.url('admin_klread', edit=True, partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&ylem_id="+fld.val();
% else:
     var url="${h.url('admin_klread', partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&ylem_id="+fld.val();
% endif
% if item.kood == 'HTUNNUS':
     url += "&testiklass=" + $('select#testiklass').val();
% endif
     url = url + '&r='+String(Math.random()).substr(2);
     ajax_url(url, 'GET', $('#griddiv'));
   }
   else
   {
     $('#griddiv').html('');
   }
}
</script>
</%def>

<%def name="filter_opitulemus(ch, item)">
## Õppeaine filter
  <div class="form-group row">
    ${ch.flb(_("Õppeaine (oppekava.edu.ee)"), 'ylem_id')}
    <div class="col-md-9">
    <%
       opt_ylem = c.opt.klread_id('OPIAINE')
    %>
    ${h.select('ylem_id', c.ylem_id, opt_ylem, empty=True, class_='nosave', ronly=False)}
    </div>
  </div>
<script>
$(function(){
  $('select#ylem_id,select#testiklass').change(refresh_klread);
});

function refresh_klread(){
   var fld = $('select#ylem_id');
   if(fld.val())
   {
% if c.is_edit:
     var url="${h.url('admin_klread', edit=True, partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&ylem_id="+fld.val();
% else:
     var url="${h.url('admin_klread', partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&ylem_id="+fld.val();
% endif
     url = url + '&r='+String(Math.random()).substr(2);
     ajax_url(url, 'GET', $('#griddiv'));
   }
   else
   {
     $('#griddiv').html('');
   }
}
</script>
</%def>

<%def name="filter_erivajadus(ch, item)">
## vanema filter, valiku tegemisel kuvatakse tabel klassifikaatoriridadest
  <div class="form-group row">
    ${ch.flb(_("Kooliaste"),'aste')}
    <div class="col-md-9">
    ${h.select('aste', c.aste, ((const.ASTE_BIT_III, _("Põhikool")),(const.ASTE_BIT_G, u'Gümnaasium'),(const.ASTE_BIT_I, u'Muu')),
    empty=True, class_='nosave', ronly=False)}
    </div>
  </div>

<script>
$(document).ready(function(){
  $('select#aste').change(refresh_klread);
});

function refresh_klread(){
   var fld = $('select#aste');
% if c.is_edit:
     var url="${h.url('admin_klread', edit=True, partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&aste="+fld.val();
% else:
     var url="${h.url('admin_klread', partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&aste="+fld.val();
% endif
     url = url + '&r='+String(Math.random()).substr(2);
     ajax_url(url, 'GET', $('#griddiv'));
}
</script>
</%def>

<span id="message"></span>
<div id="griddiv" width="100%">
% if c.items != '':
<%include file="klread.mako"/>
% endif
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
% if c.is_edit:
${h.button(_("Lisa"), id="lisa", onclick="grid_addrow('gridtbl')", level=2, mdicls='mdi-plus')}

% endif

${h.btn_back(url=h.url('admin_klassifikaatorid', lang=c.lang))}
  </div>
  <div>
% if c.user.on_admin:
${h.btn_to(_("Eksport"), h.url('admin_klassifikaator_format', id=c.item.kood, format='raw'), level=2)}
% endif
% if c.is_edit:
${h.submit()}
% endif
  </div>
</div>
${h.end_form()}
