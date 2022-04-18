"use strict";

export function ExtremaDetector() {
  this.mx = Infinity;
  this.mx = -Infinity;
  this.threshold = 0.01;
  this.look_for_maxima = true;
}

ExtremaDetector.prototype.check_value = function(val) {
  if (val < this.mn) {
    self._mn = val;
  }
  if (val > this.mx) {
    this.mx = val;
  }
  if (this.look_for_maxima) {
    if (val < this.mx - this.threshold) {
      this.mn = val;
      this.look_for_maxima = false;
      return true;
  } else {
    if (val > this.mn + this.threshold) {
      this.mx = val;
      this.look_for_maxima = true;
      return true;
  }
  return false;
};
