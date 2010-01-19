jQuery(function(){
    jQuery.getJSON('/celebrity/list', function(tags) {
        jQuery('#tag-cloud').tagCloud(tags);
        jQuery('#tag-cloud a').click(function(e){
            jQuery.post('/celebrity', {name: jQuery(this).text()}, function(data, textStatus){
            });
            e.stopPropagation();
            e.preventDefault();
            return false;
        });
    });
    
});