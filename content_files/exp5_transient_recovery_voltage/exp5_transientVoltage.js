/**
 * Transient Recovery Voltage (TRV) Simulation
 * Models the voltage across a circuit breaker after fault interruption.
 * Uses the zero-input series-RLC capacitor response for an initial inductor current.
 */
(function () {
  window.MyLibrary = window.MyLibrary || {};

  window.MyLibrary.calculate = function (args) {
    var R = args.resistance; // Ω
    var L = args.inductance; // H
    var C = args.capacitance; // F
    var I0 = args.initialCurrent; // A
    var dt = args.timeStep * 1e-3; // milliseconds to seconds
    var totalTime = args.totalTime * 1e-3; // milliseconds to seconds

    // Natural frequency and damping
    var omega0 = 1.0 / Math.sqrt(L * C);
    var alpha = R / (2 * L);
    var omega_d_sq = omega0 * omega0 - alpha * alpha;

    var x = [];
    var y = [];
    var steps = Math.floor(totalTime / dt);
    if (steps > 10000) steps = 10000;

    if (omega_d_sq > 0) {
      // Underdamped case (oscillatory TRV)
      var omega_d = Math.sqrt(omega_d_sq);
      for (var i = 0; i <= steps; i++) {
        var t = i * dt;
        var voltage = (I0 / (C * omega_d)) * Math.exp(-alpha * t) * Math.sin(omega_d * t);
        x.push(t * 1e6); // convert to µs for display
        y.push(voltage / 1000); // convert to kV
      }
    } else if (omega_d_sq === 0) {
      // Critically damped
      for (var i2 = 0; i2 <= steps; i2++) {
        var t2 = i2 * dt;
        var voltage2 = (I0 / C) * t2 * Math.exp(-alpha * t2);
        x.push(t2 * 1e6);
        y.push(voltage2 / 1000);
      }
    } else {
      // Overdamped
      var s1 = -alpha + Math.sqrt(alpha * alpha - omega0 * omega0);
      var s2 = -alpha - Math.sqrt(alpha * alpha - omega0 * omega0);
      for (var i3 = 0; i3 <= steps; i3++) {
        var t3 = i3 * dt;
        var voltage3 = (I0 / C) * (Math.exp(s1 * t3) - Math.exp(s2 * t3)) / (s1 - s2);
        x.push(t3 * 1e6);
        y.push(voltage3 / 1000);
      }
    }

    return { x: x, y: y };
  };
})();
