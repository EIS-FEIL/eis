<%
  is_main_subject = c.yaine_seq == 0
  prefix = 'ya-%d.' % c.yaine_seq
  item = c.yaine
%>

  <div class="form-group row">
    ${h.flb3(is_main_subject and _("Põhiõppeaine") or _("Õppeaine"), prefix + 'aine_kood', rq=True)}
    <div class="col-lg-8">
      <% aine_opt = c.opt.klread_kood('AINE') %>
      ${h.select(prefix + 'aine_kood', item.aine_kood, aine_opt, empty=True, class_="aine")}
    </div>
    <div class="col-lg-1 frh seotud">
      % if c.is_edit and not is_main_subject:
      ${h.grid_s_remove('div.ylesandeaine', confirm=True)}
      % endif
      ${h.hidden(prefix + 'id', item.id)}
    </div>

    ${h.flb3(_("Oskus"), prefix + 'oskus_kood')}
    <div class="col-lg-9">
      ${h.select(prefix + 'oskus_kood', item.oskus_kood,
      c.opt.klread_kood('OSKUS', item.aine_kood,ylem_required=True,empty=True, vaikimisi=item.oskus_kood),
      class_="oskus")}
    </div>
  </div>
   
  <div class="form-group row">
    ${h.flb3(_("Teema"), prefix + 'teemad2')}
    <div class="col-lg-9 div-teemad">
      % if c.is_edit:
      <%
        opt_teemad = c.opt.teemad2(item.aine_kood, c.aste_kood)
      %>
      ${h.select2(prefix + 'teemad2', item.teemad2, [], data=opt_teemad, multiple=True, multilevel=True, template_selection='template_selection2', class_="teemad2")}
      % else:
      <% ylesandeteemad = list(item.ylesandeteemad) %>
      % if ylesandeteemad:
      <div class="div-teemad">
        % for r in ylesandeteemad:
        <div class="row">
          <div class="col-md-6">
            ${h.roxt(r.teema_nimi)}
          </div>
          <div class="col-md-6">
            ${h.roxt(r.alateema_nimi)}
          </div>
        </div>
        % endfor
      </div>
      % endif
      % endif
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Õpitulemused"), prefix + 'opitulemused')}
    <div class="col-lg-9 div-opitulemused">
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

