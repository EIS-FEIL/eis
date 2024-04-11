## isikukood, nimi, synniaeg, sugu, kasutajatunnus
## eksaminand.mako määrab enne c.is_eksaminand = True

<script>
function search_by_ik(){
  var ik=$('form#form_save input[name="isikukood"]').val();
  var url = "${h.url_current('new')}?isikukood=" + ik;
  set_spinner($('#bqrr'));
  window.location.replace(url);
}
</script>

    <%
      ik_exist = c.item.id and c.item.isikukood
      # isikukoodi ei või muuta, kui:
      # - isikukood on juba olemas
      # - või isikukirje on juba olemas ja on avalik vaade
      # - või isikukirja on juba olemas ja on EKK vaade ja kasutajal pole ik muutmise luba
      ik_disabled = ik_exist or not c.is_edit \
         or (c.app_eis and c.item.id) \
         or (c.app_ekk and c.item.id and not c.user.has_permission('eksaminandid-ik', const.BT_UPDATE))
      synnikpv_disabled = ik_disabled and request.is_ext()
    %>
  <div class="form-group row">
    ${h.flb3(_("Isikukood"), 'isikukood', rq=c.app_eis and not ik_disabled)}
    % if ik_disabled:
    <div class="col-md-3">
      ${h.roxt(c.item.isikukood)}
      ${h.hidden('isikukood',c.item.isikukood)}
    </div>
    % else:
    <div class="col-md-6">    
      <div class="d-flex">
        <% riik = c.item.isikukood_riik or const.RIIK_EE %>
        ## riigi nimetuse valik
        ${h.select2('riik', riik, c.opt.KODAKOND2, wide=False, width="180")}
        ## valitud riigi ISO2 kood
        <div id="riik2" class="pl-3">${riik}</div>
        ## isikukood ilma riigita
        <div class="flex-grow-1">
          ${h.text('isikukood', c.item.isikukood_kood, class_='nosave')}
        </div>
      </div>
      <script>
        ## vea korral kuvada ISO2 kood valikvälja järgi
        $(function(){
          var val = $('#riik').val();
          if(val) $('#riik2').text(val);
        });
        ## nimetuse valiku muutmisel näidata ISO2 koodi
        $('#riik').change(function(){
            $('#riik2').text($('#riik').val());
        });
        $('input[name="isikukood"]').change(function(){
            var code = $(this).val(),
                state = $('#riik').val(), rc = true;
           ## Eesti ja Leedu isikukoodi kontroll
           if(code)
           if(state == "${const.RIIK_EE}" || state == "${const.RIIK_LT}"){
               m = code.match(/^([3456])(\d{2})(\d{2})(\d{2})\d{4}$/);
               if(m){
                 var sex = ((m[1] == '4') || (m[1] == '6') ? "${const.SUGU_N}" : "${const.SUGU_M}");
                 $('input[name="k_sugu"][value="' + sex + '"]').prop('checked', true);
                 var century = ((m[1] == '3') || (m[1] == '4') ? '19' : '20');
                 var dt = m[4] + '.' + m[3] + '.' + century + m[2];
                 $('input[name="k_synnikpv"]').val(dt);
               }
               else{
                  rc = false;
               }
           }
          $(this).toggleClass('error', !rc);
          ## otsimise nupp ainult siis, kui on Eesti isikukood
          $('#bqrr').prop('disabled', !rc || (state != "${const.RIIK_EE}"));
      });
      </script>
    </div>
    % endif
    % if c.is_edit and request.is_ext():
    <div class="col-md-3">
         % if c.item.id:
          % if request.is_ext() and (c.item.isikukood_ee or not ik_disabled):
           ${h.button(_("Päri andmed Rahvastikuregistrist"), id="bqrr", level=2)}
           <% c.rr_query_url = h.url_current('show', sub='rr', id=c.item.id) %>
           <%include file="/admin/rahvastikuregister_js.mako"/>
           <script>
             $('#bqrr').click(function(){
               % if ik_disabled:
               query_rr(${c.item.id});
               % else:
               query_rr(${c.item.id}, $('input#isikukood').val());
               % endif
             });
           </script>
           % endif
         % else:
           ## uue kasutaja loomine
          ${h.button(_("Otsi"), id="bqrr", level=2)}
           <script>
             $('#bqrr').click(search_by_ik);
           </script>
         % endif
    </div>
    % endif
  </div>
  <div class="form-group row">
    ${h.flb3(_("Sünniaeg"), 'synnikpv', rq=True)}
    <div class="col-md-3">
      % if synnikpv_disabled or not c.is_edit:
      ${h.roxt(h.str_from_date(c.item.synnikpv))}
      ${h.hidden('k_synnikpv', h.str_from_date(c.item.synnikpv))}
      % else:
      ${h.date_field('k_synnikpv', c.item.synnikpv, disabled=ik_disabled and request.is_ext())}
      % endif
    </div>
    ${h.flb3(_("Sugu"), 'k_sugu', 'text-md-right', rq=True)}
    <div class="col-md-3">
      % if synnikpv_disabled or not c.is_edit:
      ${h.roxt(c.item.sugu == const.SUGU_M and _("mees") or c.item.sugu == const.SUGU_N and _("naine") or '')}
      ${h.hidden('k_sugu', c.item.sugu)}
      % else:
      ${h.radio('k_sugu', const.SUGU_M, checkedif=c.item.sugu, label=_("mees"))}
      ${h.radio('k_sugu', const.SUGU_N, checkedif=c.item.sugu, label=_("naine"))}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Eesnimi"), 'k_eesnimi', rq=True)}
    <div class="col-md-3">
      ${h.text('k_eesnimi', c.item.eesnimi)}
    </div>
    ${h.flb3(_("Perekonnanimi"), 'k_perenimi', 'text-md-right', rq=True)}
    <div class="col-md-3">
      ${h.text('k_perenimi', c.item.perenimi)}
    </div>
  </div>
% if c.app_ekk:
  <div class="form-group row">  
    % if not c.is_eksaminand:
    ${h.flb3(_("Parool"),'parool')}
    <div class="col-md-3">
      ${h.text('parool', '', disabled=not c.can_set_pwd)}
    </div>
    % endif
  </div>
% endif
