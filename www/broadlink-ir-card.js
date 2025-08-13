/**
 * Broadlink IR Manager Card
 * Custom Lovelace card para gerenciar códigos IR
 */

class BroadlinkIRCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._config = {};
    this._hass = {};
    this._learningTimeout = null;
    this._lastCode = null;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Você precisa definir uma entidade');
    }
    this._config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.updateContent();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: var(--paper-font-body1_-_font-family);
        }
        
        ha-card {
          padding: 16px;
          background: var(--card-background-color);
          border-radius: var(--ha-card-border-radius);
          box-shadow: var(--ha-card-box-shadow);
        }
        
        .card-header {
          display: flex;
          align-items: center;
          margin-bottom: 16px;
          font-size: 1.2em;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        
        .card-header ha-icon {
          margin-right: 8px;
          color: var(--primary-color);
        }
        
        .status-section {
          margin-bottom: 20px;
          padding: 12px;
          background: var(--secondary-background-color);
          border-radius: 8px;
        }
        
        .status-indicator {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
        }
        
        .status-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          margin-right: 8px;
          transition: all 0.3s ease;
        }
        
        .status-dot.idle {
          background-color: #4caf50;
        }
        
        .status-dot.learning {
          background-color: #ff9800;
          animation: pulse 1.5s infinite;
        }
        
        .status-dot.code-received {
          background-color: #2196f3;
        }
        
        @keyframes pulse {
          0% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.2); }
          100% { opacity: 1; transform: scale(1); }
        }
        
        .controls-section {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 20px;
        }
        
        .control-button {
          padding: 12px 16px;
          border: none;
          border-radius: 8px;
          background: var(--primary-color);
          color: white;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }
        
        .control-button:hover {
          background: var(--primary-color-dark);
          transform: translateY(-1px);
        }
        
        .control-button:disabled {
          background: var(--disabled-color);
          cursor: not-allowed;
          transform: none;
        }
        
        .control-button.secondary {
          background: var(--secondary-color);
        }
        
        .control-button.danger {
          background: #f44336;
        }
        
        .code-section {
          margin-bottom: 20px;
        }
        
        .code-display {
          background: var(--code-editor-background-color, #1e1e1e);
          color: var(--code-editor-text-color, #d4d4d4);
          padding: 16px;
          border-radius: 8px;
          font-family: 'Courier New', monospace;
          font-size: 12px;
          line-height: 1.4;
          overflow-x: auto;
          white-space: pre-wrap;
          word-break: break-all;
          border: 1px solid var(--divider-color);
        }
        
        .code-label {
          font-weight: 500;
          margin-bottom: 8px;
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .copy-button {
          padding: 4px 8px;
          font-size: 12px;
          background: var(--primary-color);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .save-section {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
          margin-bottom: 12px;
        }
        
        .input-field {
          padding: 8px 12px;
          border: 1px solid var(--divider-color);
          border-radius: 4px;
          background: var(--card-background-color);
          color: var(--primary-text-color);
          font-size: 14px;
        }
        
        .input-field:focus {
          outline: none;
          border-color: var(--primary-color);
        }
        
        .save-button {
          grid-column: 1 / -1;
          padding: 10px;
          background: var(--success-color, #4caf50);
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }
        
        .database-section {
          border-top: 1px solid var(--divider-color);
          padding-top: 16px;
        }
        
        .database-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 12px;
          margin-bottom: 16px;
        }
        
        .stat-item {
          text-align: center;
          padding: 12px;
          background: var(--secondary-background-color);
          border-radius: 8px;
        }
        
        .stat-value {
          font-size: 1.5em;
          font-weight: bold;
          color: var(--primary-color);
        }
        
        .stat-label {
          font-size: 0.9em;
          color: var(--secondary-text-color);
          margin-top: 4px;
        }
        
        .recent-codes {
          max-height: 200px;
          overflow-y: auto;
        }
        
        .code-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 12px;
          margin-bottom: 4px;
          background: var(--secondary-background-color);
          border-radius: 4px;
          font-size: 14px;
        }
        
        .code-info {
          flex: 1;
        }
        
        .code-name {
          font-weight: 500;
          color: var(--primary-text-color);
        }
        
        .code-device {
          font-size: 12px;
          color: var(--secondary-text-color);
        }
        
        .hidden {
          display: none;
        }
        
        .loading {
          opacity: 0.6;
          pointer-events: none;
        }
      </style>
      
      <ha-card>
        <div class="card-header">
          <ha-icon icon="mdi:remote"></ha-icon>
          Broadlink IR Manager
        </div>
        
        <div class="status-section">
          <div class="status-indicator">
            <div class="status-dot idle" id="statusDot"></div>
            <span id="statusText">Aguardando...</span>
          </div>
          <div id="deviceInfo" class="device-info"></div>
        </div>
        
        <div class="controls-section">
          <button class="control-button" id="startLearning">
            <ha-icon icon="mdi:play"></ha-icon>
            Iniciar Learning
          </button>
          <button class="control-button secondary" id="stopLearning" disabled>
            <ha-icon icon="mdi:stop"></ha-icon>
            Parar Learning
          </button>
          <button class="control-button" id="getCode">
            <ha-icon icon="mdi:download"></ha-icon>
            Obter Código
          </button>
          <button class="control-button secondary" id="refreshData">
            <ha-icon icon="mdi:refresh"></ha-icon>
            Atualizar
          </button>
        </div>
        
        <div class="code-section" id="codeSection">
          <div class="code-label">
            Código Base64:
            <button class="copy-button" id="copyBase64">Copiar</button>
          </div>
          <div class="code-display" id="base64Display">Nenhum código capturado</div>
          
          <div class="code-label">
            Código Pronto Hex:
            <button class="copy-button" id="copyPronto">Copiar</button>
          </div>
          <div class="code-display" id="prontoDisplay">Nenhum código convertido</div>
          
          <div class="save-section" id="saveSection" style="display: none;">
            <input type="text" class="input-field" id="codeName" placeholder="Nome do código">
            <input type="text" class="input-field" id="deviceName" placeholder="Dispositivo">
            <input type="text" class="input-field" id="commandName" placeholder="Comando">
            <input type="text" class="input-field" id="codeNotes" placeholder="Notas (opcional)">
            <button class="save-button" id="saveCode">Salvar na Base de Dados</button>
          </div>
        </div>
        
        <div class="database-section">
          <div class="code-label">Base de Dados IR</div>
          <div class="database-stats" id="databaseStats">
            <div class="stat-item">
              <div class="stat-value" id="totalCodes">0</div>
              <div class="stat-label">Códigos</div>
            </div>
            <div class="stat-item">
              <div class="stat-value" id="totalDevices">0</div>
              <div class="stat-label">Dispositivos</div>
            </div>
          </div>
          <div class="recent-codes" id="recentCodes"></div>
        </div>
      </ha-card>
    `;
    
    this.setupEventListeners();
  }

  setupEventListeners() {
    const startBtn = this.shadowRoot.getElementById('startLearning');
    const stopBtn = this.shadowRoot.getElementById('stopLearning');
    const getCodeBtn = this.shadowRoot.getElementById('getCode');
    const refreshBtn = this.shadowRoot.getElementById('refreshData');
    const copyBase64Btn = this.shadowRoot.getElementById('copyBase64');
    const copyProntoBtn = this.shadowRoot.getElementById('copyPronto');
    const saveBtn = this.shadowRoot.getElementById('saveCode');

    startBtn.addEventListener('click', () => this.startLearning());
    stopBtn.addEventListener('click', () => this.stopLearning());
    getCodeBtn.addEventListener('click', () => this.getLearnedCode());
    refreshBtn.addEventListener('click', () => this.refreshData());
    copyBase64Btn.addEventListener('click', () => this.copyToClipboard('base64'));
    copyProntoBtn.addEventListener('click', () => this.copyToClipboard('pronto'));
    saveBtn.addEventListener('click', () => this.saveCode());
  }

  updateContent() {
    if (!this._hass || !this._config.entity) return;

    const entity = this._hass.states[this._config.entity];
    if (!entity) return;

    this.updateStatus(entity);
    this.updateCodeDisplay(entity);
    this.updateDatabaseStats();
  }

  updateStatus(entity) {
    const statusDot = this.shadowRoot.getElementById('statusDot');
    const statusText = this.shadowRoot.getElementById('statusText');
    const deviceInfo = this.shadowRoot.getElementById('deviceInfo');
    const startBtn = this.shadowRoot.getElementById('startLearning');
    const stopBtn = this.shadowRoot.getElementById('stopLearning');

    const state = entity.state;
    const attrs = entity.attributes;

    // Atualiza indicador de status
    statusDot.className = `status-dot ${state}`;
    
    switch (state) {
      case 'idle':
        statusText.textContent = 'Pronto para capturar';
        startBtn.disabled = false;
        stopBtn.disabled = true;
        break;
      case 'learning':
        statusText.textContent = 'Modo learning ativo - aponte o controle';
        startBtn.disabled = true;
        stopBtn.disabled = false;
        break;
      case 'code_received':
        statusText.textContent = 'Código capturado com sucesso!';
        startBtn.disabled = false;
        stopBtn.disabled = true;
        break;
      default:
        statusText.textContent = 'Status desconhecido';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }

    // Atualiza informações do dispositivo
    if (attrs.device_connected) {
      deviceInfo.innerHTML = `
        <small>Conectado: ${attrs.host || 'Auto-descoberto'}</small>
      `;
    } else {
      deviceInfo.innerHTML = '<small style="color: var(--error-color);">Dispositivo desconectado</small>';
    }
  }

  updateCodeDisplay(entity) {
    const codeEntity = this._hass.states[this._config.entity.replace('_status', '_last_code')];
    if (!codeEntity) return;

    const base64Display = this.shadowRoot.getElementById('base64Display');
    const prontoDisplay = this.shadowRoot.getElementById('prontoDisplay');
    const saveSection = this.shadowRoot.getElementById('saveSection');

    const attrs = codeEntity.attributes;

    if (attrs.base64_code) {
      base64Display.textContent = attrs.base64_code;
      prontoDisplay.textContent = attrs.pronto_code || 'Erro na conversão';
      saveSection.style.display = 'grid';
      this._lastCode = {
        base64: attrs.base64_code,
        pronto: attrs.pronto_code,
        frequency: attrs.frequency
      };
    } else {
      base64Display.textContent = 'Nenhum código capturado';
      prontoDisplay.textContent = 'Nenhum código convertido';
      saveSection.style.display = 'none';
      this._lastCode = null;
    }
  }

  updateDatabaseStats() {
    const dbEntity = this._hass.states[this._config.entity.replace('_status', '_database')];
    if (!dbEntity) return;

    const totalCodes = this.shadowRoot.getElementById('totalCodes');
    const totalDevices = this.shadowRoot.getElementById('totalDevices');
    const recentCodes = this.shadowRoot.getElementById('recentCodes');

    const attrs = dbEntity.attributes;

    totalCodes.textContent = dbEntity.state || '0';
    totalDevices.textContent = attrs.total_devices || '0';

    // Atualiza códigos recentes
    if (attrs.recent_codes && attrs.recent_codes.length > 0) {
      recentCodes.innerHTML = attrs.recent_codes.map(code => `
        <div class="code-item">
          <div class="code-info">
            <div class="code-name">${code.name}</div>
            <div class="code-device">${code.device} - ${code.command}</div>
          </div>
        </div>
      `).join('');
    } else {
      recentCodes.innerHTML = '<div style="text-align: center; color: var(--secondary-text-color); padding: 20px;">Nenhum código salvo</div>';
    }
  }

  async startLearning() {
    try {
      await this._hass.callService('broadlink_ir_manager', 'start_learning', {
        entity_id: this._config.entity,
        timeout: 30
      });
    } catch (error) {
      console.error('Erro ao iniciar learning:', error);
    }
  }

  async stopLearning() {
    try {
      await this._hass.callService('broadlink_ir_manager', 'stop_learning', {});
    } catch (error) {
      console.error('Erro ao parar learning:', error);
    }
  }

  async getLearnedCode() {
    try {
      await this._hass.callService('broadlink_ir_manager', 'get_learned_code', {});
    } catch (error) {
      console.error('Erro ao obter código:', error);
    }
  }

  async refreshData() {
    try {
      await this._hass.callService('homeassistant', 'update_entity', {
        entity_id: this._config.entity
      });
    } catch (error) {
      console.error('Erro ao atualizar dados:', error);
    }
  }

  async copyToClipboard(type) {
    if (!this._lastCode) return;

    const text = type === 'base64' ? this._lastCode.base64 : this._lastCode.pronto;
    
    try {
      await navigator.clipboard.writeText(text);
      // Feedback visual
      const button = this.shadowRoot.getElementById(type === 'base64' ? 'copyBase64' : 'copyPronto');
      const originalText = button.textContent;
      button.textContent = 'Copiado!';
      setTimeout(() => {
        button.textContent = originalText;
      }, 2000);
    } catch (error) {
      console.error('Erro ao copiar:', error);
    }
  }

  async saveCode() {
    const name = this.shadowRoot.getElementById('codeName').value;
    const device = this.shadowRoot.getElementById('deviceName').value;
    const command = this.shadowRoot.getElementById('commandName').value;
    const notes = this.shadowRoot.getElementById('codeNotes').value;

    if (!name || !device || !command || !this._lastCode) {
      alert('Preencha todos os campos obrigatórios');
      return;
    }

    try {
      await this._hass.callService('broadlink_ir_manager', 'save_code', {
        name: name,
        device: device,
        command: command,
        base64_code: this._lastCode.base64,
        notes: notes
      });

      // Limpa campos
      this.shadowRoot.getElementById('codeName').value = '';
      this.shadowRoot.getElementById('deviceName').value = '';
      this.shadowRoot.getElementById('commandName').value = '';
      this.shadowRoot.getElementById('codeNotes').value = '';

      // Atualiza estatísticas
      setTimeout(() => this.refreshData(), 1000);

    } catch (error) {
      console.error('Erro ao salvar código:', error);
      alert('Erro ao salvar código');
    }
  }

  getCardSize() {
    return 8;
  }

  getGridOptions() {
    return {
      rows: 8,
      columns: 12,
      min_rows: 6,
      max_rows: 10,
    };
  }
}

customElements.define('broadlink-ir-card', BroadlinkIRCard);

