<% c.aspekt = c.aspekt or c.new_item() %>
<%include file="/common/message.mako"/>
${h.form_save(None, h.url('ylesanded_update_juhised', id=c.item.id), class_='nodirty')}
${h.hidden('sub', 'aspekt')}
${h.hidden('aspekt_id', c.aspekt.id)}

<%
if c.is_edit and not c.item.lukus_hm_muudetav:
   c.is_edit = False
c.opt_aspektid = []
for yaine in c.item.ylesandeained:
   a_opt = c.opt.klread_kood('ASPEKT', yaine.aine_kood, ylem_required=True)
   for r in a_opt:
       c.opt_aspektid.append(('%s.%s' % (yaine.aine_kood, r[0]), r[1]))
%>
% if not c.opt_aspektid:
${h.alert_error(_("Hindamisaspekte ei saa määrata, kuna õppeainele {s} ei ole aspekte sisestatud").format(s=''))}
% endif
% if c.opt_aspektid:
${h.rqexp()}
<div class="t-aspekt rounded border p-3 mb-2">
  <div class="d-flex flex-wrap mb-2">
    <div class="item mr-5 mb-2">
      ${h.flb(_("Hindamisaspekt"), 'a_aspekt_kood', rq=True)}
      <div>
        ${h.select('a_aspekt_kood', '%s.%s' % (c.aspekt.aine_kood, c.aspekt.aspekt_kood), c.opt_aspektid, empty=True)}
      </div>
    </div>
    <div class="item mr-5 mb-2">
      ${h.flb(_("Jrk"))}
      <div>
        <% max_seq = len(c.item.hindamisaspektid) + 1 + (not c.aspekt.id and 1 or  0) %>
        ${h.select('a_seq', c.aspekt.seq or max_seq-1, range(1, max_seq), wide=False)}
      </div>
    </div>
    <div class="item mr-5 mb-2">
      ${h.flb(_("Max toorpunktid"), 'a_max_pallid', rq=True)}
      <div>
        ${h.float5('a_max_pallid', h.fstr(c.aspekt.max_pallid))}
      </div>
    </div>
    <div class="item mr-5 mb-2">
      ${h.flb(_("Intervall"), 'a_pintervall')}
      <div>
        ${h.float5('a_pintervall', h.fstr(c.aspekt.pintervall))}
      </div>
    </div>
    <div class="item mr-5 mb-2">
      ${h.flb(_("Kaal"), 'a_kaal', rq=True)}
      <div>
        ${h.float5('a_kaal', h.fstr(c.aspekt.kaal or 1))}
      </div>
    </div>
    <div class="item mr-5 mb-2">
      ${h.checkbox('a_kuvada_statistikas', 1,
      checked=c.aspekt.kuvada_statistikas or not c.aspekt.id, label=_("Kuvatakse statistikas"))}
      ${h.checkbox('a_pkirj_sooritajale', 1,
      checked=c.aspekt.pkirj_sooritajale or not c.aspekt.id, label=_("Punktide kirjeldus kuvatakse lahendajale"))}
    </div>
  </div>

  ${self.punktikirjeldused()}

  <div class="my-2">
    ${h.flb(_("Hindamisjuhis"))}
    <div>
    % if c.is_edit or c.is_tr:
    ${h.textarea('a_hindamisjuhis', c.aspekt.hindamisjuhis, class_="editable")}
    % else:
    ${c.aspekt.hindamisjuhis}
    % endif
    </div>
  </div>

  <div class="my-2">
    ${h.flb(_("Hindamisaspekti vaikimisi hindamisjuhis"))}
    <div id="klread_kirjeldus">
    <% klaspekt = c.aspekt and c.aspekt.aspekt %>
    % if klaspekt:
    ${h.literal(klaspekt.ctran.kirjeldus or '')}
    % endif
    </div>
  </div>
</div>

<div class="text-right">
% if c.is_edit:
${h.submit_dlg()}
% endif
</div>
% endif

${h.end_form()}

