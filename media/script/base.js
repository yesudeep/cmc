jQuery(function(){
           var elements = {
               external_links: jQuery('a[href^="http://"]'),
               email_links: jQuery('a[href^="mailto:"]')
           };
           
           elements.external_links.attr('target', '_blank').attr('title', 'Opens the link a new tab/window.');
           elements.email_links.attr('title', 'Opens your email client to send an email.');
       });

