<%inherit file="/common/tabpage.mako"/>
<% c.r_tab = 'tekstianalyys' %>
<%include file="hindamine_r_tabs.mako"/>
<div id="hindamine_r_body" class="tekstianalyys">
  % if not c.data:
  ${_("Puudub vastuse tekst, mida analüüsida")}
  % else:
  % for (k_kood, ks_seq, meta) in c.data:
  <h2>${k_kood}
  % if ks_seq > 1:
  (${ks_seq})
  % endif
  </h2>	
  <div class="tekstianalyys-k" data-kood="${k_kood}_${ks_seq}">
  ${self.tbl(meta)}
  </div>	
  % endfor
  % endif
</div>

<script>
$('#hindamine_r_body input.show-txt').click(function(){
    var checked = this.checked, cls = this.name.substr(5),
        id = 'ks_outer_' + $(this).closest('.tekstianalyys-k').attr('data-kood'),
	div = $('iframe.hylesanne').contents().find('#' + id + ' .mcommentable');
    if(cls == 'rpt1' || cls == 'rpt2')
    {
       ## värvimine (rpt1, rpt2)
       var elems = div.find('.mcomment-'+cls);       
       elems.each(function(){
         $(this).toggleClass('on-'+cls, checked);
         var color = (checked ? $(this).attr('data-color') : 'inherit');
         $(this).css('background-color', color);
       });
    }
    else
    {
       ## peitmine/kuvamine
       var elems = div.find('.mcomment-icon.mcomment-'+cls);
       if(cls == 'auto')
       {
          ## automaatselt leitud vigade kuvamisel ei kuva neid, mis on kustutatud
          elems = elems.filter(':not(.mcomment-rm)')
       }
       elems.toggle(checked);
    }
});
## sõnaliigiti kuvamise akordion
$('a.liigiti-link').click(function(){
  $(this).closest('table').find('tr.liigiti').toggleClass('d-none');
  });
## algatame vigade arvu kopeerimise siia aknasse, kui ylesanne on laaditud
var iframe = $('iframe.hylesanne');
if(iframe.length && iframe[0].contentWindow.$){
   iframe[0].contentWindow.$('body').trigger('mcomment:display_analyze');
}
</script>

