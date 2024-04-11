<% 
   on_alatestid = vastvorm_kood = None
   for testikoht in c.toimumisprotokoll.testikohad:
      testiosa = testikoht.toimumisaeg.testiosa
      vastvorm_kood = testiosa.vastvorm_kood
      on_alatestid = testiosa.on_alatestid
   cnt_osalejaid = 0
%>
% if c.app_eis and c.opt_testiruumid:
<div class="row">
  ${h.flb3(_("Ruum"),'testiruum_id','text-md-right')}
  <div class="col col-md-6">
    ${h.select('testiruum_id', c.testiruum_id, c.opt_testiruumid, empty=_("Kõik minu ruumid"), class_="nosave", ronly=False)}
  </div>
</div>
% endif

<h3>${_("Testisooritused")}</h3>
${h.rqexp()}
<table class="table table-striped tablesorter"  width="100%" id="tbl_osalejad">
  <thead>
  <tr>
    ${h.th(_("Testisooritus"))}
    ${h.th(_("Sooritaja"))}
    ${h.th(_("Olek"), rq=True)}
% if c.testimiskord.prot_vorm == const.PROT_VORM_DOKNR:
    ${h.th(_("Esitatud dokumendi nr"))}
% endif
% if c.testimiskord.prot_vorm == const.PROT_VORM_ALATULEMUS:
    % for label, col_id in c.alatestid_col:
    ${h.th(label)}
    % endfor
% else:
    ${h.th(_("Ruum"))}
    ${h.th(_("Protokollirühm"))}
% endif
    ${h.th(_("Lisainfo"), sorter="false")}
  </tr>
  </thead>
  <tbody>
  % for n, rcd in enumerate(c.items):
  <%
     sooritaja = rcd.sooritaja
     kasutaja = sooritaja.kasutaja
     s_nimi = sooritaja.nimi
     if rcd.staatus == const.S_STAATUS_TEHTUD:
        cnt_osalejaid += 1
  %>
  <tr class="tr_sooritus">
    <td>
      ${rcd.tahised}
    </td>
    <td>
      <span class="sooritaja-nimi">${s_nimi}</span>
      ${kasutaja.isikukood or h.str_from_date(kasutaja.synnikpv)}
      ${h.hidden('s-%d.id' % n, rcd.id)}
      % if c.is_debug:
      (${rcd.staatus_nimi}/${sooritaja.staatus_nimi})
      % endif
    </td>
    <td>
      <div>
      <%
        ei_osalenud = vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I) and not rcd.seansi_algus
        osales = bool(rcd.seansi_algus)
        pohjusega = rcd.staatus in (const.S_STAATUS_KATKESPROT, const.S_STAATUS_EEMALDATUD)
      %>
      ${h.radio('s-%d.staatus' % n, const.S_STAATUS_TEHTUD,
      checkedif=rcd.staatus, label=_("Osales"),
      disabled=ei_osalenud,
      class_='r_staatus ' + (not ei_osalenud and 'r_staatus_tehtud' or ''))}      

      ${h.radio('s-%d.staatus' % n, const.S_STAATUS_PUUDUS,
      checkedif=rcd.staatus, label=_("Puudus"), disabled=osales,
      class_='r_staatus r_staatus_puudus')}

      % if c.testimiskord.prot_vorm == const.PROT_VORM_ATS:
      ${h.radio('s-%d.staatus' % n, const.S_STAATUS_PUUDUS_HEV,
      checkedif=rcd.staatus==const.S_STAATUS_PUUDUS and rcd.puudumise_pohjus,
      label=_("Eritingimused"), class_='r_staatus r_staatus_puudus')}      
      ${h.radio('s-%d.staatus' % n, const.S_STAATUS_PUUDUS_VANEM,
      checkedif=rcd.staatus==const.S_STAATUS_PUUDUS and rcd.puudumise_pohjus,
      label=_("Lapsevanema keeldumine"), class_='r_staatus r_staatus_puudus')}
      % else:
      ${h.radio('s-%d.staatus' % n, const.S_STAATUS_KATKESPROT,
      checked=rcd.staatus in (const.S_STAATUS_KATKESPROT, const.S_STAATUS_KATKESTATUD),
      label=_("Katkestas"), class_='r_staatus r_staatus_tehtud r_staatus_katkesprot')}
      ${h.radio('s-%d.staatus' % n, const.S_STAATUS_EEMALDATUD,
      checkedif=rcd.staatus, label=_("Eemaldatud või tühistatud"),
      class_='r_staatus r_staatus_tehtud r_staatus_eemaldatud')}
      % endif
      ${h.hidden('s-%d.staatus_err' % n, '')}
      </div>
      <div class="dstpohjus" style="${not pohjusega and 'display:none' or ''}">
        % if c.app_eis:
        <div class="d-flex">
          <label class="pr-2">${_("Põhjus")}</label>
          <div class="flex-grow-1">
            ${h.text('s-%d.stpohjus' % n, rcd.stpohjus, class_="stpohjus", maxlength=100)}
          </div>
        </div>
        % endif
      </div>
    </td>
