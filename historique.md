# Historique des erreurs et solutions — NASOMA

> Fichier vivant — mis à jour à chaque session de travail.
> Dernière mise à jour : 23 mai 2026

---

## 1. FLUTTER — Erreurs de chemins d'imports

### Erreur
```
Target of URI doesn't exist: '../models/scan_model.dart'
```

### Cause
Les modèles Dart sont dans `domain/models/` mais les providers et repositories importaient depuis `data/models/` (chemin inexistant).

### Structure réelle
```
features/<feature>/
  data/
    providers/      ← importent depuis ../../domain/models/
    repositories/   ← importent depuis ../../domain/models/
  domain/
    models/         ← EMPLACEMENT RÉEL des modèles
  presentation/
```

### Fix
- `scan_provider.dart` : `'../models/scan_model.dart'` → `'../../domain/models/scan_model.dart'`
- `session_provider.dart` : idem pour session et exercise models
- `session_repository_impl.dart` : idem
- `scan_repository_impl.dart` : idem
- `session_screen.dart` : `'../../session/data/models/exercise_model.dart'` → `'../../session/domain/models/exercise_model.dart'`
- `scan_screen.dart` : `'../data/models/scan_model.dart'` → `'../domain/models/scan_model.dart'`
- Tests : `'package:nasoma/features/scan/data/models/scan_model.dart'` → `'package:nasoma/features/scan/domain/models/scan_model.dart'`

### Règle à retenir
> Toujours placer les imports de modèles sur `domain/models/`, jamais `data/models/`.

---

## 2. FLUTTER — ChangeNotifier non importé dans app_router.dart

### Erreur
```
error - Classes can only extend other classes - app_router.dart:124
error - The method 'notifyListeners' isn't defined
```

### Cause
`_AuthStateNotifier extends ChangeNotifier` sans importer `flutter/foundation.dart`.

### Fix
Ajouter en tête de `app_router.dart` :
```dart
import 'package:flutter/foundation.dart';
```

---

## 3. FLUTTER — AuthNotifier perd le phoneNumber entre les écrans

### Erreur au runtime
```
"Numéro de téléphone manquant"
```

### Cause
Le `_phoneNumber` stocké dans `AuthNotifier` peut être perdu quand Riverpod redispose le provider entre `PhoneScreen` et `OtpScreen`. L'écran OTP ne repassait pas le phone au notifier.

### Fix
1. Dans `auth_provider.dart` — `verifyOtp` accepte un paramètre `phone` optionnel :
```dart
Future<void> verifyOtp(String otp, {String? phone}) async {
  if (phone != null) _phoneNumber = phone;
  ...
}
```
2. Dans `otp_screen.dart` — passer `widget.phone` :
```dart
await ref.read(authProvider.notifier).verifyOtp(_code, phone: widget.phone);
```

### Règle à retenir
> Ne jamais compter sur l'état d'un Riverpod StateNotifier pour passer des données entre deux écrans. Toujours re-passer les données critiques explicitement.

---

## 4. ANDROID — compileSdk doit être 36

### Erreur
```
Dependency ':image_picker_android' requires compileSdk >= 36
:app is currently compiled against android-34.
```

### Cause
`flutter build apk` avec Flutter 3.44 nécessite `compileSdk = 36`. Les plugins récents (`image_picker`, `shared_preferences`, `flutter_plugin_android_lifecycle`) compilent contre API 36.

### Fix dans `android/app/build.gradle.kts`
```kotlin
compileSdk = 36   // PAS flutter.compileSdkVersion, PAS 34
```

### À vérifier avant tout build APK
- Android SDK Platform 36 installé dans Android Studio SDK Manager
- `compileSdk = 36` dans `build.gradle.kts`

---

## 5. ANDROID — Dossier android/ absent

### Symptôme
`flutter build apk` échoue ou le dossier `android/` est absent.

### Cause
Le projet Flutter avait été créé sans la plateforme Android (mode web uniquement).

### Fix
```bash
flutter create --platforms=android .
```
Puis corriger le package name dans `build.gradle.kts` et `MainActivity.kt` :
- `com.example.nasoma` → `com.ckinnovation.nasoma`

---

## 6. ANDROID — Licences SDK non acceptées

### Erreur
```
Android license status unknown.
Run flutter doctor --android-licenses
```

### Fix sur Windows (interactif bloqué)
```bash
yes | flutter doctor --android-licenses
```
Si `yes` ne fonctionne pas :
```bash
"y`ny`ny`ny`ny`ny`n" | flutter doctor --android-licenses
```

---

## 7. ANDROID — minSdk pour ML Kit

### Règle
ML Kit Text Recognition requiert `minSdk = 21` minimum.

### Dans `build.gradle.kts`
```kotlin
defaultConfig {
    minSdk = 21   // ML Kit
    multiDexEnabled = true
}
```

---

## 8. ANDROID — Permissions AndroidManifest.xml

### Permissions obligatoires pour Nasoma
```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32"/>
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES"/>
<uses-permission android:name="android.permission.VIBRATE"/>
<uses-feature android:name="android.hardware.camera" android:required="false"/>
```

---

## 9. BACKEND — Imports circulaires dans auth.py

### Erreur potentielle
`from app.models.users import User` dupliqué après ajout de `from app.core.deps import get_current_user`.

### Règle
Toujours vérifier les imports existants avant d'en ajouter de nouveaux. Garder l'ordre alphabétique :
```python
from app.core.config import settings
from app.core.deps import get_current_user      # après config, avant security
from app.core.security import ...
from app.db.session import get_db
from app.models... import ...
from app.schemas... import ...
from app.services... import ...
```

---

## 10. ANDROID — Première build très longue (Gradle + NDK)

### Symptôme
Le premier `flutter build apk` prend 1h+ car Gradle télécharge :
- NDK (~500 Mo)
- CMake 3.22.1
- Build-Tools 36

### À retenir
- Les builds suivants sont rapides (tout est en cache)
- Ne jamais interrompre le premier build
- Utiliser `run_in_background` pour ne pas bloquer le terminal

---

## 11. PUBSPEC — json_annotation version

### Erreur
```
The version constraint "^4.8.1" on json_annotation allows versions before 4.12.0
```

### Fix dans `pubspec.yaml`
```yaml
json_annotation: ^4.12.0   # PAS ^4.8.1
```

---

## 12. SCAN SCREEN — Timeout réseau sur vrai device Android

### Erreur
```
The request connection took longer than 0:00:10.000000 and it was aborted.
```

### Cause
Deux problèmes combinés :
1. `ScanRepositoryImpl` n'avait pas de mode mock (contrairement à `AuthRepository`)
2. `10.0.2.2:8000` est l'adresse de l'émulateur Android — ne fonctionne **pas** sur un vrai device physique

### Fix
Ajouter le mode mock dans `scan_repository_impl.dart` :
```dart
import '../../../../core/env/env.dart';

@override
Future<Map<String, dynamic>> uploadScan(ScanModel scan) async {
  if (Env.useMockApi) {
    await Future.delayed(const Duration(milliseconds: 800));
    return {'scan_id': 'mock-scan-...', 'status': 'processing'};
  }
  // appel réel ...
}
```

### Règle à retenir
> Tout `Repository` doit avoir un bloc `if (Env.useMockApi)` pour pouvoir tester sans backend.
> Sur vrai device Android, l'adresse du backend est l'IP locale du PC (ex: `192.168.1.X:8000`), pas `10.0.2.2`.
> `10.0.2.2` = emulateur uniquement.

---

*CK Innovation SARL — kader@ckinnovation.fr*
