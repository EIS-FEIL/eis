## Pangalingi poole suunav plokk
## kui on olemas c.sooritaja, siis minnakse yhe registreeringu eest maksma,
## muidu peab olema seatud c.tasumata, mis sisaldab kõigi tasumata
## registreeringute tasude summat
<% tasu = h.mstr(c.sooritaja and c.sooritaja.tasu or c.tasumata) %>
<h2>${_("Sul on riigilõiv {sum}").format(sum=tasu)}</h2>
<p>
  ${_("Registreerimise lõpuni viimiseks pead tasuma veel riigilõivu {sum}. Maksmiseks võid kasutada allolevat pangalinki.").format(sum=tasu)}
</p>

% if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
<p>
  ${_("Registreerimistasu kanda hiljemalt 20. jaanuariks Rahandusministeeriumi arveldusarvele:")}
  <ul>
    <li>LHV – EE777700771003813400</li>
    <li>SEB – EE891010220034796011</li>
    <li>Swedbank – EE932200221023778606</li>
    <li>Luminor – EE701700017001577198</li>
  </ul>
  ${_("Viitenumber:")} 2900082401
</p>
% endif

## 200px - et pangad kuvataks kahekaupa ridades
<div class="d-flex flex-wrap my-2" id="pangad" style="max-width:250px">
  % for pank in c.pangad:
  <% 
    if c.controller == 'pangalinktest':
        ## pangalingi testimine
        url_pank = h.url('admin_pangalinktest',pank_id=pank.id)            
    else:
        ## tuldi avalduse koostamise lehelt
        url_pank = h.url('regamine_avaldus_pangalink',pank_id=pank.id, testiliik=c.testiliik)
  %>
          <a href="${url_pank}" class="m-2">
            % if pank.logo:
            <img src="${pank.logo}" border="0" alt="${pank.alt}" title="${pank.alt}" width="88px"/>
            % else:
            ${pank.alt}
            % endif
          </a>
          % endfor
</div>

