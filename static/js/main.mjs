import { Deque } from "./Deque.mjs";

const socket =  io.connect(location.origin);
const stream_control_button = document.getElementById("start");
const canvas = document.getElementById("plot");
const max_len = 240;

var stream_running = false;
var deque = new Deque(max_len);

deque.plot(canvas);
add_stream_control_handler(stream_control_button);

function add_stream_control_handler(element) {
  element.addEventListener("click", function() {
      control_stream();
    }, {once: true});
}

function control_stream() {
  if (stream_running) {
    socket.emit("stop_stream");
  } else {
    socket.emit("start_stream");
  }
}

socket.on("stream_started", function() {
  stream_running = true;
  stream_control_button.innerHTML = "Stop";
  add_stream_control_handler(stream_control_button);
});

socket.on("stream_stopped", function() {
  stream_running = false;
  stream_control_button.innerHTML = "Start";
  add_stream_control_handler(stream_control_button);
});

socket.on("new_data", function(data) {
  console.log(data.data);
  deque.push(data.data);
  deque.plot(canvas);
});
