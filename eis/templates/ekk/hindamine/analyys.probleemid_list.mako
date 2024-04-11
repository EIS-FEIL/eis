${h.pager(c.items)}
% if c.items:
${h.form_save(None)}
<% on_sisestamata = False %>
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th width="20px">${h.checkbox1('all', 1, class_="nosave")}</th>
      % for srt, title in c.prepare_header():
      % if srt:
      ${h.th_sort(srt, title)}
      % else:
      ${h.th(title)}
      % endif
      % endfor
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <%
      tos, hindamisolek = rcd[:2]
      values, url_sis, ix_prob = c.prepare_item(rcd, 0)
    %>
    <tr><!-- s ${tos.id} ho ${hindamisolek.id} -->
      <td>
        % if hindamisolek.hindamisprobleem in (const.H_PROBLEEM_SISESTAMATA, const.H_PROBLEEM_TOOPUUDU):
        ${h.checkbox('ho_id', hindamisolek.id, class_="cb-holek nosave")}
        % endif
      </td>
      % for col, value in enumerate(values):
      % if col == 1 and url_sis:
      <td>${h.link_to(value, url_sis)}</td>
      % elif col == ix_prob:
      <td>
        % if hindamisolek.hindamisprobleem in (const.H_PROBLEEM_SISESTAMATA, const.H_PROBLEEM_TOOPUUDU):
        
        ${h.radio('probleem_%s' % hindamisolek.id, const.H_PROBLEEM_SISESTAMATA,
        checkedif=hindamisolek.hindamisprobleem, label=_("Sisestamata"), class_="prob")}
        ${h.radio('probleem_%s' % hindamisolek.id, const.H_PROBLEEM_TOOPUUDU,
        checkedif=hindamisolek.hindamisprobleem, label=_("Töö puudu"), class_="prob")}
        <% on_sisestamata = True %>

        % else:
        ${hindamisolek.selgitus or hindamisolek.hindamisprobleem_nimi}       
        % endif
        % if hindamisolek.hindamisprobleem == const.H_PROBLEEM_HINDAMISERINEVUS:
          % if hindamisolek.hindamistase == const.HINDAJA3:
            <% hindamine3 = hindamisolek.get_hindamine(const.HINDAJA3) %>
            % if hindamine3 and hindamine3.staatus == const.H_STAATUS_HINNATUD:
            (${_("vaja IV hindamist")})
            % else:
            (${_("vaja III hindamist")})
            % endif
          % elif hindamisolek.hindamistase == const.HINDAJA2:
            (${_("vaja III hindamist")})
          % endif
        % endif
      </td>
      % else:
      <td>${value}</td>
      % endif
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.button(_("Sisestamata"), id="sisestamata", level=2, style="display:none")}
    ${h.button(_("Töö puudu"), id="toopuudu", level=2, style="display:none")}
  </div>
  <div>
    % if on_sisestamata:
    ${h.submit(_("Salvesta"))}
    % endif
  </div>
</div>
${h.end_form()}
% endif

<script>
  function toggle_cbh(){
    $('#sisestamata,#toopuudu').toggle($('input.cb-holek:checked').length > 0);
  }
  $('input.cb-holek').click(toggle_cbh);
  $('input#all').click(function(){
    $('input.cb-holek').prop('checked', this.checked);
    toggle_cbh();
  });
  $('button#sisestamata').click(function(){
     $('input.cb-holek:checked').each(function(){
       $(this).closest('tr').find('input.prob[value="${const.H_PROBLEEM_SISESTAMATA}"]').prop('checked', true).change();
     });
  });
  $('button#toopuudu').click(function(){
     $('input.cb-holek:checked').each(function(){
       $(this).closest('tr').find('input.prob[value="${const.H_PROBLEEM_TOOPUUDU}"]').prop('checked', true).change();
     });
  });
</script>
