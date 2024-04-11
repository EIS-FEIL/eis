${h.form_search(url=h.url('korraldamine_otsilabiviijad',
testikoht_id=c.testikoht.id), class_="form-search-dlg")}
${h.hidden('grupp_id', c.grupp_id)}
${h.hidden('labiviija_id', c.labiviija_id)}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-8">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.button(_("Otsi"), onclick="var url='%s?'+$(this.form).serialize();dialog_load(url);" % h.url('korraldamine_otsilabiviijad',testikoht_id=c.testikoht.id))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="p-1">
  <div class="d-flex">
    <div class="flex-grow-1">
      % if c.kasutaja:
      <h4>${c.kasutaja.nimi}</h4>
      % endif
    </div>
    % if c.muuda_profiil:
    <div class="pl-2">
      ${h.btn_to_dlg(_("Muuda isiku profiili"), h.url_current('edit', id=c.kasutaja.id, grupp_id=c.grupp_id, labiviija_id=c.labiviija_id), method='get', title=c.kasutaja.nimi, width=800, level=2, mdicls='mdi-file-edit', size='lg')}
    </div>
    % endif
    % if c.seo_kohaga:
    <div class="pl-2">
      ${h.form(h.url_current('update', id=c.kasutaja.id))}
      ${h.hidden('grupp_id', c.grupp_id)}
      ${h.hidden('labiviija_id', c.labiviija_id)}
      ${h.hidden('sub', 'seo')}
      ${h.submit_dlg(_("Seo soorituskohaga"), "$('.form-search-dlg').parent()", level=2)}
      ${h.end_form()}
    </div>
    % endif
  </div>
</div>
<%include file="/common/message.mako"/>

% if c.items != '' and not c.items:
${h.alert_error(_("Otsingu tingimustele vastavaid isikuid ei leitud"))}
% elif c.items:
${h.form(h.url('korraldamine_labiviijad', testikoht_id=c.testikoht.id), method='post')}
${h.hidden('grupp_id', c.grupp_id)}
${h.hidden('labiviija_id', c.labiviija_id)}

% if not c.labiviija:
% if c.grupp_id != const.GRUPP_KOMISJON_ESIMEES or c.testikoht.toimumisaeg.on_ruumiprotokoll:
  <%
  maaramata = not c.toimumisaeg.ruum_noutud
  opt_testiruumid = c.testikoht.get_testiruumid_opt(maaramata)
  %>
  % if not opt_testiruumid:
  <% c.items = [] %>
  ${h.alert_error(_("Testiruum on määramata. Palun määra esmalt testiruum."), False)}
  % else:
  <div class="row filter">
    <div class="col-12 col-md-4 text-md-right">
      <div class="form-group">    
        ${h.flb(_("Ruum"))}
      </div>
    </div>
    <div class="col-12 col-md-8">
      <div class="form-group">    
      ${h.select('testiruum_id', c.testiruum_id or opt_testiruumid[0][0], opt_testiruumid, multiple=True)}
      </div>
    </div>
  </div>
  % endif
% endif
% endif

% if c.items:
<% testsessioon_id = c.toimumisaeg.testimiskord.testsessioon_id %>

<div class="listdiv">
      <table class="table table-striped tablesorter" id="table_isikud">
        <thead>
          <tr>
            <th></th>
            ${h.th(_("Isik"))}
            ${h.th(_("Muud osalemised"))}
          </tr>
        </thead>
        <tbody>
          % for n, rcd in enumerate(c.items):
          <tr>
            <td>
              ${h.submit_dlg(_("Vali"),op=f'valik_id_{rcd.id}')}
            </td>
            <td>${rcd.nimi}</td>
            <td>
              <%
                 muud_cnt = model.Labiviija.query.filter_by(kasutaja_id=rcd.id).join(model.Labiviija.toimumisaeg).join(model.Toimumisaeg.testimiskord).filter(model.Testimiskord.testsessioon_id==testsessioon_id).count()
              %>
              ${muud_cnt}
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
  });
</script>
</div>
% endif

${h.end_form()}

% endif

