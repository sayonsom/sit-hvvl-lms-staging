const MAX_POINTS = 2001;

function numberArg(args, name, { min = -Infinity, allowZero = true } = {}) {
  const value = Number(args?.[name]);
  const belowMinimum = allowZero ? value < min : value <= min;
  if (!Number.isFinite(value) || belowMinimum) {
    throw new Error(`${name} must be a finite ${allowZero ? "number" : "positive number"}.`);
  }
  return value;
}

function sampleTimes(total, step) {
  if (!Number.isFinite(total) || !Number.isFinite(step) || total <= 0 || step <= 0) {
    throw new Error("Simulation duration and time step must be positive.");
  }
  const requestedPoints = Math.floor(total / step) + 1;
  const pointCount = Math.max(2, Math.min(MAX_POINTS, requestedPoints));
  const effectiveStep = total / (pointCount - 1);
  return Array.from({ length: pointCount }, (_, index) => index * effectiveStep);
}

function assertSeries(series) {
  if (!series || !Array.isArray(series.x) || !Array.isArray(series.y) || series.x.length !== series.y.length) {
    throw new Error("The simulation returned an invalid series.");
  }
  if (series.x.length < 2 || series.x.some((value) => !Number.isFinite(value)) || series.y.some((value) => !Number.isFinite(value))) {
    throw new Error("The simulation returned non-finite values.");
  }
  return series;
}

export function calculateImpulseVoltage(args) {
  const chargingVoltage = numberArg(args, "chargingVoltage", { min: 0, allowZero: false }) * 1000;
  const groundCapacitance = numberArg(args, "groundCapacitance", { min: 0, allowZero: false }) * 1e-6;
  const tailCapacitance = numberArg(args, "tailCapacitance", { min: 0, allowZero: false }) * 1e-6;
  const frontResistance = numberArg(args, "frontResistance", { min: 0, allowZero: false });
  const tailResistance = numberArg(args, "tailResistance", { min: 0, allowZero: false });
  const timeStepUs = numberArg(args, "timeStep", { min: 0, allowZero: false });
  const totalTimeUs = numberArg(args, "totalTime", { min: 0, allowZero: false });

  let slowTimeConstant = tailResistance * groundCapacitance;
  let fastTimeConstant = frontResistance * tailCapacitance;
  if (fastTimeConstant > slowTimeConstant) {
    [slowTimeConstant, fastTimeConstant] = [fastTimeConstant, slowTimeConstant];
  }
  if (Math.abs(slowTimeConstant - fastTimeConstant) < Number.EPSILON) {
    fastTimeConstant *= 0.999;
  }

  const alpha = 1 / slowTimeConstant;
  const beta = 1 / fastTimeConstant;
  const peakTime = Math.log(beta / alpha) / (beta - alpha);
  const unscaledPeak = Math.exp(-alpha * peakTime) - Math.exp(-beta * peakTime);
  const efficiency = groundCapacitance / (groundCapacitance + tailCapacitance);
  const normalization = unscaledPeak > 0 ? 1 / unscaledPeak : 1;
  const timesUs = sampleTimes(totalTimeUs, timeStepUs);

  return assertSeries({
    x: timesUs.map((timeUs) => timeUs * 1e-6),
    y: timesUs.map((timeUs) => {
      const timeSeconds = timeUs * 1e-6;
      return efficiency * chargingVoltage * normalization
        * (Math.exp(-alpha * timeSeconds) - Math.exp(-beta * timeSeconds));
    }),
  });
}

export function calculateCockcroftWalton(args) {
  const supplyVoltage = numberArg(args, "supplyVoltage", { min: 0, allowZero: false });
  const loadCurrent = numberArg(args, "loadCurrent", { min: 0 }) * 1e-6;
  const stageCapacitance = numberArg(args, "stageCapacitance", { min: 0, allowZero: false }) * 1e-6;
  const frequency = numberArg(args, "acFrequency", { min: 0, allowZero: false });
  const stages = numberArg(args, "numberOfStages", { min: 0, allowZero: false });

  const idealOutput = 2 * stages * supplyVoltage;
  const loadFactor = loadCurrent / (frequency * stageCapacitance);
  const voltageDrop = loadFactor
    * ((2 * Math.pow(stages, 3)) / 3 + Math.pow(stages, 2) / 2 - stages / 6);
  const rippleAmplitude = loadFactor * (stages * (stages + 1)) / 2;
  const loadedOutput = idealOutput - voltageDrop;
  const points = 501;

  return assertSeries({
    x: Array.from({ length: points }, (_, index) => index),
    y: Array.from({ length: points }, (_, index) => {
      const phase = ((index / (points - 1)) * 5) % 1;
      return loadedOutput + rippleAmplitude * (1 - 2 * phase);
    }),
  });
}

