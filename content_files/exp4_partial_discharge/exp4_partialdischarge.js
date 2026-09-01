/**
 * Partial Discharge Simulation
 * Simulates PD pulse propagation in a cable under different conditions.
 * Models the apparent charge vs time for PD events.
 */
(function () {
  window.MyLibrary = window.MyLibrary || {};

  window.MyLibrary.calculate = function (args) {
    var cableType = Math.round(args.typeOfCable); // 1=XLPE, 2=PVC, 3=Other
    var loadPercent = args.loadingCondition; // %
    var dt = args.timeStep; // seconds
    var totalTime = args.totalTime; // seconds

    // Cable properties based on type
    var attenuationFactor, propagationSpeed, pdThreshold;
    switch (cableType) {
      case 1: // XLPE
        attenuationFactor = 0.02;
        propagationSpeed = 1.7e8; // m/s
        pdThreshold = 0.7;
        break;
      case 2: // PVC
        attenuationFactor = 0.05;
        propagationSpeed = 1.5e8;
        pdThreshold = 0.5;
        break;
      default: // Other
        attenuationFactor = 0.035;
        propagationSpeed = 1.6e8;
        pdThreshold = 0.6;
        break;
    }

    // Loading effect on PD magnitude
    var loadFactor = 1.0 + (loadPercent / 100) * 0.5;

    var x = [];
    var y = [];
    var steps = Math.floor(totalTime / dt);
    if (steps > 10000) steps = 10000;

    // Simulate PD pulses as damped oscillations at specific times
    var pdEvents = [];
    var numEvents = Math.max(3, Math.floor(totalTime * 50)); // ~50 events per second
    if (numEvents > 20) numEvents = 20;

    for (var e = 0; e < numEvents; e++) {
      pdEvents.push({
        time: (e + 0.5) * totalTime / numEvents,
        magnitude: (0.3 + 0.7 * Math.random()) * loadFactor * pdThreshold,
        decay: attenuationFactor * (500 + 500 * Math.random())
      });
    }

    // Use seeded pseudo-random for reproducibility
    var seed = Math.round(cableType * 1000 + loadPercent * 10);
    function seededRandom() {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
    }

    // Regenerate events with seeded random
    pdEvents = [];
    for (var e2 = 0; e2 < numEvents; e2++) {
      pdEvents.push({
        time: (e2 + 0.5) * totalTime / numEvents,
        magnitude: (0.3 + 0.7 * seededRandom()) * loadFactor * pdThreshold,
        decay: attenuationFactor * (500 + 500 * seededRandom())
      });
    }

    for (var i = 0; i <= steps; i++) {
      var t = i * dt;
      var voltage = 0;

      for (var j = 0; j < pdEvents.length; j++) {
        var ev = pdEvents[j];
        var tdiff = t - ev.time;
        if (tdiff >= 0 && tdiff < totalTime * 0.1) {
          // Damped oscillation pulse
          voltage += ev.magnitude * Math.exp(-ev.decay * tdiff) *
            Math.sin(2 * Math.PI * 1000 * tdiff);
        }
      }

      x.push(t);
      y.push(voltage);
    }

    return { x: x, y: y };
  };
})();
