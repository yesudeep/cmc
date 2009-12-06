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
FB.init(window.fb.apiKey, window.fb.crossDomainReceiverUrl, {
        "ifUserConnected": fbUpdateUserBox
    /*, "reloadIfSessionStateChanged": true*/
});

/*
 * Other stuff.
 */
jQuery(function(){
    var googleFriendConnectSkin = {
        BORDER_COLOR: '#cccccc',
        ENDCAP_BG_COLOR: '#e0ecff',
        ENDCAP_TEXT_COLOR: '#333333',
        ENDCAP_LINK_COLOR: '#0000cc',
        ALTERNATE_BG_COLOR: '#ffffff',
        CONTENT_BG_COLOR: '#ffffff',
        CONTENT_LINK_COLOR: '#0000cc',
        CONTENT_TEXT_COLOR: '#333333',
        CONTENT_SECONDARY_LINK_COLOR: '#7777cc',
        CONTENT_SECONDARY_TEXT_COLOR: '#666666',
        CONTENT_HEADLINE_COLOR: '#333333',
        NUMBER_ROWS: '2'
    };
    google.friendconnect.container.setParentUrl('/');
    google.friendconnect.container.renderMembersGadget({
    //google.friendconnect.container.renderSignInGadget({
        id: window.gfc.divId,
        site: window.gfc.siteId
    }, googleFriendConnectSkin);
});
