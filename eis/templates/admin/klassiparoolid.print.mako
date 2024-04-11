<div style="padding:50px">
${c.user.koht.nimi}, ${_("{s1}{s2} klass").format(s1=c.klass, s2=c.paralleel)}

<table border="1" cellpadding="8"  style="border-collapse:collapse">
  <tr>
    <th>${_("Isikukood")}</th>
    <th>${_("Eesnimi")}</th>
    <th>${_("Perekonnanimi")}</th>
    <th>${_("Parool")}</th>
  </tr>
  % for opilane in c.items:
  <% r = c.data.get(opilane.id) %>
  % if r and r[0]:
  <%
    pwd = r[0]
  %>
  <tr>
    <td>${opilane.isikukood}</td>
    <td>${opilane.eesnimi}</td>
    <td>${opilane.perenimi}</td>
    <td>${pwd}</td>
  </tr>
  % endif
  % endfor
</table>
<p>
  ${_("Genereeritud {n} parooli").format(n=c.npwd)}
</p>
</div>
