<%include file="/common/message.mako"/>
<div class="d-flex flex-wrap">
  <h2 class="flex-grow-1">${_("Minu töökogumikud")}</h2>
  ${h.button('', mdicls='mdi-folder-plus-outline', level=0, id="add_tk", title=_("Uus töökogumik..."),
  href=h.url_current('new'))}
</div>
<div>
  ${h.alert_info('<a href="https://projektid.edu.ee/pages/viewpage.action?pageId=142574997" target="_blank">%s</a>' % _("Juhend uute töökogumike loomiseks ja testide/ülesannete suunamiseks sooritajale"), False)}
</div>
<div class="tkogumikud">
  % for c.item in c.tookogumikud:
  <%include file="tookogumik.mako"/>
  % endfor
</div>
