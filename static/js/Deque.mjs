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
  //Draw x-axis
	ctx.strokeStyle = "rgb(124, 124, 124)";
	ctx.beginPath();
	ctx.moveTo(0, h/2);
	ctx.lineTo(w, h/2);
	ctx.stroke();
	ctx.closePath();
  //Draw vertical gridlines
	ctx.beginPath();
	ctx.setLineDash([2]);
	ctx.strokeStyle = "rgb(124, 124, 124)";
	for (var i = 1; i < 5; i++) {
		ctx.moveTo(i * w/5, 0);
		ctx.lineTo(i * w/5, h);
	}
  //Draw horizontal gridlines
	for (var i = 1; i < 6; i++) {
		if (i != 3) {
			ctx.moveTo(0, i * h/6);
			ctx.lineTo(w, i * h/6);
		}
	}
  ctx.stroke();
  ctx.closePath();
  if (this.length) {
    const dt = w/this.max_len;
    var t = 0;
    var present_node = this.first;
    ctx.setLineDash([]);
    ctx.strokeStyle = "rgb(25, 255, 25)";
    ctx.beginPath();
    ctx.moveTo(0, (h/2) - present_node.val);
    while (present_node) {
      ctx.lineTo(t * dt, (h/2) - present_node.val);
      t++;
      present_node = present_node.next;
    }
    ctx.stroke();
    ctx.closePath();
  }
};
