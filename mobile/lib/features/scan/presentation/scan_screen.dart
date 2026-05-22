import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:image_picker/image_picker.dart';

import '../../../core/api/api_client.dart';
import '../../../core/theme/app_theme.dart';
import '../domain/models/scan_model.dart';
import '../data/providers/scan_provider.dart';
import '../data/repositories/scan_repository_impl.dart';

final scanRepositoryProvider = Provider<ScanRepository>((ref) {
  return ScanRepositoryImpl(dio: ref.read(apiClientProvider));
});

enum _ScanPhase { idle, picking, recognizing, uploading, polling, done, error }

class ScanScreen extends ConsumerStatefulWidget {
  const ScanScreen({super.key});

  @override
  ConsumerState<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends ConsumerState<ScanScreen> {
  _ScanPhase _phase = _ScanPhase.idle;
  String? _errorMsg;
  String? _scanId;
  Timer? _pollingTimer;
  int _pollCount = 0;

  static const int _maxPolls = 30;
  static const Duration _pollInterval = Duration(seconds: 10);

  @override
  void dispose() {
    _pollingTimer?.cancel();
    super.dispose();
  }

  // ── Flux principal ─────────────────────────────────────

  Future<void> _capture(ImageSource source) async {
    if (_phase != _ScanPhase.idle) return;
    setState(() => _phase = _ScanPhase.picking);

    final XFile? file = await ImagePicker().pickImage(
      source: source,
      maxWidth: 1920,
      maxHeight: 2560,
      imageQuality: 85,
    );

    if (file == null) {
      setState(() => _phase = _ScanPhase.idle);
      return;
    }

    await _processImage(file.path);
  }

  Future<void> _processImage(String imagePath) async {
    setState(() => _phase = _ScanPhase.recognizing);

    // ── Étape 1 : ML Kit OCR on-device (gratuit) ──
    String mlkitText = '';
    double mlkitConfidence = 0.0;
    try {
      final inputImage = InputImage.fromFilePath(imagePath);
      final recognizer = TextRecognizer(script: TextRecognitionScript.latin);
      final recognized = await recognizer.processImage(inputImage);
      await recognizer.close();
      mlkitText = recognized.text;
      mlkitConfidence = _estimateConfidence(mlkitText, recognized.blocks.length);
    } catch (_) {
      // ML Kit échoue → le backend utilisera Cloud Vision ou Gemini
    }

    // ── Étape 2 : compression ≤ 200 KB ──
    setState(() => _phase = _ScanPhase.uploading);
    final Uint8List imageBytes = await _compressImage(imagePath);
    final String base64Image = base64Encode(imageBytes);

    // ── Étape 3 : upload ──
    final repo = ref.read(scanRepositoryProvider);
    final notifier = ref.read(scanProvider.notifier);

    try {
      final scan = ScanModel(
        id: '',
        sessionId: 'session-${DateTime.now().millisecondsSinceEpoch}',
        base64Image: base64Image,
        createdAt: DateTime.now(),
      );
      await notifier.setScan(scan);
      await notifier.startUpload();

      final result = await repo.uploadScan(
        ScanModel(
          id: '',
          sessionId: scan.sessionId,
          base64Image: base64Image,
          createdAt: DateTime.now(),
        ),
      );
      _scanId = result['scan_id'] as String?;

      if (_scanId == null) {
        _setError('Identifiant scan manquant dans la réponse du serveur.');
        return;
      }

      await notifier.startPolling();
      setState(() {
        _phase = _ScanPhase.polling;
        _pollCount = 0;
      });
      _startPolling();
    } catch (e) {
      _setError(e.toString());
    }
  }

  void _startPolling() {
    _pollingTimer = Timer.periodic(_pollInterval, (_) async {
      if (_phase != _ScanPhase.polling || _scanId == null) {
        _pollingTimer?.cancel();
        return;
      }

      if (++_pollCount > _maxPolls) {
        _pollingTimer?.cancel();
        _setError("Délai dépassé. L'analyse a pris trop de temps.");
        return;
      }

      // Mise à jour du compteur dans l'UI
      if (mounted) setState(() {});

      try {
        final result =
            await ref.read(scanRepositoryProvider).pollScanResult(_scanId!);
        final status = result['status'] as String?;

        if (status == 'done' || status == 'done_with_fallback') {
          _pollingTimer?.cancel();
          ref.read(scanProvider.notifier).setScanCompleted(
                ScanModel(
                  id: _scanId!,
                  sessionId: result['session_id'] as String? ?? '',
                  base64Image: '',
                  createdAt: DateTime.now(),
                  extractedText: result['summary_text'] as String?,
                  ocrConfidence: result['ocr_confidence']?.toString(),
                ),
              );
          setState(() => _phase = _ScanPhase.done);
          if (!mounted) return;
          final diagnosticId = result['diagnostic_id'] as String?;
          context.go(diagnosticId != null ? '/scan/diagnostic' : '/scan/result');
        } else if (status == 'failed') {
          _pollingTimer?.cancel();
          _setError("L'analyse a échoué. Réessayez avec une photo plus nette.");
        }
      } catch (_) {
        // Erreur réseau transitoire — on continue à poller
      }
    });
  }

  void _setError(String message) {
    _pollingTimer?.cancel();
    ref.read(scanProvider.notifier).setPollingError(message);
    if (mounted) setState(() { _phase = _ScanPhase.error; _errorMsg = message; });
  }

  void _retry() {
    ref.read(scanProvider.notifier).reset();
    setState(() { _phase = _ScanPhase.idle; _errorMsg = null; _scanId = null; _pollCount = 0; });
  }

  // ── Helpers ──────────────────────────────────

  double _estimateConfidence(String text, int blockCount) {
    if (text.length > 200 && blockCount >= 3) return 0.92;
    if (text.length > 80 && blockCount >= 2) return 0.80;
    if (text.length > 30) return 0.65;
    return 0.30;
  }

  Future<Uint8List> _compressImage(String path) async {
    final compressed = await FlutterImageCompress.compressWithFile(
      path,
      minWidth: 800,
      minHeight: 600,
      quality: 80,
    );
    if (compressed != null) return compressed;
    return File(path).readAsBytesSync();
  }

  // ── Build ─────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.black,
      extendBodyBehindAppBar: true,
      appBar: _phase == _ScanPhase.idle
          ? AppBar(
              backgroundColor: Colors.transparent,
              elevation: 0,
              leading: IconButton(
                icon: const Icon(Icons.close, color: AppColors.textPrimary),
                onPressed: () => context.go('/home'),
              ),
              title: const Text(
                'Scanner ta copie',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
            )
          : null,
      body: SafeArea(child: _buildBody()),
    );
  }

