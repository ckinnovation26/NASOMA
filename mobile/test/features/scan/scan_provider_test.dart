import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nasoma/features/scan/domain/models/scan_model.dart';
import 'package:nasoma/features/scan/data/providers/scan_provider.dart';

void main() {
  group('ScanProvider', () {
    late ProviderContainer container;

    setUp(() {
      container = ProviderContainer();
    });

    tearDown(() {
      container.dispose();
    });

    test('initial state is idle', () {
      final state = container.read(scanProvider);
      expect(state, ScanUploadState.idle);
    });

    test('setScan sets current scan and idle state', () async {
      final scan = ScanModel(
        id: 'scan123',
        sessionId: 'session123',
        base64Image: 'base64data',
        createdAt: DateTime.now(),
      );
      final notifier = container.read(scanProvider.notifier);

      await notifier.setScan(scan);
      final state = container.read(scanProvider);

      expect(state, ScanUploadState.idle);
      expect(notifier.currentScan, scan);
    });

    test('startUpload sets state to uploading', () async {
      final scan = ScanModel(
        id: 'scan123',
        sessionId: 'session123',
        base64Image: 'base64data',
        createdAt: DateTime.now(),
      );
      final notifier = container.read(scanProvider.notifier);

      await notifier.setScan(scan);
      await notifier.startUpload();
      final state = container.read(scanProvider);

      expect(state, ScanUploadState.uploading);
    });

    test('startPolling sets state to polling', () async {
      final scan = ScanModel(
        id: 'scan123',
        sessionId: 'session123',
        base64Image: 'base64data',
        createdAt: DateTime.now(),
      );
      final notifier = container.read(scanProvider.notifier);

      await notifier.setScan(scan);
      await notifier.startPolling();
      final state = container.read(scanProvider);

      expect(state, ScanUploadState.polling);
    });

    test('setScanCompleted sets state to completed', () {
      final scan = ScanModel(
        id: 'scan123',
        sessionId: 'session123',
        base64Image: 'base64data',
        createdAt: DateTime.now(),
        extractedText: 'texte extrait',
        ocrConfidence: '95',
      );
      final notifier = container.read(scanProvider.notifier);

      notifier.setScanCompleted(scan);
      final state = container.read(scanProvider);

      expect(state, ScanUploadState.completed);
      expect(notifier.isCompleted, true);
    });

    test('setPollingError sets state to error', () {
      const errorMessage = 'Polling timeout';
      final notifier = container.read(scanProvider.notifier);

      notifier.setPollingError(errorMessage);
      final state = container.read(scanProvider);

      expect(state, ScanUploadState.error);
      expect(notifier.errorMessage, errorMessage);
    });

    test('shouldContinuePolling returns true within max attempts', () {
      final notifier = container.read(scanProvider.notifier);

      for (int i = 0; i < 20; i++) {
        notifier.incrementPollAttempts();
      }

      expect(notifier.shouldContinuePolling(), true);
    });

    test('shouldContinuePolling returns false after max attempts', () {
      final notifier = container.read(scanProvider.notifier);

      for (int i = 0; i < 31; i++) {
        notifier.incrementPollAttempts();
      }

      expect(notifier.shouldContinuePolling(), false);
    });

    test('reset clears all state', () {
      final scan = ScanModel(
        id: 'scan123',
        sessionId: 'session123',
        base64Image: 'base64data',
        createdAt: DateTime.now(),
      );
      final notifier = container.read(scanProvider.notifier);

      notifier.setScanCompleted(scan);
      notifier.reset();

      expect(notifier.currentScan, null);
      expect(container.read(scanProvider), ScanUploadState.idle);
    });
  });
}
