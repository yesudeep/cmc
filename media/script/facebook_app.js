jQuery(function(){        
    jQuery('#tabs').tabs('#panes > li', {effect: 'fade'});
    
    jQuery('#form-add-celebrity').ajaxForm(function(){
        jQuery.facebox("Thank you.  Your submission will be added soon.");
    });
    jQuery('#form-register').ajaxForm(function(){
        jQuery.facebox("Thank you for your helping us improve the book!");
    });
    jQuery('#form-write-story').ajaxForm(function(){
        jQuery.facebox("Lovely!  I'd love to read your story and possibly include it into my book.");
    });
    jQuery.getJSON('/celebrity/list', function(tags) {
        jQuery('#tag-cloud').tagCloud(tags);
        jQuery('#tag-cloud a').click(function(e){
            jQuery.post('/celebrity', {
                    name: jQuery(this).text()
                }, 
                function(data, textStatus){}
            );
            jQuery.facebox('Thanks for your vote!');
            e.stopPropagation();
            e.preventDefault();
            return false;
        });
    });
});
