
// setup socket
var socket =  io.connect(location.origin);
var stream_started = false;

document.getElementById("start").addEventListener("click", start_stream);

function start_stream() {
  if (!stream_started) {
    stream_started = true;
    socket.emit("start_stream");
  }
}

// socket test
socket.on("data", function(data) {
  for (let point in data.buffer) {
      console.log(data.buffer);
  }
});