<script>
% if c.is_edit or c.is_tr:
function reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('.t-aspekt textarea.editable');
    init_ckeditor(inputs, null, '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, 100, 'body16');
}
$(function(){
  reinit_ckeditor();
});
% endif
% if c.is_edit and not c.is_tr:
function pkirjeldused(){
    ## punktikirjelduste tabeli kuvamine
       var max_pallid = parseFloat($('#a_max_pallid').val().replace(',','.')) || 0;
       var step = parseFloat($('#a_pintervall').val().replace(',','.')) || .5;     
       var new_len = Math.round(max_pallid/step) + 1;
       var tbody = $('table#choicetbl_pkirjeldus>tbody');
       var rows = tbody.children('tr');
       var tr_ind = rows.length - 1;
       DIFF = .00001
       for(var p=0; p<=max_pallid; p += step)
       {
           ## iga vajaliku rea kohta
           var found = false, curr = null;
           while(true)
           { 
              ## leiame koha olemasolevas tabelis, kuhu rida kuulub
              if(tr_ind < 0)
              {
                 ## tabeli kõik read on väiksema punktide arvuga
                 curr = null;
                 break;
              }
              curr = rows.eq(tr_ind);
              var curr_p = parseFloat(curr.data('p'));
              if(curr_p < p - DIFF)
              {
                  ## see rida on väiksema punktide arvuga, vaatame järgmist
                  curr.hide();
                  ##curr.find('td').css('background-color','#efefef');
                  curr.find('.trdeleted').val('1');
                  tr_ind -= 1;
                  continue;
              }
              else if(curr_p > p + DIFF)
              {
                  ## see on liiga suure punktide arvuga rida, uus rida tuleb selle järele lisada
                  curr.hide();
                  ##curr.find('td').css('background-color','#efefef');
                  curr.find('.trdeleted').val('1');
                  break;
              }
              else
              {
                   ## see on õige rida
                   found = true;
                   curr.show();
                   ##curr.find('td').css('background-color','#fff');
                   curr.find('.trdeleted').val('');
                   tr_ind -= 1;       
                   break;
              }
           }
           if(!found)
           {
              ## rida ei ole tabelis, lisame
              var first = (rows.length > 0 ? rows.eq(0) : null);
              tr = grid_addrow('choicetbl_pkirjeldus');
              tr.data('p', p);
              spallid = String(p).replace('.',',');
              tr.find('td.punktid').text(spallid);
              tr.find('input.punktid').val(p);
              if(curr)
              {
                  ## lisame varem leitud suurema punktide arvuga rea järele                     
                  tr.insertAfter(curr);
              }
              else if(first)
              {
                  ## lisame tabeli algusse                     
                  tr.insertBefore(first);
              }
           }
       }
}
 $(function(){
    $('select#a_aspekt_kood').change(function(){
      ## aspekti muutmisel muudetakse vaikimisi kirjeldus
       $('#klread_kirjeldus').load(
               "${h.url('pub_valikud_kirjeldus', klassifikaator_kood='AINE.ASPEKT',partial=True)}",
               {
                 kood:$('select#a_aspekt_kood').val(),
               }
            );
    });
    ## max pallide või intervalli muutmisel lisatakse/eemaldatakse punktikirjelduse tabeli ridu
    $('#a_max_pallid,#a_pintervall').change(pkirjeldused);
    pkirjeldused();
  });
% endif
</script>

<%def name="row_pkirjeldus(item, prefix)">
    <tr data-p="${item.punktid}">
      <td class="punktid">${h.fstr(item.punktid)}</td>
      <td>
        ${h.textarea(prefix + '.kirjeldus', item and item.kirjeldus)}
        ${h.hidden(prefix + '.id', item and item.id)}
        ${h.hidden(prefix + '.punktid', item and item.punktid, class_="punktid")}
        ${h.hidden(prefix + '.deleted', '', class_="trdeleted")}
      </td>
    </tr>
</%def>

<%def name="punktikirjeldused()">
<%
  items = sorted([r for r in c.aspekt.punktikirjeldused], key=lambda r: r.punktid)
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
        ${self.row_pkirjeldus(c.new_item(), '%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  % for cnt, item in enumerate(reversed(items)):
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
