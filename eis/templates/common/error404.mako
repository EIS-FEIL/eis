<%inherit file="/common/page.mako"/>
<%def name="page_main()">
<main class="page-content page-404">
    <div class="container">
      <span id="maincontent"></span>
      <div class="d-flex d-sm-inline flex-column">
        <div>
          <h1 class="display-1 bg-white-085">
            ${_("Vot see oli üks vinge leht, aga ma sõin selle ära")}
          </h1>
          <div class="alt-text">viga 404</div>
        </div>
        <div class="button-wrapper">
          <button id="btnback" type="button" class="btn btn-sm-down-block btn-primary">
            ${_("Tagasi")}
          </button>
          <a href="${h.url('avaleht')}" class="btn btn-sm-down-block btn-primary">
            Avalehele
          </a>
        </div>
      </div>
    </div>
    <div class="clipped-footer"></div>
    <script>
      $('#btnback').click(function(){ window.history.back();});
    </script>
</main>
</%def>
