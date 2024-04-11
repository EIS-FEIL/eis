% if c.no_cookies:
## tekst akna allääres, kui pole veel nõusolekut antud
<div class="cookie-compliance" id="cookiemsg" style="display:none">
  <div class="container">
    <p>
      Harno teenused lisavad su arvutisse väikesed failid, mida nimetatakse küpsisteks, mis koguvad infot sinu haridusveebide kasutuse kohta ja aitavad tõsta kasutusmugavust.
    </p>
    <div class="m2 text-right">
      <button type="button" class="btn btn-primary" id="btn_edit_cookies">${_("Küpsiste sätted")}</button>
      <button type="button" class="btn btn-primary btn-accept-cookies">${_("Nõustun küpsistega")}</button>      
    </div>
  </div>
  <div style="display:none">
    ${self.dlg_contents()}
  </div>
</div>
% else:
## kui nõusolek on antud, siis soovitakse vaadata küpsiste seadeid dialoogis
${self.dlg_contents()}
% endif

<%def name="dlg_contents()">
    <div id="cc_content">
      <p>
        Kasutame küpsiseid info kogumise eesmärgil, et tagada mugavam ja sõbralikum kasutajakogemus ning sisu.
      </p>
      <div class="accordion" id="acc_cconsent">
        <div class="accordion-card card parent-accordion-card">
          <div class="card-header" id="heading_consent_required">
            <div class="accordion-title">
              <button class="btn btn-link collapsed" type="button"
                      data-toggle="collapse"
                      data-target="#collapse_consent_required"
                      aria-controls="collapse_consent_required"
                      aria-expanded="true">
                <span class="btn-label"><i class="mdi mdi-chevron-down"></i>
                  Vajalikud küpsised
                </span>
              </button>
            </div>
          </div>
          <div id="collapse_consent_required" class="collapse" aria-labelledby="heading_consent_required">
            <div class="card-body">
              <div class="content">
                <p>
                  Hädavajalikud küpsised tagavad teenuse õigesti töötamise. Siia kuuluvad näiteks sessiooniküpsised ning küpsiste kasutamise nõusoleku küpsis.
                  Kogu info Harnos kasutatavatest küpsistest asub <a href="https://cookie.edu.ee" target="_blank" rel="noopener">https://cookie.edu.ee</a>.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="accordion-card card">
          <div class="card-header" id="heading_consent_various">
            <div class="accordion-title">
              <button class="btn btn-link collapsed" type="button"
                      data-toggle="collapse"
                      data-target="#collapse_consent_various"
                      aria-controls="collapse_consent_various"
                      aria-expanded="false">
                <span class="btn-label"><i class="mdi mdi-chevron-down"></i>                
                  Valikulised küpsised
                </span>
              </button>
            </div>
          </div>
          <div id="collapse_consent_various" class="collapse" aria-labelledby="heading_consent_various">
            <div class="card-body">
              <div class="d-flex flex-wrap">
                ##<div class="custom-control custom-switch custom-control-inline" id="cconoffl">
                ##  <input type="checkbox" class="custom-control-input" id="cconoff" />
                ##  <label class="custom-control-label" for="customSwitch1">
                ##    <span class="sr-only">switch element</span>
                ##  </label>
                ##</div>
                
                <p>
                  Harno teenused lisavad su arvutisse väikesed failid, mida nimetatakse küpsisteks, mis koguvad infot sinu haridusveebide kasutuse kohta ja aitavad tõsta kasutusmugavust. Loe lähemalt, milliseid küpsiseid me kasutame, milleks nad on mõeldud ning millal nad aeguvad. Kogu info Harnos kasutatavatest küpsistest asub <a href="https://cookie.edu.ee" target="_blank" rel="noopener">https://cookie.edu.ee</a>.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      % if not c.no_cookies:
      <div class="my-2">
        % if c.no_cookies_various:
        Praegu on lubatud ainult vajalikud küpsised.
        % else:
        Praegu on lubatud nii vajalikud kui ka valikulised küpsised.
        % endif
      </div>
      % endif

      <div class="m-2 text-right">
        % if not c.no_cookies:
        <button type="button" class="btn btn-primary btn-rm-cookies">${_("Tühistan küpsiste nõusoleku")}</button>
        % else:
        <button type="button" class="btn btn-primary btn-accept-cookies cconsent-0">${_("Nõustun vajalike küpsistega")}</button>
        % endif
        % if c.no_cookies_various:        
        <button type="button" class="btn btn-primary btn-accept-cookies">${_("Nõustun kõigi küpsistega")}</button>
        % endif
      </div>
<script>
     $('.btn-accept-cookies').click(function(){
        set_spinner($(this));
        $.getJSON("${h.url("cookieconsent")}",
             {various: ($(this).hasClass('cconsent-0') ? 0 : 1)},
             function(data){
               if(data.rc == 'ok'){
                  $('#cookiemsg').remove(); close_dialog("cconsentdlg");
               }
             });
        return false;
     });
     $('.btn-rm-cookies').click(function(){
        var form = $('<form method="POST" style="display:none"></form>')
              .attr({ action: "${h.url("deletecookieconsent")}" });
        $(document.body).append(form);
        form.submit();
        return false;
     });
     $('#btn_edit_cookies').click(function(){
        open_dialog({dialog_id: 'cconsentdlg',
                     contents_html: $('#cc_content').html(),
                     title: 'Küpsiste sätted'});        
        return false;
     });
     $('#cookiemsg').show();
</script>
    </div>
</%def>
