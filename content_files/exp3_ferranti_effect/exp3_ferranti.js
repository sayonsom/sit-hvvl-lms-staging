/**
 * Ferranti Effect Simulation
 * Computes the receiving end voltage vs distance for a long transmission line.
 * Uses the exact long-line equations with distributed parameters.
 */
(function () {
  window.MyLibrary = window.MyLibrary || {};

  window.MyLibrary.calculate = function (args) {
    var Vs = args.sendingEndVoltage; // V
    var totalLength = args.lineLength; // km
    var c_per_km = args.capacitancePerKm * 1e-9; // nF/km to F/km
    var l_per_km = args.inductancePerKm * 1e-3; // mH/km to H/km
    var r_per_km = args.resistancePerKm; // Ω/km
    var freq = args.frequency; // Hz
    var omega = 2 * Math.PI * freq;

    var x = [];
    var y = [];
    var steps = 100;
    var dx = totalLength / steps;

    for (var i = 0; i <= steps; i++) {
      var d = i * dx; // distance in km

      // Distributed line parameters
      var R = r_per_km * d;
      var L = l_per_km * d;
      var C = c_per_km * d;

      if (d === 0) {
        x.push(0);
        y.push(Vs);
        continue;
      }

      // Characteristic impedance and propagation constant
      // Z = sqrt((R + jwL) / (jwC))
      // gamma = sqrt((R + jwL) * jwC)
      var z_real = r_per_km;
      var z_imag = omega * l_per_km;
      var y_real = 0;
      var y_imag = omega * c_per_km;

      // gamma = sqrt(z * y) where z = R + jwL per km, y = jwC per km
      // z*y = (z_real + j*z_imag) * (y_real + j*y_imag)
      var zy_real = z_real * y_real - z_imag * y_imag;
      var zy_imag = z_real * y_imag + z_imag * y_real;

      // sqrt of complex number
      var zy_mag = Math.sqrt(zy_real * zy_real + zy_imag * zy_imag);
      var zy_angle = Math.atan2(zy_imag, zy_real);
      var gamma_mag = Math.sqrt(zy_mag);
      var gamma_angle = zy_angle / 2;

      var gamma_real = gamma_mag * Math.cos(gamma_angle); // attenuation per km
      var gamma_imag = gamma_mag * Math.sin(gamma_angle); // phase per km

      // For no-load (open circuit receiving end):
      // Vr = Vs / cosh(gamma * d)
      // |cosh(a + jb)| = sqrt(cosh²(a)*cos²(b) + sinh²(a)*sin²(b))
      var a = gamma_real * d;
      var b = gamma_imag * d;

      var cosh_real = Math.cosh(a) * Math.cos(b);
      var cosh_imag = Math.sinh(a) * Math.sin(b);
      var cosh_mag = Math.sqrt(cosh_real * cosh_real + cosh_imag * cosh_imag);

      var Vr = Vs / cosh_mag;

      x.push(d);
      y.push(Vr);
    }

    return { x: x, y: y };
  };
})();