  Widget _buildBody() {
    return switch (_phase) {
      _ScanPhase.idle => _IdleView(
          onCamera: () => _capture(ImageSource.camera),
          onGallery: () => _capture(ImageSource.gallery),
        ),
      _ScanPhase.picking => const _StatusView(label: 'Ouverture de la caméra…'),
      _ScanPhase.recognizing => const _StatusView(label: 'Lecture du texte…'),
      _ScanPhase.uploading => const _StatusView(label: 'Envoi de la copie…'),
      _ScanPhase.polling => _StatusView(
          label: 'Mimi analyse ta copie…',
          subtitle: 'Environ ${(_maxPolls - _pollCount) * 10} secondes',
          showProgress: true,
        ),
      _ScanPhase.done => const _StatusView(label: 'Analyse terminée !'),
      _ScanPhase.error => _ErrorView(
          message: _errorMsg ?? 'Erreur inconnue',
          onRetry: _retry,
        ),
    };
  }
}

// ══════════════════════════════════════════════
//  Sous-vues
// ══════════════════════════════════════════════

class _IdleView extends StatelessWidget {
  const _IdleView({required this.onCamera, required this.onGallery});
  final VoidCallback onCamera;
  final VoidCallback onGallery;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: 12),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24),
          child: Text(
            'Pose ta copie corrigée bien à plat.\nMimi détecte tes erreurs automatiquement.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: AppColors.textSecondary,
              height: 1.5,
              fontSize: 13,
            ),
          ),
        ),
        const SizedBox(height: 20),

        // Zone viseur
        Expanded(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: AspectRatio(
              aspectRatio: 3 / 4,
              child: Stack(
                children: [
                  Container(
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [Color(0xFF1F1F1F), Color(0xFF101010)],
                      ),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: AppColors.borderSubtle),
                    ),
                  ),
                  const Positioned.fill(
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: _ViewfinderCorners(),
                    ),
                  ),
                  Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(
                          Icons.document_scanner_outlined,
                          size: 60,
                          color: AppColors.textTertiary,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'Cadre ta copie ici',
                          style: TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    )
                        .animate(onPlay: (c) => c.repeat(reverse: true))
                        .fadeIn(duration: 1200.ms)
                        .then()
                        .fade(begin: 1, end: 0.4, duration: 1200.ms),
                  ),
                ],
              ),
            ),
          ),
        ),

        // Boutons
        Padding(
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 32),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Bouton galerie
              _ActionButton(
                icon: Icons.photo_library_outlined,
                label: 'Galerie',
                onTap: onGallery,
                small: true,
              ),
              const SizedBox(width: 32),
              // Bouton caméra principal
              GestureDetector(
                onTap: onCamera,
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: AppColors.textPrimary,
                      width: 3,
                    ),
                  ),
                  child: Center(
                    child: Container(
                      width: 64,
                      height: 64,
                      decoration: const BoxDecoration(
                        shape: BoxShape.circle,
                        color: AppColors.limeAccent,
                      ),
                    ),
                  ),
                )
                    .animate(onPlay: (c) => c.repeat(reverse: true))
                    .scale(
                      begin: const Offset(1, 1),
                      end: const Offset(1.04, 1.04),
                      duration: 1200.ms,
                      curve: Curves.easeInOut,
                    ),
              ),
              const SizedBox(width: 32),
              // Placeholder symétrie
              const SizedBox(width: 56, height: 56),
            ],
          ),
        ),
      ],
    );
  }
}

