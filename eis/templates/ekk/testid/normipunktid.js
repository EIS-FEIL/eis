var init_sortables_normid = function(sortables){
    var g_sortables = sortables.filter('.grupinormid');
    if(g_sortables.length)
    {
        new Sortable(g_sortables[0], {
            animation: 150,
            onUpdate: function(evt){
                dirty = true;                
            }
        });
/*        g_sortables.sortable({
            connectWith: '.sortable.norm',
            placeholder: "ui-state-highlight",
            forcePlaceholderSize: true,
            update: function(event, ui) {
                dirty = true;
            },
            receive: function(event, ui){
                // peale grupi muutmist salvestame normi juurde grupi prefixi
                // mis seob normi ja grupi
                var index = $(this).attr('data-grupp-prefix');
                ui.item.find('input[name$=".grupp_prefix"]').val(index);
            }
        });
*/
    }
};
var init_sortable_norm = function(sortable){
/*
    sortable.filter('.sortable.norm')
        .draggable({
            containment: '.profiiliseaded',
            revert: 'invalid',
            connectToSortable: '.grupinormid'
        });
*/
};
var set_grupp_seq = function(){
    $('.grupp.sortable').each(function(n, grp){
        // igas grupis jäetakse meelde grupi järjekorranumber
        $(grp).find('.grp_seq').val(n+1);
    });
};

$(function(){
    var g_sortables = $('.grupid.sortables');
    if(g_sortables.length)
    {
        new Sortable(g_sortables[0], {
            animation: 150,
            onUpdate: function(evt){
                dirty = true;
                set_grupp_seq();
            }
        });
    }
    init_sortables_normid($('.profiiliseaded .grupinormid'));
    init_sortable_norm($('.profiiliseaded .sortable.norm'));    
    $(document).on('DOMNodeInserted', function(e){
        init_sortables_normid($(e.target));
        init_sortable_norm($(e.target));        
    });
    var anchor = "${request.params.get('anchor') or ''}";    
    if(anchor){
        setTimeout(function(){document.getElementById(anchor).scrollIntoView();}, 10);
    }   
});
