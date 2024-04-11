## Testiosa sooritamine eelvaates

<%inherit file="/avalik/sooritamine/testiosasisu.mako"/>

<%def name="page_buttons()">
<div class="mb-3">
% if c.read_only:
    ${h.btn_to(_("Tagasi"), h.url_current('delete'), method='post', spinnerin=True, level=2)}

% elif not c.on_testivaline:

   % if c.testiosa.lopetatav or (not c.alatest and c.testiosa.on_alatestid):
      ## kui on lõpetatav või kui oleme alatestidega testi alatestide indeksis
      ${h.button(_("Lõpetan testi sooritamise"), onclick="end_test();", level=2)}
   % elif not c.testiosa.lopetatav and not c.alatest:
   <span class="on-last-task" style="display:none">
      ${h.button(_("Lõpetan testi sooritamise"), onclick="end_test();")}  
   </span>
   % endif
   % if c.testiosa.katkestatav:
        ${h.button(_("Katkestan testi sooritamise"), onclick="cancel_test();", level=2)}
   % endif
% endif
</div>
</%def>
