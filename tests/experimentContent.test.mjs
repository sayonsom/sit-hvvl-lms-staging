import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { getExperimentCalculator } from "../src/simulations/experimentCalculators.mjs";

const configPaths = [
  "content_files/exp1_impulse_voltage_generator/exp1_impulse_voltage_generator_config.json",
  "content_files/exp2_3stage_cockroft_walton/exp2_cockroft_walton.json",
  "content_files/exp3_ferranti_effect/exp3_ferranti_config.json",
  "content_files/exp4_partial_discharge/exp4_partial_discharge_config.json",
  "content_files/exp5_transient_recovery_voltage/exp5_transientvoltage_config.json",
];

test("every published experiment config produces a finite default series", async () => {
  for (const path of configPaths) {
    const config = JSON.parse(await readFile(new URL(`../${path}`, import.meta.url), "utf8"));
    const calculator = getExperimentCalculator(config.compute);
    const defaults = Object.fromEntries(
      Object.entries(config.variables).map(([name, definition]) => [name, definition.initial]),
    );
    const result = calculator(defaults);
    assert.equal(result.x.length, result.y.length, path);
    assert.ok(result.x.length > 1, path);
    assert.ok(result.x.every(Number.isFinite), path);
    assert.ok(result.y.every(Number.isFinite), path);
  }
});

test("experiment UI does not inject remote compute scripts", async () => {
  const source = await readFile(
    new URL("../src/components/ExperimentFormParameteric.jsx", import.meta.url),
    "utf8",
  );
  assert.doesNotMatch(source, /createElement\(['"]script['"]\)/);
  assert.doesNotMatch(source, /window\.MyLibrary/);
  assert.match(source, /Experiment unavailable/);
  assert.match(source, /Retry/);
});

test("TRV missing storage asset is replaced by the bundled apparatus", async () => {
  const source = await readFile(
    new URL("../src/components/ModuleViewer.jsx", import.meta.url),
    "utf8",
  );
  assert.match(source, /highvoltage_trv/);
  assert.match(source, /TransientRecoveryVoltageModel/);
  assert.match(source, /Circuit breaker TRV test arrangement/);
});
