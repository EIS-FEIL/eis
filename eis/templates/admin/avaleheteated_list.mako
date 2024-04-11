
<%
  map_kellele = {key: value for (key, value) in model.Avaleheinfo.opt_kellele()}
%>

% if c.emergency_item:
${self.list_item(c.emergency_item, map_kellele)}
% endif

${h.pager(c.items)}
% for rcd in c.items:
${self.list_item(rcd, map_kellele)}
% endfor

<script>
  $('.moreinfo .morebtn').click(function(){
  $(this).find('.mdi').toggleClass('mdi-menu-down').toggleClass('mdi-menu-up');
  $(this).closest('.moreinfo').find('.morebody').toggle();
  });
</script>

<%def name="list_item(rcd, map_kellele)">
<%
  is_logi = isinstance(rcd, model.Avaleheinfologi)
  if is_logi:
     # kontroller "avaleheteatelogid"
     logircd = rcd
     rcd = logircd.as_obj(c)
  is_valid = rcd.alates <= model.date.today() <= rcd.kuni
%>
<div class="ml-2 my-3 mr-2 pl-3 pb-1 ${not is_valid and 'bg-gray-50' or ''}">
  % if is_logi:
  <div class="py2 px-3">
    ${h.str_from_datetime(logircd.aeg, True)} ${logircd.kasutaja.nimi}
    % if logircd.liik == model.LOG_INSERT:
    ${_("lisas")}
    % elif logircd.liik == model.LOG_UPDATE:
    ${_("muutis")}
    % elif logircd.liik == model.LOG_DELETE:
    ${_("kustutas")}
    % endif
  </div>
  % endif
  ${self.infoheader(rcd, map_kellele, is_logi)}
  ${self.infobox(rcd)}
</div>
</%def>

<%def name="infoheader(rcd, map_kellele, is_logi)">
  <div class="d-flex flex-wrap">
    <div class="py-2  px-3 bg-gray-50">
      % if rcd.tyyp == model.Avaleheinfo.TYYP_EMERGENCY:
      <b>${_("Erakorraline teade")}</b>
         % if is_logi and rcd.kuni < rcd.modified.date():
             (${_("mitteaktiivne")})
         % endif
      % else:
      <b>${_("Kuvamise aeg")}:</b>
      ${h.str_from_date(rcd.alates)} - ${h.str_from_date(rcd.kuni_ui)}
      % endif
    </div>
    <div class="py-2 px-3 bg-gray-50">
      <b>${_("Nähtav")}:</b>
      <%
        li = []
        for ch in list((rcd.kellele or '').split(',')):
           li.append(map_kellele.get(ch) or '')
      %>
      ${', '.join(li)}
    </div>
    % if not is_logi:
    <div class="pt-1 pb-2 px-3 bg-gray-50">
      % if rcd.tyyp != model.Avaleheinfo.TYYP_EMERGENCY:
      ${h.dlg_edit(h.url_current('edit', id=rcd.id), title=_("Teate muutmine"), size='md')}
      ${h.ajax_remove(h.url_current('delete', id=rcd.id), '#div_avaleheteated')}
      % elif c.user.on_admin:
      ${h.dlg_edit(h.url_current('edit', id=rcd.id), title=_("Teate muutmine"), size='md')}
      % endif
    </div>
    % endif
  </div>
</%def>

<%def name="infobox(rcd)">
  <%
  map_tyyp = {model.Avaleheinfo.TYYP_HOIATUS: 'info-red',
              model.Avaleheinfo.TYYP_TULEMUS: 'info-green',
              model.Avaleheinfo.TYYP_INFO: 'info-blue',
              }  
  %>    
  <div class="infobox mt-0">
    % if rcd.tyyp == model.Avaleheinfo.TYYP_EMERGENCY:
    <div class="alert alert-danger">
      ${rcd.sisu}
    </div>
    % else:
    <div class="${map_tyyp.get(rcd.tyyp)}">
      <h6>${rcd.pealkiri}</h6>
      <div>
        ${rcd.sisu}
        % if rcd.lisasisu:
        <div class="moreinfo">
          <button type="button" class="morebtn btn btn-link">${h.mdi_icon('mdi-menu-down')} ${_("Rohkem infot")}</button>
          <div class="morebody pl-3" style="display:none">
            ${rcd.lisasisu}
          </div>
        </div>
        % endif
      </div>
    </div>
    % endif
  </div>
</%def>
