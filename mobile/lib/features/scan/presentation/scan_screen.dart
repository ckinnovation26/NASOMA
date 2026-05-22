// Écran de capture — mock pour démo (pas de vraie caméra Web sur iOS Safari).
// Tap sur le bouton viseur → navigue vers le diagnostic IA.

import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class ScanScreen extends StatelessWidget {
  const ScanScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => context.go('/home'),
        ),
        title: const Text(
          'Scanner ta copie',
          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 8),
            // Hint
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Text(
                'Pose ta copie bien à plat sur une table.\nMimi détecte les erreurs automatiquement.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: AppColors.textSecondary,
                  height: 1.45,
                  fontSize: 13,
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Viseur faux-caméra
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24),
                child: AspectRatio(
                  aspectRatio: 3 / 4,
                  child: Stack(
                    children: [
                      // Fond gradient simulant l'aperçu caméra
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
                      // Coins du viseur (style natif)
                      const Positioned.fill(
                        child: Padding(
                          padding: EdgeInsets.all(16),
                          child: _ViewfinderCorners(),
                        ),
                      ),
                      // Texte central
                      Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(
                              Icons.document_scanner_outlined,
                              size: 60,
                              color: AppColors.textTertiary,
                            ),
                            const SizedBox(height: 14),
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
                      // Badge "MOCK" en haut à droite
                      Positioned(
                        top: 12,
                        right: 12,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: AppColors.limeAccent.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(
                              color: AppColors.limeAccent.withOpacity(0.5),
                            ),
                          ),
                          child: const Text(
                            '🎬 DÉMO',
                            style: TextStyle(
                              color: AppColors.limeAccent,
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Bouton circulaire de capture
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 28),
              child: Column(
                children: [
                  GestureDetector(
                    onTap: () => context.go('/scan/diagnostic'),
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: AppColors.textPrimary,
                          width: 4,
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
                    ),
                  )
                      .animate(onPlay: (c) => c.repeat(reverse: true))
                      .scale(
                        begin: const Offset(1, 1),
                        end: const Offset(1.05, 1.05),
                        duration: 1200.ms,
                        curve: Curves.easeInOut,
                      ),
                  const SizedBox(height: 14),
                  const Text(
                    'Touche pour simuler une capture',
                    style: TextStyle(
                      color: AppColors.textTertiary,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ViewfinderCorners extends StatelessWidget {
  const _ViewfinderCorners();

  @override
  Widget build(BuildContext context) {
    const corner = SizedBox(
      width: 24,
      height: 24,
    );
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
    const color = AppColors.limeAccent;
    const w = 3.0;
    return SizedBox(
      width: 28,
      height: 28,
      child: CustomPaint(
        painter: _CornerPainter(top: top, left: left, color: color, stroke: w),
      ),
    );
  }
}

class _CornerPainter extends CustomPainter {
  _CornerPainter({
    required this.top,
    required this.left,
    required this.color,
    required this.stroke,
  });
  final bool top;
  final bool left;
  final Color color;
  final double stroke;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = stroke
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
