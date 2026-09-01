import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Button, Label, Spinner, TextInput } from 'flowbite-react';
import axios from 'axios';
import LineGraphModal from './LineGraphModal';
import { API_URL } from "../env";
import { getExperimentCalculator } from '../simulations/experimentCalculators.mjs';

function resolveContentUrl(fileUrl) {
  if (!fileUrl || typeof window === 'undefined') return fileUrl || '';
  try {
    const apiOrigin = new URL(API_URL || window.location.origin, window.location.origin).origin;
    return new URL(fileUrl, apiOrigin).toString();
  } catch (_error) {
    return fileUrl;
  }
}

function validateConfig(config) {
  if (!config || typeof config !== 'object' || !config.variables || !config.output_plot || !config.compute) {
    throw new Error('The experiment configuration is incomplete.');
  }
  return config;
}

const ExperimentFormParameteric = ({ url }) => {
  const [config, setConfig] = useState(null);
  const [calculator, setCalculator] = useState(null);
  const [variables, setVariables] = useState({});
  const [chartData, setChartData] = useState({ xAxis: [], yAxis: [] });
  const [yAxisLabel, setYAxisLabel] = useState('');
  const [previousData, setPreviousData] = useState({ xAxis: [], yAxis: [] });
  const [previousSettingsLabel, setPreviousSettingsLabel] = useState('');
  const [openModal, setOpenModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [simulationError, setSimulationError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  const fetchConfig = useCallback(async (signal) => {
    if (!url) {
      throw new Error('No experiment configuration is assigned to this module.');
    }

    const signedUrlResponse = await axios.get(`${API_URL}/generate-signed-url/`, {
      params: { blob_name: url },
      signal,
    });
    const configResponse = await fetch(resolveContentUrl(signedUrlResponse.data.url), { signal });
    if (!configResponse.ok) {
      throw new Error(`The experiment configuration could not be loaded (${configResponse.status}).`);
    }

    const configData = validateConfig(await configResponse.json());
    const resolvedCalculator = getExperimentCalculator(configData.compute);
    setConfig(configData);
    setCalculator(() => resolvedCalculator);
    setVariables(Object.fromEntries(
      Object.entries(configData.variables).map(([key, definition]) => [key, definition.initial]),
    ));
  }, [url]);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setLoadError('');
    setSimulationError('');
    setConfig(null);
    setCalculator(null);

    fetchConfig(controller.signal)
      .catch((error) => {
        if (error?.name !== 'AbortError' && error?.code !== 'ERR_CANCELED') {
          console.error('Experiment configuration failed to load', error);
          setLoadError(error?.message || 'The experiment could not be loaded.');
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false);
      });

    return () => controller.abort();
  }, [fetchConfig, reloadKey]);

  const handleInputChange = (name, value) => {
    setVariables((previous) => ({ ...previous, [name]: value }));
  };

  const handleCompute = () => {
    setSimulationError('');
    try {
      if (!calculator || !config) {
        throw new Error('The simulation calculator is not ready yet.');
      }

      const label = Object.entries(variables)
        .map(([key, value]) => `${config.variables[key].variableLabel} = ${value}`)
        .join(', ');
      const result = calculator({ ...variables });

      setPreviousSettingsLabel(yAxisLabel);
      setYAxisLabel(label);
      setPreviousData({ xAxis: chartData.xAxis, yAxis: chartData.yAxis });
      setChartData({ xAxis: result.x, yAxis: result.y });
      setOpenModal(true);
    } catch (error) {
      console.error('Experiment calculation failed', error);
      setSimulationError(error?.message || 'The simulation could not be calculated.');
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-48 items-center justify-center gap-3 text-gray-600" data-testid="experiment-loading">
        <Spinner size="sm" />
        <span>Loading experiment…</span>
      </div>
    );
  }

  if (loadError) {
    return (
      <Alert color="failure" data-testid="experiment-error">
        <div className="flex flex-col items-start gap-3">
          <div>
            <span className="font-semibold">Experiment unavailable.</span>{' '}
            {loadError}
          </div>
          <Button size="xs" color="failure" onClick={() => setReloadKey((key) => key + 1)}>
            Retry
          </Button>
        </div>
      </Alert>
    );
  }

  return (
    <form
      data-testid="experiment-form"
      onSubmit={(event) => {
        event.preventDefault();
        handleCompute();
      }}
    >
      <div className="space-y-4">
        {Object.keys(config.variables).map((key) => {
          const variableConfig = config.variables[key];
          return (
            <div key={key}>
              <div className="mb-2 block">
                <Label htmlFor={key} value={variableConfig.variableLabel} />
              </div>
              <TextInput
                id={key}
                type="number"
                value={variables[key]}
                onChange={(event) => handleInputChange(key, Number(event.target.value))}
                min={variableConfig.min}
                max={variableConfig.max}
                step={variableConfig.step || 'any'}
                helperText={variableConfig.variableDescription}
                required
              />
            </div>
          );
        })}
      </div>

      {simulationError ? (
        <Alert color="failure" className="mt-4" data-testid="simulation-error">
          {simulationError}
        </Alert>
      ) : null}

      <Button className="mt-5" type="submit" outline gradientDuoTone="pinkToOrange">
        Start Experiment
      </Button>
      <LineGraphModal
        openModal={openModal}
        setOpenModal={setOpenModal}
        xAxis={chartData.xAxis}
        yAxis={chartData.yAxis}
        previousXAxis={previousData.xAxis}
        previousYAxis={previousData.yAxis}
        xAxisLabel={config.output_plot.xAxisLabel}
        yAxisLabel={config.output_plot.yAxisLabel}
        previousSettingsLabel={previousSettingsLabel}
        title={config.output_plot.title}
      />
    </form>
  );
};

export default ExperimentFormParameteric;
