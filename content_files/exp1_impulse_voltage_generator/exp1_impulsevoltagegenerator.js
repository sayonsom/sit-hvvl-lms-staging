/**
 * Impulse Voltage Generator Simulation
 * Computes the V-t curve for a standard impulse voltage waveform.
 * Uses the double-exponential model: V(t) = k * V0 * (exp(-alpha*t) - exp(-beta*t))
 */
(function () {
  window.MyLibrary = window.MyLibrary || {};

  window.MyLibrary.calculate = function (args) {
    var V0 = args.chargingVoltage * 1000; // kV to V
    var Cg = args.groundCapacitance * 1e-6; // µF to F
    var C1 = args.tailCapacitance * 1e-6; // µF to F
    var Rf = args.frontResistance; // Ω
    var Rt = args.tailResistance; // Ω
    var dt = args.timeStep; // µs
    var totalTime = args.totalTime; // µs

    // Equivalent circuit parameters
    var R1 = Rf;
    var R2 = Rt;
    var C_g = Cg;
    var C_1 = C1;

    // Time constants
    var tau1 = R2 * C_g; // tail time constant
    var tau2 = R1 * C_1; // front time constant

    // Ensure tau1 > tau2 for proper waveform
    if (tau2 > tau1) {
      var temp = tau1;
      tau1 = tau2;
      tau2 = temp;
    }

    var alpha = 1.0 / (tau1 * 1e6); // per µs
    var beta = 1.0 / (tau2 * 1e6); // per µs

    // Efficiency factor
    var eta = C_g / (C_g + C_1);

    // Normalization factor so peak = eta * V0
    var k = 1.0 / (Math.exp((-alpha * tau2 * 1e6 * Math.log(beta / alpha)) / (beta - alpha)) -
      Math.exp((-beta * tau2 * 1e6 * Math.log(beta / alpha)) / (beta - alpha)));
    if (!isFinite(k) || isNaN(k)) {
      k = 1.0;
    }

    var x = [];
    var y = [];
    var steps = Math.floor(totalTime / dt);
    if (steps > 10000) steps = 10000;

    for (var i = 0; i <= steps; i++) {
      var t = i * dt; // µs
      var voltage = eta * V0 * k * (Math.exp(-alpha * t) - Math.exp(-beta * t));
      x.push(t * 1e-6); // convert to seconds
      y.push(voltage);
    }

    return { x: x, y: y };
  };
})();
