## -*- coding: utf-8 -*-
## Peale Veriffist naasmist alustatakse testi sooritamist
## Selleks suunatakse kasutaja testi sooritamise POST urlile.
<%inherit file="/common/page.mako"/>
<form id="test_form" action="${c.test_url}" method="POST">
</form>
<script>
  $('form#test_form').submit();
</script>