export function calculateFerrantiEffect(args) {
  const sendingEndVoltage = numberArg(args, "sendingEndVoltage", { min: 0, allowZero: false });
  const lineLength = numberArg(args, "lineLength", { min: 0, allowZero: false });
  const capacitancePerKm = numberArg(args, "capacitancePerKm", { min: 0, allowZero: false }) * 1e-9;
  const inductancePerKm = numberArg(args, "inductancePerKm", { min: 0, allowZero: false }) * 1e-3;
  const resistancePerKm = numberArg(args, "resistancePerKm", { min: 0 });
  const frequency = numberArg(args, "frequency", { min: 0, allowZero: false });
  const angularFrequency = 2 * Math.PI * frequency;
  const points = 101;
  const x = [];
  const y = [];

  for (let index = 0; index < points; index += 1) {
    const distance = (lineLength * index) / (points - 1);
    x.push(distance);
    if (distance === 0) {
      y.push(sendingEndVoltage);
      continue;
    }

    const impedanceReal = resistancePerKm;
    const impedanceImaginary = angularFrequency * inductancePerKm;
    const admittanceImaginary = angularFrequency * capacitancePerKm;
    const productReal = -impedanceImaginary * admittanceImaginary;
    const productImaginary = impedanceReal * admittanceImaginary;
    const productMagnitude = Math.hypot(productReal, productImaginary);
    const productAngle = Math.atan2(productImaginary, productReal);
    const gammaMagnitude = Math.sqrt(productMagnitude);
    const attenuation = gammaMagnitude * Math.cos(productAngle / 2);
    const phase = gammaMagnitude * Math.sin(productAngle / 2);
    const a = attenuation * distance;
    const b = phase * distance;
    const coshMagnitude = Math.hypot(Math.cosh(a) * Math.cos(b), Math.sinh(a) * Math.sin(b));
    y.push(sendingEndVoltage / coshMagnitude);
  }

  return assertSeries({ x, y });
}

export function calculatePartialDischarge(args) {
  const cableType = Math.round(numberArg(args, "typeOfCable", { min: 1 }));
  const loadingCondition = numberArg(args, "loadingCondition", { min: 0 });
  const timeStep = numberArg(args, "timeStep", { min: 0, allowZero: false });
  const totalTime = numberArg(args, "totalTime", { min: 0, allowZero: false });
  const cableProperties = {
    1: { attenuation: 0.02, threshold: 0.7 },
    2: { attenuation: 0.05, threshold: 0.5 },
    3: { attenuation: 0.035, threshold: 0.6 },
  }[cableType] || { attenuation: 0.035, threshold: 0.6 };
  const loadFactor = 1 + (loadingCondition / 100) * 0.5;
  let seed = Math.round(cableType * 1000 + loadingCondition * 10);
  const random = () => {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
  };
  const eventCount = Math.min(20, Math.max(3, Math.floor(totalTime * 50)));
  const events = Array.from({ length: eventCount }, (_, index) => ({
    time: ((index + 0.5) * totalTime) / eventCount,
    magnitude: (0.3 + 0.7 * random()) * loadFactor * cableProperties.threshold,
    decay: cableProperties.attenuation * (500 + 500 * random()),
  }));
  const x = sampleTimes(totalTime, timeStep);
  const y = x.map((time) => events.reduce((voltage, event) => {
    const elapsed = time - event.time;
    if (elapsed < 0 || elapsed >= totalTime * 0.1) return voltage;
    return voltage + event.magnitude * Math.exp(-event.decay * elapsed)
      * Math.sin(2 * Math.PI * 1000 * elapsed);
  }, 0));

  return assertSeries({ x, y });
}

export function calculateTransientRecoveryVoltage(args) {
  const resistance = numberArg(args, "resistance", { min: 0 });
  const inductance = numberArg(args, "inductance", { min: 0, allowZero: false });
  const capacitance = numberArg(args, "capacitance", { min: 0, allowZero: false });
  const initialCurrent = numberArg(args, "initialCurrent", { min: 0 });
  const timeStepMs = numberArg(args, "timeStep", { min: 0, allowZero: false });
  const totalTimeMs = numberArg(args, "totalTime", { min: 0, allowZero: false });
  const timesMs = sampleTimes(totalTimeMs, timeStepMs);
  const alpha = resistance / (2 * inductance);
  const naturalFrequency = 1 / Math.sqrt(inductance * capacitance);
  const discriminant = naturalFrequency * naturalFrequency - alpha * alpha;

  const voltageAt = (timeSeconds) => {
    if (discriminant > Number.EPSILON) {
      const dampedFrequency = Math.sqrt(discriminant);
      return (initialCurrent / (capacitance * dampedFrequency))
        * Math.exp(-alpha * timeSeconds)
        * Math.sin(dampedFrequency * timeSeconds);
    }
    if (Math.abs(discriminant) <= Number.EPSILON) {
      return (initialCurrent / capacitance) * timeSeconds * Math.exp(-alpha * timeSeconds);
    }
    const root = Math.sqrt(-discriminant);
    const firstPole = -alpha + root;
    const secondPole = -alpha - root;
    return (initialCurrent / capacitance)
      * (Math.exp(firstPole * timeSeconds) - Math.exp(secondPole * timeSeconds))
      / (firstPole - secondPole);
  };

  return assertSeries({
    x: timesMs.map((timeMs) => timeMs * 1000),
    y: timesMs.map((timeMs) => voltageAt(timeMs * 1e-3) / 1000),
  });
}

const calculatorsByFile = new Map([
  ["exp1_impulsevoltagegenerator.js", calculateImpulseVoltage],
  ["exp2_cockroftwalton.js", calculateCockcroftWalton],
  ["exp3_ferranti.js", calculateFerrantiEffect],
  ["exp4_partialdischarge.js", calculatePartialDischarge],
  ["exp5_transientvoltage.js", calculateTransientRecoveryVoltage],
]);

export function getExperimentCalculator(computePath) {
  const filename = String(computePath || "").split("/").pop().toLowerCase();
  const calculator = calculatorsByFile.get(filename);
  if (!calculator) {
    throw new Error("This experiment does not have a supported simulation calculator.");
  }
  return calculator;
}

export const supportedExperimentCalculators = Object.freeze(
  Array.from(calculatorsByFile.keys()),
);
