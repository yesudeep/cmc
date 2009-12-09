jQuery(function(){
    var elements = {
        tweetBox: jQuery("#tweets")
    };
    elements.tweetBox.tweet({
        username: ["yesudeep", "cuttingmchai"],
        join_text: "auto",
        count: 2,
        auto_join_text_default: "",
        auto_join_text_ed: "I",
        auto_join_text_ing: "was",
        auto_join_text_reply: "replied to",
        auto_join_text_url: "was checking out",
        loading_text: "fetching latest tweets..."
    });
});
