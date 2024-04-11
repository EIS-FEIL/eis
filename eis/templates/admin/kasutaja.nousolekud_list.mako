        <table width="100%" class="table table-borderless table-striped" >
          <thead>
            ${h.th(_("Test"))}
            ${h.th(_("Toimumisaeg"))}
            ${h.th(_("Roll"))}
            ${h.th(_("Määratud komisjoni"))}
            <th></th>
          </thead>
          <tbody>
            % for n, rcd in enumerate(c.items):
            <% 
               toimumisaeg, test, nousolek = rcd 
            %>
            <tr>
              <td>
                ${test.nimi}
                ${toimumisaeg.testiosa.tahis}
                ${toimumisaeg.testiosa.vastvorm_nimi}
              </td>
              <td>${toimumisaeg.millal}</td>
              <td>
                ${h.hidden('ta-%s.toimumisaeg_id' % n, toimumisaeg.id)}

                % if toimumisaeg.vaatleja_maaraja:
                <div>
                <%
                  label = _("Vaatleja")
                  if nousolek and nousolek.on_vaatleja:
                     maaraja = None
                     if nousolek.vaatleja_ekk == True:
                         maaraja = _("EKK")
                     elif nousolek.vaatleja_ekk == False:
                         maaraja = _("ise")
                     if maaraja:
                         kpv = h.str_from_date(nousolek.vaatleja_aeg)
                         label += f' ({maaraja} {kpv})'
                %>
                ${h.checkbox('ta-%s.on_vaatleja' % n, 1, 
                disabled=not toimumisaeg.vaatleja_maaraja,
                checked=nousolek and nousolek.on_vaatleja,
                label=label)}
                </div>
                % endif

                <div>
                <%
                  label = _("Hindaja")
                  if nousolek and nousolek.on_hindaja:
                     maaraja = None
                     if nousolek.hindaja_ekk == True:
                         maaraja = _("EKK")
                     elif nousolek.hindaja_ekk == False:
                         maaraja = _("ise")
                     if maaraja:
                         kpv = h.str_from_date(nousolek.hindaja_aeg)
                         label += f' ({maaraja} {kpv})'
                %>
                  ${h.checkbox('ta-%s.on_hindaja' % n, 1, 
                   checked=nousolek and nousolek.on_hindaja, label=label)}
                </div>
                
                % if toimumisaeg.intervjueerija_maaraja:
                <div>
                <%
                  label = _("Intervjueerija")
                  if nousolek and nousolek.on_intervjueerija:
                     maaraja = None
                     if nousolek.intervjueerija_ekk == True:
                         maaraja = _("EKK")
                     elif nousolek.intervjueerija_ekk == False:
                         maaraja = _("ise")
                     if maaraja:
                         kpv = h.str_from_date(nousolek.intervjueerija_aeg)
                         label += f' ({maaraja} {kpv})'
                %>
                ${h.checkbox('ta-%s.on_intervjueerija' % n, 1, 
                disabled=not toimumisaeg.intervjueerija_maaraja,
                checked=nousolek and nousolek.on_intervjueerija)}
                </div>
                % endif
                
              </td>
              <td>
                <% maaramised = toimumisaeg.get_labiviijad(c.kasutaja.id) %>
                % if len(maaramised):
                  % for s in maaramised:
                     <%
                        testiruum = s.testiruum
                        testikoht = testiruum and testiruum.testikoht
                        ruum = testiruum and testiruum.ruum
                     %>
                     % if testikoht:
                     <div>
                       ${testikoht.koht.nimi}
                       ${ruum and ruum.tahis or ''}
                     </div>
                     % endif
                     ${s.kasutajagrupp.nimi}
                  % endfor
                % else:
                     ${_("Ei ole määratud")}
                % endif
              </td>
              <td>
                % if nousolek and c.user.has_permission('kasutajad', const.BT_UPDATE):
                ${h.remove(h.url('admin_kasutaja_delete_nousolek',
                kasutaja_id=c.kasutaja.id, id=nousolek.id))}
                % endif
              </td>
            </tr>
            % endfor
          </tbody>
        </table>
