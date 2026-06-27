"""
ZEUS BOT WEB - SERVIDOR FLASK
Ejecuta: python app.py
Luego abre en el navegador: http://localhost:5000
"""

import sys
import os
import threading
import time
import webbrowser

# Añadir directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json

# Importar el bot
from bot import ZeusBot, PARES_FIJOS

app = Flask(__name__)
CORS(app)

# Instancia del bot
zeus_bot = ZeusBot()

# ==================== RUTAS ====================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Servir archivos estáticos"""
    return send_from_directory('static', path)

@app.route('/api/conectar', methods=['POST'])
def api_conectar():
    """Conectar a IQ Option"""
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Faltan credenciales'})
    
    result = zeus_bot.conectar(email, password)
    return jsonify({'success': result})

@app.route('/api/modo', methods=['POST'])
def api_modo():
    """Cambiar modo"""
    data = request.json
    modo = data.get('modo', 'DEMO')
    zeus_bot.cambiar_modo(modo)
    return jsonify({'success': True})

@app.route('/api/iniciar', methods=['POST'])
def api_iniciar():
    """Iniciar bot"""
    data = request.json
    zeus_bot.iniciar(data)
    return jsonify({'success': True})

@app.route('/api/detener', methods=['POST'])
def api_detener():
    """Detener bot"""
    zeus_bot.detener()
    return jsonify({'success': True})

@app.route('/api/pares', methods=['GET'])
def api_pares():
    """Obtener pares"""
    return jsonify(PARES_FIJOS)

@app.route('/api/balance', methods=['GET'])
def api_balance():
    """Obtener balance"""
    balance = zeus_bot.bot.get_balance() if zeus_bot.bot else 0
    return jsonify({'balance': balance})

@app.route('/api/estado', methods=['GET'])
def api_estado():
    """Obtener estado del bot"""
    return jsonify({
        'activo': zeus_bot.actualizando,
        'conectado': zeus_bot.bot.connected if zeus_bot.bot else False
    })

# ==================== EVENTOS SSE (Server-Sent Events) ====================

from flask import Response
import queue

# Cola de eventos para enviar al cliente
event_queue = queue.Queue()

def event_stream():
    """Stream de eventos para el cliente"""
    while True:
        try:
            # Esperar evento con timeout
            event = event_queue.get(timeout=1)
            yield f"data: {json.dumps(event)}\n\n"
        except queue.Empty:
            # Heartbeat para mantener conexión
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except GeneratorExit:
            break

@app.route('/api/events')
def events():
    """Endpoint para eventos SSE"""
    return Response(event_stream(), mimetype="text/event-stream")

# ==================== CALLBACKS PARA EVENTOS ====================

def enviar_evento(tipo, data):
    """Enviar evento a todos los clientes conectados"""
    try:
        event_queue.put({'type': tipo, 'data': data})
    except:
        pass

# Registrar callbacks en el bot
def callback_log(mensaje, tipo):
    enviar_evento('log', {'mensaje': mensaje, 'tipo': tipo})

def callback_balance(balance):
    enviar_evento('balance', balance)

def callback_stats(stats):
    enviar_evento('stats', stats)

def callback_estado(activo):
    enviar_evento('estado', activo)

def callback_ultima(ultima):
    enviar_evento('ultima', ultima)

# Registrar callbacks en zeus_bot
zeus_bot.on("log", callback_log)
zeus_bot.on("balance", callback_balance)
zeus_bot.on("stats", callback_stats)
zeus_bot.on("estado", callback_estado)
zeus_bot.on("ultima", callback_ultima)

# ==================== INICIAR ====================

def abrir_navegador():
    """Abrir navegador después de un retraso"""
    time.sleep(2)
    try:
        webbrowser.open('http://localhost:5000')
    except:
        pass

if __name__ == "__main__":
    print("=" * 50)
    print("⚡ ZEUS BOT WEB (FLASK)")
    print("=" * 50)
    print("🌐 Servidor en: http://localhost:5000")
    print("📱 Desde el móvil usa la IP de tu PC")
    print("=" * 50)
    print("")
    print("🔄 Abriendo navegador...")
    print("")
    
    # Abrir navegador automáticamente
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)