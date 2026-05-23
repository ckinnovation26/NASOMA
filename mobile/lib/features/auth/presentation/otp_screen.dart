import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/env/env.dart';
import '../../../core/theme/app_theme.dart';
import '../data/providers/auth_provider.dart';

class OtpScreen extends ConsumerStatefulWidget {
  const OtpScreen({super.key, required this.phone});
  final String phone;

  @override
  ConsumerState<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends ConsumerState<OtpScreen> {
  final List<TextEditingController> _controllers =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _focusNodes = List.generate(6, (_) => FocusNode());

  String get _code => _controllers.map((c) => c.text).join();

  @override
  void dispose() {
    for (final c in _controllers) c.dispose();
    for (final n in _focusNodes) n.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_code.length < 6) return;
    await ref.read(authProvider.notifier).verifyOtp(_code, phone: widget.phone);
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);
    final isLoading = authState == AuthState.verifyingOtp;

    ref.listen<AuthState>(authProvider, (_, next) {
      if (next == AuthState.authenticated) {
        context.go('/home');
      } else if (next == AuthState.error) {
        final msg = ref.read(authProvider.notifier).errorMessage ?? 'Erreur inconnue';
        // Vider les champs et afficher l'erreur
        for (final c in _controllers) c.clear();
        _focusNodes.first.requestFocus();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(msg),
            backgroundColor: AppColors.error,
            duration: const Duration(seconds: 4),
          ),
        );
        ref.read(authProvider.notifier).reset();
      }
    });

    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Code reçu sur\nWhatsApp 💬',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                      color: AppColors.textPrimary,
                      height: 1.3,
                    ),
              ),
              const SizedBox(height: 10),
              Text(
                'Envoyé au ${widget.phone}.\nEntre les 6 chiffres.',
                style: TextStyle(
                  color: AppColors.textSecondary,
                  fontSize: 14,
                  height: 1.5,
                ),
              ),

              if (Env.useMockApi) ...[
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: AppColors.limeAccent.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppColors.limeAccent.withOpacity(0.4)),
                  ),
                  child: Text(
                    '🎬 Mode démo — code : ${Env.mockOtpCode}',
                    style: const TextStyle(
                      color: AppColors.limeAccent,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 36),

              // 6 cases OTP
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  for (var i = 0; i < 6; i++)
                    SizedBox(
                      width: 48,
                      height: 56,
                      child: TextField(
                        controller: _controllers[i],
                        focusNode: _focusNodes[i],
                        enabled: !isLoading,
                        textAlign: TextAlign.center,
                        keyboardType: TextInputType.number,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly,
                          LengthLimitingTextInputFormatter(1),
                        ],
                        style: const TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 22,
                          fontWeight: FontWeight.w600,
                        ),
                        decoration: const InputDecoration(contentPadding: EdgeInsets.zero),
                        onChanged: (v) {
                          if (v.isNotEmpty && i < 5) {
                            _focusNodes[i + 1].requestFocus();
                          } else if (v.isEmpty && i > 0) {
                            _focusNodes[i - 1].requestFocus();
                          }
                          if (i == 5 && _code.length == 6) _submit();
                        },
                      ),
                    ),
                ],
              ),

              const Spacer(),

              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: isLoading ? null : _submit,
                  child: isLoading
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: AppColors.black,
                          ),
                        )
                      : const Text(
                          'Vérifier et activer →',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                        ),
                ),
              ),
              const SizedBox(height: 12),
              Center(
                child: Text(
                  'Pas reçu le code ? Vérifie ton WhatsApp.',
                  style: TextStyle(color: AppColors.textTertiary, fontSize: 13),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
