<div class="result">
  <%
    kohad = c.item.regkohad
    k_nimed = [r.nimi for r in kohad]
  %>
  ${', '.join(k_nimed)}
  <%include file="/common/message.mako"/>
</div>
## kord.regkohad.mako cp_result() tõstab .result sisu suurde aknasse .regkohad-list sisse
