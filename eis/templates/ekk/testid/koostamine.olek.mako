${h.not_top()}
<%include file="/common/message.mako"/>
${h.form(h.url('test_update_koostamine', id=c.item.id), method='put')}
${h.hidden('sub', 'olek')}
<div class="form-group row">
${h.flb3(_("Olek"), 'staatus', 'mr-3')}
<div class="col">
<%
  opt_st = c.opt.klread_kood('T_STAATUS')
%>
${h.select('staatus', c.item.staatus, opt_st)}
</div>
</div>

<div class="form-group row">
${h.flb3(_("Kasutatavus"), 'avaldamistase', 'mr-3')}
<div class="col">
<%
  opt_avalik = c.opt.opt_avalik
  ignore = []
  if c.item.testiliik_kood not in (const.TESTILIIK_KOOLIPSYH, const.TESTILIIK_LOGOPEED):
      ignore.append(const.AVALIK_LITSENTS)

  if not c.user.has_permission('sisuavaldamine', const.BT_UPDATE, c.item):
      ignore = ignore + [const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD]

  opt_avalik = [r for r in opt_avalik if (c.item.avaldamistase == int(r[0])) or (int(r[0]) not in ignore)]
%>
  ${h.select('avaldamistase', c.item.avaldamistase, opt_avalik)}
  <div class="avalik" style="display:none">
  <div class="d-flex flex-wrap my-1">
    <div class="mr-3">
    ${_("alates")}
    ${h.date_field('t_avalik_alates', c.item.avalik_alates, wide=False)}
    </div>
    <div>
    ${_("kuni")}
    ${h.date_field('t_avalik_kuni', c.item.avalik_kuni, wide=False)}
    </div>
  </div>
  </div>
</div>
</div>

<div class="my-3">
  ${h.flb(_("Märkused"))}
  <br/>
  ${h.textarea('markus', '', cols=80, rows=5)}
</div>
<div class="text-right">
  ${h.submit_dlg()}
</div>
${h.end_form()}

<script>
  ## kui valitakse testi avaldamine, siis kuvada avaldamise ajavahemik
  function show_a(){
     var a = $('#avaldamistase').val();
     $('.avalik').toggle(a == "${const.AVALIK_SOORITAJAD}" || a == "${const.AVALIK_OPETAJAD}" || a == "${const.AVALIK_MAARATUD}");
  }
  show_a();
  $('#avaldamistase').change(show_a);
</script>
