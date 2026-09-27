[app]

title = PetPal Assistant
package.name = petpalassistant
package.domain = org.petpal

source.dir = .
source.include_exts = py,kv,png,jpg,atlas,json

version = 0.1.0

requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

# icon.filename = %(source.dir)s/icon.png
# (uncomment and add a 512x512 icon.png to the repo root if you want a
# custom app icon; buildozer falls back to a default icon otherwise)

[buildozer]

log_level = 2
warn_on_root = 1

[app:android]

android.permissions = INTERNET
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
