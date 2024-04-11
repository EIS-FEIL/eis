## Hindamisprotokolli yhe hindamiskogumi hindepallide sisestamine

<script>
## dict, kus iga vy kohta on dict, milles iga aspekti kohta on max_pallid
var aspekti_toorpunktid = {};

## dict, kus iga ty kohta on dict, milles iga komplekti kohta on list vy-de loeteluga
var valitudylesanded = {};

% for ty in c.testiylesanded:
  <% 
     ## kuna aspektid on ylesande kyljes, mitte testiylesande kyljes,
     ## siis võivad sõltuvalt komplektist olla samal testiylesandel erinevad aspektid
     ## hoiame meeles valitudylesannetele vastavad aspektid
     c.kogum_aspektid[ty.id] = ty_aspektid = ty.get_aspektid(c.toimumisaeg) 
     ## leiame komplektile vastavad valitudylesanded
     ## valikylesannete korral võib yhele komplektile vastata mitu valitudylesannet
     c.valitudylesanded[ty.id] = ty_valitudylesanded = ty.get_valitudylesanded()
  %>

      valitudylesanded['${ty.id}'] = {
  % for n, (k_id, vy_list) in enumerate(ty_valitudylesanded.items()):
         ${n > 0 and ',' or ''} '${k_id}': ${str([vy.id for vy in vy_list])}
  % endfor
         };

  % for (k_id, vy_list) in ty_valitudylesanded.items():
     % for vy in vy_list:
      aspekti_toorpunktid['${vy.id}'] = {
          % for n, a in enumerate(ty_aspektid):
           <% ha = a.y_hindamisaspektid.get(vy.id) %> ${n > 0 and ',' or ''} '${a.kood}': ${ha and ha.max_pallid or 'null'}
          % endfor
         };
     % endfor
  % endfor
% endfor

## funktsioon, mis käivitub komplekti valiku muutmisel
function set_komplekt(fld)
{
  ## tos rida, millel toimub tegevus
  var tr_tos = $(fld).closest('tr#tos');
  ## hindamise prefiks, kehtib kõigile tabeli sama rea (soorituse) väljadele
  var hm_prefix = get_prefix($(fld).attr('name'));
  ## valitud komplekt
  var komplekt_id = $(fld).val();
  ## leiame kõik sama sisestuse testiylesanded sellel real
  var ty_id_list = tr_tos.find('input[name^="'+hm_prefix+'"]').filter('[name$="ty_id"]');
  ## rea iga ty kohta
  $.each(ty_id_list, function(n, item)
  {
    var ty_prefix = get_prefix($(item).attr('name'));
    var ty_id = $(item).val();
    var vy_id = '';
    ## leiame ty pallide sisestusvälja
    var fld_ty_toorpunktid = $('input[name="'+ty_prefix+'.toorpunktid"]');

    if(komplekt_id)
    {
        ## valiti komplekt (mitte --Vali--)
        ## eeldame, et valikylesannetel on samad toorpunktid ja kasutame esimest valikylesannet
        vy_id = valitudylesanded[ty_id][komplekt_id][0];
    }

    ## kas ty palle saab sisestada
    var enable_ty_toorpunktid = true;

    ## otsime kõik selle ty aspektide lahtrid
    a_kood_list = tr_tos.find('input[name^="'+ty_prefix+'.ha"]').filter('[name$="toorpunktid"]');
    $.each(a_kood_list, function(n2, fld_a_toorpunktid)
    {
           ## aspekti kood
           var a_kood = $(fld_a_toorpunktid).closest('td').find('input[name$="a_kood"]').val();
           ## mitu palli on aspektile max lubatud sisestada
           var max_pallid = null;
           if(vy_id)
           {
               max_pallid = aspekti_toorpunktid[vy_id][a_kood];
           }

           ## muudame aspekti toorpunktide sisestusvälja kasutatavust
           if(max_pallid)
           {
               ## aspekt on selles ylesandes kasutusel
               $(fld_a_toorpunktid).removeAttr('disabled');
               $(fld_a_toorpunktid).attr('maxvalue', max_pallid);

               ## kuna vähemalt üks aspekt on kasutusel, 
               ## siis ei luba kasutajal  ty kogupalle sisestada
               enable_ty_toorpunktid = false;
           }
           else
           {
               ## aspekt ei ole selles ylesandes kasutusel
               $(fld_a_toorpunktid).attr('disabled', true);
           }
    });

    
    ## muudame ty kogutoorpunktide sisestusvälja kasutatavust
    if(enable_ty_toorpunktid)
    {
        ## aspekte pole, sisestatakse kogutoorpunktid
        fld_ty_toorpunktid.removeAttr('disabled');
    }
    else
    {
        ## see on aspektidega ylesanne, ty kogupalle ei saa sisestada
        fld_ty_toorpunktid.attr('disabled', true);
    }

  });
}

## funktsioon, mis arvutab peale aspekti toorpunktide sisestamist ty kogutoorpunktid
function calc_ty_total(item)
{
  ## hk-N.hmine-N.ty-N.ha-N.toorpunktid -> hk-N.hmine-N.ty-N.toorpunktid
  var ty_prefix = get_ty_prefix_of_ha($(item).attr('name'));
  var total = 0;
  var a_toorpunktid =
    $('input[name^="'+ty_prefix+'.ha"]').filter('[name$="toorpunktid"]');
  for(var i=0; i<a_toorpunktid.length; i++)
  {
    var str_a_toorpunktid = a_toorpunktid.eq(i).val().replace(',','.');
    if(str_a_toorpunktid)
       total += parseFloat(str_a_toorpunktid);
  }
  $('input[name^="'+ty_prefix+'.toorpunktid"]').val(total);
}
## hindamisaspekti välja nimest tuletatakse ty prefiks
function get_ty_prefix_of_ha(name)
{
  var pos = name.lastIndexOf('.ha');
  return name.substr(0,pos);
}
## välja nimest tuletatakse prefiks
function get_prefix(name)
{
  var pos = name.lastIndexOf('.');
  return name.substr(0,pos);
}
function change_loobun(cb)
{
  $(cb).closest('td').nextAll().toggle(!cb.checked);
}
$(document).ready(function(){
 $.each($('table#tbl_hk_${c.hk_n}').find('input[name$=".loobun"]').filter(':checked'),
        function(index, cb){
          change_loobun(cb);
        });

## kui salvestamisel leiti vigu, siis komplekt on salvestamata ja aspekte 
## ei lasta salvestada, seetõttu seame komplektid uuesti
 $.each($('select.inp_komplekt'), function(n, item){
     set_komplekt(item);
 });

});
</script>
