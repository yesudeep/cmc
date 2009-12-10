/*
 * Common to all templates.
 */
jQuery(function(){
    var elements = {
        externalLinks: jQuery('a[href^="http://"]'),
        exposables: jQuery('.portrait, .polaroids, .a2a_menu'),
        linkVoteTitleNo: jQuery('#link-vote-title-no')
    };
    var defaultFancyBoxPreferences = {
        overlayShow: true,
        overlayColor: '#000',
        overlayOpacity: 0.6,
        hideOnContentClick: false,
        showCloseButton: true,
        centerOnScoll: true,
        autoDimensions: true,
        autoScale: true,
        padding: 15,
        enableEscapeButton: true,
        zoomSpeedIn: 300,
        zoomSpeedOut: 300
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
    elements.linkVoteTitleNo.fancybox(jQuery.extend({

    }, defaultFancyBoxPreferences));
    elements.externalLinks.attr('target', '_blank');
});
