[app]

# (str) Title of your application
title = ZEUS BOT

# (str) Package name
package.name = zeusbot

# (str) Package domain (needed for android/ios packaging)
package.domain = org.zeus

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,html,css,js

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec

# (list) List of directory names to not include at all
source.exclude_dirs = tests, bin, build, dist, .git, __pycache__

# (list) Android specific libraries to include
android.include_libs = 

# (list) Java classes to add to the project
android.add_src = 

# (list) permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, WRITE_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 30

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version
android.sdk = 30

# (str) Android NDK version to use
android.ndk = 23b

# (bool) Use --private data storage
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path = 

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
android.sdk_path = 

# (str) ANT directory (if empty, it will be automatically downloaded.)
android.ant_path = 

# (bool) If True, then openssl will be included
android.include_openssl = True

# (bool) If True, then the Python interpreter will be statically linked
android.static_link_python = True

# (str) Python for android distribution to use
android.python_arch = arm64-v8a

# (list) Python for android requirements
requirements = python3,kivy,kivymd,flask,flask-cors,numpy,iqoptionapi,requests

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (bool) Whether to allow Android to start Java services
android.allow_background_service_usage = True

# (str) launch.py to use instead of the default one
android.launcher = 

# (bool) Whether to use the old Python for Android (legacy) or the new (SDL2)
android.new = True

# (str) Orientation of app, choices: landscape, portrait, sensor
orientation = portrait

# (bool) Indicates whether the app should be fullscreen or not
fullscreen = 1

# (bool) If True, the status bar will be hidden
android.statusbar_hide = True

# (str) Window size (width x height) - SOLO UNA VEZ
window.size = 420x800

# (bool) Enable/disable focus on touch
android.focus_on_touch = True

# (bool) Enable/disable touch events
android.touch_events = True

# (bool) Enable/disable the use of the Android on-screen keyboard
android.use_activity_keyboard = True

# (bool) Enable/disable the use of the Android back button
android.back_button = True

# (str) The Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Enable/disable the display of the logcat on the screen
android.logcat_on_screen = False

# (str) The Android SDK built tools to use
android.sdk_build_tools = 

# (str) The Java version to use
android.java_version = 11

# ==================== KIVY PROPERTIES ====================
# (Opcional) Configuraciones adicionales de Kivy
window.title = ZEUS BOT
window.icon = 
window.fullscreen = False
window.resizable = False
window.borderless = False
window.statusbar = True
window.toolbar = True
window.mouse = True
window.touch = True
window.multitouch = True
window.screensaver = True

# ==================== IOS PROPERTIES ====================
ios.title = ZEUS BOT
ios.name = ZEUS BOT
ios.bundle = org.zeus.zeusbot
ios.version = 1.0.0
ios.build = 1
ios.copyright = Copyright (c) 2026
ios.required_devices = iphone, ipad
ios.min_ios_version = 10.0
ios.camera = False
ios.photo_library = False
ios.location = False
ios.push_notifications = False

# ==================== DEPLOYMENT ====================
deploy.dir = deploy
deploy.system_python = False
deploy.log = deploy.log
deploy.error_log = deploy_error.log
