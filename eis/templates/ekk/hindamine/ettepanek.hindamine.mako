## Ühe soorituse ühe ülesande hindamise ettepaneku sisestamine 
## kuvatakse ülesande sisu ja kõik selle hindamised

<%
  c.counter = -1
  c.koik_alatestid = True
  c.item = c.sooritus

  ## list kõigist hindamistest, mida kuvatakse
  c.holek = c.sooritus.get_hindamisolek(c.hindamiskogum)
  if c.holek:
      c.hindamised = [rcd for rcd in c.holek.hindamised \
                      if rcd != c.hindamine and rcd.sisestus==1 and \
                       rcd.staatus not in (const.H_STAATUS_LYKATUD, const.H_STAATUS_SUUNATUD)]
  else:
      ## seda olukorda ei tohiks olla
      c.hindamised = []


  c.eksperdivaade = True
  c.komplekt = c.holek and c.holek.komplekt or None
%>
  % if c.testiylesanne.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
    <%include file="ettepanek.hindamine.ylesanne.mako"/>
  % else:
  <%
  c.testiruum = c.sooritus.testiruum
  c.items = [c.sooritus]
  %>
   <%include file="ekspert.suulinesisu.mako"/>
  % endif


