function getLocationOnce() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(create_post_once);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

$('#submit_point_button').on('click', getLocationOnce);

function create_post_once(position) {
    var {latitude , longitude } = position.coords;

    $('#id_latitude').val(latitude)
    $('#id_longitude').val(longitude)
    console.log(latitude, longitude);

    $('#post-form').submit()
}

function getLocationPeriodically() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(create_post_periodically);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function create_post_periodically(position) {
    var {latitude , longitude } = position.coords;
    console.log(latitude, longitude);
    $.ajax({
        url : "/player_location/",
        type : "GET",
        data : { lat : latitude,
                 long : longitude,
                 csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(), },
    })

}

setInterval(getLocationPeriodically, 10000)