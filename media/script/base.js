jQuery(function(){
           var elements = {
               external_links: jQuery('a[href^="http://"]'),
               email_links: jQuery('a[href^="mailto:"]'),
               exposables: jQuery('#about-the-chaiwala, .icons, a#link-share, .awesome-button')
           };

           elements.exposables.hover(function(){
                                    jQuery(this).expose({api:true, opacity: 0.7, loadSpeed: 100, backgroundColor: '#000'}).load();
                                }, function(){
                                    jQuery(this).expose({api:true, closeSpeed: 100}).close();
                                });
           elements.external_links.attr('target', '_blank').attr('title', 'Opens the link a new tab/window.');
           elements.email_links.attr('title', 'Opens your email client to send an email.');
       });

