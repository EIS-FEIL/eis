
<%inherit file="komplektid.mako"/>
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Ülesanded"))}
${h.crumb(_("Eritingimused"))}
</%def>
&nbsp;
${h.form_save(c.komplekt.id)}

<table width="100%" border="0"  class="table table-borderless table-striped tablesorter">
  <caption>${_("Eritingimustega testisooritajate ülesandekomplekti lisatingimused")}</caption>
  <tr>
    ${h.th(_("Alatest"))}
    ${h.th(_("Lahendamise piiraeg"))}
    ${h.th(_("Lisaaeg"))}
    ${h.th(_("Diferentseeritud hindamine"))}
  </tr>
  % if c.testiosa.on_alatestid:
    % for cnt, alatest in enumerate(c.komplekt.komplektivalik.alatestid):
    ${self.row_erialatest(c.testiosa, c.komplekt, alatest, cnt)}
    % endfor
  % else:
    ## ei ole alateste
    ${self.row_erialatest(c.testiosa, c.komplekt, None, 0)}
  % endif
</table>

<table width="100%">
  <tr>
    <td nowrap class="fh">
      ${_("Testiosa lahendamise piiraeg")}: ${h.str_from_time(c.testiosa.piiraeg) or '-'} ${_("minutit")}
      &nbsp; &nbsp; &nbsp; &nbsp;
      ${_("Lisaaeg")}: ${h.str_from_time(c.komplekt.lisaaeg) or '-'} ${_("minutit")}
    </td>
    <td align="right">
    % if c.can_update:
      % if c.is_edit:
      ${h.submit()}
      % else:
      ${h.btn_to(_("Muuda"), h.url('test_edit_erialatest', test_id=c.test.id, id=c.komplekt.id))}
      % endif
    % endif
    </td>
  </tr>
  <tr>
    <td nowrap class="fh">
      ${_("Diferentseeritud hindamine")}
      ${h.sbool(c.komplekt.dif_hindamine)}
    </td>
  </tr>
</table>

${h.end_form()}

&nbsp;

<table class="table table-borderless table-striped tablesorter">
  <caption>${_("Testi ülesandekomplekt on järgmiste eritingimustega testisooritajate jaoks")}:</caption>
  <tr>
    ${h.th('')}
    ${h.th(_("Testisooritaja"))}
    ${h.th(_("Soorituskoht"))}
    ${h.th(_("Testsessioon"))}
    ${h.th(_("Eritingimused"))}
  </tr>
  % for rcd in c.komplekt.erikomplektid:
  <tr>
    <% 
       sooritus = rcd.sooritus
       sooritaja = sooritus.sooritaja 
    %>
    <td>
    % if c.can_update:
      ${h.remove(h.url('test_komplekt_delete_erisooritus', test_id=c.test.id,
      komplekt_id=c.komplekt.id, id=rcd.id))}
    % endif
    </td>
    <td>
      ${sooritaja.kasutaja.isikukood}
      ${sooritaja.kasutaja.nimi}
    </td>
    <td>
      ${sooritus.testikoht and sooritus.testikoht.koht.nimi or ''}
    </td>
    <td>
      ${sooritaja.testimiskord.testsessioon and sooritaja.testimiskord.testsessioon.nimi or ''}
    </td>
    <td>
      <%
         vajadused = []
         for p in sooritus.erivajadused:
             buf = p.erivajadus_nimi or ''
             if p.kinnitus_markus:
                buf += ' (%s)' % p.kinnitus_markus
             vajadused.append(buf)
         str_vajadused = ', '.join(vajadused) or '-'
      %>
      ##${h.link_to(str_vajadused, h.url('test_erivajadus',id=sooritus.id))}
      ${h.link_to(str_vajadused,
         h.url('test_komplekt_erivajadus',test_id=c.test.id,
         komplekt_id=c.komplekt.id, id=sooritus.id))}
    </td>
  </tr>
  % endfor
</table>
<br/>

% if c.can_update:
${h.btn_to_dlg(_("Lisa testisooritaja"), h.url('test_komplekt_erisooritused',
test_id=c.test.id, komplekt_id=c.komplekt_id, partial=True), 
dlgtitle=_("Testile registreeritud eritingimustega sooritajad"),
size='lg')}
% endif

<%def name="row_erialatest(testiosa, komplekt, alatest, cnt)">
  <% 
     if alatest:
        item = komplekt.give_erialatest(alatest.id) 
     else:
        item = komplekt
  %>
  <tr>
    % if alatest:
    <td>${alatest.nimi}</td>
    <td>${h.str_from_time(alatest.piiraeg)}</td>
    % else:
    <td></td>
    <td>${h.str_from_time(testiosa.piiraeg)}</td>
    % endif
    <td>
      ${h.timedelta_min('ek-%s.lisaaeg' % cnt, item.lisaaeg)}
    </td>
    <td>
      ${h.checkbox('ek-%s.dif_hindamine' % cnt, checked=item.dif_hindamine)}
      ${h.hidden('ek-%s.alatest_id' % cnt, alatest and alatest.id or 0)}
    </td>
  </tr>
</%def>
