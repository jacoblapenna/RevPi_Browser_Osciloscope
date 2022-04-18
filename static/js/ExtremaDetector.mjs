"use strict;"

export function ExtremaDetector(max_len) {
  this.max_len = max_len;
  this.length = 0;
  this.first = null;
  this.last = null;
  // this.extrema_detector = ExtremaDetector(0.01);
}
// export function ExtremaDetector(threshold) {
//   this.threshold = threshold;
//   this.mn = Infinity;
//   this.mx = -Infinity;
//   this.look_for_maxima = true;
// }
//
// ExtremaDetector.prototype.check_value = function(val) {
//   if (val < this.mn) {
//     self._mn = val;
//   }
//   if (val > this.mx) {
//     this.mx = val;
//   }
//   if (this.look_for_maxima) {
//     if (val < this.mx - this.threshold) {
//       this.mn = val;
//       this.look_for_maxima = false;
//       return true;
//     }
//   } else {
//     if (val > this.mn + this.threshold) {
//       this.mx = val;
//       this.look_for_maxima = true;
//       return true;
//     }
//   }
//   return false;
// };
