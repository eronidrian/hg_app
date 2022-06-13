function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(create_post);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

$('#submit_point_button').on('click', getLocation);

function create_post(position) {
    var {latitude , longitude } = position.coords;

    $('#id_latitude').val(latitude)
    $('#id_longitude').val(longitude)

    $('#post-form').submit()
}

function hello() {
    // $.post()
    console.log('ahoj');
}

setInterval(hello, 10000)