% if c.items:
<div class="d-flex">
  <div>
    <div id="dgmj"></div>
    <script>
      $('#dgmj').width($('.modal-body').width() - 190);
      Plotly.newPlot(document.getElementById("dgmj"), ${c.json_data});
    </script>
  </div>
  <div width="180px">
      <table width="100%" class="table table-borderless table-striped" border="0" >
        <thead>
          <tr>
            ${h.th(_("Tulemus"))}
            ${h.th(_("Arv"))}
            ${h.th(u'%')}
          </tr>
        </thead>
        <tbody>
          % for n, rcd in enumerate(c.items):
          <%
             range_title, cnt, prot = rcd
          %>
          <tr>
            <td>${range_title}</td>
            <td>${cnt}</td>
            <td>
              ${h.fstr(prot, 1)}%
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
  </div>
</div>
% endif
