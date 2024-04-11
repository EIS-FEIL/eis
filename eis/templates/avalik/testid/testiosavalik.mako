
<% testiosad = list(c.test.testiosad) %>
% if len(testiosad) > 1:
${h.form_search(c.testiosavalik_action)}
<div class="px-3 pb-2">
  <div class="d-flex flex-wrap justify-content-end">
    ${h.flb(_("Testiosa"), 'testiosa_id', 'pr-3 pt-1')}
    <div>
      <% opt_testiosad = [(o.id, o.nimi) for o in testiosad] %>
      ${h.select('testiosa_id', c.testiosa_id, opt_testiosad, ronly=False, wide=False)}
      <script>
        $('select#testiosa_id').change(function(){
          this.form.submit();
        });
      </script>
    </div>
  </div>
</div>
${h.end_form()}
% endif
