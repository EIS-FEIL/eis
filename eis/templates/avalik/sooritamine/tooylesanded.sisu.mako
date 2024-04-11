<h1>${c.test.nimi}</h1>
<div class="gray-legend d-flex flex-wrap mb-2 p-3">
  <div class="item mr-5">
    ${h.flb(_("Õppeaine"), 'aine_nimi')}
    <div id="aine_nimi">
      ${model.Klrida.get_str('AINE', c.test.aine_kood)}
    </div>
  </div>
  % if c.nimekiri and c.nimekiri.esitaja_kasutaja_id:
  <div class="item mr-5">
    ${h.flb(_("Lahendamiseks suunaja"), 'esitaja_kasutaja')}
    <div id="esitaja_kasutaja">
      ${c.nimekiri.esitaja_kasutaja.nimi}
    </div>
  </div>
  % endif
  % if c.nimekiri and (c.nimekiri.alates or c.nimekiri.kuni):
  <div class="item mr-5">
    ${h.flb(_("Ülesannete lahendamise ajavahemik"), 'ajavahemik')}
    <div id="ajavahemik">
      ${h.str_from_date(c.nimekiri.alates)} - ${h.str_from_date(c.nimekiri.kuni) or _("määramata")}
    </div>
  </div>
  % endif
  % if c.sooritus.piiraeg:
  <div class="item mr-5">
    ${h.flb(_("Lahendaja piiraeg"), 'piiraeg')}
    <div id="piiraeg">
      ${h.str_from_time(c.sooritus.piiraeg)}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Ajakulu"),'ajakulu')}
    <div id="ajakulu">
      ${h.str_from_time(c.sooritus.ajakulu or 0)}
    </div>
  </div>
  % endif
</div>

<% testiosa_sooritajajuhend = c.testiosa.sooritajajuhend %>
% if testiosa_sooritajajuhend:
<p class="mb-3">${testiosa_sooritajajuhend}</p>
% endif

<%
  today = model.date.today()
  can_solve = not c.nimekiri or (not c.nimekiri.alates or c.nimekiri.alates <= today) and \
              (not c.nimekiri.kuni or c.nimekiri.kuni >= today)
%>
<table width="100%" class="table" >
  <thead>
    <tr>
      <th>${_("Ülesanne")}</th>
      <th colspan="2">${_("Olek")}</th>
      <th colspan="2">${_("Tulemus")}</th>
    </tr>
  </thead>
  <tbody>
    % for ty in c.testiylesanded:
    ${self.nav_task(ty, can_solve)}
    % endfor
  </tbody>
</table>


<%def name="nav_task(ty, can_solve)">
<%
  vy = model.SessionR.query(model.Valitudylesanne).filter_by(testiylesanne_id=ty.id).first()
  yv = c.sooritus.get_ylesandevastus(ty.id, kehtiv=True)
  on_pooleli = c.pooleli_tyy_id and (ty.id in c.pooleli_tyy_id)
  url_show = h.url_current('show', id=vy.id)
  url_edit = h.url_current('edit', id=vy.id)

  ylesanne = vy.ylesanne
  result = tagasiside_msg = ''
  if yv:
     if ylesanne.on_tagasiside:
        if ylesanne.on_pallid and yv.pallid is not None:
           # kui tagasiside on punktide alusel, siis kuvatakse tulemusena punkte
           result = '%sp' % h.fstr(yv.pallid,1)
        tagasiside_msg = yv.get_tagasiside(request.handler, ylesanne, c.lang)
     if not result:
        prot = yv.get_protsent()
        if prot is not None:
           result = '%s%%' % h.fstr(prot, 0)
%>
    <tr>
      <td>
        ${ty.seq}.
        % if not ylesanne:
        ${_("Ülesanne puudub")}
        % elif yv and not on_pooleli and url_show:
        ## kinnitatud vastuse vaatamine
        ${h.link_to(ylesanne.nimi, url_show)}
        % elif url_edit and can_solve:
        ## lahendamine
        ${h.link_to(ylesanne.nimi, url_edit, method='get')}
        % else:
        ${ylesanne.nimi}
        % endif
      </td>
      <td>
        % if yv:
        ${_("Kinnitatud")}
        % elif on_pooleli:
        ${_("Pooleli")}
        % else:
        ${_("Alustamata")}
        % endif
      </td>
      <td>
        % if yv and not on_pooleli and can_solve:
        ${h.btn_to(_("Proovi uuesti"), url_edit, method='get', level=2)}
        % endif
      </td>
      <td>
        % if result:
        ${result}
        % endif
      </td>
      <td>
      % if tagasiside_msg:
        ${h.button(_("Loe tagasisidet"),
        onclick="dialog_el($(this).closest('td').find('.tsmsg'), '%s', 600);" % (_("Tagasiside")))}
        <div class="tsmsg" style="display:none">
          ${tagasiside_msg}
        </div>
      % endif
      </td>
    </tr>

</%def>
