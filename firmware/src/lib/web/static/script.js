const state = {
    configs: [],
    selectedConfig: null,
    loadedConfig: null,
    mappings: [],
    currentTheme: 'dark'
};

const MIDI_NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

function midiToNoteName(midiNumber) {
    const octave = Math.floor(midiNumber / 12) - 1;
    const note = MIDI_NOTES[midiNumber % 12];
    return `${note}${octave}`;
}

const API = {
    async getConfigs() {
        try {
            const res = await fetch('/api/configs');
            if (!res.ok) throw new Error('Failed to fetch configs');
            return await res.json();
        } catch (e) {
            console.error('getConfigs error:', e);
            return [];
        }
    },

    async selectConfig(name) {
        try {
            const res = await fetch(`/api/select/${name}`, { method: 'POST' });
            if (!res.ok) throw new Error('Failed to select config');
            return await res.json();
        } catch (e) {
            console.error('selectConfig error:', e);
            return { ok: false };
        }
    },

    async loadConfig(name) {
        try {
            const res = await fetch(`/api/load/${name}`);
            if (!res.ok) throw new Error('Config not found');
            return await res.json();
        } catch (e) {
            console.error('loadConfig error:', e);
            return null;
        }
    },

    async saveConfig(filename, mappings) {
        try {
            const res = await fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename, mappings })
            });
            if (!res.ok) throw new Error('Failed to save config');
            return await res.json();
        } catch (e) {
            console.error('saveConfig error:', e);
            return { ok: false };
        }
    },

    async deleteConfig(name) {
        try {
            const res = await fetch(`/api/config/${name}`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Failed to delete config');
            return await res.json();
        } catch (e) {
            console.error('deleteConfig error:', e);
            return { ok: false };
        }
    },

    async getStatus() {
        try {
            const res = await fetch('/api/status');
            if (!res.ok) throw new Error('Failed to fetch status');
            return await res.json();
        } catch (e) {
            console.error('getStatus error:', e);
            return {
                wifi: { connected: false },
                bluetooth: { connected: false, advertising: false },
                temperature: null
            };
        }
    }
};

