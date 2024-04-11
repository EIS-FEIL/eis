## helivastusfaili kuulamine ja faili andmed
<%
  hvf = c.helivastusfail
  url = h.url_current('download', id=hvf.id, format=hvf.fileext or 'file')
%>
<div class="d-flex flex-wrap hvf" id="hvf_${hvf.id}">
  <%namespace name="audiorecorder" file='/sisuplokk/audiorecorder.mako'/>
  <div class="pr-1">
    ${audiorecorder.play_audio(url, hvf.mimetype, height='32px')}
  </div>
  <div>
    ${h.link_to(hvf.filename, url)}
    ${h.filesize(hvf.filesize)}
    ${h.str_from_datetime(hvf.modified)}

    ## kuvame failiga seotud sooritajate nimed juhul, kui fail ei sisalda kõiki sooritajaid
    <%
      s_nimed = ''
      q = (model.Session.query(model.Helivastus.sooritus_id)
          .filter(model.Helivastus.helivastusfail_id==hvf.id))
      hv_sooritused_id = [r[0] for r in q.all()]
      set_hv_sooritused_id = set(hv_sooritused_id)
      if c.sooritused_id:
         set_sooritused_id = set(c.sooritused_id)
         if set_sooritused_id != set_hv_sooritused_id:
            # fail ei käi samade sooritajate kohta
            muud_nimed = [model.Sooritus.get(s_id).sooritaja.nimi \
               for s_id in hv_sooritused_id if s_id not in set_sooritused_id]
            if set_sooritused_id - set_hv_sooritused_id:
               # kõik hinnatavad sooritused ei ole failis 
               samad_nimed = [nimi for (s_id, nimi) in c.sooritajate_nimed if s_id in hv_sooritused_id]
               s_nimed = ', '.join(muud_nimed + samad_nimed)
            else:
               s_nimed = '+ ' + ', '.join(muud_nimed)
    %>
    % if s_nimed:
    (${s_nimed})
    % endif
  </div>
</div>
