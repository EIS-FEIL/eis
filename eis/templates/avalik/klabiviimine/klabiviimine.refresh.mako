## automaatne lk uuendamine
<div>
  <div class="refr-msg">
    <%include file="/common/message.mako"/>
  </div>
  % if c.testiruum and c.testiruum.arvuti_reg:
  <%include file="arvutid_list.mako"/>
  % endif
  <%include file="sooritajad_list.mako"/>
</div>
