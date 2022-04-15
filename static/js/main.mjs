
var socket =  io.connect(location.origin);
var stream_running = false;
var stream_control_button = document.getElementById("start");

add_stream_control_handler(stream_control_button);

function add_stream_control_handler(element) {
  element.addEventListener("click", function() {
      control_stream(this);
    }, {once: true});
}

function control_stream(element) {
  if (stream_running) {
    socket.emit("stop_stream");
  } else {
    socket.emit("start_stream");
  }
  add_stream_control_handler(element); // consider moving to stream_started and stream_stopped events to reset event listener
}

socket.on("stream_started", function() {
  stream_running = true;
  get_new_data();
});

socket.on("stream_stopped", function() {
  stream_running = false;
});

socket.on("new_data", function(data) {
  console.log(data);
  get_new_data();
});

function get_new_data() {
  socket.emit("get_new_data");
}

// socket.on("extrema", function(data) {
//   console.log(data);
// });
