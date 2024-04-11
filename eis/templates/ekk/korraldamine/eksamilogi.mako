<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Eksamilogi"),h.url_current())}
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'muu' %>
<%include file="tabs.mako"/>
</%def>

<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="draw_subtabs()">
<%include file="muu.subtabs.mako"/>
</%def>

${h.form_search(None)}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">
        <div>${h.checkbox1('kok', 1, checked=c.kok or not c.mrk and not c.ktk, label=_("Kõik protokollitud soorituskohad"))}</div>
        <div>${h.checkbox1('mrk', 1, checked=c.mrk, label=_("Märkustega soorituskohad"))}</div>
        <div>${h.checkbox1('ktk', 1, checked=c.ktk, label=_("Katkestanute või eemaldatutega soorituskohad"))}</div>
        <script>
          $('#kok').click(function(){ if(this.checked) $('#mrk,#ktk').prop('checked', false); });
          $('#mrk,#ktk').click(function(){ if(this.checked) $('#kok').prop('checked', false); });        
        </script>
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
      ${h.btn_search()}
      ${h.submit(_("Väljasta Excel"), id="xls", level=2, class_="filter")}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.toimumisaeg.alates:
<i>${_("Kuupäev")}: ${c.toimumisaeg.millal}</i>
% endif

<% prev_prk = '-' %>
% for r in c.items:
  <%
    prk_nimi, k_nimi, testikoht_id, testiruum_id, tpr_id, lang, tpr_markus = r
    esimees = c.get_esimees(testikoht_id, testiruum_id)
    katkestajad = c.get_sooritused(testikoht_id, testiruum_id, lang)
    ruumifailid = list(model.Session.query(model.Ruumifail)
                   .filter_by(toimumisprotokoll_id=tpr_id)
                   .order_by(model.Ruumifail.id).all())
  %>
  % if prk_nimi != prev_prk:
  <% prev_prk = prk_nimi %>
  <h3 class="mt-4">${prk_nimi or _("Piirkonnata soorituskohad")}</h3>
  % endif

  <div class="mb-2">
    <div>
    <b>
    ${h.link_to(k_nimi, h.url('sisestamine_protokoll_osalejad', toimumisprotokoll_id=tpr_id))}
    ${esimees}
    </b>
    </div>
    % if len(katkestajad):
    <div class="pl-2 pt-1">
      ${self.katkestajad(katkestajad)}
    </div>
    % endif
    % if tpr_markus:
    <div class="pl-2">
      <b>${_("Eksamiprotokolli märkused:")}</b>
      <div>${tpr_markus.replace('\n', '<br/>')}</div>
    </div>
    % endif
    % if ruumifailid:
    <div class="pl-2">
      <b>${_("Ruumide failid")}</b>
      <div>
        % for rf in ruumifailid:
        <div class="px-2 d-inline-block rounded border">
        ${h.link_to(rf.filename, h.url_current('downloadfile', id=0, file_id=rf.id, format=rf.fileext))}
        ${h.filesize(rf.filesize)}
        <%
          tr = rf.testiruum
          ruum = tr.ruum
        %>
        ${_("ruum")} ${tr.tahis} (${ruum and ruum.tahis or _("määramata")})
        </div>
        % endfor
      </div>
    </div>
    % endif
  </div>
% endfor

<%def name="katkestajad(katkestajad)">
    <table class="table">
      <thead>
        <tr>
          <th>${_("Eksaminand")}</th>
          <th>${_("Isikukood")}</th>
          <th>${_("Olek")}</th>
          <th>${_("Põhjendus / märkus")}</th>
        </tr>
      </thead>
      <tbody>
        % for n_tos, r1 in enumerate(katkestajad):
        <% eesnimi, perenimi, isikukood, staatus, markus, stpohjus = r1 %>
        <tr>
          <td>${eesnimi} ${perenimi}</td>
          <td>${isikukood}</td>
          <td>${c.opt.S_STAATUS.get(staatus)}</td>
          <td>
            % if stpohjus:
            <div>${stpohjus}</div>
            % endif
            % if markus:
            ${markus.replace('\n', '<br/>')}
            % endif
          </td>
        </tr>
        % endfor
      </tbody>
    </table>
</%def>
