// Aura Dashboard JavaScript
class AuraDashboard {
  constructor() {
    this.apiBaseUrl = "http://localhost:5000/api";
    this.machines = {};
    this.alerts = [];
    this.charts = {};
    this.selectedMachine = null;
    this.updateInterval = 3000; // 3 seconds
    this.isLoading = true;

    this.init();
  }

  async init() {
    console.log("🚀 Initializing Aura Dashboard...");

    try {
      // Hide loading overlay after initial load
      setTimeout(() => {
        const loadingOverlay = document.getElementById("loadingOverlay");
        if (loadingOverlay) {
          loadingOverlay.style.display = "none";
        }
        this.isLoading = false;
      }, 2000);

      // Initial data load
      await this.loadDashboardData();

      // Start real-time updates
      this.startRealTimeUpdates();

      // Setup event listeners
      this.setupEventListeners();

      console.log("✅ Dashboard initialized successfully");
    } catch (error) {
      console.error("❌ Failed to initialize dashboard:", error);
      this.showError(
        "Failed to load dashboard. Please check if the server is running."
      );
    }
  }

  async loadDashboardData() {
    try {
      // Load machine status
      const statusResponse = await fetch(`${this.apiBaseUrl}/status`);
      if (!statusResponse.ok) throw new Error(`HTTP ${statusResponse.status}`);

      const statusData = await statusResponse.json();
      this.machines = statusData.machines;

      // Load alerts
      const alertsResponse = await fetch(`${this.apiBaseUrl}/alerts?limit=20`);
      if (!alertsResponse.ok) throw new Error(`HTTP ${alertsResponse.status}`);

      const alertsData = await alertsResponse.json();
      this.alerts = alertsData.alerts;

      // Update UI
      this.updateSystemOverview(statusData);
      this.updateMachinesGrid();
      this.updateAlertsPanel();
      this.updateLastUpdateTime();
    } catch (error) {
      console.error("Error loading dashboard data:", error);
      throw error;
    }
  }

  updateSystemOverview(data) {
    // System Health
    const systemHealthEl = document.getElementById("systemHealth");
    if (systemHealthEl && data.system_health !== undefined) {
      systemHealthEl.textContent = `${data.system_health}%`;
      systemHealthEl.className = `text-3xl font-bold ${this.getHealthColor(
        data.system_health
      )}`;
    }

    // Active Machines
    const activeMachinesEl = document.getElementById("activeMachines");
    if (activeMachinesEl) {
      activeMachinesEl.textContent = data.total_machines || 0;
    }

    // Active Alerts
    const activeAlertsEl = document.getElementById("activeAlerts");
    if (activeAlertsEl) {
      activeAlertsEl.textContent = data.active_alerts || 0;
    }

    // Efficiency (calculated based on system health)
    const efficiencyEl = document.getElementById("efficiency");
    if (efficiencyEl && data.system_health !== undefined) {
      const efficiency = Math.min(
        100,
        Math.max(0, data.system_health + Math.random() * 10 - 5)
      );
      efficiencyEl.textContent = `${efficiency.toFixed(1)}%`;
    }
  }

  updateMachinesGrid() {
    const grid = document.getElementById("machinesGrid");
    if (!grid) return;

    grid.innerHTML = "";

    Object.values(this.machines).forEach((machine) => {
      const card = this.createMachineCard(machine);
      grid.appendChild(card);
    });
  }

