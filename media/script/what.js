jQuery(function(){
        var polaroids = window.polaroids;
        for (var len=polaroids.length, i = 0; i < len; i++){
            loadImage(polaroids[i], '#polaroid-' + i);
        }

        function loadImage(metaimg, polaroid){
            var img = new Image();
            jQuery(img)
                .load(function(){
                        var elem = jQuery(this);
                        elem.hide();
                        jQuery(polaroid).removeClass('.loading').append(this).addClass('left').css({width: metaimg.width + "px", height: metaimg.height + "px"});
                        elem.fadeIn();
                    })
                .error(function(){
                        // Error occurred.
                    })
                .attr('src', metaimg.url);
        }
    });