% if c.testimiskord.prot_vorm == const.PROT_VORM_DOKNR:    
    <td>
      ${h.text('s-%d.isikudok_nr' % n, rcd.isikudok_nr, maxlength=25, size=25)}
    </td>
% endif
% if c.testimiskord.prot_vorm == const.PROT_VORM_ALATULEMUS:
    <% tos_data = c.get_alatestitulemused(rcd) %>
    % for label, col_id in c.alatestid_col:
    <td>${tos_data.get(col_id)}</td>
    % endfor
% else:
    <td>
      ${rcd.testiruum and rcd.testiruum.tahis}
    </td>
    <td>
      ${rcd.testiprotokoll and rcd.testiprotokoll.tahis}
    </td>
% endif    
    <td>
      ${h.button(_("Lisainfo"), id='btn_lisainfo_%s' % rcd.id, class_="b-lisainfo",
      level=2, mdicls2=rcd.markus and 'mdi-check' or 'mdi-check d-none')}


      % if vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
      ${h.button(_("Läbiviijad"), id="btn_labiviijad_%s" % rcd.id, class_="b-labiviijad", level=2)}

      <div id="labiviijad_${rcd.id}" class="dlg-labiviijad d-none">
        <table  class="table" width="100%">
          % for ho in rcd.hindamisolekud:
            % if len(rcd.hindamisolekud)>1:
          <tr>
            <td class="fh">${_("Hindamiskogum")}</td>
            <td>${ho.hindamiskogum.tahis}</td>
          </tr>
            % endif
            % if ho.komplekt_id:
          <tr>
            <td class="fh">${_("Ülesandekomplekt")}</td>
            <td>${ho.komplekt.tahis}</td>
          </tr>
            % endif
            % for hindamine in ho.hindamised:
              % if hindamine.sisestus in (1,0):
                % if hindamine.intervjuu_labiviija:
          <tr>
            <td class="fh">${_("Intervjueerija")}</td>
            <td>${hindamine.intervjuu_labiviija.kasutaja.nimi}</td>
          </tr>          
                % endif
          <tr>
            <td class="fh">${hindamine.liik_nimi}</td>
            <td>
              % if hindamine.hindaja_kasutaja_id:
              ${hindamine.hindaja_kasutaja.nimi}
              % endif
            </td>
          </tr>
              % endif
            % endfor
          % endfor
        </table>
      </div>
      % endif

     <div id="lisainfo_${rcd.id}" class="dlg-lisainfo d-none">
       % if rcd.stpohjus:
       <div class="mb-3">
         <div>${rcd.staatus_nimi}</div>
         <div>${rcd.stpohjus}</div>
       </div>
       % endif

       ${h.flb(_("Märkus"))}
       <div class="mb-2">
       ${h.textarea('s-%d.markus' % n, rcd.markus, rows=8, class_="markus")}
       </div>
        % if on_alatestid:
            <table class="table table-striped mb-2">
              <tr>
                <th>${_("Osales")}</th>
                <th>${_("Alatest")}</th>
              </tr>
              % for n1, alatest in enumerate(rcd.alatestid):
              <% alatestisooritus = rcd.get_alatestisooritus(alatest.id) %>
              <tr>
                <td>
                  % if alatestisooritus and alatestisooritus.staatus == const.S_STAATUS_VABASTATUD:
                  ${_("Vabastatud")}
                  % else:
                  ${h.radio('s-%d.ats-%d.staatus' % (n, n1), const.S_STAATUS_TEHTUD,
                  checkedif=alatestisooritus and alatestisooritus.staatus,
                  label=_("Jah"), class_='r_alatestistaatus_tehtud',
                  id='li_ats_st_%s_%s_1' % (rcd.id, alatest.id))}            
                  ${h.radio('s-%d.ats-%d.staatus' % (n, n1), const.S_STAATUS_PUUDUS,
                  checkedif=alatestisooritus and alatestisooritus.staatus,
                  label=_("Ei"), class_='r_alatestistaatus_puudus',
                  id='li_ats_st_%s_%s_0' % (rcd.id, alatest.id))}                   
                  % endif
                </td>
                <td>
                  ${alatest.id} ${alatest.nimi}
                  ${h.hidden('s-%d.ats-%d.id' % (n, n1), alatest.id)}
                </td>
              </tr>
              % endfor
            </table>
        % endif

       <div class="d-flex">
         ${h.button(_("Katkesta"), class_="btn-lisainfo-close", level=2)}
         % if c.is_edit:
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

