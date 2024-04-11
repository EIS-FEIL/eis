<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'lisavalikud' %>
<%include file="nimistu.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))} 
${h.crumb(_("Registreerimise taotluse sisestamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

## peale faili yleslaadimist
${h.form_save(None, h.url('regamine_nimistu_create_lisavalikud', korrad_id=c.korrad_id, protsess_id=c.protsess_id))}
${h.hidden('testiliik', c.testiliik)}

<%
   dkursused = dict()
%>
<table  class="table">
  <thead>
    <tr>
      <th>${_("Isikukood")}</th>
      <th>${_("Nimi")}</th>
      % for n_kord, kord in enumerate(c.korrad):
      <th>
        ${kord.tahised}
% if not c.tyhistatud:
        % if len(kord.get_keeled()) > 1:
        ${h.select('lang',c.lang, kord.opt_keeled, wide=False, 
           onchange="$('select[name$=\"tk-%d.lang\"]').val($(this).val())" % n_kord)}
        % endif

        <% dkursused[kord.id] = test_opt_kursused = kord.test.opt_kursused %>
        % if len(test_opt_kursused) > 1:
        ${h.select('kursus', c.kursus, test_opt_kursused, wide=False,
           onchange="$('select[name$=\"tk-%d.kursus\"]').val($(this).val())" % n_kord)}
        % endif        
% endif
      </th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n,row in enumerate(c.rows):
    <% 
       prefix = 'k-%d' % n 
       k, sooritajad = row
    %>
    <tr>
      <td>${k.isikukood}</td>
      <td>
        ${k.nimi}
        ${h.hidden('%s.id' % prefix, k.id)}
      </td>

      % for n_kord, sooritaja in enumerate(sooritajad):
      <td>
      % if sooritaja and c.tyhistatud:
        ${sooritaja.staatus_nimi}
      % elif sooritaja:
        <% 
           k_prefix = '%s.tk-%d' % (prefix, n_kord) 
           kord = sooritaja.testimiskord
        %>
        ${h.hidden('%s.tk_id' % (k_prefix), kord.id)}
        ${h.checkbox('%s.s_id' % (k_prefix), sooritaja.id, checked=True)}

        % if len(kord.opt_keeled) > 1 or sooritaja.lang not in kord.get_keeled():
        ${h.select('%s.lang' % (k_prefix), sooritaja.lang, kord.opt_keeled, wide=False)}
        % else:
        ${sooritaja.lang_nimi}
        % endif

        % if len(dkursused[kord.id]) > 1:
        ${h.select('%s.kursus' % (k_prefix), sooritaja.kursus_kood, dkursused[kord.id], wide=False)}
        % else:
        ${sooritaja.kursus_nimi}
        % endif
        
        % if sooritaja.staatus > const.S_STAATUS_REGAMATA:
        <span style="color:red">${_("On juba registreeritud")}</span>
        % endif

        ## tugiisikud
        <%
          sooritused = list(sooritaja.sooritused)
          mitu = len(sooritused) > 1
          tugikud = []
          for tos in sooritused:
             tugik = tos.tugiisik_kasutaja
             if tugik:
                buf = tugik.nimi
                if mitu:
                    buf += ' (%s)' % tos.testiosa.nimi
                tugikud.append(buf)
        %>
        % if tugikud:
        ${_("Tugiisik")}:
        % for buf in tugikud:
        <div>${buf}</div>
        % endfor
        % endif

      % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>

% if not c.tyhistatud:
${h.checkbox('teated', 1, checked=True, label=_("Saata registreerimise teated"))}

<div class="mt-2 d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('regamine_nimistu_edit_sooritajad', korrad_id=c.korrad_id, testiliik=c.testiliik, lang=c.lang),
    level=2, mdicls='mdi-arrow-left-circle')}
  </div>
  <div>
    ${h.submit(_("Salvesta"))}
  </div>
</div>
% endif
${h.end_form()}

% if not c.tyhistatud:
<script>
## et kasutaja saaks lahkumisel hoiatuse
  dirty = true;
</script>
% endif
