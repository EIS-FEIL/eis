% if c.json_data:
    <div id="dgmk"></div>
    <script>
      $('#dgmk').width($('.modal-body').width() - 20);
      Plotly.newPlot(document.getElementById("dgmk"), ${c.json_data});
    </script>
% endif
