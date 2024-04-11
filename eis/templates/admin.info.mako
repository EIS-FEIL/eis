<div>Ver ${c.version}</div>

<%
  data = c.test_data
  kasutaja = c.user.get_kasutaja()
%>
% if kasutaja:
<div class="row">
  <div class="col-md-8">
    ${self.show_load()}
  </div>
  <div class="col-md-4">
    ${self.show_conn()}
    <p>
      ${h.form(h.url('dbgtest'))}
      ${h.checkbox('is_debug', 1, checked=c.is_debug, label=_("Debug info"), onchange="this.form.submit()", ronly=False)}
      ${h.end_form()}
    </p>
  </div>
</div>  
${self.show_proc()}
${self.show_env(data)}
% endif

<%def name="show_load()">
<table class="table table-borderless table-striped my-2" border="0" >
  <caption>${_("Kasutajate arv süsteemis")}</caption>
  <col width="50%"/>
  % for n in (2,5,10):
  <tr>
    <td class="frh">${_("Kasutajaseansside arv viimase {n} minuti jooksul").format(n=n)}</td>
    <td>
      ${_("autentinud {n2}, autentimata {n3}").format(n2=c.user.get_user_count(n, True), n3=c.user.get_user_count(n, False))}
      (${c.user.get_user_count(n)})
    </td>
  </tr>
  % endfor
  <%
    today = h.date.today()
    yesterday = today - h.timedelta(days=1)
  %>
  <tr>
    <td class="frh">${_("Erinevate autenditud kasutajate arv täna")}</td>
    <td>${c.user.get_distinct_user_count(today)}</td>
  </tr>
  <tr>
    <td class="frh">${_("Erinevate autenditud kasutajate arv eile")}</td>
    <td>${c.user.get_distinct_user_count(yesterday, today)}</td>
  </tr>
  <% cnt, duration = c.user.get_testtaker_count(1) %>
  <tr><td class="frh">${_("Pooleli testisoorituste arv")}</td><td>${cnt}</td></tr>
  % if duration:
  <tr><td class="frh">${_("Keskmine pöördumise kestus testi sooritamisel")}</td><td>${h.fstr(duration)} s</td>
    % endif
  <% duration = c.user.get_testtaker_count(3) %>
  <tr><td class="frh">${_("Keskmine pöördumise kestus")}</td><td>${h.fstr(duration)} s</td>        

  <tr>
    <td class="frh">
      ${c.hostname}
      ${request.environ.get('HOSTNAME')}
    </td>
    <td>
      ${request.environ.get('SERVER_ADDR')}
    </td>
  </tr>
</table>
</%def>

<%def name="show_conn()">
<table class="table table-borderless table-striped my-2" border="0" >
  <caption>${_("Andmebaasiühendused")}</caption>
  <col width="50%"/>
  % for dbuser, values in c.list_dbconn:
  <tr>
    <td class="frh">${dbuser}</td>
    <td>
      % for value in values:
      <div>${value}</div>
      % endfor
    </td>
  </tr>
  % endfor
</table>
</%def> 

<%def name="show_proc()">
% if not c.protsessid:
${h.alert_notice('Pooleli arvutusprotsesse ei ole', False)}
% else:
<table class="table table-borderless table-striped" border="0" >
  <caption>Pooleli arvutusprotsessid</caption>
  <thead>
    <tr>
      <th>Server</th>
      <th>PID</th>
      <th>Edenemisprotsent</th>
      <th>Algus</th>
      <th>Muudetud</th>
      <th>Kirjeldus</th>
      <th>Viga</th>
      <th>Kasutaja</th>
    </tr>
  </thead>
  <tbody>
    % for r in c.protsessid:
    <% k = model.Kasutaja.get_by_ik(r.creator) %>
    <tr>
      <td>${r.hostname}</td>
      <td>${r.pid}</td>
      <td>${r.edenemisprotsent}%</td>
      <td>${h.str_from_datetime(r.algus)}</td>
      <td>${h.str_from_datetime(r.modified)}</td>
      <td>${r.kirjeldus}
        % if r.test_id:
        (test ${r.test_id})
        % endif
      </td>
      <td>${r.viga}</td>
      <td>${k and k.nimi or r.creator}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
</%def>

<%def name="show_env(data)">
<table class="table table-borderless table-striped" border="0" >
  <caption>${_("Keskkonnamuutujad")}</caption>
  <% 
    keys = list(data.keys())
    keys.sort() 
    %>
  % for key in keys:
  <tr>
    <td class="text-nowrap">${key}</td>
    <td>${data[key]}</td>
  </tr>
  % endfor
</table>
<table class="table table-borderless table-striped" border="0" >
  <caption>${_("HTTP päised")}</caption>
  % for key, value in request.headers.items():
  <tr>
    <td class="text-nowrap">${key}</td>
    <td>${value}</td>
  </tr>
  % endfor
</table>
URL: ${request.url}
</%def>

<%def name="show_perm(kasutaja)">
<table class="list tablesorter" border="0" >
  <caption>${_("Kasutajale antud õigused")}</caption>
  <thead>
    <tr>
      <th>${_("Grupp")}</th>
      <th>${_("Max koormus")}</th>
      <th>${_("Alates")}</th>
      <th>${_("Kuni")}</th>
      <th>${_("Õigus")}</th>
      <th>${_("Asukoht")}</th>
      <th>${_("Piirkond")}</th>
      <th>${_("Õppeaine")}</th>
      <th>${_("Oskus")}</th>
      <th>${_("Testiliik")}</th>
    </tr>
  </thead>
  <tbody>
    
    % for rcd in kasutaja.kasutajarollid:
    % for o in rcd.kasutajagrupp.kasutajagrupp_oigused:
    <tr>
      <td>${rcd.kasutajagrupp.nimi}</td>
      <td>${rcd.kasutajagrupp.max_koormus}</td>
      <td>${h.str_from_date(rcd.kehtib_alates)}</td>
      <td>${h.str_from_date(rcd.kehtib_kuni)}</td>
      <td>${o.nimi} ${o.bitimask}</td>
      <td>${rcd.koht_id}</td>
      <td>${rcd.piirkond_id}</td>
      <td>${rcd.aine_kood}</td>
      <td>${rcd.oskus_kood}</td>
      <td>${rcd.testiliik_kood}</td>
    </tr>
    % endfor
    % endfor
  </tbody>
</table>
<br/>
</%def>
