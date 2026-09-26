/**
 * AirSense AI — React.js Mobile Components (Milestone 3)
 * Implements React 18 functional components with hooks for:
 * - Personal AQI Exposure History
 * - Notification Preferences Management
 * - Mobile PWA Status & Controls
 */

(function () {
  'use strict';

  const { useState, useEffect, useCallback, useMemo } = React;

  // ─────────────────────────────────────────────────────────────────────────────
  // 1. Personal Exposure History (React Component)
  // ─────────────────────────────────────────────────────────────────────────────
  function ReactExposureHistory() {
    const [trips, setTrips] = useState([]);
    const [filterMode, setFilterMode] = useState('all');
    const [isOnline, setIsOnline] = useState(navigator.onLine);

    // Sync with storage on mount and window focus
    const loadTrips = useCallback(() => {
      try {
        const stored = localStorage.getItem('airsense_exposure_history');
        if (stored) {
          setTrips(JSON.parse(stored));
        } else {
          // Default initial trip if empty
          const sample = [
            {
              id: 1711200000001,
              date: new Date(Date.now() - 3600000 * 4).toISOString(),
              origin: 'Kothrud Depot, Pune',
              destination: 'Hinjawadi Phase 1, Pune',
              mode: 'Car',
              avgAqi: 74,
              exposureUg: 36.5,
              exposureScore: 42,
              category: 'Moderate',
              durationMin: 32,
              distanceKm: 16.4,
              recommendation: 'Use Route C for 18% lower particulate intake.'
            }
          ];
          localStorage.setItem('airsense_exposure_history', JSON.stringify(sample));
          setTrips(sample);
        }
      } catch (e) {
        console.error('[ReactExposureHistory] Storage error:', e);
      }
    }, []);

    useEffect(() => {
      loadTrips();

      const handleOnline = () => setIsOnline(true);
      const handleOffline = () => setIsOnline(false);
      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    }, [loadTrips]);

    // Delete a single trip
    const handleDeleteTrip = (id) => {
      const updated = trips.filter((t) => t.id !== id);
      setTrips(updated);
      localStorage.setItem('airsense_exposure_history', JSON.stringify(updated));
      if (window.App && window.App.showToast) {
        window.App.showToast('Journey removed from history', 'info');
      }
    };

    // Clear all history
    const handleClearAll = () => {
      if (window.confirm('Are you sure you want to clear your entire exposure history?')) {
        setTrips([]);
        localStorage.removeItem('airsense_exposure_history');
        if (window.App && window.App.showToast) {
          window.App.showToast('All journey history cleared', 'info');
        }
      }
    };

    // Export CSV
    const handleExportCSV = () => {
      if (trips.length === 0) return;
      const headers = ['Date', 'Origin', 'Destination', 'Mode', 'Distance (km)', 'Duration (min)', 'Avg AQI', 'Category', 'Exposure (ug)', 'Score (0-100)'];
      const rows = trips.map((r) => [
        `"${new Date(r.date).toLocaleString('en-IN')}"`,
        `"${r.origin}"`,
        `"${r.destination}"`,
        `"${r.mode}"`,
        r.distanceKm,
        r.durationMin,
        r.avgAqi,
        `"${r.category}"`,
        r.exposureUg,
        r.exposureScore
      ]);
      const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `airsense_exposure_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    };

    // Calculate aggregated metrics
    const stats = useMemo(() => {
      if (trips.length === 0) return { count: 0, avgAqi: '--', totalUg: '0', bestAqi: '--' };
      const avgAqi = Math.round(trips.reduce((acc, t) => acc + (t.avgAqi || 0), 0) / trips.length);
      const totalUg = Math.round(trips.reduce((acc, t) => acc + (t.exposureUg || 0), 0));
      const bestAqi = Math.min(...trips.map((t) => t.avgAqi || 999));
      return { count: trips.length, avgAqi, totalUg, bestAqi: bestAqi === 999 ? '--' : bestAqi };
    }, [trips]);

    // Filtered list
    const filteredTrips = useMemo(() => {
      if (filterMode === 'all') return trips;
      return trips.filter((t) => (t.mode || '').toLowerCase() === filterMode.toLowerCase());
    }, [trips, filterMode]);

    const getAqiColor = (val) => {
      if (val <= 50) return '#10b981';
      if (val <= 100) return '#f59e0b';
      if (val <= 150) return '#f97316';
      if (val <= 200) return '#ef4444';
      return '#8b5cf6';
    };

    const getModeIcon = (mode) => {
      const m = (mode || '').toLowerCase();
      if (m.includes('car')) return '🚗';
      if (m.includes('bus') || m.includes('public')) return '🚌';
      if (m.includes('motor') || m.includes('bike')) return '🏍️';
      if (m.includes('cycl')) return '🚲';
      if (m.includes('walk')) return '🚶';
      return '📍';
    };

    return React.createElement(
      'div',
      { className: 'react-exposure-history-wrapper', style: { padding: '24px' } },

      // Header row
      React.createElement(
        'div',
        { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' } },
        React.createElement(
          'div',
          null,
          React.createElement('h2', { style: { fontSize: '1.35rem', fontWeight: 800, color: '#0f172a', margin: '0 0 4px' } }, 'Personal AQI Exposure History'),
          React.createElement('p', { style: { color: '#64748b', fontSize: '0.86rem', margin: 0 } }, 'React 18 Component — Tracks cumulative personal pollution exposure across your urban journeys.')
        ),
        React.createElement(
          'div',
          { style: { display: 'flex', gap: '10px', alignItems: 'center' } },
          React.createElement(
            'div',
            { className: `pwa-status-bar ${isOnline ? 'online' : 'offline'}`, style: { display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 12px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: 600, background: isOnline ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', color: isOnline ? '#059669' : '#dc2626' } },
            React.createElement('span', { style: { width: '8px', height: '8px', borderRadius: '50%', background: isOnline ? '#10b981' : '#ef4444' } }),
            isOnline ? 'PWA Online' : 'Offline Cached'
          ),
          trips.length > 0 &&
            React.createElement(
              'button',
              { className: 'export-csv-btn', onClick: handleExportCSV, style: { display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '8px 14px', borderRadius: '8px', border: '1px solid #cbd5e1', background: '#ffffff', color: '#1e293b', fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer' } },
              '📥 Export CSV'
            )
        )
      ),

      // Stats KPI Grid
      React.createElement(
        'div',
        { className: 'exposure-stats-grid', style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '14px', marginBottom: '22px' } },
        React.createElement(
          'div',
          { className: 'exposure-stat-card', style: { background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '16px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' } },
          React.createElement('div', { style: { fontSize: '1.6rem', fontWeight: 800, color: '#2563eb' } }, stats.count),
          React.createElement('div', { style: { fontSize: '0.76rem', color: '#64748b', fontWeight: 600, marginTop: '4px' } }, 'Journeys Logged')
        ),
        React.createElement(
          'div',
          { className: 'exposure-stat-card', style: { background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '16px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' } },
          React.createElement('div', { style: { fontSize: '1.6rem', fontWeight: 800, color: getAqiColor(stats.avgAqi || 75) } }, stats.avgAqi),
          React.createElement('div', { style: { fontSize: '0.76rem', color: '#64748b', fontWeight: 600, marginTop: '4px' } }, 'Mean Journey AQI')
        ),
        React.createElement(
          'div',
          { className: 'exposure-stat-card', style: { background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '16px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' } },
          React.createElement('div', { style: { fontSize: '1.6rem', fontWeight: 800, color: '#7c3aed' } }, `${stats.totalUg} µg`),
          React.createElement('div', { style: { fontSize: '0.76rem', color: '#64748b', fontWeight: 600, marginTop: '4px' } }, 'Total PM Inhaled')
        ),
        React.createElement(
          'div',
          { className: 'exposure-stat-card', style: { background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '16px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' } },
          React.createElement('div', { style: { fontSize: '1.6rem', fontWeight: 800, color: '#059669' } }, stats.bestAqi),
          React.createElement('div', { style: { fontSize: '0.76rem', color: '#64748b', fontWeight: 600, marginTop: '4px' } }, 'Cleanest Trip AQI')
        )
      ),

      // Mode filter bar
      React.createElement(
        'div',
        { style: { display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap', marginBottom: '20px' } },
        React.createElement('span', { style: { fontSize: '0.78rem', fontWeight: 700, color: '#475569', marginRight: '6px' } }, 'Filter Transit:'),
        ['all', 'Car', 'Public Transport', 'Motorcycle', 'Cycling', 'Walking'].map((mode) =>
          React.createElement(
            'button',
            {
              key: mode,
              onClick: () => setFilterMode(mode),
              style: {
                padding: '6px 14px',
                borderRadius: '20px',
                border: filterMode === mode ? '1.5px solid #2563eb' : '1px solid #e2e8f0',
                background: filterMode === mode ? 'rgba(37,99,235,0.08)' : '#ffffff',
                color: filterMode === mode ? '#1d4ed8' : '#475569',
                fontSize: '0.78rem',
                fontWeight: filterMode === mode ? 700 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }
            },
            mode === 'all' ? 'All Transit' : `${getModeIcon(mode)} ${mode}`
          )
        ),
        trips.length > 0 &&
          React.createElement(
            'button',
            { onClick: handleClearAll, style: { marginLeft: 'auto', padding: '6px 12px', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.2)', background: 'transparent', color: '#dc2626', fontSize: '0.76rem', fontWeight: 600, cursor: 'pointer' } },
            '🗑 Clear History'
          )
      ),

      // Timeline / Journey Cards
      filteredTrips.length === 0
        ? React.createElement(
            'div',
            { style: { textAlign: 'center', padding: '48px 20px', background: '#f8fafc', borderRadius: '12px', border: '1px dashed #cbd5e1' } },
            React.createElement('div', { style: { fontSize: '2.5rem', marginBottom: '10px' } }, '🗺️'),
            React.createElement('h3', { style: { fontSize: '1rem', color: '#1e293b', margin: '0 0 6px' } }, filterMode !== 'all' ? 'No journeys match this filter' : 'No journeys logged yet'),
            React.createElement('p', { style: { color: '#64748b', fontSize: '0.82rem', margin: 0 } }, 'Use the Route Exposure Estimator tab to plan a route, then click "Save Route to History" to track your exposure.')
          )
        : React.createElement(
            'div',
            { style: { display: 'flex', flexDirection: 'column', gap: '12px' } },
            filteredTrips.map((r) => {
              const color = getAqiColor(r.avgAqi);
              const dateStr = new Date(r.date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
              const timeStr = new Date(r.date).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
              return React.createElement(
                'div',
                {
                  key: r.id,
                  style: {
                    display: 'flex',
                    alignItems: 'center',
                    gap: '16px',
                    padding: '16px',
                    background: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderLeft: `4px solid ${color}`,
                    borderRadius: '10px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.03)',
                    position: 'relative',
                    flexWrap: 'wrap'
                  }
                },
                // AQI circle badge
                React.createElement(
                  'div',
                  { style: { width: '52px', height: '52px', borderRadius: '10px', background: `${color}15`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flexShrink: 0 } },
                  React.createElement('span', { style: { fontSize: '1.25rem', fontWeight: 800, color, lineHeight: 1 } }, r.avgAqi),
                  React.createElement('span', { style: { fontSize: '0.62rem', fontWeight: 700, color, marginTop: '2px' } }, 'AQI')
                ),
                // Trip info
                React.createElement(
                  'div',
                  { style: { flex: 1, minWidth: '200px' } },
                  React.createElement('div', { style: { fontSize: '0.92rem', fontWeight: 700, color: '#0f172a', marginBottom: '4px' } }, `${r.origin.split(',')[0]} → ${r.destination.split(',')[0]}`),
                  React.createElement(
                    'div',
                    { style: { display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center', fontSize: '0.74rem', color: '#64748b' } },
                    React.createElement('span', { style: { background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 } }, `${getModeIcon(r.mode)} ${r.mode}`),
                    React.createElement('span', null, `📅 ${dateStr} at ${timeStr}`),
                    React.createElement('span', null, `📍 ${r.distanceKm} km`),
                    React.createElement('span', null, `⏱ ${r.durationMin} min`),
                    React.createElement('span', { style: { color, fontWeight: 700 } }, r.category)
                  )
                ),
                // Exposure score
                React.createElement(
                  'div',
                  { style: { textAlign: 'right', flexShrink: 0 } },
                  React.createElement('div', { style: { fontSize: '0.68rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 700 } }, 'Exposure'),
                  React.createElement('div', { style: { fontSize: '1.1rem', fontWeight: 800, color } }, `${r.exposureUg} µg`),
                  React.createElement('div', { style: { fontSize: '0.68rem', color: '#94a3b8' } }, `Score: ${r.exposureScore}/100`)
                ),
                // Delete button
                React.createElement(
                  'button',
                  {
                    onClick: () => handleDeleteTrip(r.id),
                    title: 'Remove trip',
                    style: { background: 'none', border: 'none', color: '#94a3b8', fontSize: '1rem', cursor: 'pointer', padding: '4px 8px', borderRadius: '4px' }
                  },
                  '✕'
                )
              );
            })
          )
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 2. Notification Preferences Management (React Component)
  // ─────────────────────────────────────────────────────────────────────────────
  function ReactNotificationPrefs() {
    const [prefs, setPrefs] = useState(() => {
      try {
        const stored = localStorage.getItem('airsense_notification_prefs');
        return stored
          ? JSON.parse(stored)
          : {
              aqiThreshold: 120,
              healthProfile: 'general',
              pushEnabled: false,
              alertRouteHazards: true,
              alertDailyDigest: true
            };
      } catch (e) {
        return {
          aqiThreshold: 120,
          healthProfile: 'general',
          pushEnabled: false,
          alertRouteHazards: true,
          alertDailyDigest: true
        };
      }
    });

    const [pushPermission, setPushPermission] = useState(
      typeof Notification !== 'undefined' ? Notification.permission : 'default'
    );

    // Save changes to localStorage
    const updatePref = (key, value) => {
      setPrefs((prev) => {
        const updated = { ...prev, [key]: value };
        localStorage.setItem('airsense_notification_prefs', JSON.stringify(updated));
        if (key === 'healthProfile' && window.App) {
          window.App.state.selectedHealthProfile = value;
        }
        return updated;
      });
      if (window.App && window.App.showToast) {
        window.App.showToast('Preference updated', 'info');
      }
    };

    // Push notification toggle
    const handlePushToggle = async () => {
      if (typeof Notification === 'undefined') {
        alert('Push notifications are not supported by this browser.');
        return;
      }

      if (prefs.pushEnabled) {
        updatePref('pushEnabled', false);
      } else {
        const perm = await Notification.requestPermission();
        setPushPermission(perm);
        if (perm === 'granted') {
          updatePref('pushEnabled', true);
          if (window.App && window.App.showToast) {
            window.App.showToast('Push notifications enabled for AQI alerts!', 'success');
          }
        } else {
          alert('Notification permission was denied. Please allow notifications in your browser settings.');
        }
      }
    };

    // Send a test notification
    const handleTestNotification = () => {
      if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
        new Notification('AirSense AI Alert (Test)', {
          body: `Test Alert: Current Pune AQI is ${prefs.aqiThreshold} (Threshold Breach Simulation). Wear an N95 mask.`,
          icon: '/static/manifest.json'
        });
      }
      if (window.App && window.App.showToast) {
        window.App.showToast('Simulated notification triggered!', 'success');
      }
    };

    const getThresholdColor = (val) => {
      if (val <= 50) return '#10b981';
      if (val <= 100) return '#f59e0b';
      if (val <= 150) return '#f97316';
      if (val <= 200) return '#ef4444';
      return '#8b5cf6';
    };

    const getThresholdLabel = (val) => {
      if (val <= 50) return 'Good (0–50)';
      if (val <= 100) return 'Moderate (51–100)';
      if (val <= 150) return 'Sensitive Groups (101–150)';
      if (val <= 200) return 'Unhealthy / Poor (151–200)';
      return 'Hazardous / Severe (201+)';
    };

    return React.createElement(
      'div',
      { className: 'react-notification-prefs-wrapper', style: { padding: '24px', maxWidth: '780px', margin: '0 auto' } },

      // Header
      React.createElement(
        'div',
        { style: { marginBottom: '24px' } },
        React.createElement('h2', { style: { fontSize: '1.35rem', fontWeight: 800, color: '#0f172a', margin: '0 0 6px' } }, 'Notification & Health Preferences'),
        React.createElement('p', { style: { color: '#64748b', fontSize: '0.86rem', margin: 0 } }, 'React 18 Component — Configure automated pollution threshold warnings and vulnerability adjustments.')
      ),

      // Card 1: AQI Threshold Slider
      React.createElement(
        'div',
        { style: { background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', marginBottom: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' } },
        React.createElement(
          'div',
          { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' } },
          React.createElement(
            'div',
            null,
            React.createElement('div', { style: { fontWeight: 700, color: '#0f172a', fontSize: '0.94rem' } }, 'AQI Hazard Alert Threshold'),
            React.createElement('div', { style: { fontSize: '0.78rem', color: '#64748b' } }, 'Receive an instant alert when ambient or route AQI exceeds this level.')
          ),
          React.createElement(
            'span',
            { style: { padding: '4px 12px', borderRadius: '12px', fontWeight: 800, fontSize: '0.9rem', color: '#ffffff', background: getThresholdColor(prefs.aqiThreshold) } },
            `${prefs.aqiThreshold} AQI`
          )
        ),
        React.createElement('input', {
          type: 'range',
          min: '50',
          max: '300',
          step: '5',
          value: prefs.aqiThreshold,
          onChange: (e) => updatePref('aqiThreshold', parseInt(e.target.value, 10)),
          style: { width: '100%', accentColor: getThresholdColor(prefs.aqiThreshold), cursor: 'pointer' }
        }),
        React.createElement(
          'div',
          { style: { display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#94a3b8', marginTop: '6px' } },
          React.createElement('span', null, '50 (Good)'),
          React.createElement('span', { style: { color: getThresholdColor(prefs.aqiThreshold), fontWeight: 700 } }, getThresholdLabel(prefs.aqiThreshold)),
          React.createElement('span', null, '300 (Severe)')
        )
      ),

      // Card 2: Health Vulnerability Profile
      React.createElement(
        'div',
        { style: { background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', marginBottom: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' } },
        React.createElement('div', { style: { fontWeight: 700, color: '#0f172a', fontSize: '0.94rem', marginBottom: '4px' } }, 'Health Profile & Inhalation Sensitivity'),
        React.createElement('p', { style: { fontSize: '0.78rem', color: '#64748b', margin: '0 0 14px' } }, 'Adjusts route inhalation scoring factor according to user physiological susceptibility.'),
        React.createElement(
          'div',
          { style: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' } },
          [
            { id: 'general', title: 'General Public', icon: '👤', desc: 'Standard ventilation (1.0×)' },
            { id: 'asthmatic', title: 'Asthmatic / Resp.', icon: '🫁', desc: 'High sensitivity (1.4×)' },
            { id: 'elderly', title: 'Senior Citizen', icon: '🧓', desc: 'Elevated risk (1.3×)' },
            { id: 'child', title: 'Children', icon: '🧒', desc: 'High inhalation rate (1.2×)' }
          ].map((profile) =>
            React.createElement(
              'div',
              {
                key: profile.id,
                onClick: () => updatePref('healthProfile', profile.id),
                style: {
                  padding: '12px',
                  borderRadius: '10px',
                  border: prefs.healthProfile === profile.id ? '2px solid #2563eb' : '1px solid #e2e8f0',
                  background: prefs.healthProfile === profile.id ? 'rgba(37,99,235,0.06)' : '#ffffff',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }
              },
              React.createElement('div', { style: { fontSize: '1.25rem', marginBottom: '4px' } }, profile.icon),
              React.createElement('div', { style: { fontSize: '0.84rem', fontWeight: 700, color: prefs.healthProfile === profile.id ? '#1d4ed8' : '#1e293b' } }, profile.title),
              React.createElement('div', { style: { fontSize: '0.72rem', color: '#64748b', marginTop: '2px' } }, profile.desc)
            )
          )
        )
      ),

      // Card 3: Alert Channels & Push Notification Toggle
      React.createElement(
        'div',
        { style: { background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '20px', marginBottom: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' } },
        React.createElement('div', { style: { fontWeight: 700, color: '#0f172a', fontSize: '0.94rem', marginBottom: '14px' } }, 'Push & In-App Notification Channels'),

        // Push toggle row
        React.createElement(
          'div',
          { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '14px', borderBottom: '1px solid #f1f5f9' } },
          React.createElement(
            'div',
            null,
            React.createElement('div', { style: { fontSize: '0.86rem', fontWeight: 600, color: '#1e293b' } }, 'Browser Web Push Notifications'),
            React.createElement('div', { style: { fontSize: '0.74rem', color: '#64748b' } }, `Permission: ${pushPermission}`)
          ),
          React.createElement(
            'button',
            {
              onClick: handlePushToggle,
              style: {
                padding: '6px 16px',
                borderRadius: '20px',
                border: 'none',
                background: prefs.pushEnabled ? '#10b981' : '#cbd5e1',
                color: '#ffffff',
                fontWeight: 700,
                fontSize: '0.78rem',
                cursor: 'pointer'
              }
            },
            prefs.pushEnabled ? '✓ Enabled' : 'Enable Push'
          )
        ),

        // Route hazards toggle
        React.createElement(
          'div',
          { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 0', borderBottom: '1px solid #f1f5f9' } },
          React.createElement(
            'div',
            null,
            React.createElement('div', { style: { fontSize: '0.86rem', fontWeight: 600, color: '#1e293b' } }, 'Route High-Pollution Corridor Warnings'),
            React.createElement('div', { style: { fontSize: '0.74rem', color: '#64748b' } }, 'Alert when evaluated transit routes cross severe urban pollution hotspots.')
          ),
          React.createElement('input', {
            type: 'checkbox',
            checked: prefs.alertRouteHazards,
            onChange: (e) => updatePref('alertRouteHazards', e.target.checked),
            style: { width: '18px', height: '18px', accentColor: '#2563eb', cursor: 'pointer' }
          })
        ),

        // Daily morning digest toggle
        React.createElement(
          'div',
          { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '14px' } },
          React.createElement(
            'div',
            null,
            React.createElement('div', { style: { fontSize: '0.86rem', fontWeight: 600, color: '#1e293b' } }, 'Daily Morning AQI Forecast Digest'),
            React.createElement('div', { style: { fontSize: '0.74rem', color: '#64748b' } }, 'Scheduled 7:30 AM summary with Neural GRU 24-hour diurnal forecasts.')
          ),
          React.createElement('input', {
            type: 'checkbox',
            checked: prefs.alertDailyDigest,
            onChange: (e) => updatePref('alertDailyDigest', e.target.checked),
            style: { width: '18px', height: '18px', accentColor: '#2563eb', cursor: 'pointer' }
          })
        )
      ),

      // Test Alert Action
      React.createElement(
        'div',
        { style: { display: 'flex', justifyContent: 'flex-end', gap: '10px' } },
        React.createElement(
          'button',
          {
            onClick: handleTestNotification,
            style: {
              padding: '10px 20px',
              borderRadius: '8px',
              border: '1px solid #2563eb',
              background: '#2563eb',
              color: '#ffffff',
              fontWeight: 700,
              fontSize: '0.84rem',
              cursor: 'pointer',
              boxShadow: '0 2px 4px rgba(37,99,235,0.2)'
            }
          },
          '🔔 Send Test Alert'
        )
      )
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // 3. React Mount Manager
  // ─────────────────────────────────────────────────────────────────────────────
  const ReactMountManager = {
    historyRoot: null,
    prefsRoot: null,

    renderHistoryTab() {
      const container = document.getElementById('tab-module3');
      if (!container || !window.ReactDOM || !window.React) return;
      if (!this.historyRoot) {
        this.historyRoot = ReactDOM.createRoot(container);
      }
      this.historyRoot.render(React.createElement(ReactExposureHistory));
    },

    renderPrefsTab() {
      const container = document.getElementById('tab-module3_prefs') || document.getElementById('tab-module3-prefs');
      if (!container || !window.ReactDOM || !window.React) return;
      if (!this.prefsRoot) {
        this.prefsRoot = ReactDOM.createRoot(container);
      }
      this.prefsRoot.render(React.createElement(ReactNotificationPrefs));
    }
  };

  window.ReactExposureHistory = ReactExposureHistory;
  window.ReactNotificationPrefs = ReactNotificationPrefs;
  window.ReactMountManager = ReactMountManager;
})();
