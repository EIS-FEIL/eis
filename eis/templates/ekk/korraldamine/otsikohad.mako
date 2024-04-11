${h.form_search(url=h.url('korraldamine_otsikohad',
toimumisaeg_id=c.toimumisaeg.id))}

% for tr_id in c.suunatavad_tr_id:
${h.hidden('tr_id', tr_id)}
% endfor

<% 
   tpr_maht = c.toimumisaeg.protok_ryhma_suurus
%>

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Piirkond"),'piirkond_id')}
        <div>
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Vabade kohtade arv"),'vabukohti')}
        <div>${h.posint('vabukohti', c.vabukohti)}</div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Maakond"), 'maakond_kood')}
        ${h.select('maakond_kood', c.maakond_kood, model.Aadresskomponent.get_opt(None), empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">    
      <div class="form-group d-flex flex-wrap">
        <div class="brown mr-3">${_("Suunatavate sooritajate arv")}: ${c.suunatavate_arv}</div>
        ${h.submit_dlg(_("Otsi"))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<%include file="/common/message.mako"/>
% if c.items:
${h.form(h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id), method='post')}
${h.hidden('sub','suunamine')}
% for tr_id in c.suunatavad_tr_id:
${h.hidden('tr_id', tr_id)}
% endfor

<div class="listdiv">
      <table border="0"  class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th sorter="false"></th>
            % if c.show_tpr:
            <th sorter="false">${_("Protokollirühm")}</th>
            % endif
            ${h.th(_("Soorituskoht"))}
            ${h.th(_("Asukoht"))}
            ${h.th(_("Testiruum"))}
            ${h.th(_("Ruum"))}
            ${h.th(_("Kohti"))}
            ${h.th(_("Sooritajaid"))}
            ${h.th(_("Algus"))}
          </tr>
        </thead>
        <tbody>
          % for n, rcd in enumerate(c.items):
          <% 
             testiruum, koht, ruum = rcd 
             vabu = testiruum.vabukohti
             on_vabu = vabu is None or vabu >= c.suunatavate_arv
          %>
          <tr>
            <td>
              % if on_vabu:
              ${h.submit(_("Vali"),id='valik_id_%d' % testiruum.id)}
              % endif
            </td>
            % if c.show_tpr:
            <td>
              % if on_vabu:
                % for tpr in testiruum.testiprotokollid:
                  <% 
                     tpr_arv = tpr.soorituste_arv
                     ei_mahu = tpr_maht and tpr_maht < tpr_arv + c.suunatavate_arv
                  %>
                 ${h.radio('tpr_id', tpr.id, disabled=ei_mahu)}
                 ${tpr.tahis} (${tpr_arv})
                % endfor
              % endif
            </td>
            % endif
            <td>${koht.nimi}</td>
            <td>
              % if koht.aadress:
              ${koht.aadress.tais_aadress}
              % endif
            <td>${testiruum.tahis}</td>
            <td>${ruum and ruum.tahis or _("Määramata")}</td>
            <td>${testiruum.kohti}</td>
            <td>${testiruum.sooritajate_arv}</td>
            <td>${h.str_from_datetime(testiruum.algus)}</td>
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

${h.end_form()}

% endif

