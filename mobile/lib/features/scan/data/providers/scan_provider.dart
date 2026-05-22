import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/scan_model.dart';

enum ScanUploadState {
  idle,
  uploading,
  polling,
  completed,
  error,
}

class ScanNotifier extends StateNotifier<ScanUploadState> {
  ScanNotifier() : super(ScanUploadState.idle);

  ScanModel? _currentScan;
  String? _errorMessage;
  int _pollAttempts = 0;
  static const int _maxPollAttempts = 30; // ~5 min avec 10s interval

  ScanModel? get currentScan => _currentScan;
  String? get errorMessage => _errorMessage;
  bool get isUploading => state == ScanUploadState.uploading;
  bool get isPolling => state == ScanUploadState.polling;
  bool get isCompleted => state == ScanUploadState.completed;

  Future<void> setScan(ScanModel scan) async {
    _currentScan = scan;
    _errorMessage = null;
    state = ScanUploadState.idle;
  }

  Future<void> startUpload() async {
    if (_currentScan == null) {
      _errorMessage = 'Aucun scan à uploader';
      state = ScanUploadState.error;
      return;
    }

    state = ScanUploadState.uploading;
    _errorMessage = null;
    // appel à repository se fera via un autre provider (voir M6)
  }

  Future<void> startPolling() async {
    if (_currentScan == null) {
      _errorMessage = 'Aucun scan à sonder';
      state = ScanUploadState.error;
      return;
    }

    state = ScanUploadState.polling;
    _pollAttempts = 0;
    _errorMessage = null;
    // polling logic se fera via un autre provider (voir M6)
  }

  void setScanCompleted(ScanModel completedScan) {
    _currentScan = completedScan;
    state = ScanUploadState.completed;
  }

  void setPollingError(String message) {
    _errorMessage = message;
    state = ScanUploadState.error;
  }

  int incrementPollAttempts() {
    _pollAttempts++;
    return _pollAttempts;
  }

  bool shouldContinuePolling() {
    return _pollAttempts < _maxPollAttempts;
  }

  void reset() {
    _currentScan = null;
    _errorMessage = null;
    _pollAttempts = 0;
    state = ScanUploadState.idle;
  }
}

final scanProvider =
    StateNotifierProvider<ScanNotifier, ScanUploadState>((ref) {
  return ScanNotifier();
});
