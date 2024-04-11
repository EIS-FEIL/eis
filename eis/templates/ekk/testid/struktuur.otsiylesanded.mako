${h.form_search(url=h.url_current('index'), id="form_search")}
${h.hidden('partial', 1)}
<script>
  function search_ylesanded()
  {
     var form = $('form#form_search');
     var url = $(form).attr('action');
     var data = $(form).serialize();
     dialog_load(url, data, 'GET', $('div.listdiv')); 
     return false;
  }
  $(document).ready(function(){
    $('form#form_search').submit(search_ylesanded);
  });
</script>

<div class="gray-legend p-3 filter-w">

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ID"),'id')}
        ${h.text('id', '')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Nimetus"),'nimi')}
        ${h.text('nimi', '')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Märksõna"))}
        ${h.text('marksona', '')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Keel"))}
        <div>
          % for keel in c.test.keeled:
          <div>${h.checkbox('lang_%s' % keel, value=1, checked=True, label=model.Klrida.get_lang_nimi(keel))}</div>
          % endfor
        </div>
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">
          ${h.checkbox('st_avalik', value=const.Y_STAATUS_AVALIK, checked=c.st_avalik, label=_("Kõigile lahendamiseks"))}
          ${h.checkbox('st_pedagoog', value=const.Y_STAATUS_PEDAGOOG, checked=c.st_pedagoog, label=_("Kõigile pedagoogidele"))}
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeaine"))}
        <% if not c.aine: c.aine = c.test.aine_kood %>
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Kooliaste"))}
        ${h.select('aste', c.aste, c.opt.astmed(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Teema"))}
        ${h.select('valdkond', c.valdkond, 
           c.opt.klread_kood('TEEMA',c.aine,ylem_required=True,bit=c.opt.aste_bit(c.aste, c.aine)), empty=True, names=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Alateema"))}
        ${h.select('teema', c.teema, c.opt.klread_kood('ALATEEMA',ylem_id=c.teema_id,ylem_required=True, empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Keeleoskuse tase"))}
        ${h.select('keeletase', c.keeletase, 
             c.opt.klread_kood('KEELETASE',c.aine,ylem_required=True,empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Mõtlemistasand"))}
        ${h.select('mote', c.mote, c.opt.klread_kood('MOTE', empty=True))}    
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("E-kogu"))}
        <% opt_ylkogu = c.opt.ylkogud(c.aine) %>
        ${h.select('ylkogu_id', c.ylkogu_id, opt_ylkogu, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Osaoskused"))}
        ${h.select('oskus', c.oskus, 
             c.opt.klread_kood('OSKUS',c.aine,ylem_required=True,empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Liik"))}
        ${h.select('tyyp', c.kysimus, c.opt.interaction_empty)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.button150(_("Otsi"), onclick="search_ylesanded()")}
      </div>
    </div>
  </div>
</div>


<script>
      $(function(){
         $('select#aine').change(function(){change_valdkond();});
         $('select#aste').change(function(){change_valdkond();});
         $('select#valdkond').change(function(){change_teema();});
         $('select#aine').change(
           callback_select("${h.url('pub_formatted_valikud', kood='OSKUS', format='json')}", 
                           'ylem_kood', 
                           $('select#oskus'))
           );
         $('select#aine').change(
           callback_select("${h.url('pub_formatted_valikud', kood='YLKOGU', format='json')}", 
                           'aine', 
                           $('select#ylkogu_id'))
           );
         $('select#aine').change(
           callback_select("${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}", 
                           'ylem_kood', 
                           $('select#keeletase'))
           );
     });

      function change_valdkond()
      {
           var aine_field = $('select#aine');          
           var aste_field = $('select#aste');
           var url = "${h.url('pub_formatted_valikud', kood='TEEMA', format='json')}";
           var data = {aste: aste_field.val()};
           var target = $('select#valdkond');
           var subtarget = $('select#teema');
           update_options(aine_field, url, 'ylem_kood', target, data, subtarget, true);
      }
      function change_teema()
      {
           var teema_id = $('select#valdkond option:selected').attr('name');
           if(teema_id)
           {
              var url = "${h.url('pub_formatted_valikud', kood='ALATEEMA', format='json')}";
              var data = {ylem_id: teema_id};
              var target = $('select#teema');
              update_options(null, url, null, target, data);
           }
      }
</script>

${h.end_form()}

${h.form_save(1)}
${h.hidden('alatest_id', c.alatest_id)}
${h.hidden('testiplokk_id', c.testiplokk_id)}

<div class="listdiv">
% if c.items != '':
<%include file="struktuur.otsiylesanded_list.mako"/>
% endif
</div>

${h.end_form()}
