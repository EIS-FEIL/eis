## -*- coding: utf-8 -*- 
<% 
   n = -1
   c.opt_toimumispaevad = c.toimumisaeg.get_toimumispaevad_opt()
   sorted_paketid = sorted(c.testikoht.testipaketid, key=lambda r: model.lang_sort(r.lang))
%>
<table width="100%" class="table table-borderless table-striped tablesorter mb-1" border="0" >
  <caption>${_("Testisooritusruumid")}</caption>
  <thead>
    <tr>
      % if c.toimumisaeg.ruumide_jaotus:
      <th></th>
      % endif
      ${h.th(_("Testiruum"))}
      ${h.th(_("Ruum"))}
      ${h.th(_("Kohti"))}
      ${h.th(_("Sooritajaid"))}
      % for tpakett in sorted_paketid:
         % if len(sorted_paketid) == 1:
          ${h.th(_("Protokollirühmad"))}
         % else:
          ${h.th(_("Protokollirühmad") + ' (%s)' % tpakett.lang_nimi)}
         % endif
      % endfor
      % for grupp_id in c.grupid_id:
        ${h.th(model.Kasutajagrupp.get(grupp_id).nimi)}
      % endfor
      ${h.th(_("Kuupäev"))}
      ${h.th(_("Kell"))}
    </tr>
  </thead>
  <tbody>
    <% on_maaratud_ruum = on_maaramata = on_kellata = False %>
    % for n, rcd in enumerate(c.testikoht.testiruumid):
    <%
      ruum = rcd.ruum
      cnt_sooritused = len(rcd.sooritused)
      mk_maaramata = not ruum and c.toimumisaeg.ruum_noutud
      if ruum:
         on_maaratud_ruum = True
      elif mk_maaramata and cnt_sooritused:
         on_maaramata = True
    %>
    <tr>
      % if c.toimumisaeg.ruumide_jaotus:
      <td>
        % if not mk_maaramata:
        ${h.radio('t_id', rcd.id, onchange="$('form#form_save #tpr_id').val('');$('form#form_save #testiruum_id').val($(this).val());toggle_add();")}
        % endif
      </td>
      % endif
      <td>
        ${rcd.tahis}
        ${h.hidden('ruum-%d.id' % n, rcd.id)}
      </td>
      <td>
        ${ruum and ruum.tahis or _("määramata")}
      </td>
      <td>
        % if not mk_maaramata:
        ${rcd.kohti}
        % endif
      </td>
      <td>
        ${cnt_sooritused}
      </td>
      % for tpakett in sorted_paketid:
      <td>
        % for tpr in rcd.testiprotokollid:
        % if tpr.testipakett_id == tpakett.id:
          <%
            tpr_arv = tpr.soorituste_arv
            if tpr.kursus_kood:
               label = f'{tpr.tahis} ({tpr.kursus_kood}, {tpr_arv})'
            else:
               label = f'{tpr.tahis} ({tpr_arv})'
          %>
          % if c.toimumisaeg.ruumide_jaotus and not mk_maaramata:
            ${h.radio('t_id', tpr.id, label=label, 
             onchange="$('form#form_save #testiruum_id').val('');$('form#form_save #tpr_id').val($(this).val());toggle_add();")}
          % else:
            ${label}
          % endif
          % if tpr_arv == 0 and c.toimumisaeg.ruumide_jaotus:
               ${h.remove(h.url('korraldamine_delete_testiprotokoll', testikoht_id=c.testikoht.id, testipakett_id=tpakett.id, testiruum_id=rcd.id, id=tpr.id))}
          % endif
        % endif
        % endfor

        % if c.toimumisaeg.ruumide_jaotus and not mk_maaramata:        
          <span class="ml-2">
          ${h.add(h.url('korraldamine_create_testiprotokollid', testikoht_id=c.testikoht.id, 
          testipakett_id=tpakett.id, testiruum_id=rcd.id))}
          </span>
        % endif
      </td>
      % endfor
      % if mk_maaramata:
      <td colspan="${len(c.grupid_id) + 2}">
      </td>
      % else:
      % for grupp_id in c.grupid_id:
      <td>
        % for lv in rcd.labiviijad:
            % if lv.kasutajagrupp_id == grupp_id:
                <div>
                % if lv.kasutaja_id:
                     ${lv.kasutaja.nimi} 
                % else:
                     ${_("Määramata")}
                % endif
                </div>
            % endif
        % endfor
      </td>
      % endfor
      <td>
        <% dt = rcd.algus %>
        ${h.str_from_date(dt)}
      </td>
      <td>
        % if h.is_null_time(dt):
        ${_("Määramata")}
        <% on_kellata = True %>
        % else:
        ${h.str_time_from_datetime(dt)}
        % endif
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>

% if c.toimumisaeg.ruum_noutud and c.toimumisaeg.ruumide_jaotus:
% if not on_maaratud_ruum:
${h.alert_error(_("Sooritajad on vaja suunata ruumidesse. Loo testiruum ja suuna sooritajad sinna või või vali määramata ruumi asemel päris ruum."), False)}
% elif on_maaramata:
${h.alert_error(_("Sooritajad on vaja suunata ruumidesse. Suuna sooritajad ruumi või vali määramata ruumi asemel päris ruum."), False)}
% endif
% if on_kellata:
${h.alert_error(_("Testisooritusruumi kellaaeg on määramata."), False)}
% endif
% endif
