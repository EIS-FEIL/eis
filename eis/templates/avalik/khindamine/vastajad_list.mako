% if c.staatus == const.H_STAATUS_POOLELI_VALMIS and c.items:
${h.alert_info(_("Vali tööd, mida soovid kinnitada!"), False)}
% endif
${h.pager(c.items, msg_not_found=_("Töid ei leitud"), msg_found_one=_("Leiti 1 töö"), msg_found_many=_("Leiti {n} tööd"))}
<% 
  sisestatud_cnt = 0
%>

% if c.items:
<% on_hindamise_luba = c.toimumisaeg.on_hindamise_luba %>
<table class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % if c.staatus == const.H_STAATUS_POOLELI_VALMIS:
      <th sorter="false" width="20px">
        <span id="all_span" class="d-none">
          ${h.checkbox1('all', 1, class_="nosave", title=_("Vali kõik"))}
        </span>
      </th>
      % endif
      % for sort_fld, label in c.header:
      ${h.th_sort(sort_fld, label)}
      % endfor
      ${h.th('')}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%  
       tos, holek, hindamine = rcd
       too, pallid = c.prepare_item(rcd)

       if c.testiosa.vastvorm_kood == const.VASTVORM_SH:
          # suuline hindamine
          if c.app_ekk:
             url_edit = h.url('hindamine_hindajavaade_shindamised', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id, sooritus_id=tos.id, lst=c.staatus)
          else:
             url_edit = h.url('shindamine_hindamised', hindaja_id=c.hindaja.id, sooritus_id=tos.id, lst=c.staatus)
       else:
          # kirjalik hindamine
          if c.app_ekk:
             url_edit = h.url('hindamine_hindajavaade_hkhindamised', toimumisaeg_id=c.toimumisaeg.id, hindamiskogum_id=c.hindamiskogum.id, hindaja_id=c.hindaja.id, sooritus_id=tos.id, lst=c.staatus)
          else:
             url_edit = h.url('khindamine_hkhindamised', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id, sooritus_id=tos.id, lst=c.staatus)
       if hindamine and hindamine.on_probleem and hindamine.probleem_varv:
          trstyle = 'style="background-color:%s"' % hindamine.probleem_varv
       else:
          trstyle = ''
       if c.app_eis and not on_hindamise_luba:
          url_edit = None
    %>
    <tr ${trstyle}>
      % if c.staatus == const.H_STAATUS_POOLELI_VALMIS:
      <td>
        % if hindamine and hindamine.sisestatud:
        <% sisestatud_cnt += 1 %>
        ${h.checkbox('hindamine_id', hindamine.id, class_="hindamine_id nosave",
        title=_("Vali rida {s}").format(s=too))}
        % endif
      </td>
      % endif
      <td>
        ${too}
      </td>
      <td>
        ${pallid}
      </td>
      % if c.staatus == const.H_STAATUS_POOLELI:
      <td>
        % if hindamine and hindamine.on_probleem:
        ${_("Jah")}
        % endif
      </td>
      <td>
        % if hindamine:
        ${h.html_nl(hindamine.probleem_sisu)}
        % endif
      </td>
      % endif
      <td>
        % if url_edit:
        % if not hindamine or hindamine.staatus == const.H_STAATUS_HINDAMATA:
        ${h.btn_to(_("Alusta hindamist"), url_edit)}
        % elif hindamine.staatus != const.H_STAATUS_HINNATUD:
        ${h.btn_to(_("Jätka hindamist"), url_edit)}
        % endif
        % endif
        <!-- 
             holek ${holek.id}
             staatus ${holek.staatus_nimi}
             tase ${holek.hindamistase})
             hindamine ${hindamine and hindamine.id}
             ${holek.selgitus or holek.hindamisprobleem_nimi}
         -->
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

% if c.staatus == const.H_STAATUS_POOLELI_VALMIS and sisestatud_cnt:
## peatatud hindamiste sakk ja on selliseid hindamisi, mida saaks kinnitada
<script>
  function toggle_add(){
       var visible = ($('input:checked.hindamine_id').length > 0);
       $('span#add').toggleClass('d-none', !visible);
  }
  $('#all_span').removeClass('d-none');
  $('input#all').click(function(){
       $('input.hindamine_id').prop('checked', this.checked); toggle_add();
  });
  $('input.hindamine_id').click(toggle_add);
</script>
% endif
