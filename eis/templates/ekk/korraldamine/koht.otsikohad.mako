## post index, et saaks paljude soorituste ID-d edasi kanda
${h.form(url=h.url('korraldamine_koht_otsikohad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id), method='post', id='form_search')}

<% sooritused_id = isinstance(c.sooritus_id, list) and c.sooritus_id or [c.sooritus_id] %>
% for sooritus_id in sooritused_id:
${h.hidden('sooritus_id', sooritus_id)}
% endfor

<% 
   suunatavate_arv = len(sooritused_id)
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
      <div class="form-group d-flex flex-wrap justify-content-end">
        <div class="brown mr-3">${_("Suunatavate sooritajate arv")}: ${suunatavate_arv}
        </div>
        ${h.submit_dlg(_("Otsi"))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<%include file="/common/message.mako"/>
% if c.items:
${h.form(h.url('korraldamine_koht_sooritajad', toimumisaeg_id=c.toimumisaeg.id,testikoht_id=c.testikoht_id), method='post')}
${h.hidden('sub','suunamine')}
% for sooritus_id in sooritused_id:
${h.hidden('sooritus_id', sooritus_id)}
% endfor

<div class="listdiv">
      <table class="table table-borderless table-striped tablesorter" id="table_isikud">
        <thead>
          <tr>
            ${h.th('', sorter=False)}
            % if c.show_tpr:
            ${h.th(_("Protokollirühm"), sorter=False)}
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
             on_vabu = vabu is None or vabu >= suunatavate_arv
             if not on_vabu:
                jubaruumis = c.suunatavad.get(testiruum.id) or 0
                on_vabu = vabu >= suunatavate_arv - jubaruumis
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
                     ei_mahu = tpr_maht and tpr_maht < tpr_arv + suunatavate_arv
                     if tpr.kursus_kood:
                         label = f'{tpr.tahis} ({tpr.kursus_nimi}, {tpr_arv})'                                  
                     else:
                         label = f'{tpr.tahis} ({tpr_arv})'                                  
                  %>
                    ${h.radio('tpr_id', tpr.id, disabled=ei_mahu, label=label)}
                % endfor
              % endif
            </td>
            % endif
            <td>${koht.nimi}</td>
            <td>
              ${koht.tais_aadress}
            <td>${testiruum.tahis}</td>
            <td>${ruum and ruum.tahis or _("Määramata")}</td>
            <td>${testiruum.kohti}</td>
            <td>${testiruum.sooritajate_arv}</td>
            <td>${h.str_from_datetime(testiruum.algus, hour0=False)}</td>
          </tr>
          % endfor
        </tbody>
      </table>
</div>

${h.end_form()}

% endif

