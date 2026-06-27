#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZEUS BOT - Versión Android
Punto de entrada para Kivy con WebView
"""

import os
import sys
import threading
import time
import json
import subprocess
from datetime import datetime

# Configurar entorno
os.environ['KIVY_NO_FILELOG'] = '1'
os.environ['KIVY_NO_CONSOLELOG'] = '0'

# Importar Kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.webview import WebView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# Importar el servidor Flask
try:
    import app
    import bot
    print("✅ Módulos importados correctamente")
except Exception as e:
    print(f"❌ Error importando módulos: {e}")

# ==================== VARIABLES GLOBALES ====================
servidor_iniciado = False
webview = None

# ==================== CLASE PRINCIPAL ====================
class ZeusBotApp(App):
    def build(self):
        # Configurar ventana
        Window.clearcolor = get_color_from_hex('#0a0a1a')
        Window.size = (420, 780)
        
        # Layout principal
        layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Header nativo
        header = BoxLayout(
            size_hint_y=0.08, 
            padding=[10, 5, 10, 5],
            spacing=8,
            background_color=get_color_from_hex('#12122a')
        )
        
        # Título
        title = Label(
            text='⚡ ZEUS BOT',
            font_size='22sp',
            bold=True,
            color=get_color_from_hex('#ffd700'),
            size_hint_x=0.6,
            halign='left'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        # Botón Recargar
        reload_btn = Button(
            text='↻',
            size_hint_x=0.15,
            background_color=get_color_from_hex('#1a1a3a'),
            font_size='20sp',
            color=get_color_from_hex('#ffffff')
        )
        reload_btn.bind(on_press=self.reload_webview)
        header.add_widget(reload_btn)
        
        # Botón Salir
        exit_btn = Button(
            text='✕',
            size_hint_x=0.15,
            background_color=get_color_from_hex('#cc2244'),
            font_size='20sp',
            color=get_color_from_hex('#ffffff')
        )
        exit_btn.bind(on_press=self.exit_app)
        header.add_widget(exit_btn)
        
        layout.add_widget(header)
        
        # WebView (ocupa el resto de la pantalla)
        global webview
        webview = WebView(
            url='http://localhost:5000',
            size_hint_y=0.92
        )
        layout.add_widget(webview)
        
        # Iniciar servidor Flask en hilo separado
        threading.Thread(target=self.iniciar_servidor, daemon=True).start()
        
        # Verificar servidor
        Clock.schedule_interval(self.verificar_servidor, 3.0)
        
        print("✅ ZEUS BOT iniciado en Android")
        print("📱 Abriendo: http://localhost:5000")
        
        return layout
    
    def iniciar_servidor(self):
        """Inicia el servidor Flask"""
        global servidor_iniciado
        
        try:
            print("🚀 Iniciando servidor Flask...")
            
            # Importar app
            from app import app as flask_app
            
            # Iniciar servidor en hilo principal del Flask
            flask_app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
                threaded=True,
                use_reloader=False
            )
            
        except Exception as e:
            print(f"❌ Error en servidor: {e}")
            time.sleep(5)
    
    def verificar_servidor(self, dt):
        """Verifica que el servidor esté corriendo"""
        global webview, servidor_iniciado
        
        try:
            import requests
            response = requests.get('http://localhost:5000', timeout=2)
            if response.status_code == 200:
                if not servidor_iniciado:
                    servidor_iniciado = True
                    print("✅ Servidor listo")
                    if webview:
                        Clock.schedule_once(lambda dt: webview.reload(), 0.5)
        except:
            if servidor_iniciado:
                servidor_iniciado = False
                print("⏳ Servidor no disponible...")
    
    def reload_webview(self, instance):
        """Recarga el WebView"""
        global webview
        try:
            if webview:
                webview.reload()
                print("🔄 WebView recargado")
        except Exception as e:
            print(f"❌ Error recargando: {e}")
    
    def exit_app(self, instance):
        """Sale de la aplicación"""
        print("👋 Cerrando ZEUS BOT...")
        try:
            import requests
            requests.post('http://localhost:5000/shutdown', timeout=1)
        except:
            pass
        self.stop()

# ==================== MAIN ====================
if __name__ == '__main__':
    try:
        print("=" * 50)
        print("⚡ ZEUS BOT - ANDROID")
        print("=" * 50)
        print("📱 Cargando aplicación...")
        print("=" * 50)
        
        # Crear directorios necesarios
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static', exist_ok=True)
        
        # Iniciar app
        ZeusBotApp().run()
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona ENTER para salir...")
