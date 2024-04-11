<%inherit file="/common/page.mako"/>
<%def name="require()">
<% c.includes['ckeditor'] = True %>
</%def>
<%def name="page_title()">
${_("Klassifikaatorid")} | ${c.item.nimi} (${c.lang})
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Klassifikaatorid"), h.url('admin_tklassifikaatorid', lang=c.lang))} 
${h.crumb('%s (%s)' % (c.item.nimi, c.lang))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
${h.form_save(c.item.kood)}
<table class="table" >
  <tbody>
    <tr>
      <td width="100px" class="fh">${_("Kood")}</td>
      <td width="90%">${c.item.kood}</td>
    </tr>
    <tr>
      <td class="fh">${_("Nimi")}</td>
      <td nowrap>
        ${c.item.nimi}
        <br/>
        <% tran = c.item.tran(c.lang, False) %>
        ${h.text('f_nimi', tran and tran.nimi or '')}
      </td>
    </tr>
    <tr>
      <td class="fh">${_("Tõlkekeel")}</td>
      <td nowrap>
        ${model.Klrida.get_str('SOORKEEL', c.lang)}
      </td>
    </tr>
    <tr>
      <td class="fh">${_("Kehtiv")}</td>
      <td>${h.sbool(c.item.kehtib)}</td>
    </tr>
% if c.item.ylem_kood:
  ${self.filter1(c.item)}
% elif c.item.kood == 'ERIVAJADUS':
  ${self.filter_erivajadus(c.item)}    
% endif
  </tbody>
</table>
<%def name="filter2(item, target_kood)">
## vanavanema filter, valiku tegemisel täidetakse vanem filtri select-väli
<tr>
  <td class="fh">${item.ylem.nimi}</td>
  <td>
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
  </td>
</tr>
</%def>

<%def name="filter1(item)">
## vanema filter, valiku tegemisel kuvatakse tabel klassifikaatoriridadest
  % if item.ylem.ylem_kood:
    ## kaks vanemate taset

    ## esmalt kuvame vanavanema
    ${self.filter2(item.ylem, item.ylem_kood)}
    &nbsp;
    
    ## siis kuvame vanema
<tr>
  <td class="fh">
    ${item.ylem.nimi}
    % if c.lang != const.LANG_XX:
    <br/>
    <% tran = item.ylem.tran(c.lang, False) %>
    ${tran and tran.nimi or ''}
    % endif
  </td>
  <td>
    % if c.ylem_id2:
       ## kui vanavanem on valitud
       ${h.select('ylem_id', c.ylem_id, 
                  c.opt.klread_id(item.ylem_kood, ylem_id=c.ylem_id2, empty=True),
                  class_='nosave', ronly=False)}
    % else:
       ## kui vanavanemat pole valitud
       ${h.select('ylem_id', c.ylem_id, [], class_='nosave', ronly=False)}

    % endif
  </td>
</tr>
  % else:
    ## ainult yks vanema tase
<tr>
  <td class="fh">
    ${item.ylem.nimi}
    % if c.lang != const.LANG_XX:
    <br/>
    <% tran = item.ylem.tran(c.lang, False) %>
    ${tran and tran.nimi or ''}
    % endif
   
  </td>
  <td>
    ${h.select('ylem_id', c.ylem_id, c.opt.klread_id(item.ylem_kood),
empty=True, class_='nosave', ronly=False)}
  </td>
</tr>
  % endif

<script>
$(document).ready(function(){
  $('select#ylem_id').change(refresh_klread);
});

function refresh_klread(){
   var fld = $('select#ylem_id');
   if(fld.val())
   {
% if c.is_edit:
     var url="${h.url('admin_tklread', edit=True, partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&ylem_id="+fld.val();
% else:
     var url="${h.url('admin_tklread', partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&ylem_id="+fld.val();
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

<%def name="filter_erivajadus(item)">
## vanema filter, valiku tegemisel kuvatakse tabel klassifikaatoriridadest
<tr>
  <td class="fh">${_("Kooliaste")}</td>
  <td>
    ${h.select('aste', c.aste, ((const.ASTE_BIT_III, _("Põhikool")),(const.ASTE_BIT_G, u'Gümnaasium'),(const.ASTE_BIT_I, u'Muu')),
    empty=True, class_='nosave', ronly=False)}
  </td>
</tr>

<script>
$(document).ready(function(){
  $('select#aste').change(refresh_klread);
});

function refresh_klread(){
   var fld = $('select#aste');
% if c.is_edit:
     var url="${h.url('admin_tklread', edit=True, partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&aste="+fld.val();
% else:
     var url="${h.url('admin_tklread', partial=True, klassifikaator_kood=item.kood, lang=c.lang)}&aste="+fld.val();
% endif
     url = url + '&r='+String(Math.random()).substr(2);
     ajax_url(url, 'GET', $('#griddiv'));
}
</script>
</%def>

<span id="message"></span>
<div id="griddiv" width="100%">
% if c.items != '':
<%include file="tklread.mako"/>
% endif
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_back(url=h.url('admin_tklassifikaatorid', lang=c.lang))}
  </div>
  <div>
    % if c.is_edit:
    ${h.submit()}
    % endif
  </div>
</div>

${h.end_form()}
