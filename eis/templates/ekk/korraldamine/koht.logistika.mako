<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Soorituskohtade planeerimine"), h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(c.testikoht.koht.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'soorituskohad' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="koht.tabs.mako"/>
</%def>

<table width="100%"  class="search2">
  <tr>
    <td class="frh">${_("Testisooritajate arv kokku")}</td>
    <td><span class="brown">${c.testikoht.get_sooritajatearv()}</span></td>
  </tr>
  % for lang in c.toimumisaeg.testimiskord.get_keeled():
     <%
        toodearv = 0
        valjastusymbrikearv = 0
        pakett = c.testikoht.get_testipakett(lang)
        if pakett:
           toodearv = pakett.toodearv or 0
           valjastusymbrikearv = pakett.valjastusymbrikearv or 0
     %>
  <tr>
    <td class="frh">${model.Klrida.get_lang_nimi(lang)}</td>
    <td><span class="brown">${c.testikoht.get_sooritajatearv(lang)}</span>
      (${_("sooritajate arv")}
      <span class="brown">${toodearv}</span>,
      ${_("väljastusümbrike arv")} 
      <span class="brown">${valjastusymbrikearv}</span>)
    </td>
  </tr>
  % endfor
</table>
<br/>

<table width="100%"  class="table table-borderless table-striped tablesorter">
  <caption>
    ${_("Testitööde väljastamise ümbrikud")}
  </caption>
  <thead>
    <tr>
      ${h.th(_("Keel"))}
      ${h.th(_("Kursus"))}
      ${h.th(_("Testiruum"))}
      ${h.th(_("Ruum"))}
      ${h.th(_("Ümbriku liik"))}
      ${h.th(_("Tööde arv"))}
      ${h.th(_("Ümbrike arv"))}
    </tr>
  </thead>
  <tbody>
    % for tr in c.testikoht.testiruumid:
        % for ymb in tr.valjastusymbrikud:
    <tr>
      <td>${model.Klrida.get_lang_nimi(ymb.testipakett.lang)}</td>
      <td>${ymb.kursus_nimi}</td>
      <td>${tr.tahis}</td>
      <td>${tr.ruum and tr.ruum.tahis or _("määramata")}</td>
      <td>${ymb.valjastusymbrikuliik.tahis}. ${ymb.valjastusymbrikuliik.nimi}</td>
      <td>${ymb.toodearv}</td>
      <td>${ymb.ymbrikearv}</td>
    </tr>
        % endfor
    % endfor
  </tbody>
</table>
<br/>

<table width="100%"  class="table table-borderless table-striped tablesorter">
  <caption>
    ${_("Testitööde tagastamise ümbrikud")}
  </caption>
  <thead>
    <tr>
      ${h.th(_("Keel"))}
      ${h.th(_("Kursus"))}
      ${h.th(_("Testiruum"))}
      ${h.th(_("Ruum"))}
      ${h.th(_("Ümbriku tähis"))}
      ${h.th(_("Protokollirühm"))}
      ${h.th(_("Ümbriku liik"))}
      ${h.th(_("Sooritajate arv"))}
      ${h.th(_("Ümbrike arv"))}
      ${h.th(_("Olek"))}
    </tr>
  </thead>
  <tbody>
    ## esmalt peaümbrikud
    % for tp in c.testikoht.testipaketid:
      % for ymb in tp.tagastusymbrikud:
        % if ymb.tagastusymbrikuliik_id == None:
    <tr>
      <td>${model.Klrida.get_lang_nimi(tp.lang)}</td>
      <td></td>
      <td></td>
      <td></td>
      <td>${ymb.tahised}</td>
      <td></td>
      <td>Peaümbrik</td>
      <td></td>
      <td>${ymb.ymbrikearv}</td>
      <td>${ymb.staatus_nimi}</td>
    </tr>
        % endif
      % endfor
    % endfor

    % for tr in c.testikoht.testiruumid:
      % for tpr in tr.testiprotokollid:
        % for ymb in tpr.tagastusymbrikud:
    <tr>
      <td>${model.Klrida.get_lang_nimi(tpr.testipakett.lang)}</td>
      <td>${tpr.kursus_nimi}</td>
      <td>${tr.tahis}</td>
      <td>${tr.ruum and tr.ruum.tahis or _("määramata")}</td>
      <td>${ymb.tahised}</td>
      <td>${tpr.tahis}</td>
      <td>${ymb.tagastusymbrikuliik.tahis}. ${ymb.tagastusymbrikuliik.nimi}</td>
      <td>${tpr.toodearv}</td>
      <td>${ymb.ymbrikearv}</td>
      <td>${ymb.staatus_nimi}</td>
    </tr>
        % endfor
      % endfor
    % endfor
  </tbody>
</table>
<br/>

<table width="100%"  class="table table-borderless table-striped tablesorter">
    <%
       arv = 0
       for pakett in c.testikoht.testipaketid:
          arv += pakett.valjastuskottidearv or 0
    %>
  <caption>
    ${_("Testitööde väljastamise turvakotid ({n} tk)").format(n=arv)}
  </caption>
  <thead>
    <tr>
      ${h.th(_("Koti number"))}
      ${h.th(_("Keel"))}
      ${h.th(_("Olek"))}
    </tr>
  </thead>
  <tbody>
       % for pakett in c.testikoht.testipaketid:
          % for kott in pakett.valjastuskotid:
    <tr>
      <td>${kott.kotinr}</td>
      <td>${model.Klrida.get_lang_nimi(pakett.lang)}</td>
      <td>${kott.staatus_nimi}</td>
    </tr>
          % endfor
       % endfor
  </tbody>
</table>
<br/>


<table width="100%"  class="table table-borderless table-striped tablesorter">
    <%
       arv = 0
       for pakett in c.testikoht.testipaketid:
          arv += pakett.tagastuskottidearv or 0
    %>
  <caption>
    ${_("Testitööde tagastamise turvakotid ({n} tk)").format(n=arv)}
  </caption>
  <thead>
    <tr>
      ${h.th(_("Koti number"))}
      ${h.th(_("Keel"))}
      ${h.th(_("Olek"))}
    </tr>
  </thead>
  <tbody>
       % for pakett in c.testikoht.testipaketid:
          % for kott in pakett.tagastuskotid:
    <tr>
      <td>${kott.kotinr}</td>
      <td>${model.Klrida.get_lang_nimi(pakett.lang)}</td>
      <td>${kott.staatus_nimi}</td>
    </tr>
          % endfor
       % endfor
  </tbody>
</table>
<br/>

