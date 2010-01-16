String.prototype.startsWith = function(str)
{return (this.match("^"+str)==str)}

/*
String.prototype.endsWith = function(str)
{return (this.match(str+"$")==str)}
*/

String.prototype.isUpperCase = function(){
   var re = new RegExp("^[^a-z]*$", "g");
   return !!re.test(this);
}
String.prototype.isLowerCase = function(){
   var re = new RegExp("^[^A-Z]*$", "g");
   return !!re.test(this);
}
String.prototype.isSameCase = function(){
   return (this.isLowerCase() || this.isUpperCase());
}
String.prototype.sanitizeCapitalization = function(){
   // Requires the titlecaps function by john resig.
   if(this && this.isSameCase()){
       return titleCaps(this.toLowerCase());
   } else {
       return this;
   }
}
String.prototype.lowerSanitizeCapitalization = function(){
   if(this && this.isLowerCase()){
       return titleCaps(this);
   } else {
       return this;
   }
}

jQuery(function(){
    var elements = {
        mobile_or_phone_fields: jQuery('form input.mobile, form input.phone'),
        form_decorated_fields: jQuery('form.decorated-fields'),
        url_fields: jQuery('form input.url'),
        capitalization_fields: jQuery('form input.capitalize'),
        lower_capitalization_fields: jQuery('form input.lower-capitalize')
    }, HTTP = "http://";

    elements.mobile_or_phone_fields.numeric({allow: '+-() '});
    elements.url_fields.keyup(function(event){
        var elem = jQuery(this), value = elem.val();
        if (value == 'http:/'){
            // For now handle only one common case where the user may press a backspace
            // to clear the last front slash.
            elem.val(HTTP);
        } else if (!value.startsWith(HTTP)){
            elem.val(HTTP + value);
        }
    });
    elements.capitalization_fields.change(function(event){
       var elem = jQuery(this), value = jQuery.trim(elem.val());
       elem.val(value.sanitizeCapitalization());
    });
    elements.lower_capitalization_fields.change(function(event){
        var elem = jQuery(this), value = jQuery.trim(elem.val());
        elem.val(value.lowerSanitizeCapitalization());
    });
    elements.form_decorated_fields.validate({
        rules: {
            presentation: {
              //required: true,
              accept: "ppt|doc|pdf"
            },
            mobile_number: {
                mobile: true
            },
            phone_number: {
                phone: true
            }
        },
        messages: {
            presentation: {
                accept: "Please upload a PowerPoint presentation, a Word document, or a PDF document only."
            }
        }
    });
});
