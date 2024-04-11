${h.form_save(c.item.id)}
<% c.on_avalik_test = c.item.avalik_test %>
% if c.item.avalik_test_id:
<div style="text-align:right">
  % if c.on_avalik_test:
  ${h.link_to(_("Avalik test") + ' %s' %  c.avalik_test.id, h.url('test', id=c.avalik_test.id))}
  % else:
  ${_("Avalik test")} ${c.item.avalik_test_id} (${_("kustutatud")})
  <% c.can_update = False %>
  % endif
</div>
% endif

${self.eeltest()}

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    <% markused = c.avalik_test and c.avalik_test.testimarkused or [] %>
    % if len(markused):
    ${h.btn_to_dlg(_("Korraldajate tagasiside") + ' (%s)' % len(markused), 
    h.url('test_eeltest', test_id=c.test.id, id=c.item.id, sub='markus', partial=True), 
    title=_("Korraldajate tagasiside"), size='lg', level=2)}
    % endif
  </div>
  % if c.can_update:
  % if c.is_edit:
  ${h.submit()}
  % else:
  ${h.btn_to(_("Muuda"), h.url('test_edit_eeltest',
  test_id=c.test.id, id=c.item.id))}
  % endif
  % endif
</div>

${h.end_form()}

% if c.on_avalik_test:
      ${self.korraldajad()}
      <br/>

      <%
        opt_korraldajad = c.avalik_test.opt_korraldajad
        on_sooritajad = model.SessionR.query(model.Sooritaja.id).filter_by(test_id=c.avalik_test.id).first()
      %>
      % if opt_korraldajad and on_sooritajad:
      ${h.form(h.url('test_eeltest', test_id=c.test.id, id=c.item.id), method='get',id='form_korraldaja')}
      ${self.lahendajad(opt_korraldajad)}
      ${h.end_form()}
      <br/>
      ${h.btn_to_dlg(_("Saada korraldajatele teade"), 
      h.url('test_edit_eeltest', test_id=c.test.id, id=c.item.id, sub='mail',partial=True), 
      title=_("Teate saatmine"), width=560)}

      ${h.btn_to_dlg(_("Statistika"),
      h.url_current('edit', test_id=c.test.id, id=c.item.id, sub='statistika',partial=True), 
      title=_("Tulemuste statistika"), width=700)}
      % endif
% endif

% if c.item.stat_ts:
      ${h.btn_to(_("Vastuste statistika"), h.url_current('download', format='pdf'))}
% endif      

% if c.on_avalik_test and on_sooritajad or c.item.stat_ts:
<%
url = None
if c.on_avalik_test:
   try:
      ta = c.avalik_test.testimiskorrad[0].toimumisajad[0]
      url = h.url('hindamine_analyys_vastused', toimumisaeg_id=ta.id)
   except:
      url = None
if c.item.stat_ts:
   buf = _("Vastuste statistika on salvestatud {s}").format(s=h.str_from_datetime(c.item.stat_ts))
else:
   buf = _("Vastuste statistikat pole salvestatud")
%>
<div class="mt-4 ${not c.item.stat_ts and 'alert alert-secondary' or ''}">
${url and h.link_to(buf, url) or buf}
</div>
% endif
      
% if c.dialog_mail:
<div id="div_dialog_mail">
  <%include file="eeltest.mail.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_mail'), 'title':'${_("Teate saatmine")}'});
  });
</script>
% endif