class _StatusView extends StatelessWidget {
  const _StatusView({required this.label, this.subtitle, this.showProgress = false});
  final String label;
  final String? subtitle;
  final bool showProgress;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (showProgress)
              const SizedBox(
                width: 56,
                height: 56,
                child: CircularProgressIndicator(
                  color: AppColors.limeAccent,
                  strokeWidth: 3,
                ),
              )
            else
              const SizedBox(
                width: 40,
                height: 40,
                child: CircularProgressIndicator(
                  color: AppColors.limeAccent,
                  strokeWidth: 2.5,
                ),
              ),
            const SizedBox(height: 24),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: AppColors.textPrimary,
                fontSize: 16,
                fontWeight: FontWeight.w600,
                height: 1.5,
              ),
            ),
            if (subtitle != null) ...[
              const SizedBox(height: 8),
              Text(
                subtitle!,
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 13,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, color: AppColors.error, size: 56),
            const SizedBox(height: 20),
            Text(
              message,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
                height: 1.5,
              ),
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.limeAccent,
                  foregroundColor: AppColors.black,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                onPressed: onRetry,
                child: const Text(
                  'Réessayer',
                  style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ActionButton extends StatelessWidget {
  const _ActionButton({
    required this.icon,
    required this.label,
    required this.onTap,
    this.small = false,
  });
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool small;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: small ? 48 : 56,
            height: small ? 48 : 56,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.charcoal,
              border: Border.all(color: AppColors.borderSubtle),
            ),
            child: Icon(icon, color: AppColors.textSecondary, size: small ? 20 : 24),
          ),
          const SizedBox(height: 6),
          Text(
            label,
            style: TextStyle(color: AppColors.textTertiary, fontSize: 11),
          ),
        ],
      ),
    );
  }
}

// ══════════════════════════════════════════════
//  Viseur (coins animés)
// ══════════════════════════════════════════════

class _ViewfinderCorners extends StatelessWidget {
  const _ViewfinderCorners();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned(top: 0, left: 0, child: _Corner(top: true, left: true)),
        Positioned(top: 0, right: 0, child: _Corner(top: true, left: false)),
        Positioned(bottom: 0, left: 0, child: _Corner(top: false, left: true)),
        Positioned(bottom: 0, right: 0, child: _Corner(top: false, left: false)),
      ],
    );
  }
}

class _Corner extends StatelessWidget {
  const _Corner({required this.top, required this.left});
  final bool top;
  final bool left;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 28,
      height: 28,
      child: CustomPaint(
        painter: _CornerPainter(top: top, left: left),
      ),
    );
  }
}

class _CornerPainter extends CustomPainter {
  const _CornerPainter({required this.top, required this.left});
  final bool top;
  final bool left;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = AppColors.limeAccent
      ..strokeWidth = 3.0
      ..strokeCap = StrokeCap.round;

    final double x0 = left ? 0 : size.width;
    final double x1 = left ? size.width : 0;
    final double y0 = top ? 0 : size.height;
    final double y1 = top ? size.height : 0;

    canvas.drawLine(Offset(x0, y0), Offset(x1, y0), paint);
    canvas.drawLine(Offset(x0, y0), Offset(x0, y1), paint);
  }

  @override
  bool shouldRepaint(_) => false;
}
