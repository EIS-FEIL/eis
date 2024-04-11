## -*- coding: utf-8 -*- 

<table  class="table" width="100%">
  <col width="225px"/>
  <tr>
    <td class="fh">${_("Töövaldkond")}</td>
    <td>${h.select('f_tvaldkond_kood', c.sooritaja.tvaldkond_kood, 
      c.opt.klread_kood('TVALDKOND', vaikimisi=c.sooritaja.tvaldkond_kood), 
      empty=True, wide=False)}
      % if not c.is_edit and c.sooritaja.tvaldkond_kood == const.TVALDKOND_MUU:
      ${c.sooritaja.tvaldkond_muu}
      % endif
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Amet")}</td>
    <td>
      ##${h.select('f_amet_kood', c.sooritaja.amet_kood, 
      ##c.opt.klread_kood('AMET', vaikimisi=c.sooritaja.amet_kood), 
      ##empty=True, wide=False)}
      ${h.text('k_amet_muu', c.sooritaja.amet_muu)}
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Haridus")}</td>
    <td>${h.select('f_haridus_kood', c.sooritaja.haridus_kood, 
      c.opt.klread_kood('HARIDUS', vaikimisi=c.sooritaja.haridus_kood), 
      empty=True, wide=False)}</td>
  </tr>
  <tr>
    <td class="fh">${_("Kodakondsus")}</td>
    <td>
      ${h.select('f_kodakond_kood', c.sooritaja.kodakond_kood, 
      c.opt.klread_kood('KODAKOND', vaikimisi=c.sooritaja.kodakond_kood), 
      empty=True, wide=False)}
    </td>
  </tr>
 
  <tr>
    <td class="fh">
      ${h.checkbox('on_lisatingimused', 1, checked=bool(c.kasutaja.lisatingimused),
      onchange="$('#k_lisatingimused').toggleClass('invisible', !this.checked);")}
      ${_("Lisatingimused")}
    </td>
    <td>
      ${h.textarea('k_lisatingimused', c.kasutaja.lisatingimused, rows=4,
      class_=not c.kasutaja.lisatingimused and 'invisible' or None)}
    </td>
  </tr>
</table>
