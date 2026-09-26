/**
 * EcoAir Intelligence — Chart.js Visualization Engine
 * High-performance canvas charting for historical trends,
 * multi-step neural forecast trajectories with 95% confidence bounds,
 * and pollutant breakdowns.
 */

const ChartEngine = {
  instances: {},

  isMobile() {
    return window.innerWidth <= 768 || document.body.classList.contains('mobile-preview-active');
  },

  resizeAll() {
    Object.values(this.instances).forEach(inst => {
      if (inst && typeof inst.resize === 'function') {
        inst.resize();
      }
    });
  },

  _destroyExisting(canvasId) {
    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
      delete this.instances[canvasId];
    }
  },

  /**
   * Renders 24-hour historical air quality trajectory.
   */
  renderHistoricalChart(canvasId, records = []) {
    this._destroyExisting(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const labels = records.map(r => {
      const dt = new Date(r.timestamp);
      return isNaN(dt.getTime()) ? r.timestamp.split('T')[1]?.substring(0, 5) || r.timestamp : `${dt.getHours()}:00`;
    });
    const aqiData = records.map(r => r.aqi);
    const pm25Data = records.map(r => r.pm25);
    const mobile = this.isMobile();

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Overall AQI',
            data: aqiData,
            borderColor: '#f59e0b',
            backgroundColor: 'rgba(245, 158, 11, 0.08)',
            fill: true,
            tension: 0.35,
            borderWidth: mobile ? 2 : 2.5,
            pointRadius: mobile ? 1.5 : 2.5,
            pointHoverRadius: 5
          },
          {
            label: 'PM2.5 (µg/m³)',
            data: pm25Data,
            borderColor: '#38bdf8',
            backgroundColor: 'transparent',
            borderDash: [4, 4],
            borderWidth: mobile ? 1.4 : 1.8,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        layout: {
          padding: { left: mobile ? 2 : 8, right: mobile ? 6 : 14, top: 4, bottom: 4 }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#0f172a',
              boxWidth: mobile ? 10 : 14,
              padding: mobile ? 8 : 12,
              font: { family: 'Inter', size: mobile ? 10 : 11 }
            }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            titleColor: '#f8fafc',
            bodyColor: '#ffffff',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            padding: mobile ? 8 : 10
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(0, 0, 0, 0.04)' },
            ticks: {
              color: '#0f172a',
              font: { family: 'Inter', size: mobile ? 8.5 : 10 },
              maxTicksLimit: mobile ? 6 : 12,
              maxRotation: 0,
              autoSkip: true
            }
          },
          y: {
            grid: { color: 'rgba(0, 0, 0, 0.04)' },
            ticks: {
              color: '#0f172a',
              font: { family: 'Inter', size: mobile ? 8.5 : 10 },
              maxTicksLimit: mobile ? 5 : 8
            }
          }
        }
      }
    });
  },

  /**
   * Renders unified 72-hour timeline:
   *   - Past 24h   → historical AQI records (blue solid line)
   *   - NOW marker → vertical annotation dividing past from future
   *   - Next 24h   → GRU/LSTM forecast trajectory + 95% CI band (teal)
   *
   * @param {string}   canvasId  - Canvas element id
   * @param {object}   forecast  - API forecast response
   * @param {Array}    history   - Array of {timestamp, aqi} historical records (24 items)
   */
  renderForecastChart(canvasId, forecast, history = []) {
    this._destroyExisting(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const now = new Date();

    // ── Build past 24h labels + data ────────────────────────────────────────
    const histCount = Math.min(history.length, 24);
    const pastLabels = [];
    const pastAQI    = [];

    if (histCount > 0) {
      history.slice(-histCount).forEach((r, i) => {
        const dt = r.timestamp ? new Date(r.timestamp) : new Date(now - (histCount - i) * 3600000);
        const hh = dt.getHours().toString().padStart(2, '0');
        const mm = dt.getMinutes().toString().padStart(2, '0');
        pastLabels.push(`${hh}:${mm}`);
        pastAQI.push(parseFloat(r.aqi) || null);
      });
    } else {
      // Synthesise past labels if no history available
      for (let i = 24; i >= 1; i--) {
        const t = new Date(now - i * 3600000);
        pastLabels.push(`${t.getHours().toString().padStart(2,'0')}:00`);
        pastAQI.push(null);
      }
    }

    // ── Build next 24h forecast labels + data ───────────────────────────────
    const horizon     = forecast.horizon_hours || forecast.aqi_trajectory.length;
    const trajectory  = forecast.aqi_trajectory.slice(0, horizon);
    const upperBounds = (forecast.confidence_intervals || []).map(ci => ci.upper_bound).slice(0, horizon);
    const lowerBounds = (forecast.confidence_intervals || []).map(ci => ci.lower_bound).slice(0, horizon);

    const futureLabels = [];
    for (let i = 1; i <= horizon; i++) {
      const t = new Date(now.getTime() + i * 3600000);
      futureLabels.push(`${t.getHours().toString().padStart(2,'0')}:00`);
    }

    // ── Unified axis: [past24] + ["NOW"] + [future24] ───────────────────────
    const nowLabel   = '▼ NOW';
    const allLabels  = [...pastLabels, nowLabel, ...futureLabels];
    const pastLen    = pastLabels.length;
    const nowIdx     = pastLen;           // index of "NOW" marker
    const totalLen   = allLabels.length;

    // Pad past data to full length (nulls for future)
    const histDataset = new Array(totalLen).fill(null);
    pastAQI.forEach((v, i) => { histDataset[i] = v; });
    // Bridge: connect last historical point into NOW slot for visual continuity
    if (pastAQI.length > 0 && pastAQI[pastAQI.length - 1] !== null) {
      histDataset[nowIdx] = pastAQI[pastAQI.length - 1];
    }

    // Pad forecast data to full length (nulls for past)
    const forecastDataset = new Array(totalLen).fill(null);
    const upperDataset    = new Array(totalLen).fill(null);
    const lowerDataset    = new Array(totalLen).fill(null);

    // Bridge: start forecast from NOW slot
    if (histDataset[nowIdx] !== null) {
      forecastDataset[nowIdx] = histDataset[nowIdx];
    }
    trajectory.forEach((v, i)  => { forecastDataset[nowIdx + 1 + i] = v; });
    upperBounds.forEach((v, i) => { upperDataset[nowIdx + 1 + i]    = v; });
    lowerBounds.forEach((v, i) => { lowerDataset[nowIdx + 1 + i]    = v; });

    // Bridge CI band to NOW
    if (upperBounds.length > 0 && forecastDataset[nowIdx] !== null) {
      upperDataset[nowIdx] = forecastDataset[nowIdx];
      lowerDataset[nowIdx] = forecastDataset[nowIdx];
    }

    // Current AQI reference (dashed horizontal line across full chart)
    const currentAQI = parseFloat(forecast.current_aqi) || null;
    const currentLine = new Array(totalLen).fill(currentAQI);

    const mobile = this.isMobile();

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels: allLabels,
        datasets: [
          // ── CI Upper band ──
          {
            label: 'Upper 95% CI',
            data: upperDataset,
            borderColor: 'transparent',
            backgroundColor: 'rgba(56, 189, 248, 0.10)',
            fill: '+1',
            pointRadius: 0,
            tension: 0.3,
            spanGaps: false
          },
          // ── CI Lower band ──
          {
            label: 'Lower 95% CI',
            data: lowerDataset,
            borderColor: 'transparent',
            backgroundColor: 'transparent',
            fill: false,
            pointRadius: 0,
            tension: 0.3,
            spanGaps: false
          },
          // ── Past 24h Historical ──
          {
            label: 'Historical AQI (Past 24h)',
            data: histDataset,
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.08)',
            fill: false,
            borderWidth: mobile ? 2 : 2.5,
            pointRadius: (ctx) => ctx.dataIndex === nowIdx ? 0 : (mobile ? 1.5 : 3),
            pointBackgroundColor: '#6366f1',
            pointBorderColor: '#0a0e17',
            pointBorderWidth: 1.5,
            pointHoverRadius: 5,
            tension: 0.35,
            spanGaps: true
          },
          // ── GRU Forecast Trajectory ──
          {
            label: `${forecast.architecture || 'GRU'} Forecast (Next 24h)`,
            data: forecastDataset,
            borderColor: '#2dd4bf',
            backgroundColor: 'rgba(45, 212, 191, 0.12)',
            fill: false,
            borderWidth: mobile ? 2.4 : 3,
            borderDash: [],
            pointRadius: (ctx) => ctx.dataIndex === nowIdx ? 0 : (mobile ? 2 : 3.5),
            pointBackgroundColor: '#2dd4bf',
            pointBorderColor: '#0a0e17',
            pointBorderWidth: 1.5,
            pointHoverRadius: 6,
            tension: 0.35,
            spanGaps: false
          },
          // ── Current AQI reference line ──
          {
            label: `Current AQI (${Math.round(currentAQI || 0)})`,
            data: currentLine,
            borderColor: 'rgba(251, 191, 36, 0.50)',
            backgroundColor: 'transparent',
            borderWidth: 1.5,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false,
            tension: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        layout: {
          padding: { left: mobile ? 2 : 6, right: mobile ? 6 : 14, top: 4, bottom: 4 }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              filter: item => !['Upper 95% CI', 'Lower 95% CI'].includes(item.text),
              color: '#1e293b',
              font: { family: 'Inter', size: mobile ? 9.5 : 11 },
              boxWidth: mobile ? 10 : 14,
              padding: mobile ? 6 : 12
            }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            titleColor: '#f8fafc',
            bodyColor: '#ffffff',
            borderColor: 'rgba(56, 189, 248, 0.3)',
            borderWidth: 1,
            padding: mobile ? 8 : 10,
            callbacks: {
              label: function(context) {
                if (context.parsed.y === null) return null;
                return `${context.dataset.label}: ${context.parsed.y.toFixed(1)} AQI`;
              },
              title: function(items) {
                const lbl = items[0]?.label || '';
                return lbl === '▼ NOW' ? '🕐 Now (Current Reading)' : lbl;
              }
            }
          },
          annotation: undefined
        },
        scales: {
          x: {
            grid: { color: 'rgba(0, 0, 0, 0.04)' },
            ticks: {
              color: (ctx) => ctx.tick?.label === '▼ NOW' ? '#d97706' : '#1e293b',
              font: (ctx) => ctx.tick?.label === '▼ NOW'
                ? { family: 'Inter', size: mobile ? 9 : 10, weight: '700' }
                : { family: 'Inter', size: mobile ? 8 : 9 },
              maxRotation: 0,
              maxTicksLimit: mobile ? 6 : 14,
              autoSkip: true
            }
          },
          y: {
            grid: { color: 'rgba(0, 0, 0, 0.04)' },
            ticks: { color: '#0f172a', font: { family: 'Inter', size: mobile ? 8.5 : 10 }, maxTicksLimit: 5 },
            title: {
              display: !mobile,
              text: 'AQI',
              color: '#1e293b',
              font: { family: 'Inter', size: 10 }
            }
          }
        }
      },
      plugins: [{
        // Draw a golden vertical "NOW" divider line
        id: 'nowLine',
        afterDraw(chart) {
          const xScale = chart.scales.x;
          const meta = chart.getDatasetMeta(2); // historical dataset
          if (!meta || !xScale) return;
          const nowPx = xScale.getPixelForValue(nowIdx);
          if (!nowPx || isNaN(nowPx)) return;
          const { ctx, chartArea } = chart;
          ctx.save();
          ctx.beginPath();
          ctx.setLineDash([6, 4]);
          ctx.strokeStyle = 'rgba(217, 119, 6, 0.85)';
          ctx.lineWidth = 2;
          ctx.moveTo(nowPx, chartArea.top);
          ctx.lineTo(nowPx, chartArea.bottom);
          ctx.stroke();
          // Label
          ctx.setLineDash([]);
          ctx.fillStyle = '#b45309';
          ctx.font = 'bold 9px Inter, sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText('NOW', nowPx, chartArea.top + 11);
          ctx.restore();
        }
      }]
    });
  },

  /**
   * Renders multi-pollutant trajectory breakdown (PM2.5, PM10, NO2).
   */
  renderPollutantForecastChart(canvasId, breakdown = {}) {
    this._destroyExisting(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    const len = (breakdown.pm25 || []).length;
    const labels = Array.from({ length: len }, (_, i) => `+${i + 1}h`);
    const mobile = this.isMobile();

    this.instances[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'PM2.5 (µg/m³)',
            data: breakdown.pm25 || [],
            borderColor: '#f43f5e',
            backgroundColor: 'transparent',
            borderWidth: mobile ? 1.6 : 2,
            tension: 0.3,
            pointRadius: mobile ? 1 : 2
          },
          {
            label: 'PM10 (µg/m³)',
            data: breakdown.pm10 || [],
            borderColor: '#fb923c',
            backgroundColor: 'transparent',
            borderWidth: mobile ? 1.6 : 2,
            tension: 0.3,
            pointRadius: mobile ? 1 : 2
          },
          {
            label: 'NO2 (µg/m³)',
            data: breakdown.no2 || [],
            borderColor: '#a855f7',
            backgroundColor: 'transparent',
            borderWidth: mobile ? 1.6 : 2,
            tension: 0.3,
            pointRadius: mobile ? 1 : 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { left: mobile ? 2 : 6, right: mobile ? 6 : 14, top: 2, bottom: 2 }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              color: '#0f172a',
              boxWidth: mobile ? 10 : 14,
              padding: mobile ? 6 : 12,
              font: { family: 'Inter', size: mobile ? 9.5 : 11 }
            }
          },
          tooltip: {
            backgroundColor: '#0f172a',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            padding: mobile ? 8 : 10
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(0, 0, 0, 0.04)' },
            ticks: {
              color: '#0f172a',
              font: { family: 'Inter', size: mobile ? 8.5 : 10 },
              maxTicksLimit: mobile ? 6 : 12,
              autoSkip: true
            }
          },
          y: {
            grid: { color: 'rgba(0, 0, 0, 0.04)' },
            ticks: { color: '#0f172a', font: { family: 'Inter', size: mobile ? 8.5 : 10 }, maxTicksLimit: 5 }
          }
        }
      }
    });
  },

  /**
   * Renders station comparison horizontal bar chart with clean light theme styling,
   * high-contrast typography, and detailed tooltips.
   */
  renderStationComparisonChart(canvasId, stations, metric = 'aqi') {
    this._destroyExisting(canvasId);
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    let rawList = [];
    if (Array.isArray(stations)) {
      rawList = stations;
    } else if (stations && typeof stations === 'object') {
      rawList = Object.entries(stations).map(([id, s]) => ({
        station_id: id,
        station_name: id.replace(/_\d+$/, '').replace(/_/g, ' '),
        aqi: s.aqi || 0,
        pm25: s.pm25 || 0,
        pm10: s.pm10 || 0,
        no2: s.no2 || 0,
        dominant_pollutant: s.dominant_pollutant || 'PM2.5',
        category: s.category || 'Moderate'
      }));
    }

    if (rawList.length === 0) return;

    const list = rawList.map(item => {
      const aqi = Math.round(item.aqi || 0);
      let color = '#10b981';
      if (aqi > 250) color = '#7c3aed';
      else if (aqi > 200) color = '#dc2626';
      else if (aqi > 150) color = '#ef4444';
      else if (aqi > 100) color = '#f97316';
      else if (aqi > 50) color = '#f59e0b';

      let val = aqi;
      let valLabel = `${aqi} AQI`;
      if (metric === 'pm25') {
        val = parseFloat(item.pm25 || 0);
        valLabel = `${val} µg/m³`;
      } else if (metric === 'pm10') {
        val = parseFloat(item.pm10 || 0);
        valLabel = `${val} µg/m³`;
      }

      // Format clean station name
      let cleanName = item.station_name || item.name || 'Station';
      cleanName = cleanName.replace(/_\d+$/, '')
        .replace(/Square/g, ' Sq')
        .replace(/Bus_stand/g, 'Bus Stn')
        .replace(/Station/g, ' Stn')
        .replace(/Road/g, ' Rd')
        .replace(/Gadital/g, ' Gadital')
        .replace(/_/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

      return {
        ...item,
        name: cleanName,
        val: val,
        valLabel: valLabel,
        aqi: aqi,
        color: color
      };
    }).sort((a, b) => b.val - a.val);

    const mobile = this.isMobile();

    this.instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: list.map(item => item.name),
        datasets: [{
          label: metric === 'pm25' ? 'PM2.5 Concentration' : metric === 'pm10' ? 'PM10 Concentration' : 'Current AQI',
          data: list.map(item => item.val),
          backgroundColor: list.map(item => item.color),
          borderRadius: 4,
          borderWidth: 0,
          barThickness: mobile ? 11 : 16
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: { left: 2, right: mobile ? 8 : 16, top: 2, bottom: 2 }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0f172a',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            titleFont: { family: 'Inter', size: mobile ? 11 : 12, weight: '700' },
            bodyFont: { family: 'Inter', size: mobile ? 10 : 11 },
            padding: mobile ? 8 : 10,
            cornerRadius: 6,
            callbacks: {
              label: (context) => {
                const item = list[context.dataIndex];
                if (!item) return `AQI: ${context.raw}`;
                return [
                  `Current AQI: ${item.aqi} (${item.category || 'Moderate'})`,
                  `PM2.5: ${item.pm25 || '--'} µg/m³  |  Dominant: ${item.dominant_pollutant || 'PM2.5'}`
                ];
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              color: 'rgba(0, 0, 0, 0.05)',
              drawBorder: false
            },
            ticks: {
              color: '#1e293b',
              font: { family: 'Inter', size: mobile ? 8.5 : 10 },
              maxTicksLimit: 5
            }
          },
          y: {
            grid: { display: false, drawBorder: false },
            ticks: {
              color: '#1e293b',
              font: { family: 'Inter', size: mobile ? 9 : 11, weight: '600' }
            }
          }
        }
      }
    });
  }
};
