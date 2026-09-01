/**
 * Cockcroft-Walton Voltage Multiplier Simulation
 * Computes the output voltage, ripple voltage, and voltage drop under load.
 */
(function () {
  window.MyLibrary = window.MyLibrary || {};

  window.MyLibrary.calculate = function (args) {
    var Vs = args.supplyVoltage; // V (peak)
    var Il = args.loadCurrent * 1e-6; // µA to A
    var C = args.stageCapacitance * 1e-6; // µF to F
    var f = args.acFrequency; // Hz
    var n = args.numberOfStages; // number of stages

    // Ideal no-load output voltage
    var Vout_ideal = 2 * n * Vs;

    // Voltage drop under load: ΔV = Il/(f*C) * (2n³/3 + n²/2 - n/6)
    var voltageDrop = (Il / (f * C)) * ((2 * Math.pow(n, 3) / 3) + (Math.pow(n, 2) / 2) - (n / 6));

    // Ripple voltage: δV = Il/(f*C) * n(n+1)/2
    var rippleAmplitude = (Il / (f * C)) * (n * (n + 1) / 2);

    // Output voltage under load
    var Vout = Vout_ideal - voltageDrop;

    // Generate time-domain ripple waveform
    var periods = 5;
    var totalTime = periods / f;
    var steps = 500;
    var dt_val = totalTime / steps;

    var x = [];
    var y = [];

    for (var i = 0; i <= steps; i++) {
      var t = i * dt_val;
      // Simulate ripple as sawtooth-like on top of DC output
      var phase = (t * f) % 1.0; // normalized phase within one cycle
      var ripple = rippleAmplitude * (1 - 2 * phase); // triangular ripple approximation
      var voltage = Vout + ripple;
      x.push(i);
      y.push(voltage);
    }

    return { x: x, y: y };
  };
})();