  createMachineCard(machine) {
    const card = document.createElement("div");
    card.className = `machine-card bg-white rounded-xl shadow-sm p-6 border border-gray-200 cursor-pointer fade-in ${machine.alert_level}`;
    card.onclick = () => this.openMachineModal(machine.machine_id);

    const healthColor = this.getHealthColor(machine.health_score);
    const statusIcon = this.getStatusIcon(machine.alert_level);
    const alertBadge =
      machine.alert_level !== "healthy"
        ? `<div class="alert-badge absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold">${machine.potential_issues.length}</div>`
        : "";

    card.innerHTML = `
            <div class="relative">
                ${alertBadge}
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                            <i data-lucide="${this.getMachineIcon(
                              machine.type
                            )}" class="w-5 h-5 text-gray-600"></i>
                        </div>
                        <div>
                            <h3 class="font-semibold text-gray-900">${
                              machine.name
                            }</h3>
                            <p class="text-sm text-gray-500">${
                              machine.type
                            } • ${machine.location}</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <div class="status-indicator status-${
                          machine.alert_level
                        }"></div>
                        <span class="text-sm font-medium ${this.getAlertLevelColor(
                          machine.alert_level
                        )}">${machine.alert_level.toUpperCase()}</span>
                    </div>
                </div>
                
                <div class="mb-4">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-sm font-medium text-gray-700">Health Score</span>
                        <span class="text-lg font-bold ${healthColor}">${
      machine.health_score
    }%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="h-2 rounded-full transition-all duration-500 ${this.getHealthBarColor(
                          machine.health_score
                        )}" 
                             style="width: ${machine.health_score}%"></div>
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-3 mb-4">
                    <div class="bg-gray-50 rounded-lg p-3">
                        <div class="flex items-center space-x-2">
                            <i data-lucide="thermometer" class="w-4 h-4 text-red-500"></i>
                            <span class="text-xs text-gray-600">Temp</span>
                        </div>
                        <p class="text-sm font-semibold text-gray-900">${
                          machine.current_readings.temperature
                        }°C</p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3">
                        <div class="flex items-center space-x-2">
                            <i data-lucide="activity" class="w-4 h-4 text-blue-500"></i>
                            <span class="text-xs text-gray-600">Vibration</span>
                        </div>
                        <p class="text-sm font-semibold text-gray-900">${
                          machine.current_readings.vibration
                        }</p>
                    </div>
                </div>
                
                <div class="grid grid-cols-2 gap-3 mb-4">
                    <div class="bg-gray-50 rounded-lg p-3">
                        <div class="flex items-center space-x-2">
                            <i data-lucide="rotate-cw" class="w-4 h-4 text-green-500"></i>
                            <span class="text-xs text-gray-600">RPM</span>
                        </div>
                        <p class="text-sm font-semibold text-gray-900">${
                          machine.current_readings.rotation_speed
                        }</p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3">
                        <div class="flex items-center space-x-2">
                            <i data-lucide="gauge" class="w-4 h-4 text-purple-500"></i>
                            <span class="text-xs text-gray-600">Load</span>
                        </div>
                        <p class="text-sm font-semibold text-gray-900">${
                          machine.current_readings.load
                        }%</p>
                    </div>
                </div>
                
                ${
                  machine.potential_issues.length > 0
                    ? `
                    <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                        <div class="flex items-center space-x-2 mb-2">
                            <i data-lucide="alert-triangle" class="w-4 h-4 text-red-500"></i>
                            <span class="text-sm font-medium text-red-700">Issues Detected</span>
                        </div>
                        <ul class="text-xs text-red-600 space-y-1">
                            ${machine.potential_issues
                              .slice(0, 2)
                              .map((issue) => `<li>• ${issue}</li>`)
                              .join("")}
                            ${
                              machine.potential_issues.length > 2
                                ? `<li>• +${
                                    machine.potential_issues.length - 2
                                  } more...</li>`
                                : ""
                            }
                        </ul>
                    </div>
                `
                    : `
                    <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div class="flex items-center space-x-2">
                            <i data-lucide="check-circle" class="w-4 h-4 text-green-500"></i>
                            <span class="text-sm font-medium text-green-700">Operating Normally</span>
                        </div>
                    </div>
                `
                }
                
                <div class="mt-4 pt-3 border-t border-gray-100">
                    <div class="flex items-center justify-between text-xs text-gray-500">
                        <span>Last updated: ${this.formatTime(
                          machine.last_updated
                        )}</span>
                        <span class="flex items-center space-x-1">
                            <i data-lucide="eye" class="w-3 h-3"></i>
                            <span>Click for details</span>
                        </span>
                    </div>
                </div>
            </div>
        `;

    return card;
  }