function showToast(text, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = text;
    toast.className = `toast show ${type}`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function showModal(title, label, defaultValue = '') {
    return new Promise((resolve) => {
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modal-title');
        const modalLabel = document.getElementById('modal-label');
        const modalInput = document.getElementById('modal-input');

        modalTitle.textContent = title;
        modalLabel.textContent = label;
        modalInput.value = defaultValue;
        modal.classList.add('show');
        modalInput.focus();

        const handleConfirm = () => {
            cleanup();
            resolve(modalInput.value);
        };

        const handleCancel = () => {
            cleanup();
            resolve(null);
        };

        const handleKeydown = (e) => {
            if (e.key === 'Enter') handleConfirm();
            if (e.key === 'Escape') handleCancel();
        };

        const handleBackdrop = (e) => {
            if (e.target.id === 'modal') handleCancel();
        };

        const cleanup = () => {
            modal.classList.remove('show');
            document.getElementById('modal-confirm').removeEventListener('click', handleConfirm);
            document.getElementById('modal-cancel').removeEventListener('click', handleCancel);
            modalInput.removeEventListener('keydown', handleKeydown);
            modal.removeEventListener('click', handleBackdrop);
        };

        document.getElementById('modal-confirm').addEventListener('click', handleConfirm);
        document.getElementById('modal-cancel').addEventListener('click', handleCancel);
        modalInput.addEventListener('keydown', handleKeydown);
        modal.addEventListener('click', handleBackdrop);
    });
}

function setTheme(theme) {
    document.body.className = `theme-${theme}`;
    state.currentTheme = theme;
    localStorage.setItem('plantain-theme', theme);

    document.querySelectorAll('.theme-option').forEach(option => {
        option.classList.toggle('active', option.dataset.theme === theme);
    });
}

function toggleThemeMenu() {
    const menu = document.getElementById('theme-menu');
    menu.classList.toggle('show');
}

function closeThemeMenu() {
    document.getElementById('theme-menu').classList.remove('show');
}

function updateStatus(status) {
    const wifiDot = document.getElementById('wifi-status');
    const wifiText = document.getElementById('wifi-text');
    const bleDot = document.getElementById('ble-status');
    const bleText = document.getElementById('ble-text');
    const tempDot = document.getElementById('temp-status');
    const tempText = document.getElementById('temp-text');

    if (status.wifi?.connected) {
        wifiDot.className = 'status-dot active';
        wifiText.textContent = `WiFi: ${status.wifi.ssid || 'Connected'}`;
        document.getElementById('dashboard-wifi').textContent = '✓';
    } else {
        wifiDot.className = 'status-dot';
        wifiText.textContent = 'WiFi: Disconnected';
        document.getElementById('dashboard-wifi').textContent = '✗';
    }

    if (status.bluetooth?.advertising) {
        bleDot.className = 'status-dot active';
        bleText.textContent = `BLE: ${status.bluetooth.connected ? 'Connected' : 'Ready'}`;
        document.getElementById('dashboard-ble').textContent = status.bluetooth.connected ? '✓' : '◆';
    } else {
        bleDot.className = 'status-dot';
        bleText.textContent = 'BLE: Off';
        document.getElementById('dashboard-ble').textContent = '✗';
    }

    if (status.temperature !== undefined && status.temperature !== null) {
        tempDot.className = status.temperature > 60 ? 'status-dot warning' : 'status-dot active';
        tempText.textContent = `Temp: ${status.temperature}°C`;
        document.getElementById('dashboard-temp').textContent = `${status.temperature}°C`;
    } else {
        tempDot.className = 'status-dot';
        tempText.textContent = 'Temp: --°C';
        document.getElementById('dashboard-temp').textContent = '—';
    }
}

function updateActiveConfigDisplay() {
    const display = document.getElementById('active-config-display');
    display.textContent = state.loadedConfig || 'None';
}

async function loadConfigList() {
    try {
        state.configs = await API.getConfigs();
        renderConfigPanel();
    } catch (error) {
        showToast('Failed to load configs', 'error');
    }
}

function renderConfigPanel() {
    const panel = document.getElementById('config-panel');
    panel.innerHTML = state.configs.map(name => `
        <div class="config-item ${state.selectedConfig === name ? 'active' : ''} ${state.loadedConfig === name ? 'loaded' : ''}"
             role="option" aria-selected="${state.selectedConfig === name}"
             data-config="${name}">
            ${name}
        </div>
    `).join('');

    document.querySelectorAll('.config-item').forEach(item => {
        item.addEventListener('click', () => selectConfigItem(item.dataset.config));
    });

    updateConfigButtons();
}

async function selectConfigItem(name) {
    state.selectedConfig = name;
    renderConfigPanel();
    updateConfigButtons();

    const result = await API.selectConfig(name);
    if (result.ok) {
        showToast(`Selected: ${name}`);
        await loadConfigData(name);
    } else {
        showToast('Failed to select config', 'error');
    }
}

async function loadConfigData(name) {
    const data = await API.loadConfig(name);
    if (data) {
        state.loadedConfig = name;
        state.mappings = data.mappings || [];
        renderMappings();
        renderConfigPanel();
        updateActiveConfigDisplay();
        showToast(`Loaded: ${name}`);
    } else {
        showToast('Failed to load config data', 'error');
    }
}

function renderMappings() {
    const grid = document.getElementById('button-grid');
    const card = document.getElementById('mappings-card');

    if (!state.mappings.length) {
        card.classList.add('hidden');
        return;
    }

    card.classList.remove('hidden');
    grid.innerHTML = state.mappings.map(m => `
        <div class="button-card">
            <h3>Button ${m.button}</h3>
            <div class="note-display">${midiToNoteName(m.note)}</div>
            <label>Note</label>
            <input type="number" data-button="${m.button}" data-field="note" min="0" max="127" value="${m.note}">
            <label>Velocity</label>
            <input type="number" data-button="${m.button}" data-field="velocity" min="0" max="127" value="${m.velocity || 100}">
        </div>
    `).join('');

    document.querySelectorAll('#button-grid input[data-field="note"]').forEach(input => {
        input.addEventListener('input', (e) => {
            const display = document.querySelector(`[data-button="${e.target.dataset.button}"] .note-display`);
            if (display) display.textContent = midiToNoteName(parseInt(e.target.value));
        });
    });
}

function updateConfigButtons() {
    const hasSelected = state.selectedConfig !== null;
    document.getElementById('edit-config-btn').disabled = !hasSelected;
    document.getElementById('delete-config-btn').disabled = !hasSelected;
}

async function handleNewConfig() {
    const name = await showModal('New Configuration', 'Config Name');
    if (!name) return;

    const filename = name.endsWith('.pl_conf') ? name : `${name}.pl_conf`;
    const defaultMappings = [
        { button: 0, note: 60, velocity: 100 },
        { button: 1, note: 62, velocity: 100 },
        { button: 2, note: 64, velocity: 100 },
        { button: 3, note: 67, velocity: 100 }
    ];

    const result = await API.saveConfig(filename, defaultMappings);
    if (result.ok) {
        await loadConfigList();
        showToast(`Created: ${filename}`);
    } else {
        showToast('Failed to create config', 'error');
    }
}

async function handleEditConfig() {
    if (!state.loadedConfig) {
        showToast('Load a config first', 'error');
        return;
    }

    const mappings = [];
    document.querySelectorAll('#button-grid input[data-field="note"]').forEach(input => {
        const button = parseInt(input.dataset.button);
        const note = parseInt(input.value);
        const velocity = parseInt(document.querySelector(`input[data-button="${button}"][data-field="velocity"]`).value);
        mappings.push({ button, note, velocity });
    });

    const result = await API.saveConfig(state.loadedConfig, mappings);
    if (result.ok) {
        state.mappings = mappings;
        showToast(`Saved: ${state.loadedConfig}`);
    } else {
        showToast('Failed to save config', 'error');
    }
}

async function handleDeleteConfig() {
    if (!state.selectedConfig) {
        showToast('Select a config to delete', 'error');
        return;
    }

    const confirm = await showModal('Delete Configuration', 'Type DELETE to confirm');
    if (confirm !== 'DELETE') return;

    const result = await API.deleteConfig(state.selectedConfig);
    if (result.ok) {
        state.configs = state.configs.filter(c => c !== state.selectedConfig);
        if (state.loadedConfig === state.selectedConfig) {
            state.loadedConfig = null;
            state.mappings = [];
            document.getElementById('mappings-card').classList.add('hidden');
            updateActiveConfigDisplay();
        }
        state.selectedConfig = null;
        renderConfigPanel();
        showToast(`Deleted config`);
    } else {
        showToast('Failed to delete config', 'error');
    }
}

async function updateStatusPeriodic() {
    try {
        const status = await API.getStatus();
        updateStatus(status);
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

function init() {
    const savedTheme = localStorage.getItem('plantain-theme') || 'dark';
    setTheme(savedTheme);

    document.getElementById('theme-button').addEventListener('click', toggleThemeMenu);
    document.querySelectorAll('.theme-option').forEach(option => {
        option.addEventListener('click', () => {
            setTheme(option.dataset.theme);
            closeThemeMenu();
        });
    });

    document.addEventListener('click', (e) => {
        const switcher = document.querySelector('.theme-switcher');
        if (!switcher.contains(e.target)) closeThemeMenu();
    });

    document.getElementById('new-config-btn').addEventListener('click', handleNewConfig);
    document.getElementById('edit-config-btn').addEventListener('click', handleEditConfig);
    document.getElementById('delete-config-btn').addEventListener('click', handleDeleteConfig);

    loadConfigList();
    updateStatusPeriodic();
    setInterval(updateStatusPeriodic, 5000);
}

document.addEventListener('DOMContentLoaded', init);