<%def name="tbl(meta)">
  <table class="table my-3">
    <thead>
      <tr>
        ${h.th(_("Nimetus"))}
        ${h.th(_("Näitaja"))}
        ${h.th(_("Märgi tekstis"))}
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          ${h.flb(_("Lausete arv tekstis"), 'lausete_arv')}
        </td>
        <td id="lausete_arv">
          ${meta.get('lausete_arv')}
        </td>
	<td></td>
      </tr>
      <tr>
        <td>
          ${h.flb(_("Teksti pikkus sõnades"), 'sonede_arv')}
        </td>
        <td id="sonede_arv">
          ${meta.get('sonede_arv')}
        </td>
	<td></td>
      </tr>
      <tr>
        <td>
          ${h.flb(_("Keskmine lausepikkus sõnades"), 'lausekeskm')}
        </td>
        <td id="lausekeskm">
          ${h.fstr(meta.get('lausekeskm'))}
        </td>
	<td></td>
      </tr>
      <tr>
        <td>
          ${h.flb(_("Kasutatud sõnade arv"), 'lemmade_arv')}
        </td>
        <td id="lemmade_arv">
          ${meta.get('lemmade_arv')}
        </td>
	<td></td>
      </tr>
      <tr class="evenback">
        <td>
          ${h.flb(_("EstNLTK abil leitud vigaste sõnade arv"), 'err_auto')}
        </td>
        <td class="err_auto" id="err_auto">
          ${meta.get('vigaste_sonade_arv')}
        </td>
        <td>
	      ${h.checkbox1('show_auto', 1, checked=True, class_="show-txt")}
        </td>
      </tr>
      <tr class="evenback">	
        <td align="right">
      	  ${h.flb(_("sh valesti vigaseks märgitud sõnad"), 'err_rm')}
        </td>
        <td class="err_rm" id="err_rm">
          ${meta.get('vead_valesti')}	
	    </td>
	    <td>
          ${h.checkbox1('show_rm', 1, checked=False, class_="show-txt")}         
        </td>
      </tr>
      <tr>
        <td>
          ${h.flb(_("Vigade arv vealiikide kaupa"))}
          ##${h.flb(_("Hindaja poolt märgitud vigade arv"))}
        </td>
        <td colspan="2"></td>
      </tr>
      <%
        vead = [['I', _('Ortograafiaviga')],
                ['p', _('Interpunktsiooniviga')],
                ['X', _('Sõnakordus')],
                ['V', _('Vormimoodustuse viga')],
                ['L', _('Lausestusviga')],
                ['S', _('Sobimatu sõnavalik')],
                ['typo', _('Trükiviga')],
                ['Z', _('Liigendusviga')],
               ]
      %>
      % for mtype, title in vead:
      <tr>
        <td align="right">
          ${h.flb(title, f"err_{mtype}")}
          <span class="mcomment-menuicon mcomment-${mtype}"></span>
        </td>
        <td class="err_${mtype}" id="err_${mtype}">

        </td>
        <td>
	      ${h.checkbox1(f'show_{mtype}', 1, checked=True, class_="show-txt")}          
        </td>
      </tr>
      % endfor
      
      <tr class="evenback">
        <td>
          ${h.flb(_("Pikkade (7 ja rohkem tähte) sõnade %"), 'pikad_protsent')}
        </td>
        <td id="pikad_protsent">
          ${h.fstr(meta.get('pikad_protsent'))}%
        </td>
	    <td></td>
      </tr>
      <tr class="evenback">
        <td>
          ${h.flb(_("Teksti loetavus (Lix indeks)"), 'lix')}
        </td>
        <td id="lix">
          ${h.fstr(meta.get('lix'))}
        </td>
	    <td></td>
      </tr>
      <tr class="evenback">
        <td>
          ${h.flb(_("Sõnakordused lauses"), 'show_rpt1')}
        </td>
        <td></td>
        <td>
          ${h.checkbox1('show_rpt1', 1, checked=False, class_="show-txt")}
        </td>
      </tr>
      <tr class="evenback">
        <td>
          ${h.flb(_("Sõnakordused järjestikustes lausetes"), 'show_rpt2')}
        </td>
        <td></td>
        <td>
          ${h.checkbox1('show_rpt2', 1, checked=False, class_="show-txt")}
        </td>
      </tr>
      <tr>
        <td>
          ${h.flb(_("Stoppsõnade %"), 'stopp_protsent')}
        </td>
        <td id="stopp_protsent">
          ${h.fstr(meta.get('stopp_protsent'))}%
        </td>
	    <td></td>
      </tr>
      <tr>

        <td>
          ${h.flb(_("Nimisõnade % (teksti nominaalsus)"), 'nimisonade_protsent')}
        </td>
        <td id="nimisonade_protsent">
          ${h.fstr(meta.get('nimisonade_protsent'))}%
        </td>
	    <td></td>
      </tr>
      <tr>
	<td>
	<u><a class="liigiti-link">${_("Sõnade analüüs liikide kaupa")}</a></u>
	</td>
	<td></td>
	<td></td>
      </tr>	
      <% liigiti = meta.get('liigiti') %>
      % if liigiti:
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Nimisõnade arv"))}
        </td>
        <td>
          ${liigiti['S']}
        </td>
	<td></td>
      </tr>
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Määrsõnade arv"))}
        </td>
        <td>
          ${liigiti['D']}
        </td>
	<td></td>
      </tr>
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Sidesõnade arv"))}
        </td>
        <td>
          ${liigiti['J']}
        </td>
	<td></td>
      </tr>
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Omadussõnade arv"))}
        </td>
        <td>
          ${liigiti['A'] + liigiti['C'] + liigiti['U']}
        </td>
	<td></td>
      </tr>
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Asesõnade arv"))}
        </td>
        <td>
          ${liigiti['P']}
        </td>
	<td></td>
      </tr>
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Kaassõnade arv"))}
        </td>
        <td>
          ${liigiti['K']}
        </td>
	<td></td>
      </tr>
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Tegusõnade arv"))}
        </td>
        <td>
          ${liigiti['V']}
        </td>
	<td></td>
      </tr>
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Arvsõnade arv"))}
        </td>
        <td>
          ${liigiti['N'] + liigiti['O']}
        </td>
	<td></td>
      </tr>
      <tr class="liigiti d-none">
        <td>
          ${h.flb(_("Hüüdsõnade arv"))}
        </td>
        <td>
          ${liigiti['I']}
        </td>
	<td></td>
      </tr>
      <tr class="evenback">
        <td>
          ${h.flb(_("Sõnarikkus"), "sonarikkus")}
        </td>
        <td id="sonarikkus">
          ${h.fstr(meta.get('sonarikkus'))}%
        </td>
	<td></td>
      </tr>
      <tr class="evenback">
        <td>
          ${h.flb(_("Sõnarikkust iseloomustav Uberi indeks"), 'uber')}
        </td>
        <td id="uber">
          ${h.fstr(meta.get('uber'))}
        </td>
	<td></td>
      </tr>
      % endif
    </tbody>
  </table>
</%def>	
