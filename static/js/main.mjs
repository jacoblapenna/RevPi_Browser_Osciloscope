
var socket =  io.connect(location.origin);
var stream_running = false;
var stream_control_button = document.getElementById("start");

add_stream_control_handler(stream_control_button);

function add_stream_control_handler(element) {
  element.addEventListener("click", function() {
      control_stream(this);
    }, {once: true});
}
// comment

function control_stream(element) {
  if (stream_running) {
    stream_running = false;
    socket.emit("stop_stream");
  } else {
    stream_running = true;
    socket.emit("start_stream");
  }
  add_stream_control_handler(element);
}

socket.on("data", function(data) {

});


socket.on("extrema", function(data) {
  console.log(data);
});
