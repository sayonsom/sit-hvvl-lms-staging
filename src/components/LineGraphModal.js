'use client';

import { Button, Modal } from 'flowbite-react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';

function numericSeries(xValues = [], yValues = []) {
  return xValues
    .slice(0, yValues.length)
    .map((xValue, index) => [Number(xValue), Number(yValues[index])])
    .filter(([xValue, yValue]) => Number.isFinite(xValue) && Number.isFinite(yValue));
}

function formatAxisValue(value) {
  const magnitude = Math.abs(value);
  if (magnitude === 0) return '0';
  if (magnitude >= 100) return String(Math.round(value));
  if (magnitude >= 1) return Number(value.toFixed(2)).toString();
  if (magnitude >= 0.01) return Number(value.toFixed(3)).toString();
  return value.toExponential(2);
}

export default function LineGraphModal({
  openModal,
  setOpenModal,
  xAxis,
  yAxis,
  previousXAxis,
  previousYAxis,
  previousSettingsLabel,
  xAxisLabel,
  yAxisLabel,
  title,
}) {
    const series = [
      {
        name: yAxisLabel,
        data: numericSeries(xAxis, yAxis),
      },
    ];
    const comparisonData = numericSeries(previousXAxis, previousYAxis);
    if (comparisonData.length > 0) {
      series.push({ name: previousSettingsLabel || 'Previous run', data: comparisonData });
    }

    return (
      <>

        <Modal show={openModal} onClose={() => setOpenModal(false)}>
          <Modal.Header>Experiment Output</Modal.Header>
          <Modal.Body>
            <HighchartsReact
              highcharts={Highcharts}
              options={{
                title: {
                  text: title,
                },
                credits: {
                    enabled: false,
                    },
                exporting: {
                  enabled: true,
                },
                xAxis: {
                  type: 'linear',
                  title: {
                    text: xAxisLabel,
                  },
                  labels: {
                    formatter() {
                      return formatAxisValue(this.value);
                    },
                  },
                },
                yAxis: {
                  title: {
                    text: yAxisLabel,
                  },
                },
                tooltip: {
                  shared: true,
                  valueDecimals: 4,
                },
                series,
              }}
            />
          </Modal.Body>
          <Modal.Footer>
            <Button onClick={() => setOpenModal(false)}>Okay</Button>
          </Modal.Footer>
        </Modal>
      </>
    );
  }
