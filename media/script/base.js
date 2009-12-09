/*
 * Common to all templates.
 */
jQuery(function(){
    var elements = {
        external_links: jQuery('a[href^="http://"]'),
        exposables: jQuery('#nav, .portrait, .polaroids, .a2a_menu')
    };

    elements.exposables.hover(function(){
        jQuery(this)
            .expose({
                api:true,
                opacity: 0.6,
                loadSpeed: 100,
                color: '#000'})
            .load();
    }, function(){
        jQuery(this)
            .expose({
                api:true,
                closeSpeed: 100
            })
            .close();
    });
    elements.external_links.attr('target', '_blank');
});

