const state = {
    currentConfig: null,
    configs: [],
    mappings: [],
    modalResolve: null,
    currentTheme: 'dark'
};

const MIDI_NOTES = [
    'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'
];

function midiToNoteName(midiNumber) {
    const octave = Math.floor(midiNumber / 12) - 1;
    const note = MIDI_NOTES[midiNumber % 12];
    return `${note}${octave}`;
}

function noteNameToMidi(noteName) {
    const match = noteName.match(/^([A-G]#?)(-?\d+)$/);
    if (!match) return 60;
    
    const note = match[1];
    const octave = parseInt(match[2]);
    const noteIndex = MIDI_NOTES.indexOf(note);
    
    if (noteIndex === -1) return 60;
    return (octave + 1) * 12 + noteIndex;
}

const API = {
    async getConfigs() {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve(['default.pl_conf', 'piano.pl_conf', 'drums.pl_conf']);
            }, 300);
        });
    },

    async loadConfig(filename) {
        return new Promise(resolve => {
            setTimeout(() => {
                const mappings = [
                    { button: 0, note: 60, velocity: 100 },
                    { button: 1, note: 62, velocity: 100 },
                    { button: 2, note: 64, velocity: 100 },
                    { button: 3, note: 67, velocity: 100 }
                ];
                resolve({ success: true, mappings });
            }, 300);
        });
    },

    async saveConfig(filename, mappings) {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({ success: true });
            }, 300);
        });
    },

    async deleteConfig(filename) {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({ success: true });
            }, 300);
        });
    },

    async getStatus() {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve({
                    wifi: { connected: true, ssid: 'HomeNet' },
                    bluetooth: { connected: false, advertising: true },
                    temperature: 42
                });
            }, 200);
        });
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
        
        state.modalResolve = resolve;
    });
}

function closeModal(confirmed) {
    const modal = document.getElementById('modal');
    const modalInput = document.getElementById('modal-input');
    const value = confirmed ? modalInput.value : null;
    
    modal.classList.remove('show');
    
    if (state.modalResolve) {
        state.modalResolve(value);
        state.modalResolve = null;
    }
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
    const menu = document.getElementById('theme-menu');
    menu.classList.remove('show');
}

function updateStatus(status) {
    const wifiDot = document.getElementById('wifi-status');
    const wifiText = document.getElementById('wifi-text');
    const btDot = document.getElementById('bluetooth-status');
    const btText = document.getElementById('bluetooth-text');
    const tempDot = document.getElementById('temp-status');
    const tempText = document.getElementById('temp-text');

    if (status.wifi && status.wifi.connected) {
        wifiDot.className = 'status-dot active';
        wifiText.textContent = `WiFi: ${status.wifi.ssid || 'Connected'}`;
    } else {
        wifiDot.className = 'status-dot';
        wifiText.textContent = 'WiFi: Disconnected';
    }

    if (status.bluetooth && status.bluetooth.advertising) {
        btDot.className = 'status-dot active';
        btText.textContent = `BLE: ${status.bluetooth.connected ? 'Connected' : 'Ready'}`;
    } else {
        btDot.className = 'status-dot';
        btText.textContent = 'BLE: Off';
    }

    if (status.temperature !== undefined) {
        tempDot.className = status.temperature > 60 ? 'status-dot warning' : 'status-dot active';
        tempText.textContent = `Temp: ${status.temperature}°C`;
    } else {
        tempDot.className = 'status-dot';
        tempText.textContent = 'Temp: --°C';
    }
}

function populateConfigList(configs) {
    const select = document.getElementById('config-select');
    select.innerHTML = configs.map(name => 
        `<option value="${name}">${name}</option>`
    ).join('');
    
    if (configs.length > 0 && !state.currentConfig) {
        state.currentConfig = configs[0];
        select.value = configs[0];
    }
}

function getMappingsFromUI() {
    const inputs = document.querySelectorAll('#button-mapping input');
    const mappings = [];
    
    for (let i = 0; i < 4; i++) {
        const note = document.querySelector(`input[data-button="${i}"][data-field="note"]`).value;
        const velocity = document.querySelector(`input[data-button="${i}"][data-field="velocity"]`).value;
        mappings.push({
            button: i,
            note: parseInt(note),
            velocity: parseInt(velocity)
        });
    }
    
    return mappings;
}