  updateAlertsPanel() {
    const alertsList = document.getElementById("alertsList");
    if (!alertsList) return;

    if (this.alerts.length === 0) {
      alertsList.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <i data-lucide="check-circle" class="w-12 h-12 mx-auto mb-3 text-green-500"></i>
                    <p class="text-lg font-medium">No Active Alerts</p>
                    <p class="text-sm">All systems are operating normally</p>
                </div>
            `;
      return;
    }

    alertsList.innerHTML = this.alerts
      .slice(0, 10)
      .map(
        (alert) => `
            <div class="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg border-l-4 ${this.getAlertBorderColor(
              alert.severity
            )}">
                <div class="flex-shrink-0">
                    <i data-lucide="${this.getAlertIcon(
                      alert.severity
                    )}" class="w-5 h-5 ${this.getAlertIconColor(
          alert.severity
        )}"></i>
                </div>
                <div class="flex-grow">
                    <p class="text-sm font-medium text-gray-900">${
                      alert.message
                    }</p>
                    <p class="text-xs text-gray-500">${this.formatTime(
                      alert.timestamp
                    )} • ${alert.machine_id}</p>
                </div>
                <div class="flex-shrink-0">
                    <span class="inline-flex px-2 py-1 text-xs font-medium rounded-full ${this.getAlertBadgeColor(
                      alert.severity
                    )}">
                        ${alert.severity.toUpperCase()}
                    </span>
                </div>
            </div>
        `
      )
      .join("");
  }

  async openMachineModal(machineId) {
    this.selectedMachine = machineId;
    const machine = this.machines[machineId];
    if (!machine) return;

    // Update modal content
    document.getElementById("modalMachineName").textContent = machine.name;

    // Show modal
    document.getElementById("machineModal").classList.remove("hidden");

    // Load detailed machine data
    try {
      const response = await fetch(`${this.apiBaseUrl}/machine/${machineId}`);
      const data = await response.json();

      this.updateModalContent(data);
      this.createModalCharts(data);
    } catch (error) {
      console.error("Error loading machine details:", error);
    }
  }

  updateModalContent(data) {
    const machine = data.machine;

    // Update machine info
    const infoContainer = document.getElementById("modalMachineInfo");
    infoContainer.innerHTML = `
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-sm font-medium text-gray-600">Health Score</label>
                        <p class="text-2xl font-bold ${this.getHealthColor(
                          machine.health_score
                        )}">${machine.health_score}%</p>
                    </div>
                    <div>
                        <label class="text-sm font-medium text-gray-600">Status</label>
                        <p class="text-lg font-semibold ${this.getAlertLevelColor(
                          machine.alert_level
                        )}">${machine.alert_level.toUpperCase()}</p>
                    </div>
                </div>
                
                <div>
                    <label class="text-sm font-medium text-gray-600">Current Readings</label>
                    <div class="grid grid-cols-2 gap-3 mt-2">
                        <div class="bg-white rounded-lg p-3 border">
                            <div class="flex items-center space-x-2">
                                <i data-lucide="thermometer" class="w-4 h-4 text-red-500"></i>
                                <span class="text-sm text-gray-600">Temperature</span>
                            </div>
                            <p class="text-lg font-semibold">${
                              machine.current_readings.temperature
                            }°C</p>
                        </div>
                        <div class="bg-white rounded-lg p-3 border">
                            <div class="flex items-center space-x-2">
                                <i data-lucide="activity" class="w-4 h-4 text-blue-500"></i>
                                <span class="text-sm text-gray-600">Vibration</span>
                            </div>
                            <p class="text-lg font-semibold">${
                              machine.current_readings.vibration
                            }</p>
                        </div>
                        <div class="bg-white rounded-lg p-3 border">
                            <div class="flex items-center space-x-2">
                                <i data-lucide="rotate-cw" class="w-4 h-4 text-green-500"></i>
                                <span class="text-sm text-gray-600">RPM</span>
                            </div>
                            <p class="text-lg font-semibold">${
                              machine.current_readings.rotation_speed
                            }</p>
                        </div>
                        <div class="bg-white rounded-lg p-3 border">
                            <div class="flex items-center space-x-2">
                                <i data-lucide="gauge" class="w-4 h-4 text-purple-500"></i>
                                <span class="text-sm text-gray-600">Load</span>
                            </div>
                            <p class="text-lg font-semibold">${
                              machine.current_readings.load
                            }%</p>
                        </div>
                    </div>
                </div>
                
                <div>
                    <label class="text-sm font-medium text-gray-600">Recommendation</label>
                    <p class="text-sm text-gray-900 mt-1 p-3 bg-white rounded-lg border">${
                      machine.recommendation
                    }</p>
                </div>
            </div>
        `;

    // Update recent alerts
    const alertsContainer = document.getElementById("modalRecentAlerts");
    if (data.recent_alerts && data.recent_alerts.length > 0) {
      alertsContainer.innerHTML = data.recent_alerts
        .map(
          (alert) => `
                <div class="flex items-center space-x-3 p-3 bg-white rounded-lg border">
                    <i data-lucide="${this.getAlertIcon(
                      alert.severity
                    )}" class="w-4 h-4 ${this.getAlertIconColor(
            alert.severity
          )}"></i>
                    <div class="flex-grow">
                        <p class="text-sm font-medium text-gray-900">${
                          alert.message
                        }</p>
                        <p class="text-xs text-gray-500">${this.formatTime(
                          alert.timestamp
                        )}</p>
                    </div>
                </div>
            `
        )
        .join("");
    } else {
      alertsContainer.innerHTML = `
                <div class="text-center py-4 text-gray-500">
                    <i data-lucide="check-circle" class="w-8 h-8 mx-auto mb-2 text-green-500"></i>
                    <p class="text-sm">No recent alerts</p>
                </div>
            `;
    }

    // Update maintenance history (new section)
    const maintenanceContainer = document.getElementById(
      "modalMaintenanceHistory"
    );
    if (maintenanceContainer) {
      if (data.maintenance_history && data.maintenance_history.length > 0) {
        maintenanceContainer.innerHTML = data.maintenance_history
          .slice(0, 5)
          .map(
            (log) => `
                    <div class="flex items-center space-x-3 p-3 bg-white rounded-lg border">
                        <div class="flex-shrink-0">
                            <i data-lucide="${this.getMaintenanceIcon(
                              log.activity_type
                            )}" class="w-4 h-4 text-blue-500"></i>
                        </div>
                        <div class="flex-grow">
                            <p class="text-sm font-medium text-gray-900">${
                              log.activity_type.charAt(0).toUpperCase() +
                              log.activity_type.slice(1)
                            }</p>
                            <p class="text-xs text-gray-600">${
                              log.description
                            }</p>
                            <p class="text-xs text-gray-500">${this.formatTime(
                              log.timestamp
                            )} • ${log.technician}</p>
                        </div>
                    </div>
                `
          )
          .join("");
      } else {
        maintenanceContainer.innerHTML = `
                    <div class="text-center py-4 text-gray-500">
                        <i data-lucide="wrench" class="w-8 h-8 mx-auto mb-2 text-gray-400"></i>
                        <p class="text-sm">No maintenance history</p>
                    </div>
                `;
      }
    }
  }

  createModalCharts(data) {
    // Destroy existing charts
    Object.values(this.charts).forEach((chart) => {
      if (chart) chart.destroy();
    });
    this.charts = {};

    // Create temperature chart
    const tempCtx = document.getElementById("temperatureChart");
    if (tempCtx && data.historical_readings) {
      const tempData = data.historical_readings.slice(-24); // Last 24 hours

      this.charts.temperature = new Chart(tempCtx, {
        type: "line",
        data: {
          labels: tempData.map((d) =>
            new Date(d.timestamp).toLocaleTimeString()
          ),
          datasets: [
            {
              label: "Temperature (°C)",
              data: tempData.map((d) => d.temperature),
              borderColor: "rgb(239, 68, 68)",
              backgroundColor: "rgba(239, 68, 68, 0.1)",
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
          },
          scales: {
            y: {
              beginAtZero: false,
              grid: {
                color: "rgba(0, 0, 0, 0.1)",
              },
            },
            x: {
              grid: {
                color: "rgba(0, 0, 0, 0.1)",
              },
            },
          },
        },
      });
    }

    // Create vibration chart
    const vibCtx = document.getElementById("vibrationChart");
    if (vibCtx && data.historical_readings) {
      const vibData = data.historical_readings.slice(-24); // Last 24 hours

      this.charts.vibration = new Chart(vibCtx, {
        type: "line",
        data: {
          labels: vibData.map((d) =>
            new Date(d.timestamp).toLocaleTimeString()
          ),
          datasets: [
            {
              label: "Vibration",
              data: vibData.map((d) => d.vibration),
              borderColor: "rgb(59, 130, 246)",
              backgroundColor: "rgba(59, 130, 246, 0.1)",
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false,
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: "rgba(0, 0, 0, 0.1)",
              },
            },
            x: {
              grid: {
                color: "rgba(0, 0, 0, 0.1)",
              },
            },
          },
        },
      });
    }
  }

  closeMachineModal() {
    document.getElementById("machineModal").classList.add("hidden");
    this.selectedMachine = null;

    // Destroy charts to free memory
    Object.values(this.charts).forEach((chart) => {
      if (chart) chart.destroy();
    });
    this.charts = {};
  }

  startRealTimeUpdates() {
    setInterval(async () => {
      if (!this.isLoading) {
        try {
          await this.loadDashboardData();

          // Update modal if it's open
          if (this.selectedMachine) {
            const response = await fetch(
              `${this.apiBaseUrl}/machine/${this.selectedMachine}`
            );
            const data = await response.json();
            this.updateModalContent(data);
          }
        } catch (error) {
          console.error("Error during real-time update:", error);
        }
      }
    }, this.updateInterval);
  }

  setupEventListeners() {
    // Close modal when clicking outside
    document.getElementById("machineModal").addEventListener("click", (e) => {
      if (e.target.id === "machineModal") {
        this.closeMachineModal();
      }
    });

    // Escape key to close modal
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.selectedMachine) {
        this.closeMachineModal();
      }
    });
  }

  updateLastUpdateTime() {
    const lastUpdateEl = document.getElementById("lastUpdate");
    if (lastUpdateEl) {
      lastUpdateEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    }
  }

  // Utility functions
  getHealthColor(score) {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    if (score >= 40) return "text-orange-600";
    return "text-red-600";
  }

  getHealthBarColor(score) {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    if (score >= 40) return "bg-orange-500";
    return "bg-red-500";
  }

  getAlertLevelColor(level) {
    const colors = {
      healthy: "text-green-600",
      warning: "text-yellow-600",
      critical: "text-orange-600",
      danger: "text-red-600",
    };
    return colors[level] || "text-gray-600";
  }

  getAlertBorderColor(severity) {
    const colors = {
      info: "border-blue-500",
      warning: "border-yellow-500",
      critical: "border-orange-500",
      danger: "border-red-500",
    };
    return colors[severity] || "border-gray-500";
  }

  getAlertIconColor(severity) {
    const colors = {
      info: "text-blue-500",
      warning: "text-yellow-500",
      critical: "text-orange-500",
      danger: "text-red-500",
    };
    return colors[severity] || "text-gray-500";
  }

  getAlertBadgeColor(severity) {
    const colors = {
      info: "bg-blue-100 text-blue-800",
      warning: "bg-yellow-100 text-yellow-800",
      critical: "bg-orange-100 text-orange-800",
      danger: "bg-red-100 text-red-800",
    };
    return colors[severity] || "bg-gray-100 text-gray-800";
  }

  getAlertIcon(severity) {
    const icons = {
      info: "info",
      warning: "alert-triangle",
      critical: "alert-circle",
      danger: "alert-octagon",
    };
    return icons[severity] || "info";
  }

  getMachineIcon(type) {
    const icons = {
      Conveyor: "arrow-right",
      Press: "compress",
      Motor: "rotate-cw",
      Compressor: "fan",
      Pump: "droplet",
    };
    return icons[type] || "cpu";
  }

  getMaintenanceIcon(activityType) {
    const icons = {
      inspection: "search",
      repair: "wrench",
      replacement: "package",
      calibration: "settings",
    };
    return icons[activityType] || "tool";
  }

  getStatusIcon(level) {
    const icons = {
      healthy: "check-circle",
      warning: "alert-triangle",
      critical: "alert-circle",
      danger: "x-circle",
    };
    return icons[level] || "help-circle";
  }

  formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
  }

  showError(message) {
    // Simple error display - could be enhanced with a proper notification system
    console.error(message);
    alert(message);
  }
}

// Global functions for UI interactions
function closeMachineModal() {
  if (window.dashboard) {
    window.dashboard.closeMachineModal();
  }
}

async function scheduleMaintenance() {
  if (window.dashboard && window.dashboard.selectedMachine) {
    const machineId = window.dashboard.selectedMachine;
    const machine = window.dashboard.machines[machineId];

    // Create maintenance form modal
    const formHtml = `
            <div id="maintenanceModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
                <div class="bg-white rounded-xl shadow-2xl max-w-md w-full">
                    <div class="p-6 border-b border-gray-200">
                        <h3 class="text-xl font-bold text-gray-900">Schedule Maintenance</h3>
                        <p class="text-sm text-gray-600 mt-1">${machine.name}</p>
                    </div>
                    <form id="maintenanceForm" class="p-6 space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Activity Type</label>
                            <select id="activityType" class="w-full border border-gray-300 rounded-lg px-3 py-2" required>
                                <option value="">Select activity type</option>
                                <option value="inspection">Inspection</option>
                                <option value="repair">Repair</option>
                                <option value="replacement">Component Replacement</option>
                                <option value="calibration">Calibration</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                            <textarea id="description" class="w-full border border-gray-300 rounded-lg px-3 py-2 h-24" 
                                      placeholder="Describe the maintenance activity..." required></textarea>
                        </div>
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Technician</label>
                            <input type="text" id="technician" class="w-full border border-gray-300 rounded-lg px-3 py-2" 
                                   placeholder="Technician name" value="System User">
                        </div>
                        <div class="flex space-x-3 pt-4">
                            <button type="submit" class="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                                Schedule Maintenance
                            </button>
                            <button type="button" onclick="closeMaintenanceModal()" 
                                    class="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-400 transition-colors">
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

    // Add modal to page
    document.body.insertAdjacentHTML("beforeend", formHtml);

    // Setup form submission
    document.getElementById("maintenanceForm").onsubmit = async (e) => {
      e.preventDefault();

      const formData = {
        machine_id: machineId,
        activity_type: document.getElementById("activityType").value,
        description: document.getElementById("description").value,
        technician: document.getElementById("technician").value,
      };

      try {
        const response = await fetch(
          `${window.dashboard.apiBaseUrl}/maintenance`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(formData),
          }
        );

        if (response.ok) {
          alert("Maintenance scheduled successfully!");
          closeMaintenanceModal();
          // Refresh machine details
          window.dashboard.openMachineModal(machineId);
        } else {
          alert("Failed to schedule maintenance. Please try again.");
        }
      } catch (error) {
        console.error("Error scheduling maintenance:", error);
        alert("Failed to schedule maintenance. Please try again.");
      }
    };
  }
}

function closeMaintenanceModal() {
  const modal = document.getElementById("maintenanceModal");
  if (modal) {
    modal.remove();
  }
}

async function acknowledgeProblem() {
  if (window.dashboard && window.dashboard.selectedMachine) {
    const machineId = window.dashboard.selectedMachine;

    try {
      // Log an acknowledgment as a maintenance activity
      const response = await fetch(
        `${window.dashboard.apiBaseUrl}/maintenance`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            machine_id: machineId,
            activity_type: "inspection",
            description: "Issues acknowledged by operator - monitoring closely",
            technician: "System User",
          }),
        }
      );

      if (response.ok) {
        alert("Issues acknowledged successfully!");
        // Refresh machine details
        window.dashboard.openMachineModal(machineId);
      } else {
        alert("Failed to acknowledge issues. Please try again.");
      }
    } catch (error) {
      console.error("Error acknowledging issues:", error);
      alert("Failed to acknowledge issues. Please try again.");
    }
  }
}

// Initialize dashboard when page loads
document.addEventListener("DOMContentLoaded", () => {
  window.dashboard = new AuraDashboard();
});
