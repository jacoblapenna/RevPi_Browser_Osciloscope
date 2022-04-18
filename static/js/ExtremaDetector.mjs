"use strict;"

export function ExtremaDetector(threshold) {
  this.threshold = threshold;
  this.mn = Infinity;
  this.mx = -Infinity;
  this.look_for_maxima = true;
}

ExtremaDetector.prototype.check_value = function(val) {
  if (val < this.mn) {
    this.mn = val;
  }
  if (val > this.mx) {
    this.mx = val;
  }
  if (this.look_for_maxima) {
    if (val < this.mx - this.threshold) {
      this.mn = val;
      this.look_for_maxima = false;
      return true;
    }
  } else {
    if (val > this.mn + this.threshold) {
      this.mx = val;
      this.look_for_maxima = true;
      return true;
    }
  }
  return false;
};
