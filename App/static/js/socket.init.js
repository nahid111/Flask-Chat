//========================================================================================
//                      Socket.IO Create connection to the server
//========================================================================================

// var socket = io.connect('server_url_with_port');     // var socket = io.connect('http://127.0.0.1:5000');
var socket = io.connect('http://' + document.domain + ':' + location.port);


// ----------------------------------------------------------------------
//                  on connection call function
// ----------------------------------------------------------------------
socket.on('connect', function () {
    // update session id
    socket.emit('update sid request', function () {
        console.log('Connected: ', socket.connected);
        console.log('Socket id updated, Current Socket id: ', socket.id);
    });
    // broadcast online status
    socket.emit('broadcast online request');
});


// ----------------------------------------------------------------------
//                  on disconnection call function
// ----------------------------------------------------------------------
socket.on('disconnect', function () {
    console.log('Disconnected');
});


// ----------------------------------------------------------------------
//                      Broadcast Online Status
// ----------------------------------------------------------------------
// socket.on('event_name', function (JSON) {}
socket.on('broadcast online response', function (data_JSON) {
    console.log('User: ' + data_JSON.user_id + ' is Online');
});


