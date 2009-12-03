jQuery(function(){
           var elements = {
               external_links: jQuery('a[href^="http://"]'),
               email_links: jQuery('a[href^="mailto:"]'),
               exposables: jQuery('#about-the-chaiwala, .polaroids, .a2a_menu')
           };

           elements.exposables.hover(function(){
                                    jQuery(this).expose({api:true, opacity: 0.6, loadSpeed: 100, color: '#000'}).load();
                                }, function(){
                                    jQuery(this).expose({api:true, closeSpeed: 100}).close();
                                });
           elements.external_links.attr('target', '_blank').attr('title', 'Opens the link a new tab/window.');
           elements.email_links.attr('title', 'Opens your email client to send an email.');
       });

