## eksaminandi rahvusvaheliste eksamite sooritused
<div class="accordion" id="acc_rvj">
  <div class="accordion-card card parent-accordion-card">
    <div class="card-header" id="acc_heading_rvj">
      <div class="accordion-title">
        <button class="btn btn-link" type="button"
                data-toggle="collapse" data-target="#collapse_rvj" aria-expanded="true" aria-controls="collpase_rvj">
          <span class="btn-label">
            <i class="mdi mdi-chevron-down"></i>
            ${_("Rahvusvahelised eksamitunnistused")}
          </span>
          <span class="badge badge-pill badge-light">${len(c.rvsooritajad)}</span>                    
        </button>
      </div>
    </div>
    <div id="collapse_rvj" class="collapse show" aria-labelledby="acc_heading_rvj">
      <div class="card-body">
        <div class="content pt-2">
          ${self.list_results()}
        </div>
      </div>
    </div>
  </div>
</div>

<%def name="list_results()">
<table width="100%" class="table table-borderless table-striped tablesorter" border="0" >
  <thead>
    <tr>
      ${h.th(_("Rahvusvaheline eksamitunnistus"))}
      ${h.th(_("Õppeaine"))}
      ${h.th(_("Tase"))}
      ${h.th(_("Väljastamisaeg"))}
      ${h.th(_("Kehtimise lõpp"))}
      ${h.th(_("Tulemus"))}
      ${h.th(_("Arvestatakse lõpetamisel"))}
      ${h.th(_("Tunnistuse nr"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.rvsooritajad):
    <%
       rveksam = rcd.rveksam
       tunnistus = rcd.tunnistus
       rvet = rcd.rveksamitulemus
       url_show = h.url('otsing_rvtunnistus', id=rcd.id)
    %>
    <tr>
      <td>
        ${h.link_to(rveksam.nimi, url_show)}
      </td>
      <td>${rveksam.aine_nimi}</td>
      <td>${rcd.keeletase_nimi}</td>
      <td>${h.str_from_date(tunnistus.valjastamisaeg)}</td>
      <td>${h.str_from_date(rcd.kehtib_kuni)}</td>
      <td>
        <% 
           if rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PALL:
              yhik = 'p'
           elif rveksam.tulemusviis == model.Rveksam.TULEMUSVIIS_PROTSENT:
              yhik = '%'
           else:
              yhik = ''
        %>
        % if rcd.tulemus != None:
        ${h.fstr(rcd.tulemus)}${yhik}
        % elif rvet and (rvet.alates or rvet.kuni):
        ${h.fstr(rvet.alates)}-${h.fstr(rvet.kuni)}${yhik}
        % elif rvet:
        ${rvet.tahis}
        % endif
      </td>
      <td>${h.sbool(rcd.arvest_lopetamisel)}</td>
      <td>${tunnistus.tunnistusenr}</td>
    </tr>
    % endfor
  </tbody>
</table>
</%def>