<table class="mb-2" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td>
% if c.is_edit:
<p>
${h.button(_("Märgi kõik sooritajad osalenuks"), id='margi_tehtuks', level=2)}
</p>
<script>
$(function(){
  ## läbiviijate nupp
  $('button.b-labiviijad').click(function(){
     var div = $(this).closest('.tr_sooritus').find('.dlg-labiviijad'),
         nimi = $(this).closest('.tr_sooritus').find('.sooritaja-nimi').text();
     dialog_el(div, nimi);
  });
  
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

  $('input.r_staatus_tehtud').change(function(){
    ## kui soorituse olekut muudetakse, siis muuta ka alatestisoorituste olekuid
    $(this).closest('tr.tr_sooritus').find('input.r_alatestistaatus_tehtud').prop('checked',true);
  });
  $('input.r_staatus_puudus').change(function(){
    ## kui soorituse olekut muudetakse, siis muuta ka alatestisoorituste olekuid
    $(this).closest('tr.tr_sooritus').find('input.r_alatestistaatus_puudus').prop('checked',true);
  });
  $('button#margi_tehtuks').click(function(){
     var fields = $('#tbl_osalejad input[name$="staatus"][value="${const.S_STAATUS_TEHTUD}"]');
     fields.prop('checked',true);
     $.each(fields, function(n, item){
        set_row_color($(item));
     });
     $('#tbl_osalejad input.r_alatestistaatus_tehtud').prop('checked',true);
  });

  ## osaleja oleku järgi seatakse osaleja tabelirea taustavärv
  $('input.r_staatus_tehtud,input.r_staatus_puudus').change(function(){
     set_row_color($(this));
  });
  $.each($('input.r_staatus_tehtud,input.r_staatus_puudus').filter(':checked'), function(n, item){
     set_row_color($(item));
  });

  $('input.r_staatus').change(function(){
     ## katkestanuks või eemaldatuks märkimisel kysida põhjust
     var pohjusega = $(this).hasClass('r_staatus_katkesprot') ||
                     $(this).hasClass('r_staatus_eemaldatud');
     $(this).closest('td').find('.dstpohjus').toggle(pohjusega);
  });
  $('.dstpohjus').each(function(){
     var pohjusega = $(this).closest('td').find('input.r_staatus:checked')
                     .is('.r_staatus_katkesprot,.r_staatus_eemaldatud');
     $(this).toggle(pohjusega);
  });
});

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
