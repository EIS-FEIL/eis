<%
   koht_maaratud = len([tos.testiruum_id for tos in c.sooritaja.sooritused if tos.testiruum_id])
   opt_kursused = c.sooritaja.test.opt_kursused
   testimiskord = c.sooritaja.testimiskord
%>
${h.form_save(c.sooritaja.id, h.url('regamine_avaldus_update_test',
id=c.kasutaja.id, sooritaja_id=c.sooritaja.id))}
<table  class="table table-borderless table-striped" width="100%">
  <col width="160"/>
  <tbody>
    <tr>
      <td class="fh">${_("Keel")}</td>
      <td>
        % if len(testimiskord.opt_keeled) > 1 and not koht_maaratud:
        ${h.select('lang', c.sooritaja.lang, testimiskord.opt_keeled)}
        % else:
        ${c.sooritaja.lang_nimi}
        % endif
      </td>
    </tr>
    % if opt_kursused:
    <tr>
      <td class="fh">${_("Kursus")}</td>
      <td>
        ${h.select('kursus', c.sooritaja.kursus_kood, opt_kursused, wide=False)}
      </td>
    </tr>
    % endif
    <tr>
      <td class="fh">${_("Soovitud piirkond")}</td>
      <td>
        % if not koht_maaratud:
            <%
               c.piirkond_id = c.sooritaja.piirkond_id
               c.piirkond_field = 'piirkond_id'
               c.piirkond_filtered = testimiskord.get_piirkonnad_id()
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
        % else:
            ${c.sooritaja.piirkond_nimi}
        % endif
      </td>
    </tr>
    % if c.sooritaja.test.on_tseis:
    <tr>
      <td class="fh">${_("Soovib konsultatsiooni")}</td>
      <td>${h.checkbox('soovib_konsultatsiooni', 1, checked=c.sooritaja.soovib_konsultatsiooni)}</td>
    </tr>
    % endif
    <tr>
      <td class="fh">${_("Sooritaja märkused")}</td>
      <td>${h.textarea('reg_markus', c.sooritaja.reg_markus)}</td>
    </tr>
    <tr>
      <td class="fh">${_("Etteantud toimumispäev")}</td>
      <td>
        <table>
          % for tos in c.sooritaja.sooritused:
          <% ta = tos.toimumisaeg %>
          <tr>
            <td>${ta.tahised}</td>
            <td>
                <%
                  opt_tp = ta.get_toimumispaevad_opt()
                %>
                % if opt_tp:
                ${h.select('toimumispaev_id_%s' % ta.id, tos.reg_toimumispaev_id, opt_tp, empty=True)}
                % else:
                <i>${_("Toimumispäevi pole veel määratud")}</i>
                % endif
            </td>
          </tr>
          % endfor
        </table>
      </td>
    </tr>
  </tbody>
</table>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to_dlg(_("Määra tugiisik"), h.url('regamine_avaldus_tugiisikud', kasutaja_id=c.kasutaja.id, sooritaja_id=c.sooritaja.id), level=2, title=_("Määra tugiisik"), size='md')}    
  </div>
  <div>
    ${h.submit_dlg()}
  </div>
</div>

${h.end_form()}

