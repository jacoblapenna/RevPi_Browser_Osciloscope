"use strict";

export function Deque(max_len) {
  this.max_len = max_len;
  this.length = 0;
  this.first = null;
  this.last = null;
}

Deque.prototype.Node = function(val, next, prev) {
  this.val = val;
  this.next = next;
  this.prev = prev;
};

Deque.prototype.push = function(val) {
  if (this.length == this.max_len) {
    this.pop();
  }
  const node_to_push = new this.Node(val, null, this.last);
  if (this.last) {
    this.last.next = node_to_push;
  } else {
    this.first = node_to_push;
  }
  this.last = node_to_push;
  this.length++;
};

Deque.prototype.pop = function () {
  if (this.length) {
    let val = this.first.val;
    this.first = this.first.next;
    if (this.first) {
      this.first.prev = null;
    } else {
      this.last = null;
    }
    this.length--;
    return val;
  } else {
    return null;
  }
};

Deque.prototype.to_string = function() {
  if (this.length) {
    var str = "[";
    var present_node = this.first;
    while (present_node) {
      if (present_node.next) {
        str += `${present_node.val}, `;
      } else {
        str += `${present_node.val}`
      }
      present_node = present_node.next;
    }
    str += "]";
    return str
  } else {
    return "[]";
  }
};

Deque.prototype.plot = function(canvas) {
  const w = canvas.width;
  const h = canvas.height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, w, h);
  //Draw vertical gridlines
  ctx.beginPath();
  ctx.setLineDash([2]);
  ctx.strokeStyle = "rgb(124, 124, 124)";
  for (var i = 1; i < 9; i++) {
    ctx.moveTo(i * w/9, 0);
    ctx.lineTo(i * w/9, h);
  }
  //Draw horizontal gridlines
  for (var i = 1; i < 10; i++) {
    ctx.moveTo(0, i * h/10);
    ctx.lineTo(w, i * h/10);
  }
  ctx.stroke();
  ctx.closePath();
  if (this.length) {
    var present_node = this.first;
    var x = 0;
    ctx.setLineDash([]);
    ctx.strokeStyle = "rgb(255, 51, 51)";
    ctx.beginPath();
    ctx.moveTo(x, h - present_node.val * (h/10));
    while (present_node) {
      ctx.lineTo(x * w/9, h - present_node.val * (h/10));
      x++;
      present_node = present_node.next;
    }
    ctx.stroke();
    ctx.closePath();
  }
};
