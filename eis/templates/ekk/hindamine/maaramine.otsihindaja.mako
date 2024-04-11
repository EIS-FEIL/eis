${h.form_search()}
${h.hidden('sub','otsihindaja')}
${h.hidden('partial','true')}

% if c.on_hindaja or c.on_hindaja3:
% for hindamiskogum_id in c.hk_id:
${h.hidden('hk_id', hindamiskogum_id)}
% endfor
${h.hidden('lang', c.lang)}
${h.hidden('planeeritud_toode_arv', c.planeeritud_toode_arv)}
${h.hidden('kasutaja1_id', c.kasutaja1_id)}
${h.hidden('valimis', c.valimis and '1' or '')}
% endif

<h2>
% if c.on_hindaja3:
${_("Kolmanda hindaja valik")}
% elif c.on_suunamine:
${_("Uue hindaja valik")}
% elif c.on_hindaja:
  % if c.otsihindaja1_2st:
${_("Esimese hindaja valik")}
  % elif c.kasutaja1_id:
  ${_("Teise hindaja valik")}
  % else:
  ${_("Hindaja valik")}
  % endif
% endif
</h2>
<%include file="/common/message.mako"/>

% if c.test.testityyp == const.TESTITYYP_AVALIK:
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-6 col-lg-6">
      <div class="form-group">
        ${h.flb(_("Isikukood"), 'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
<%
   uri = h.url_current('index')
   uri += uri.find('?') > -1 and '&' or '?'
%>
      ${h.button(_("Otsi"), onclick="var url='%s'+$(this.form).serialize();dialog_load(url);" % uri)}
      </div>
    </div>
  </div>
</div>
% else:
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col">
      <div class="form-group">    
        ${h.flb(_("Nimi"), 'nimi')}
        <div>
          ${h.text('nimi', '')}
        </div>
      </div>
    </div>
  </div>
  <script>
          ## nime sisestamisel piiratakse tulemuste loetelu
          $('input#nimi').keyup(function(){
            var value = $(this).val().toUpperCase();
            $('.tr-list').each(function(){
               $(this).toggle($(this).find('.name').text().toUpperCase().indexOf(value) > -1);
            });
          });
  </script>
</div>
% endif

${h.end_form()}

${h.form_save(None, form_name='form_otsihindaja')}

% if c.on_hindaja and c.kasutaja1_id:
${h.hidden('sub', 'otsihindajapaar')}
% else:
${h.hidden('sub', 'otsihindaja')}
% endif

% if c.on_suunamine: 
## III hindamise sakk või suunamise sakk
${h.hidden('hindamised_id', c.hindamised_id)}
<script>
  $(document).ready(function(){
    var f = $('#hindamine1_id:checked');
    var buf = "";
    for(var i=0; i<f.length; i++) buf += ','+f.eq(i).val();
    $('#hindamised_id').val(buf);
  });
</script>
% elif c.on_hindaja or c.on_hindaja3:

## I ja II hindamise sakk
${h.hidden('kasutaja1_id', c.kasutaja1_id)}
% for hindamiskogum_id in c.hk_id:
${h.hidden('hk_id', hindamiskogum_id)}
% endfor
${h.hidden('lang', c.lang)}
${h.hidden('planeeritud_toode_arv', c.planeeritud_toode_arv)}
${h.hidden('valimis', c.valimis and '1' or '')}
% endif

% if len(c.items):
<table width="100%"  class="table table-borderless table-striped">
  <col width="20px"/>
  <thead>
  <tr>
    <th></th>
    ${h.th(_("Läbiviija"))}
    % if c.test.testityyp == const.TESTITYYP_EKK:
    ${h.th(_("Märkused"))}
    % endif
  </tr>
  </thead>
  <tbody>
  % for rcd in c.items:
  <%
    k = rcd
  %>
  <tr class="tr-list">
    <td>
      % if c.otsihindaja1_2st:
      ${h.button(_("Vali"), onclick="choose(%s)" % k.id)}
      % elif c.kasutaja1_id or c.test.testityyp == const.TESTITYYP_AVALIK:
      ${h.submit(_("Vali"), id='kasutaja_%s' % k.id)}
      % else:
      ${h.checkbox('kasutaja_%s' % k.id, class_="vali", onclick="toggle_vali()")}
      % endif
    </td>
    <td class="name">${k.nimi}</td>
    % if c.test.testityyp == const.TESTITYYP_EKK:    
    <td>${k.markus}</td>
    % endif
  </tr>
  % endfor
  </tbody>
</table>
% elif c.items != '':
${_("Sobivaid isikuid ei leitud")}
% endif

% if c.on_hindaja and c.otsihindaja1_2st:
<script>
function choose(kasutaja1_id)
{
  $('form#form_otsihindaja input[name="kasutaja1_id"]').val(kasutaja1_id);
  var data = $('form#form_otsihindaja').serialize();
<%
   uri = h.url_current('index')
   uri += uri.find('?') > -1 and '&' or '?'
%>
  var url='${uri}' + data;
  dialog_load(url);
}
</script>
% else:
<script>
  function toggle_vali()
  {
         var visible = ($('input:checked.vali').length > 0);
         $('div#add').toggleClass('invisible', !visible);
  }
</script>
<div id="add" class="invisible text-right">
  % if c.vali1v2 and not c.on_hindaja3:
  ${h.submit(_("Vali I hindaja"), name="vali1")}
  ${h.submit(_("Vali II hindaja"), name="vali2")}
  % else:
  ${h.submit(_("Vali"), name="vali")}
  % endif
</div>
% endif

${h.end_form()}
