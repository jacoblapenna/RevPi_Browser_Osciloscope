
// setup socket
var socket =  io.connect(location.origin);
var stream_running = false;
var control_button = document.getElementById("start");

control_button.addEventListener("click", function(e) {
  console.log(`Stream control requested...`);
  if (stream_running) {
    stream_running = false;
    // socket.emit("stop_stream");
  } else {
    stream_running = true;
    // socket.emit("start_stream");
  }
  await new Promise(resolve => setTimeout(resolve, 1000));
});

// socket test
socket.on("data", function(data) {
  for (let point in data.buffer) {
      // console.log(data.buffer);
  }
});


socket.on("extrema", function(data) {
  console.log(data.point);
});
