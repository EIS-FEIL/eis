        <table width="100%" class="table table-borderless table-striped" >
          <thead>
            ${h.th( _('Test'))}
            ${h.th( _('Vastamise vorm'))}
            ${h.th( _('Toimumisaja tähis'))}
            ${h.th( _('Toimumise aeg'))}
            ${h.th( _('Roll'))}
            ${h.th( _('Määratud komisjoni'))}
            <th></th>
          </thead>
          <tbody>
            % for n, rcd in enumerate(c.items):
            <% 
               toimumisaeg, test = rcd
               testiosa = toimumisaeg.testiosa
               on_roll = lambda g_id: toimumisaeg.get_valik_q(g_id, kasutaja_id=c.user.id, on_piirkond=False, on_kaskkiri=False, on_koolitus=False).count() > 0
               if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
                  on_intervjueerija = toimumisaeg.intervjueerija_maaraja and on_roll(const.GRUPP_INTERVJUU)
                  on_hindaja = on_roll(const.GRUPP_HINDAJA_S)
               elif testiosa.vastvorm_kood == const.VASTVORM_I:
                  on_intervjueerija = toimumisaeg.intervjueerija_maaraja and on_roll(const.GRUPP_INTERVJUU)
                  on_hindaja = on_roll(const.GRUPP_HINDAJA_K)
               else:
                  on_intervjueerija = False
                  on_hindaja = on_roll(const.GRUPP_HINDAJA_K)

               on_vaatleja = toimumisaeg.vaatleja_maaraja and on_roll(const.GRUPP_VAATLEJA)
               maaramised = toimumisaeg.get_labiviijad(c.kasutaja.id)
            %>
            % if on_intervjueerija or on_hindaja or on_vaatleja or len(maaramised):
            <%
               nousolek = toimumisaeg.get_nousolek(c.kasutaja.id)
               c.on_moni_eksam = True
            %>
            <tr>
              <td>
                ${test.nimi}
                ${h.hidden('ta-%s.toimumisaeg_id' % n, toimumisaeg.id)}
              </td>
              <td>${testiosa.vastvorm_nimi}</td>
              <td>${toimumisaeg.tahised}</td>
              <td>${toimumisaeg.millal}</td>
              <td>
                <%
                   opt_bool = (('1',  _('jah')), ('0',  _('ei')))
                   nbool = lambda b: b == False and '0' or b == True and '1' or 'none'
                %>
                <table width="100%">
                  <col width="80"/>
                  <col/>
                  <col/>                  
                % if on_vaatleja:
                <tr>
                  <td class="frh2">Vaatleja:</td>
                  <td>
                    ${h.select_radio('ta-%s.on_vaatleja' % n,
                    nbool(nousolek and nousolek.on_vaatleja),
                    opt_bool,
                    class_='onoff',
                    disabled=not toimumisaeg.vaatleja_maaraja or not toimumisaeg.reg_labiviijaks)}
                  </td>
                  <td>
                    % if nousolek and nousolek.on_vaatleja:
                      (${_("nõusolek antud {dt}").format(dt=h.str_from_date(nousolek.hindaja_aeg))})
                    % endif
                  </td>
                </tr>
                % endif
                % if on_hindaja:
                <tr>
                  <td class="frh2">${_("Hindaja:")}</td>
                  <td>
                    ${h.select_radio('ta-%s.on_hindaja' % n,
                    nbool(nousolek and nousolek.on_hindaja),
                    opt_bool,
                    class_='onoff',
                    disabled=not toimumisaeg.reg_labiviijaks)}
                    <!-- ns ${nousolek and nousolek.id or ''} -->
                  </td>
                  <td>
                    % if nousolek and nousolek.on_hindaja:
                      (nõusolek antud ${h.str_from_date(nousolek.hindaja_aeg)})
                    % endif
                  </td>
                </tr>
                % endif
                % if on_intervjueerija:
                <tr>
                  <td class="frh2">${_("Intervjueerija:")}</td>
                  <td>
                    ${h.select_radio('ta-%s.on_intervjueerija' % n,
                    nbool(nousolek and nousolek.on_intervjueerija),
                    opt_bool,
                    class_='onoff',
                    disabled=not toimumisaeg.intervjueerija_maaraja or not toimumisaeg.reg_labiviijaks)}
                  </td>
                  <td>
                    % if nousolek and nousolek.on_intervjueerija:
                      (nõusolek antud ${h.str_from_date(nousolek.intervjueerija_aeg)})
                    % endif
                  </td>
                </tr>
                % endif
                </table>
              </td>
              <td>
                % if len(maaramised):
                  % for s in maaramised:
                  <div>
                     % if s.testiruum:
                     <%
                       testiruum = s.testiruum
                       koht = testiruum.testikoht.koht
                       ruum = testiruum.ruum
                     %>
                       % if koht:
                       ${koht.nimi}
                       % endif
                     ${s.testiruum.ruum and s.testiruum.ruum.tahis or ''}
                     <br/>
                     % endif
                     ${s.kasutajagrupp.nimi}
                  </div>
                  % endfor
                % else:
                  ${_("Ei ole määratud")}
                % endif
              </td>
              <td>
              </td>
            </tr>
            % endif
            % endfor
          </tbody>
        </table>
<br/>

<table class="form epost" width="100%" style="display:none">
  <col width="180"/>
  <tr>
    <td class="fh">${_("E-post")}</td>
    <td class="err-parent">${h.text('k_epost', c.kasutaja.epost, size=40)}</td>
  </tr>
</table>

<script>
  $(document).ready(function(){
     $('table.epost').toggle($('input.onoff[value="1"]:checked').length > 0);
     $('input.onoff').change(function(){
          $('table.epost').toggle($('input.onoff[value="1"]:checked').length > 0);
     });
    $('div#savefooter').toggle(${c.on_moni_eksam and 'true' or 'false'});
  });
</script>
