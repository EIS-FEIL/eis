var aine_vald = ${h.json.dumps(model.Klrida.get_kood_ryhm('AINE'))};
var vald_nimed = ${h.json.dumps(c.opt.klread_kood('AINEVALD'))};
  
function ainevald_by_aine(aine)
{
    for(var i=0; i<aine_vald.length; i++)
    {
        if(aine_vald[i][0] == aine) return aine_vald[i][1];
    }                              
}
function update_ainevald()
{
    var aine = $('[name="f_aine_kood"]').val(), vald = null, vald_nimi = '';
    if(aine == "${const.AINE_YLD}")
    {
        var ained = $('[name="f_seotud_ained"]').val() || [];
        for(var i=0; i<ained.length; i++)
        {
            var vald1 = ainevald_by_aine(ained[i]);
            if(vald == null){ vald = vald1; }                        
            else if(vald != vald1){ vald = null; break;}                        
        }
    }
    if(vald == null) vald = ainevald_by_aine(aine);
    if(vald) for(var i=0; i<vald_nimed.length; i++){
        if(vald_nimed[i][0] == vald) { vald_nimi = vald_nimed[i][1]; break; }
    }
    $('input[name="f_ainevald_kood"]').val(vald);
    $('span.ainevald_nimi').text(vald_nimi);
}
function show_tase()
{
    var on_voorkeel = $('[name="f_ainevald_kood"]').val() == "${const.AINEVALD_VRK}";
    $('div.keeletase').toggle(on_voorkeel);
    return on_voorkeel;
}
function update_tase()
{
    var target = $('select#f_keeletase_kood');
    if(show_tase())
    {
        var aine_field = $('select#f_aine_kood');
        var url = "${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}";
        var data = {};
        update_options(aine_field, url, 'ylem_kood', target, data, null, true);
    }
    else
    {
        target.empty();
    }
}
function show_oskus()
{
    var on_keel = $('[name="f_ainevald_kood"]').val() == "${const.AINEVALD_VRK}";
    if(!on_keel)
    {
        var aine = $('[name="f_aine_kood"]').val();
        on_keel = aine == "${const.AINE_ET}" || aine == "${const.AINE_EE}" || aine == "${const.AINE_W}";
    }
    $('div.oskus').toggle(on_keel);
    return on_keel;
}
function update_oskus()
{
    var target = $('select#f_oskus_kood');
    if(show_oskus())
    {
           var aine_field = $('select#f_aine_kood');
           var url = "${h.url('pub_formatted_valikud', kood='OSKUS', format='json')}";
           var data = {};
           update_options(aine_field, url, 'ylem_kood', target, data, null, true);
    }
    else
    {
        target.empty();
    }
}                                                      
function update_teema()
{
    var data = {'aine': $('#f_aine_kood').val(),
                'aste': $('#f_kooliaste_kood').val()};
    var url = "${h.url('pub_formatted_valikud', kood='TEEMA2', format='json')}";
    $.getJSON(url, data,
              function(data){
                  var old_value = $('#teemad2').val();
                  $('#teemad2').empty();
                  ${h.select2_js('teemad2', old_value, [], data='data', multiple=True, multilevel=True, template_selection='template_selection2')}
              });
}
function update_klass()
{
    ## peale astme valimist kuvame ainult valitud kooliastme klassid
    var aste = $('select#f_aste_kood').val();
    if(aste)
    {
        var options = $('select#f_klass option:not([value=""])');
        var selected = options.filter(':selected');
        if((selected.length > 0) && !(selected.is('[name="' + aste + '"]')))
        {
            console.log('selected ' + selected.attr('name') + '<>' + aste);
            selected.prop('selected', false);
        }
        options.filter(':not([name="' + aste + '"])').hide();
        options.filter('[name="' + aste + '"]').show();
    }
}
// select2 jooksvate väärtuste kuvamise mall
function template_selection2(n){
    // viimane tase
    var divs = '<div class="col-sm-6">' + n.text + '</div>';
    if(n.p_text)
    {
        // teise taseme korral lisame esimese taseme
        divs = '<div class="col-sm-6">' + n.p_text + '</div>' + divs;
    }
    return $('<div class="row">' + divs + '</div>');
}
$(function(){
    $('.seotud').toggle($('[name="f_aine_kood"]').val()=="${const.AINE_YLD}");
    show_tase();
    $('[name="f_aine_kood"]').change(function(){
        $('.seotud').toggle($(this).val()=="${const.AINE_YLD}");
        update_ainevald();
        update_tase();
        update_oskus();
        update_teema();
    });
    $('[name="f_seotud_ained"]').change(function(){
        update_ainevald();
    });
    $('select#f_aste_kood').change(function(){
        update_klass();
        update_teema();
    });
    update_klass();
});

