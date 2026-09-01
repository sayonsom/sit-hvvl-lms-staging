import assert from "node:assert/strict";
import test from "node:test";

import {
  calculateCockcroftWalton,
  calculateTransientRecoveryVoltage,
  getExperimentCalculator,
  supportedExperimentCalculators,
} from "../src/simulations/experimentCalculators.mjs";

test("all five published experiment calculators are bundled", () => {
  assert.equal(supportedExperimentCalculators.length, 5);
  for (const filename of supportedExperimentCalculators) {
    assert.equal(typeof getExperimentCalculator(`folder/${filename}`), "function");
  }
});

test("Cockcroft-Walton default output stays near the analytical 3-stage value", () => {
  const series = calculateCockcroftWalton({
    supplyVoltage: 220,
    loadCurrent: 0.1,
    stageCapacitance: 0.1,
    acFrequency: 50,
    numberOfStages: 3,
  });
  assert.equal(series.x.length, 501);
  const mean = series.y.reduce((sum, value) => sum + value, 0) / series.y.length;
  assert.ok(mean > 1319 && mean < 1320, `unexpected mean output ${mean}`);
});

test("TRV uses the RLC initial-current response and millisecond inputs", () => {
  const args = {
    resistance: 10,
    inductance: 0.005,
    capacitance: 0.000001,
    initialCurrent: 1,
    timeStep: 0.001,
    totalTime: 0.3,
  };
  const series = calculateTransientRecoveryVoltage(args);
  assert.equal(series.x[0], 0);
  assert.equal(series.y[0], 0);
  assert.equal(series.x[1], 1);

  const alpha = args.resistance / (2 * args.inductance);
  const dampedFrequency = Math.sqrt(1 / (args.inductance * args.capacitance) - alpha ** 2);
  const timeSeconds = 1e-6;
  const expectedKv = (
    args.initialCurrent
    / (args.capacitance * dampedFrequency)
    * Math.exp(-alpha * timeSeconds)
    * Math.sin(dampedFrequency * timeSeconds)
  ) / 1000;
  assert.ok(Math.abs(series.y[1] - expectedKv) < 1e-12);
  assert.ok(Math.max(...series.y) > 0.06 && Math.max(...series.y) < 0.07);
});

test("unknown calculators fail closed instead of rendering a blank experiment", () => {
  assert.throws(
    () => getExperimentCalculator("unknown.js"),
    /supported simulation calculator/,
  );
});