function setMappingsInUI(mappings) {
    mappings.forEach(mapping => {
        const noteInput = document.querySelector(`input[data-button="${mapping.button}"][data-field="note"]`);
        const velocityInput = document.querySelector(`input[data-button="${mapping.button}"][data-field="velocity"]`);
        
        if (noteInput) {
            noteInput.value = mapping.note;
            updateNoteDisplay(noteInput);
        }
        if (velocityInput) velocityInput.value = mapping.velocity || 100;
    });
}

function updateNoteDisplay(input) {
    const button = input.dataset.button;
    const displaySpan = document.getElementById(`note-display-${button}`);
    if (displaySpan) {
        displaySpan.textContent = midiToNoteName(parseInt(input.value));
    }
}

async function loadConfigList() {
    try {
        const configs = await API.getConfigs();
        state.configs = configs;
        populateConfigList(configs);
    } catch (error) {
        showToast('Failed to load config list', 'error');
    }
}

async function handleLoad() {
    const select = document.getElementById('config-select');
    const filename = select.value;
    
    if (!filename) {
        showToast('Select a config to load', 'error');
        return;
    }

    try {
        const data = await API.loadConfig(filename);
        state.currentConfig = filename;
        state.mappings = data.mappings;
        setMappingsInUI(data.mappings);
        showToast(`Loaded: ${filename}`);
    } catch (error) {
        showToast('Failed to load config', 'error');
    }
}

async function handleSave() {
    const select = document.getElementById('config-select');
    const filename = select.value;
    
    if (!filename) {
        showToast('Select a config to save', 'error');
        return;
    }

    const mappings = getMappingsFromUI();

    try {
        await API.saveConfig(filename, mappings);
        state.mappings = mappings;
        showToast(`Saved: ${filename}`);
    } catch (error) {
        showToast('Failed to save config', 'error');
    }
}

async function handleNew() {
    const name = await showModal('New Configuration', 'Config Name');
    
    if (!name) return;
    
    if (name === 'default') {
        showToast('Cannot use reserved name "default"', 'error');
        return;
    }

    const filename = name.endsWith('.pl_conf') ? name : `${name}.pl_conf`;
    const mappings = getMappingsFromUI();

    try {
        await API.saveConfig(filename, mappings);
        state.configs.push(filename);
        populateConfigList(state.configs);
        document.getElementById('config-select').value = filename;
        state.currentConfig = filename;
        showToast(`Created: ${filename}`);
    } catch (error) {
        showToast('Failed to create config', 'error');
    }
}

async function handleDelete() {
    const select = document.getElementById('config-select');
    const filename = select.value;
    
    if (!filename) {
        showToast('Select a config to delete', 'error');
        return;
    }

    if (filename === 'default.pl_conf') {
        showToast('Cannot delete default config', 'error');
        return;
    }

    const confirm = await showModal('Delete Configuration', 'Type DELETE to confirm', '');
    if (confirm !== 'DELETE') return;

    try {
        await API.deleteConfig(filename);
        state.configs = state.configs.filter(c => c !== filename);
        populateConfigList(state.configs);
        showToast(`Deleted: ${filename}`);
    } catch (error) {
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
    
    document.getElementById('load-btn').addEventListener('click', handleLoad);
    document.getElementById('save-btn').addEventListener('click', handleSave);
    document.getElementById('new-btn').addEventListener('click', handleNew);
    document.getElementById('delete-btn').addEventListener('click', handleDelete);
    
    document.getElementById('modal-cancel').addEventListener('click', () => closeModal(false));
    document.getElementById('modal-confirm').addEventListener('click', () => closeModal(true));
    
    document.getElementById('modal').addEventListener('click', (e) => {
        if (e.target.id === 'modal') closeModal(false);
    });
    
    document.getElementById('modal-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') closeModal(true);
        if (e.key === 'Escape') closeModal(false);
    });
    
    document.getElementById('theme-button').addEventListener('click', toggleThemeMenu);
    
    document.querySelectorAll('.theme-option').forEach(option => {
        option.addEventListener('click', () => {
            setTheme(option.dataset.theme);
            closeThemeMenu();
        });
    });
    
    document.addEventListener('click', (e) => {
        const themeSwitcher = document.querySelector('.theme-switcher');
        if (!themeSwitcher.contains(e.target)) {
            closeThemeMenu();
        }
    });
    
    document.querySelectorAll('input[data-field="note"]').forEach(input => {
        updateNoteDisplay(input);
        input.addEventListener('input', (e) => updateNoteDisplay(e.target));
    });

    loadConfigList();
    updateStatusPeriodic();
    setInterval(updateStatusPeriodic, 5000);
}

document.addEventListener('DOMContentLoaded', init);
