
// setup socket
var socket =  io.connect(location.origin);
var stream_running = false;

document.getElementById("start").addEventListener("click", start_stream);

function start_stream() {
  console.log("Stream control requested...");
  if (stream_running) {
    stream_running = false;
    socket.emit("stop_stream");
  } else {
    stream_running = true;
    socket.emit("start_stream");
  }
}

// socket test
socket.on("data", function(data) {
  for (let point in data.buffer) {
      // console.log(data.buffer);
  }
});


socket.on("extrema", function(data) {
  console.log(data.point);
});
