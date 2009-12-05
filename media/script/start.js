/*
 * Facebook connect integration
 */
function fbUpdateUserBox(){
    var userBox = document.getElementById("user-box");
    userBox.innerHTML = "<span>"
        + "<fb:profile-pic uid='loggedinuser' facebook-logo='true'></fb:profile-pic>"
        + "Welcome, <fb:name uid='loggedinuser' useyou='false'></fb:name>. "
        + "You are signed in with your Facebook account."
        + "</span>";
    FB.XFBML.Host.parseDomTree();
}
FB.init(window.fb.api_key, window.fb.cross_domain_receiver_url, {
        "ifUserConnected": fbUpdateUserBox,
            "reloadIfSessionStateChanged": true
            });

/*
 * Other stuff.
 */
jQuery(function(){

    });
