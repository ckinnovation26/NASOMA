import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _kAccessToken = 'auth_access_token';
const _kUserId = 'auth_user_id';

class TokenStorage {
  const TokenStorage(this._prefs);
  final SharedPreferences _prefs;

  String? get accessToken => _prefs.getString(_kAccessToken);
  String? get userId => _prefs.getString(_kUserId);
  bool get hasToken => accessToken != null && accessToken!.isNotEmpty;

  Future<void> save({required String token, required String userId}) async {
    await _prefs.setString(_kAccessToken, token);
    await _prefs.setString(_kUserId, userId);
  }

  Future<void> clear() async {
    await _prefs.remove(_kAccessToken);
    await _prefs.remove(_kUserId);
  }
}

final tokenStorageProvider = Provider<TokenStorage>((ref) {
  throw UnimplementedError('Initialise TokenStorage via ProviderScope overrides');
});
