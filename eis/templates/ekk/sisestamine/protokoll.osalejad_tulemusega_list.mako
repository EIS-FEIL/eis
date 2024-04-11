<%
   test = c.testimiskord.test
   prot_yl_tulemusega = c.testimiskord.prot_vorm == const.PROT_VORM_YLTULEMUS
   testiosad = list(test.testiosad)
   cnt_osalejaid = 0
   li_hinded = ["[%s, '%s']" % (hinne.pallid, hinne.hinne) for hinne in test.testihinded]
   auto_hinne = len(li_hinded) > 0
   mitu_testiosa = len(testiosad) > 1

   c.ei_teinud_opt = (
                  (const.S_STAATUS_PUUDUS, _("Puudus")),
                  (const.S_STAATUS_KATKESPROT, _("Katkestas")),
                  (const.S_STAATUS_EEMALDATUD, _("Eemaldatud või tühistatud")),
                 )
   c.ei_teinud_staatus = [r[0] for r in c.ei_teinud_opt]
%>

<h3>${_("Testisooritused")}</h3>
${h.alert_info(_("Kui testi sooritaja puudus, kõrvaldati või katkestas testi, tuleb tulemuse lahtrisse panna kriips ning valida kriipsu põhjus"), False)}
${h.rqexp()}
<table class="table table-borderless table-striped tablesorter" id="tbl_osalejad">
  <thead>
  <tr>
    ${h.th(_("Testisooritus"))}
    ${h.th(_("Sooritaja"))}
    % if mitu_testiosa:
    % for testiosa in testiosad:
    ${h.th(testiosa.nimi)}
    ${h.th(_("Eritingimused"))}
    % endfor
    % elif prot_yl_tulemusega:
    ${h.th(_("Ülesanded"), rq=True)}
    % endif
    % if mitu_testiosa or not prot_yl_tulemusega:
    ${h.th(_("Punktid"), rq=True)}
    % endif
    % if not mitu_testiosa:
    ${h.th(_("Eritingimused"))}
    % endif
    ${h.th(_("Tulemus protsentides"))}
    % if auto_hinne:
    ${h.th(_("Hinne"))}
    % endif
    ${h.th(_("Lisainfo"), sorter="false")}
  </tr>
  </thead>
  <tbody>
  <% n = 0 %>
  % for rcd in c.items:
  <%
     sooritaja = rcd.sooritaja
     if rcd.staatus == const.S_STAATUS_TEHTUD:
        cnt_osalejaid += 1
     prefix = 's-%d' % n
     tos0 = None
     tos_is_edit = c.is_edit and (c.can_edit or len([r for r in sooritaja.testiopetajad if r.opetaja_kasutaja_id == c.ainult_opetaja_id]))
     if tos_is_edit:
        n += 1
  %>
  <tr class="tr_sooritus" data-max="${sooritaja.max_pallid}">
    <td>
      ${rcd.tahised}
    </td>
    <td>
      <span class="sooritaja-nimi">${sooritaja.nimi}</span>
      ${sooritaja.kasutaja.isikukood or h.str_from_date(sooritaja.kasutaja.synnikpv)}
% if tos_is_edit:
      ${h.hidden('%s.id' % prefix, sooritaja.id)}
