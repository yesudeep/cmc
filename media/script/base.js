/*
 * Common to all templates.
 */
jQuery(function(){
    var elements = {
        external_links: jQuery('a[href^="http://"]'),
        exposables: jQuery('.portrait, .polaroids, .a2a_menu'),
        fancybox_dialogs: jQuery('.fancybox-dialog')
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
    }).click(function(){
        jQuery(this)
            .expose({
                api:true,
                closeSpeed: 100
            })
            .close();
    });
    elements.fancybox_dialogs.fancybox({
        overlayShow: false,
        overlayColor: '#000',
        overlayOpacity: 0.6,
        hideOnContentClick: false,
        showCloseButton: true,
        centerOnScoll: true,
        autoDimensions: true,
        zoomSpeedIn: 300,
        zoomSpeedOut: 300
    });
    elements.external_links.attr('target', '_blank');
});