<%def name="eeltest()">
${h.rqexp()}
<div class="form-wrapper mb-2">
  <div class="form-group  row">
    ${h.flb3(_("Ülesandekomplektid"), rq=True)}
    <div class="col">
            <table id="kvalikud">
              <tbody>
                <%
                  is_select_k = c.action in ('new','create')
                  mitu_testiosa = len(c.test.testiosad) > 1
                  komplektid_id = [k.id for k in c.item.komplektid]
                  kvalikud_id = [k.komplektivalik_id for k in c.item.komplektid]
                %>
                % for osa in c.test.testiosad:
                <%
                  on_alatestid = osa.on_alatestid
                  kvalikud = list(osa.komplektivalikud)
                  if not is_select_k:
                     kvalikud = [kv for kv in kvalikud if kv.id in kvalikud_id]
                %>
                % for ind, kv in enumerate(kvalikud):
                <tr class="kvalik-${osa.id}">
                  % if mitu_testiosa and ind == 0:
                  <td rowspan="${len(kvalikud)}">${_("Testiosa")} ${osa.tahis}</td>
                  % endif
                  <td>
                    % if on_alatestid:
                    ${_("Alatest")} ${kv.str_alatestid}:
                    % endif
                  </td>
                  <td>
                    % if not is_select_k:
                    ## kui eeltest on juba loodud, siis enam komplektide valikut ei muuda
                    ${', '.join([k.tahis for k in kv.komplektid if k.id in komplektid_id])}
                    % else:
                    ## enne uue eeltesti loomist saab valida komplektid
                    % for k in kv.komplektid:
                    % if k.staatus != const.K_STAATUS_ARHIIV:
                    ${h.checkbox('komplekt_id', k.id, checkedif=komplektid_id, label=k.tahis)}
                    % endif
                    % endfor
                    % endif
                  </td>
                </tr>
                % endfor
                % endfor
              </tbody>
            </table>
            <script>
              ## peale komplekti valimist eemaldada teiste testiosade komplektide valik
              $('input[name="komplekt_id"]').change(function(){
                 var osakls = $(this).closest('tr').attr('class');
                 $('#kvalikud tr:not(.' + osakls + ') input[name="komplekt_id"]').prop('checked', false);
              });
            </script>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Avaldamise tase"), rq=True)}
    <div class="col">
            ${h.select('t_avaldamistase', c.avalik_test and c.avalik_test.avaldamistase,
            ((const.AVALIK_OPETAJAD, _("Kõikidele pedagoogidele kasutamiseks")),
            (const.AVALIK_MAARATUD, _("Määratud isikutele kasutamiseks"))),
            wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Avalik"))}
    <div class="col">
            ${_("alates")}
            ${h.date_field('t_avalik_alates', c.avalik_test and c.avalik_test.avalik_alates, wide=False)}
            ${_("kuni")}
            ${h.date_field('t_avalik_kuni', c.avalik_test and c.avalik_test.avalik_kuni, wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Märkused"))}
    <div class="col">
      ${h.textarea('e_markus_korraldajatele',
      c.item.markus_korraldajatele, rows=5, cols=70)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      ${h.checkbox1('e_tagasiside_sooritajale', 1, checked=c.item.tagasiside_sooritajale,
      label=_("Sooritaja näeb tagasisidet"))}
      <br/>
      ${h.checkbox1('e_tagasiside_koolile', 1, checked=c.item.tagasiside_koolile,
      label=_("Korraldaja näeb tagasisidet"))}      
    </div>
  </div>
</div>
</%def>

<%def name="korraldajad()">
      <table width="100%" border="0"  class="table table-borderless table-striped tablesorter">
        <caption>${_("Korraldajad")}</caption>
        <thead>
          <tr>
            <th></th>
            ${h.th(_("Korraldaja isikukood"))}
            ${h.th(_("Korraldaja nimi"))}
            ${h.th(_("Lahendajaid"))}
            ${h.th(_("Lahendatud"))}
          </tr>
        </thead>
        <tbody>
          % if c.avalik_test.avaldamistase == const.AVALIK_MAARATUD:
          % for k in c.avalik_test.testiisikud:
            % if k.kasutajagrupp_id == c.korraldaja_grupp.id:
            <% kasutaja = k.kasutaja %>
          <tr>
            <td>
              % if c.can_update:
              ${h.remove(h.url('test_delete_eeltest', test_id=c.test.id,
              id=c.item.id, sub='korraldaja', isik_id=k.id))}
              % endif
            </td>
            <td>${kasutaja.isikukood}</td>
            <td>${kasutaja.nimi}</td>
            ##<td>${h.str_from_date(k.kehtib_kuni_ui)}</td>
            <% sooritajad = c.get_sooritajad(c.avalik_test, k.kasutaja_id) %>
            <td>${len(sooritajad)}</td>
            <td>${len([s for s in sooritajad if s.staatus == const.S_STAATUS_TEHTUD])}</td>
          </tr>
             % endif
          % endfor
          % else:
          % for k in c.avalik_test.nimekirjad:
          <% kasutaja = k.esitaja_kasutaja %>
          <tr>
            <td>
            </td>
            <td>
              % if kasutaja:
              ${kasutaja.isikukood}
              % endif
            </td>
            <td>
              % if kasutaja:
              ${kasutaja.nimi}
              % endif
            </td>
            <% sooritajad = c.get_sooritajad(c.avalik_test, k.esitaja_kasutaja_id) %>
            <td>${len(sooritajad)}</td>
            <td>${len([s for s in sooritajad if s.staatus == const.S_STAATUS_TEHTUD])}</td>
          </tr>
          % endfor
          % endif
        </tbody>
        % if c.avalik_test.avaldamistase == const.AVALIK_MAARATUD:
          % if c.can_update:
        <tfoot>
          <tr>
            <td colspan="5"  class="field_body">
              ${h.btn_to_dlg(_("Lisa"), h.url('test_korraldajad', test_id=c.test.id, komplekt_id=c.item.id),
              title=_("Korraldaja lisamine"), width=600)}
              ${h.btn_to_dlg(_("Lisa failist"), h.url('test_korraldajad', test_id=c.test.id, komplekt_id=c.item.id, sub='file'),
              title=_("Korraldajate lisamine"), width=600)}
            </td>
          </tr>
        </tfoot>
          % endif
        % endif
      </table>
</%def>

<%def name="lahendajad(opt_korraldajad)">      
      <table width="100%" class="table table-borderless table-striped" border="0" >
        <caption>
          Lahendajad
        </caption>
        <thead>
          <tr>
            <td colspan="5">
              ${_("Korraldaja")} &nbsp; 
              ${h.select('korraldaja_id', c.korraldaja_id, opt_korraldajad, ronly=False,class_='nosave',empty=True, style="width:400px;", onchange="$('form#form_korraldaja').submit();")}
            </td>
          </tr>
          <tr>
            ${h.th(_("Korraldaja isikukood"))}
            ${h.th(_("Korraldaja nimi"))}
            ${h.th(_("Lahendaja isikukood"))}
            ${h.th(_("Lahendaja nimi"))}
            ${h.th(_("Lahendamise olek"))}
          </tr>
        </thead>
        <tbody>
          % for s in c.sooritajad:
          <tr>
            % if s.nimekiri and s.nimekiri.esitaja_kasutaja_id:
            <td>${s.nimekiri.esitaja_kasutaja.isikukood}</td>
            <td>${s.nimekiri.esitaja_kasutaja.nimi}</td>
            % else:
            <td colspan="2"></td>
            % endif
            <td>${s.kasutaja.isikukood}</td>
            <td>${s.nimi}</td>
            <td>
              <%
                s_url = None
                if s.staatus == const.S_STAATUS_TEHTUD:
                   for tos in s.sooritused:
                      s_url = h.url('tulemus_osa', test_id=c.test.id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id)
                      break
              %>
              % if s_url:
                 ${h.link_to(s.staatus_nimi, s_url, target="_blank")}
              % else:
                 ${s.staatus_nimi}
              % endif
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
</%def>
