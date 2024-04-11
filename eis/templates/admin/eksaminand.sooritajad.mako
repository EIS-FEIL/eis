## eksaminandi testisooritused
<div class="accordion" id="acc_j">
  <div class="accordion-card card parent-accordion-card">
    <div class="card-header" id="acc_heading_j">
      <div class="accordion-title">
        <button class="btn btn-link" type="button"
                data-toggle="collapse" data-target="#collapse_j" aria-expanded="true" aria-controls="collpase_j">
          <span class="btn-label">
            <i class="mdi mdi-chevron-down"></i>
            ${_("Testid")}
          </span>
          <span class="badge badge-pill badge-light">${len(c.sooritajad)}</span>          
        </button>
      </div>
    </div>
    <div id="collapse_j" class="collapse show" aria-labelledby="acc_heading_j">
      <div class="card-body">
        <div class="content pt-2">
          ${self.search_filter()}
          ${self.list_results()}
        </div>
      </div>
    </div>
  </div>
</div>

<%def name="search_filter()">
${h.form_search(h.url_current('show', id=c.item.id), id="form_search_j")}
${h.hidden('sub', 'sooritajad')}
<div class="gray-legend p-3 mb-1 filter-w">
  <div class="row">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi liik"), 'testiliik')}
        ${h.select('testiliik', c.testiliik, c.opt.testiliik, empty=True, ronly=False)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Sooritamise olek"),'staatus')}
        ${h.select('staatus', c.staatus, c.opt.opt_s_staatus_test, empty=True, ronly=False)}        
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit_dlg(_("Otsi"), container="$('#sooritajad')", clicked=True)}
      </div>
    </div>
  </div>
</div>
${h.end_form()}
</%def>

<%def name="list_results()">
% if not c.sooritajad:
${_("Kirjeid ei leitud")}
% else:
<table width="100%" class="table table-borderless table-striped tablesorter" border="0" >
  <thead>
    <tr>
      ${h.th(_("Test"))}
      ${h.th(_("Testi liik"))}
      ${h.th(_("Tase"))}
      ${h.th(_("Testimiskord"))}
      ${h.th(_("Aeg"))}
      ${h.th(_("Olek"))}
      ${h.th(_("Tulemus"))}
      ${h.th(_("Märkused"))}
      ${h.th(_("Sooritaja märkused"))}
      ${h.th(_("Tunnistus"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.sooritajad):
    <%
       test = rcd.test
       testimiskord = rcd.testimiskord
       tunnistused = [r.tunnistus for r in rcd.testitunnistused]
    %>
    <tr>
      <td>${test.nimi}
        % if rcd.kursus_kood:
        (${rcd.kursus_nimi})
        % endif
      </td>
      <td>
        ${test.testiliik_nimi}
      </td>
      <td>
        % if rcd.keeletase_kood:
        ${rcd.keeletase_nimi}
        % elif rcd.staatus < const.S_STAATUS_KATKESTATUD:
        ${test.keeletase_nimi}
        % endif
      </td>
      <td>
        % if testimiskord:
        ${testimiskord.tahised}
        % endif
      </td>
      <td>${rcd.millal}</td>
      <td>${h.link_to(rcd.staatus_nimi, h.url('regamine', id=rcd.id))}</td>
      <td>
        % if rcd.hindamine_staatus == const.H_STAATUS_HINNATUD:
        <span class="invisible">${'%03d' % (rcd.tulemus_protsent or 0)}</span>
        ${h.link_to(rcd.get_tulemus(nl=False), h.url('otsing_testisooritus', id=rcd.id))}
        % endif
      </td>
      <td>
        ${rcd.markus}
        <%
          sooritused = list(rcd.sooritused)
          mitu = len(sooritused) > 1
        %>
        % for tos in sooritused:
        % if tos.on_rikkumine:
        <div>
          % if mitu:
          ${_("Rikkumise tõttu on testiosa {s} hinnatud 0 punktiga.").format(s=tos.testiosa.tahis)}
          % else:
          ${_("Rikkumise tõttu on töö hinnatud 0 punktiga.")}
          % endif
        </div>
        <div>
          ${tos.rikkumiskirjeldus}
        </div>
        % endif
        % endfor
      </td>
      <td>${rcd.reg_markus}</td>
      <td>
        % for n, tunnistus in enumerate(tunnistused):
        <% url_edit = h.url('otsing_tunnistus', id='%s.%s' % (tunnistus.id, tunnistus.fileext)) %>
        <div>
          ${tunnistus.testiliik_nimi}
          % if tunnistus.has_file:
          ${h.link_to(tunnistus.tunnistusenr, url_edit)}
          % else:
          ${tunnistus.tunnistusenr}
          % endif
          ${tunnistus.staatus_nimi}
          ${tunnistus.alus}

          % if tunnistus.pohjendus:
          <div>${tunnistus.pohjendus}</div>
          % endif
          % if tunnistus.tyh_pohjendus:
          <div>${tunnistus.tyh_pohjendus}</div>
          % endif
        </div>
        % endfor
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
</%def>
