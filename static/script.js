// ==================== ESTADO ====================
let estado = {
    conectado: false,
    bot_activo: false,
    balance: 0,
    ops: 0,
    wins: 0,
    losses: 0,
    profit: 0,
    racha: 0
};

// ==================== DOM REFS ====================
const $ = (id) => document.getElementById(id);

const dom = {
    led: $('led'),
    modo: $('modo'),
    balance: $('balance'),
    email: $('email'),
    password: $('password'),
    btnConectar: $('btn-conectar'),
    estadoConexion: $('estado-conexion'),
    loginSection: $('login-section'),
    configSection: $('config-section'),
    parSelect: $('par-select'),
    monto: $('monto'),
    tiempo: $('tiempo'),
    martingala: $('martingala'),
    multiplicador: $('multiplicador'),
    umbral: $('umbral'),
    btnIniciar: $('btn-iniciar'),
    btnDetener: $('btn-detener'),
    ops: $('ops'),
    winrate: $('winrate'),
    gp: $('gp'),
    racha: $('racha'),
    profit: $('profit'),
    enfoque: $('enfoque'),
    ultima: $('ultima'),
    logContent: $('log-content')
};

// ==================== PARES ====================
fetch('/api/pares')
    .then(r => r.json())
    .then(pares => {
        pares.forEach(par => {
            const option = document.createElement('option');
            option.value = par;
            option.textContent = par;
            dom.parSelect.appendChild(option);
        });
    });

// ==================== LOG ====================
function log(mensaje, tipo = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-entry log-${tipo}`;
    const time = new Date().toLocaleTimeString();
    entry.textContent = `[${time}] ${mensaje}`;
    dom.logContent.appendChild(entry);
    dom.logContent.scrollTop = dom.logContent.scrollHeight;
    
    while (dom.logContent.children.length > 50) {
        dom.logContent.removeChild(dom.logContent.firstChild);
    }
}

// ==================== CONEXIÓN ====================
dom.btnConectar.addEventListener('click', () => {
    const email = dom.email.value.trim();
    const password = dom.password.value.trim();
    
    if (!email || !password) {
        dom.estadoConexion.textContent = '⚠️ Ingresa usuario y contraseña';
        dom.estadoConexion.style.color = '#ff3355';
        return;
    }
    
    dom.btnConectar.disabled = true;
    dom.btnConectar.textContent = '⏳ CONECTANDO...';
    dom.estadoConexion.textContent = '🔄 Conectando...';
    dom.estadoConexion.style.color = '#ffcc00';
    
    fetch('/api/conectar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    })
    .then(r => r.json())
    .then(data => {
        dom.btnConectar.disabled = false;
        dom.btnConectar.textContent = '⚡ CONECTAR';
        
        if (data.success) {
            estado.conectado = true;
            dom.estadoConexion.textContent = '✅ Conectado!';
            dom.estadoConexion.style.color = '#00ff88';
            dom.loginSection.style.display = 'none';
            dom.configSection.style.display = 'block';
            dom.led.className = 'led off';
            actualizarBalance();
        } else {
            dom.estadoConexion.textContent = '❌ Error de conexión';
            dom.estadoConexion.style.color = '#ff3355';
        }
    })
    .catch(err => {
        dom.btnConectar.disabled = false;
        dom.btnConectar.textContent = '⚡ CONECTAR';
        dom.estadoConexion.textContent = '❌ Error de red';
        dom.estadoConexion.style.color = '#ff3355';
    });
});

// ==================== MODO ====================
dom.modo.addEventListener('click', () => {
    const nuevo = dom.modo.textContent === 'DEMO' ? 'REAL' : 'DEMO';
    dom.modo.textContent = nuevo;
    
    fetch('/api/modo', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({modo: nuevo})
    });
    
    log(`🔄 Modo cambiado a ${nuevo}`, 'info');
});

// ==================== BALANCE ====================
function actualizarBalance() {
    fetch('/api/balance')
        .then(r => r.json())
        .then(data => {
            estado.balance = data.balance || 0;
            dom.balance.textContent = `$${estado.balance.toFixed(2)}`;
        })
        .catch(() => {});
}

// ==================== BOT ====================
dom.btnIniciar.addEventListener('click', () => {
    if (!estado.conectado) {
        log('❌ No conectado a IQ Option', 'error');
        return;
    }
    
    const config = {
        par: dom.parSelect.value,
        monto: dom.monto.value,
        tiempo: dom.tiempo.value,
        martingala: dom.martingala.value,
        multiplicador: dom.multiplicador.value,
        umbral: dom.umbral.value
    };
    
    dom.btnIniciar.disabled = true;
    dom.btnDetener.disabled = false;
    dom.led.className = 'led on';
    estado.bot_activo = true;
    
    fetch('/api/iniciar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(config)
    });
});

dom.btnDetener.addEventListener('click', () => {
    dom.btnIniciar.disabled = false;
    dom.btnDetener.disabled = true;
    dom.led.className = 'led off';
    estado.bot_activo = false;
    
    fetch('/api/detener', {method: 'POST'});
});

// ==================== EVENTOS SSE ====================
function conectarEventos() {
    const eventSource = new EventSource('/api/events');
    
    eventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'log':
                    log(data.data.mensaje, data.data.tipo);
                    break;
                    
                case 'balance':
                    estado.balance = data.data;
                    dom.balance.textContent = `$${estado.balance.toFixed(2)}`;
                    break;
                    
                case 'stats':
                    const s = data.data;
                    estado.ops = s.ops || 0;
                    estado.wins = s.wins || 0;
                    estado.losses = s.losses || 0;
                    estado.profit = s.profit || 0;
                    estado.racha = s.racha || 0;
                    
                    dom.ops.textContent = estado.ops;
                    dom.gp.textContent = `${estado.wins}/${estado.losses}`;
                    dom.racha.textContent = estado.racha;
                    
                    const winrate = estado.ops > 0 ? Math.round((estado.wins / estado.ops) * 100) : 0;
                    dom.winrate.textContent = `${winrate}%`;
                    
                    const profitEl = dom.profit;
                    profitEl.textContent = `$${estado.profit.toFixed(2)}`;
                    profitEl.className = estado.profit >= 0 ? 'profit-positive' : 'profit-negative';
                    break;
                    
                case 'estado':
                    estado.bot_activo = data.data;
                    dom.led.className = data.data ? 'led on' : 'led off';
                    dom.btnIniciar.disabled = data.data;
                    dom.btnDetener.disabled = !data.data;
                    break;
                    
                case 'ultima':
                    dom.ultima.textContent = data.data;
                    break;
                    
                case 'ping':
                    // Heartbeat
                    break;
            }
        } catch(e) {
            // Ignorar errores de parseo
        }
    };
    
    eventSource.onerror = function() {
        // Reintentar después de 3 segundos
        setTimeout(conectarEventos, 3000);
    };
}

// ==================== INICIO ====================
log('⚡ ZEUS BOT WEB (FLASK)', 'info');
log('💡 Conéctate a IQ Option para comenzar', 'info');
log('📊 Estrategia: Bandas Bollinger (MACD CRUCE)', 'info');

// Conectar eventos
conectarEventos();

// Actualizar balance periódicamente
setInterval(actualizarBalance, 5000);
