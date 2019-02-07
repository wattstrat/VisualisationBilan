/* CSRF protection */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/** Real code **/
$(document).ready(function(){
    $(".simulation-list-toggle-btn").click(function(event){
        event.preventDefault();
        $(this).nextAll('ul').first().slideToggle(400);
    }).siblings('ul').hide();
    
    $(".multiple-select").each(function(index, element){
        var $element = $(element);
        $element
        .removeClass('form-control')
        .multipleSelect({
            selectAll: false,
            width: '100%',
            placeholder: $element.attr('placeholder'),
            allSelected: false
        });
    });
    
    $("a.subscription-change").click(function(event){
        event.preventDefault();
        $.post("", {subscription: $(this).attr("data-subscription")}, function(){
            $('#subscription-change-modal').modal();
        });
    });
});