% endif      
    </td>
    % for n_ta, testiosa in enumerate(testiosad):
      <%
         tos = sooritaja.get_sooritus(testiosa_id=testiosa.id)
         if not tos0: tos0 = tos
         tos_staatus = tos.staatus
         if tos_staatus == const.S_STAATUS_KATKESTATUD:
            tos_staatus = const.S_STAATUS_KATKESPROT
         ei_teinud = tos.staatus in c.ei_teinud_staatus
         tosprefix = '%s.tos-%d' % (prefix, n_ta)
         r_cls = 'r_staatus' + (not ei_teinud and ' invisible' or '')
      %>
      % if tos_staatus == const.S_STAATUS_VABASTATUD:
      <td colspan="2">
        ${tos.staatus_nimi}
      </td>
      % else:
     <td>
       <div class="d-flex flex-wrap">
        % if prot_yl_tulemusega:
        <div class="pr-2">
          ${self.prot_yl(tosprefix, tos, sooritaja, testiosa)}
        </div>
        % endif
        % if tos_is_edit:
        <div class="pr-2">
          ${h.float5('%s.pallid' % (tosprefix), ei_teinud and '-' or tos.pallid, maxvalue=testiosa.max_pallid, class_='val-tp pallid-%s' % tos.id)}
        </div>
        <div class="pr-2">
          ${h.select('%s.staatus' % (tosprefix), tos_staatus, c.ei_teinud_opt, class_=r_cls, wide=False)}
          ${h.hidden('%s.staatus_err' % tosprefix, '')}
          ${h.hidden('%s.id' % (tosprefix), tos.id)}
        </div>
        % elif ei_teinud:
        <div class="pr-2">
          ${tos.staatus_nimi}
        </div>
        % else:
        <div class="pr-2">
          ${h.fstr(tos.pallid)}
        </div>
        % endif
       </div>
    </td>
    <td>
      % if tos.on_kinnitatud_erivajadusi:
      ${h.btn_to_dlg(_("Eritingimused"), h.url_current(tos_is_edit and 'edit' or 'show', id=tos.id, sub='eri'),
                     title=_("Eritingimused"), width=600, level=2, size='lg')}
      <br/>
      ${tos.get_str_erivajadused('<br/>', True)}
      % endif
    </td>      
    % endif
    % endfor
    
    % if mitu_testiosa:
    <td class="val-total-tp">
      ${h.fstr(sooritaja.pallid)}
    </td>
    % endif
    <td>
      <% prot = sooritaja.tulemus_protsent %>
      <span class="val-prot"
            ${sooritaja.staatus == const.S_STAATUS_PUUDUS and 'class="invisible"' or ''}>
        % if prot is not None:
        ${h.fstr(prot,0)}%
        % endif
      </span>
    </td>
    % if auto_hinne:
    <td>
      % if sooritaja.staatus == const.S_STAATUS_PUUDUS:
      <span class="val-hinne" style="display:none">
      % else:
      <span class="val-hinne">
      % endif
        ${sooritaja.hinne}
      </span>
    </td>
    % endif
    <td>
      ${h.button(_("Lisainfo"),  id='btn_lisainfo_%s' % rcd.id, class_="b-lisainfo",
      level=2, mdicls2=sooritaja.markus and 'mdi-check' or 'mdi-check d-none')}
     <div id="lisainfo_${rcd.id}" class="dlg-lisainfo d-none">
       ${h.flb(_("Märkus"))}
       <div class="mb-2">
       % if tos_is_edit and c.can_edit:
       ${h.textarea('%s.markus' % prefix, sooritaja.markus, rows=3, class_="markus")}
       % else:
       ${sooritaja.markus}
       % endif
       </div>
       <div class="d-flex">
         ${h.button(_("Katkesta"), class_="btn-lisainfo-close", level=2)}
         % if tos_is_edit:
         <div class="flex-grow-1 text-right">
           ${h.button(_("Salvesta"), class_="btn-lisainfo-save")}
         </div>
         % endif
       </div>
     </div>

    </td>
  </tr>
  % endfor
  </tbody>
</table>

