${h.form(h.url('admin_klassiopilased'), method='post', multipart=True)}
${h.hidden('sub', 'fail')}
<table width="100%">
  <tr>
    <td class="fh">${_("Õppeasutus")}</td><td>${c.user.koht.nimi}</td>
  </tr>
  <tr>
    <td class="fh">${_("Klass")}</td>
    <td>
      ${h.select('klass', c.klass, const.EHIS_KLASS, wide=False)}
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Paralleel")}</td>
    <td>${h.text5('paralleel', c.paralleel)}</td>
  </tr>
  <tr>
    <td class="fh"></td>
    <td colspan="2">
      ${_("CSV faili iga rida peab sisaldama ühe õpilase andmeid kujul:")}
      <br/>
      <i>
        ${_("isikukood; eesnimi; perekonnanimi; sugu (M/N); sünnikuupäev (dd.mm.yyyy)")}
      </i>
    </td>
  </tr>
  <tr>    
    <td class="fh">${_("Fail")}</td>
    <td>${h.file('ik_fail', value=_("Fail"))}</td>
    <td>${h.submit(_("Salvesta"))}</td>
  </tr>
</table>
${h.end_form()}
