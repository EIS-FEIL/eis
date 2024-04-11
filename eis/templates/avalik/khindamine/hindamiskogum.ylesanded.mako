## -*- coding: utf-8 -*- 
<%
  testimiskord = c.toimumisaeg.testimiskord
  test = testimiskord.test
  lang = c.hindaja.lang
%>
<h2>${_("Ülesanded")}</h2>
<table class="table table-borderless table-striped tablesorter">
  <tr>
    ${h.th(_("Jrk"))}
    ${h.th(_("Ülesanne"))}
    ${h.th(_("Ülesandekomplekt"))}
  </tr>
  % for rcd in c.items_ylesanded:
  <%
     alatest_seq, ty_seq, vy = rcd
     ty = vy.testiylesanne
     ylesanne = vy.ylesanne
     tabs_data = c.f_r_tabs_data(vy, ylesanne, True)
     url_yl = tabs_data[0][1]
  %>
  <tr>
    <td>
      ${ty.tahis}
    </td>
    <td>
      <%
        ty_nimi = ty.tran(c.lang).nimi
        if ty.tahis != ty_nimi:
            nimi = f' {ty.tahis} {ty_nimi}'
        else:
            nimi = ty_nimi
      %>
      ${h.link_to_dlg(nimi, url_yl, title=nimi, size='lg')}
      % if ylesanne and ylesanne.hindamisjuhist_muudetud():
      ${h.mdi_icon('mdi-flag', title=_("Ülesande hindamisjuhendit on hiljuti muudetud!"))}
      % endif
    </td>
    <td>
      ${vy.komplekt.tahis}
    </td>
  </tr>
  % endfor
</table>