% if c.is_edit:
<script>
$(function(){
  ## lisainfo dialoogi avamise nupp
  $('button.b-lisainfo').click(function(){
     var div = $(this).closest('.tr_sooritus').find('.dlg-lisainfo'),
         nimi = $(this).closest('.tr_sooritus').find('.sooritaja-nimi').text();
     dialog_el(div, nimi);
  });
  $('body').on('click', 'button.btn-lisainfo-close', function(){ close_dialog();});
  $('body').on('click', 'button.btn-lisainfo-save', function(){
       save_dialog();
       ## lisainfo kirjutamisel muudetakse nupu välimus, et oleks aru saada, kui lisainfo on sisestatud
       var dlg = $(this).closest('.modal'), btn_id = 'btn_' + dlg.attr('contents_id'), btn = $('#' + btn_id);
       is_txt = dlg.find('textarea.markus').val() != '';
       btn.find('.mdi-check').toggleClass('d-none', !is_txt);
  });

  ## osaleja oleku järgi seatakse osaleja tabelirea taustavärv
  var set_nullipohj = function()
  {
    var is_zero = $(this).val() == '-', prot = $(this).closest('tr').find('.val-prot'),
        nullipohj = $(this).closest('td').find('select.r_staatus');
    nullipohj.toggleClass('invisible', !is_zero);
    prot.toggleClass('invisible', is_zero);
    if(is_zero) nullipohj.focus();
  }
  $('input[name$="pallid"]').change(set_nullipohj).keyup(set_nullipohj);

  ## testiosatulemuste jooksev kokkuliitmine
  $('input.val-tp').change(function(){
    var tr = $(this).closest('tr.tr_sooritus');
    var total=0;
    var osales = false;
    var puudus = false;
    tr.find('input.val-tp').each(function(){
    var p = numval($(this));
    if((p !== '') && (puudus == false))
     {
        osales = true;
        total += p;
     }
     else
     {
        puudus = true;
     }
    });
    if(!osales || puudus) total = '';
    tr.find('td.val-total-tp').text(fstr(total));
  % if test.ymardamine:
    total = Math.round(total);
  % endif
    var tos_max = tr.data('max'), prot = calc_prot(total, parseFloat(tos_max));
    tr.find('span.val-prot').text(Math.round(prot)+'%');
  % if auto_hinne:
    tr.find('span.val-hinne').text(calc_hinne(prot)); 
  % endif
  });
});

function calc_prot(pallid, max_pallid)
{
  if(pallid === '') return '';
  if(max_pallid === '' || max_pallid == 0) return '';
  var protsent = pallid *100 / max_pallid;
  return protsent;
}
% if auto_hinne:
function calc_hinne(protsent)
{
  var hinded = [${','.join(li_hinded)}];
  for(var i=0; i<hinded.length; i++)
  {
    if(protsent + .00001 >= hinded[i][0]){
    return hinded[i][1];
    }
  }
  return '';  
}
% endif

function numval(fld)
{
  var v = $(fld).val();
  if(v != '')
     {
         var p = Number(v.replace(',','.'));
         if(!isNaN(p))
         {
            return p;
         }
     }
    return '';
}
  
## osaleja oleku järgi seatakse osaleja tabelirea taustavärv
function set_row_color(field)
{
     var value = field.val();
     var color = '#f0f0f0';
     if(value == '${const.S_STAATUS_TEHTUD}') color = '#fafafa';
     else if(value == '${const.S_STAATUS_PUUDUS}') color = '#E0D7DA';
     else if(value == '${const.S_STAATUS_KATKESPROT}') color = '#E9DFF5';
     else if(value == '${const.S_STAATUS_EEMALDATUD}') color = '#FAD4DF';
     field.closest('tr.tr_sooritus').find('td').css('background-color',color);
}
</script>
% endif

<div class="text-right">
  ${_("Kokku {n} sooritajat").format(n=h.literal('<span class="brown">%s</span>' % cnt_osalejaid))}
</div>

<%def name="prot_yl(prefix, tos, sooritaja, testiosa)">
<%
   found = True
   for ty in testiosa.testiylesanded:
      yv = tos.get_ylesandevastus(ty.id)
      if not yv or yv.pallid is None:
         found = False
         break
%>
      ${h.btn_to_dlg(_("Ülesannete punktid"),
                     h.url_current('edit', id=tos.id),
                     title='%s: %s, %s' % (_("Ülesannete punktid"), sooritaja.nimi, testiosa.nimi),
                     level=2, mdicls2=found and 'mdi-check' or None)}
</%def>
