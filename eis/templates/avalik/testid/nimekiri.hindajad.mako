<%
  grupp_id = const.GRUPP_HINDAJA_K
  labiviijad = [r for r in c.testiruum.labiviijad if r.kasutajagrupp_id == grupp_id]
%>
% if labiviijad:
<table class="table table-striped tablesorter">
  <caption>
    ${_("Hindajad")}
  </caption>
  <thead>
    <tr>
      ${h.th(_('Nimi'))}
      ${h.th(_("Ülesanded"))}
      ${h.th(_("Planeeritud tööde arv"))}
      ${h.th(_("Pooleli hindamiste arv"))}
      ${h.th(_("Hinnatud tööde arv"))}
      % if c.can_update:
      ${h.th('', sorter='false', width="20px")}
      % endif
    </tr>
  </thead>
  <tbody>
    % for lv in labiviijad:
    <% kasutaja = lv.kasutaja %>
    <tr>
      <td>${kasutaja.nimi}</td>
      <td>
        <% tahised = ', '.join([ly.testiylesanne.tahis for ly in lv.labiviijaylesanded]) %>
        ${tahised or _("kõik ülesanded")}
      </td>
      <td>${lv.planeeritud_toode_arv}</td>
      <td>${(lv.toode_arv or 0 ) - (lv.hinnatud_toode_arv or 0)}</td>
      <td>${lv.hinnatud_toode_arv}</td>
      % if c.can_update:
      <td>
        <% in_use = model.Session.query(model.Hindamine.id).filter_by(labiviija_id=lv.id).first() %>
        % if not in_use:
        ${h.remove(h.url('test_nimekiri_delete_otsihindaja', test_id=c.test.id, nimekiri_id=c.nimekiri.id, testiruum_id=c.testiruum.id, id=lv.id))}
        % endif
      </td>
      % endif
    </tr>
    % endfor    
  </tbody>
</table>
% endif

% if c.can_update:
<%
  testiosa_id = c.testiruum.testikoht.testiosa_id
  q = (model.Session.query(model.sa.func.count(model.Testiylesanne.id))
       .filter_by(testiosa_id=testiosa_id)
       .filter_by(arvutihinnatav=False))
  on_hinnatav = q.scalar() > 0
%>
% if on_hinnatav:
${h.btn_to_dlg(_("Lisa hindaja"),
h.url('test_nimekiri_otsihindajad', test_id=c.test.id, nimekiri_id=c.nimekiri.id, testiruum_id=c.testiruum.id),
title=_("Hindaja lisamine"), level=2)}
<span class="helpable" id="hlisahindaja"></span>
% endif
% endif
