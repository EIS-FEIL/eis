<div id="maatriks" class="invisible">
<table class="table table-borderless table-striped" width="100%">
  <tr>
    % for ty in c.testiylesanded:
    <th>
      ${_("Ülesanne")} ${ty.sisestuskogum_seq}
      ##% if ty.tahis:
      ##<br/>tähis ${ty.tahis}
      ##% endif
      <br/>max ${h.fstr(ty.max_pallid)}p
    </th>
    % endfor
  </tr>
    <% 
       maatriks = {}
       ridu = 1
       tmp_komplektid = c.testikoht.toimumisaeg.komplektid
       if len(tmp_komplektid):
          komplekt = tmp_komplektid[0]
          for n1, ty in enumerate(c.testiylesanded):
             ## ty118, k66
             vy = ty.get_valitudylesanne(komplekt) 
             ylesanne = vy.ylesanne
             if len(ylesanne.hindamisaspektid):
                veerg = [ha for ha in ylesanne.hindamisaspektid]
             else:
                veerg = [None]
             maatriks[n1] = veerg
             ridu = max(ridu, len(veerg))
    %>
    % for rida in range(ridu):
  <tr>
       % for n1, ty in enumerate(c.testiylesanded):
       <td>
         % if len(maatriks[n1]) > rida:
           <% ha = maatriks[n1][rida] %>
           % if ha is None:
            ülesande hinne
           % else:
             ${ha.aspekt_kood}
             ${ha.aspekt.ctran.nimi}
             <br/>max ${h.fstr(ha.max_pallid)}p
           % endif
         % endif
       </td>
       % endfor
  </tr>
    % endfor
</table>
</div>
