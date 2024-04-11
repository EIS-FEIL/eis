<% c.krit = c.item or c.new_item() %>
<%include file="/common/message.mako"/>
${h.form_save(c.krit.id, class_="nodirty")}
<%
  c.opt_aspektid = []
  a_opt = c.opt.klread_kood('ASPEKT', c.test.aine_kood, ylem_required=True)
  for r in a_opt:
      c.opt_aspektid.append(('%s.%s' % (c.test.aine_kood, r[0]), r[1]))
%>
% if not c.opt_aspektid:
${h.alert_error(_("Hindamiskriteeriume ei saa määrata, kuna õppeainele {s} ei ole aspekte sisestatud").format(s=''))}
% endif

% if c.opt_aspektid:
<table class="table kriteerium" width="100%" >
<col width="10px"/>
<col/>
<tbody>
<tr height="30px" valign="bottom">
  <td class="fh">${_("Hindamisaspekt")}</td>
  <td colspan="6">
    ${h.select('a_aspekt_kood', '%s.%s' % (c.krit.aine_kood, c.krit.aspekt_kood), c.opt_aspektid, empty=True)}
  </td>
</tr>
<tr height="30px" valign="bottom">
  <td class="fh">${_("Jrk")}</td>
  <td>
    <% max_seq = len(c.hindamiskogum.hindamiskriteeriumid) + 1 + (not c.krit.id and 1 or  0) %>
    ${h.select('a_seq', c.krit.seq or max_seq-1, range(1, max_seq), wide=False)}
  </td>
  <td class="frh">${_("Max toorpunktid")}</td>
  <td>
    ${h.float5('a_max_pallid', h.fstr(c.krit.max_pallid))}
  </td>
  <td class="frh">${_("Kaal")}</td>
  <td>
    ${h.float5('a_kaal', h.fstr(c.krit.kaal or 1))}
  </td>  
  <td>
    ${h.checkbox('a_kuvada_statistikas', 1,
    checked=c.krit.kuvada_statistikas or not c.krit.id, label=_("Kuvatakse statistikas"))}
  </td>
</tr>
<tr>
  <td colspan="7">
    ${h.checkbox('a_pkirj_sooritajale', 1,
    checked=c.krit.pkirj_sooritajale or not c.krit.id, label=_("Punktide kirjeldus kuvatakse lahendajale"))}
    ${self.punktikirjeldused()}
  </td>
</tr>
<tr>
  <td class="fh" colspan="7">${_("Hindamisjuhis")}</td>
</tr>
<tr>
  <td colspan="7">
    ##${h.ckeditor('a_hindamisjuhis', c.krit.hindamisjuhis)}          
    ${h.textarea('a_hindamisjuhis', c.krit.hindamisjuhis, cols=70, rows=8, class_="editable")}
  </td>
</tr>

<tr>
  <td class="fh" colspan="7">${_("Hindamiskriteeriumi vaikimisi hindamisjuhis")}</td>
</tr>
<tr>
  <td colspan="7" id="klread_kirjeldus" class="view" height="40">
    % if c.krit and c.krit.aspekt:
    ${h.literal(c.krit.aspekt.ctran.kirjeldus or '')}
    % endif
  </td>
</tr>
</tbody>
</table>
% if c.is_edit:
${h.submit_dlg()}
% endif
% endif

${h.end_form()}
<script>
% if c.is_edit or c.is_tr:
function reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('table.kriteerium>tbody textarea.editable');
    init_ckeditor(inputs, null, '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}
$(function(){
  reinit_ckeditor();
});
% endif
% if c.is_edit and not c.is_tr:
$(function(){
    $('select#a_aspekt_kood').change(function(){
            $('td#klread_kirjeldus').load(
               "${h.url('pub_valikud_kirjeldus', klassifikaator_kood='AINE.ASPEKT',partial=True)}",
               {
                 kood:$('select#a_aspekt_kood').val(),
               }
            );
    });
    $('#a_max_pallid').change(function(){
       var pallid = parseFloat($('#a_max_pallid').val()) || 0;
       var step = .5;     
       var new_len = Math.round(pallid/step) + 1;
       var tbody = $('table#choicetbl_pkirjeldus>tbody');
       var old_len = tbody.children('tr:visible').length;
##console.log('pallid='+pallid+', vana='+old_len+', uus='+new_len);
       while(old_len < new_len)
       {
           var tr = tbody.children('tr').eq(old_len);
           old_len += 1;
           if(tr.length)
              {
                tr.show();
## console.log('show old_len='+old_len + ' tr ' + tr.find('.punktid').text());
              }
           else
              {
                grid_addrow('choicetbl_pkirjeldus');
                pallid = String((old_len-1)*step).replace('.',',');
##  console.log('old_len='+old_len+', old_len/2='+ pallid);       
                tr = tbody.children('tr').last();
                tr.find('td.punktid').text(pallid);
              }
        }
       while(old_len > new_len)
        {
           var tr = tbody.children('tr:visible').last();
           tr.hide();
##           console.log('hide '+tr.find('.punktid').text());
           old_len -= 1;
        }
    });
  });
% endif
</script>

<%def name="row_pkirjeldus(item, prefix)">
    <tr>
      <td class="punktid">${h.fstr(item.punktid)}</td>
      <td style="padding:0">
        ${h.textarea(prefix + '.kirjeldus', item and item.kirjeldus)}
        ${h.hidden(prefix + '.id', item and item.id)}
      </td>
    </tr>
</%def>

<%def name="punktikirjeldused()">
<%
  items = [r for r in c.krit.kritkirjeldused]
  prefix = 'pkirjeldus'
%>
% if c.is_edit or items:
<table width="100%" id="choicetbl_${prefix}" class="table" > 
  <col width="20px"/>
  <col/>
  <thead>
    <tr>
      <th>${_("Punktid")}</th>
      <th>${_("Kirjeldus")}</th>
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_pkirjeldus(c.new_item(punktid=cnt*.5), '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  % for cnt in range(int((c.krit.max_pallid or 0)*2)+1):
    <%
      punktid = cnt * .5
      item = c.new_item(punktid=punktid)
      for r in items:
         if r.punktid == punktid:
             item = r
             break
    %>
    % if c.is_edit or item.id:
    ${self.row_pkirjeldus(item, '%s-%s' % (prefix, cnt))}
    % endif
  % endfor
  % endif
  </tbody>
  <tfoot>
% if c.is_edit and not c.lang:
    <tr>
      <td colspan="2">
<div id="sample_choicetbl_${prefix}" class="invisible">
<!--
   ${self.row_pkirjeldus(c.new_item(), '%s__cnt__' % prefix)}
-->
</div>
      </td>
    </tr>
% endif
  </tfoot>
</table>
% endif
</%def>
