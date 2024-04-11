<%include file="/common/message.mako"/>
${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', c.sub)}

<%
  li_ained = [c.new_item()]
  prefix = 'ya'
  if c._arrayindexes != '':
     ya_indexes = c._arrayindexes.get('ya')
     li_ained = [li_ained[n] for n in ya_indexes if n < len(li_ained)]
     while len(ya_indexes) > len(li_ained):
        li_ained.append(c.new_item())
%>
<div class="ylesandeained" id="tblaine" counter="${len(li_ained)}">
  % if c._arrayindexes != '':
  ## valideerimisvigade korral
  % for cnt in c._arrayindexes.get(prefix) or []:
     ${self.row_aine(c.new_item(), prefix, '-%s' % (cnt))}
  % endfor
  % else:
  % for cnt, item in enumerate(li_ained):
    ${self.row_aine(item, prefix, '-%s' % cnt)}
  % endfor
  % endif
</div>
<div class="table" style="background-color:#fff">
  <div class="pull-right">${h.button(_("Lisa õppeaine"), onclick="grid_addrow('tblaine')")}</div>
  <div id="sample_tblaine" class="invisible sample">
<!--   ${self.row_aine(c.new_item(), prefix, '__cnt__')} -->
  </div>
</div>

${h.submit_dlg()}
${h.end_form()}

<%def name="row_aine(item, baseprefix, cnt)">
<%
  prefix = '%s%s.' % (baseprefix, cnt)
  is_main_subject = cnt == '-0'
%>
<div class="form ylesandeaine">
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      % if is_main_subject:
      ${_("Põhiõppeaine")}
      % else:
      ${_("Õppeaine")}
      % endif
    </div>
    <div class="col-sm-6 col-xs-7">
      <% aine_opt = c.opt.klread_kood('AINE') %>
      ${h.select(prefix + 'aine_kood', item.aine_kood, aine_opt, empty=True, class_="aine")}
    </div>
    
    <div class="col-sm-4 col-xs-1 frh seotud">
      % if c.is_edit and not is_main_subject:
      ${h.grid_s_remove('div.ylesandeaine', confirm=True)}
      % endif
      ${h.hidden(prefix + 'id', item.id)}
    </div>
  </div>
  % if c.sub == 'teema':
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      ${_("Teema")}
    </div>
    <div class="col-sm-10 col-xs-8 div-teemad">
      % if c.is_edit:
      <%
        opt_teemad = c.opt.teemad2(item.aine_kood, c.aste_kood)
      %>
      ${h.select2(prefix + 'teemad2', item.teemad2, [], data=opt_teemad, multiple=True, multilevel=True, template_selection='template_selection2', class_="teemad2")}
      % else:
      <% ylesandeteemad = list(item.ylesandeteemad) %>
      % if ylesandeteemad:
      <div class="div-teemad">
        <table width="100%" id="teemad" border="0" >
          <tbody>
            % for r in ylesandeteemad:
            <tr class="uline"><td>${r.teema_nimi}</td><td>${r.alateema_nimi}</td></tr>
            % endfor
          </tbody>
        </table>
      </div>
      % endif
      % endif
    </div>
  </div>

  % elif c.sub == 'opitulemus':
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      ${_("Õpitulemus")}
    </div>
    <div class="col-sm-10 col-xs-8 div-teemad">
      % if c.is_edit:
      <%
        opt_opitulemused = c.opt.opitulemused(item.aine_kood)
      %>
      ${h.select2(prefix + 'opitulemused', item.opitulemused_idd, [], data=opt_opitulemused, multiple=True, multilevel=True, class_="opitulemused")}
      % else:
      % for yo in item.ylopitulemused:
      ${h.roxt(yo.opitulemus_klrida.nimi)}
      % endfor
      % endif
    </div>
  </div>
  % endif
</div>
</%def>

% if c.sub == 'teema':
<script>
function template_selection2(n){
    // viimane tase
    var divs = '<div class="col-sm-6">' + n.text + '</div>';
    if(n.p_text)
    {
        // teise taseme korral lisame esimese taseme
        divs = '<div class="col-sm-6">' + n.p_text + '</div>' + divs;
    }
    return $('<div class="row">' + divs + '</div>');
}
function update_teemad(el_teemad2, aine)
{
    if(!aine)
    {
        aine = el_teemad2.closest('div.ylesandeaine').find('select.aine').val();
    }
    var aste = $('#f_aste_kood').val();
    var data = {'aine': aine, 'aste': aste};
    var url = "${h.url('pub_formatted_valikud', kood='TEEMA2', format='json')}";
    $.getJSON(url, data,
                     function(data){
                         var old_value = el_teemad2.val();
                         el_teemad2.empty();
                         ${h.select2_js(None, old_value, [], data='data', multiple=True, multilevel=True, template_selection='template_selection2', element='el_teemad2')}
                         el_teemad2.val(old_value).trigger('change.select2');
                     });
}
$(function(){
  $('div.ylesandeained').on('change', 'select.aine', function(){
    var div_aine = $(this).closest('div.ylesandeaine');
    var aine = $(this).val();
    var el_teemad2 = div_aine.find('.teemad2');
    update_teemad(el_teemad2, aine);
  });
});
</script>

% elif c.sub == 'opitulemus':
<script>
function update_opitulemused(el_opitulemused, aine)
{
    ## peale õppeaine muutmist muudame opitulemuste valiku
    var data = {'aine': aine};
    var url = "${h.url('pub_formatted_valikud', kood='OPITULEMUS2', format='json')}";
    $.getJSON(url, data,
                     function(data){
                         var old_value = el_opitulemused.val();
                         el_opitulemused.empty();
                         ${h.select2_js(None, old_value, [], data='data', multiple=True, multilevel=True, element='el_opitulemused')}
                         el_opitulemused.val(old_value).trigger('change.select2');
                     });
}
$(function(){
  $('div.ylesandeained').on('change', 'select.aine', function(){
    var div_aine = $(this).closest('div.ylesandeaine');
    var aine = $(this).val();
    var opitul = div_aine.find('.opitulemused');
    update_opitulemused(opitul, aine);
  });
});
</script>
% endif
