<h1>${_("Tulemused")} – ${c.test.nimi}</h1>
<div class="question-status d-flex mb-4">
  <div class="item mr-5"><b>${_("ID")}</b> ${c.test.id}</div>
  <div class="item mr-5"><b>${_("Õppeaine")}</b> ${c.test.aine_nimi}</div>
  <div class="item mr-5"><b>${_("Toimumise aeg")}</b> ${c.testimiskord.millal}</div>
  % if not c.test.pallideta:
  <div class="item mr-5"><b>${_("Max")}</b> ${h.fstr(c.test.max_pallid)}p</div>  
  % endif
  % if c.kursus:
  <div class="item mr-5"><b>${_("Kursus")}</b> ${model.Klrida.get_str('KURSUS', c.kursus, c.test.aine_kood)}</div>
  % endif
</div>
