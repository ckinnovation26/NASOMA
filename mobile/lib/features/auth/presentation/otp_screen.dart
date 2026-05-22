// OTP entry — vérifie le code reçu par WhatsApp.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/api/auth_repository.dart';
import '../../../core/env/env.dart';
import '../../../core/theme/app_theme.dart';

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
  bool _loading = false;
  String? _error;

  String get _code => _controllers.map((c) => c.text).join();

  Future<void> _submit() async {
    if (_code.length < 6) {
      setState(() => _error = 'Entre les 6 chiffres');
      return;
    }
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final repo = ref.read(authRepositoryProvider);
      await repo.verifyOtp(phone: widget.phone, code: _code);
      if (!mounted) return;
      context.go('/home');
    } catch (e) {
      setState(() => _error = 'Code incorrect ou expiré.\n$e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    for (final c in _controllers) c.dispose();
    for (final n in _focusNodes) n.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Code reçu sur\nWhatsApp 💬',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 12),
              Text(
                'Envoyé au ${widget.phone}.\nEntre les 6 chiffres.',
                style: const TextStyle(color: AppColors.textSecondary, height: 1.5),
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
              const SizedBox(height: 32),

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
                        decoration: const InputDecoration(
                          contentPadding: EdgeInsets.zero,
                        ),
                        onChanged: (v) {
                          if (v.isNotEmpty && i < 5) {
                            _focusNodes[i + 1].requestFocus();
                          } else if (v.isEmpty && i > 0) {
                            _focusNodes[i - 1].requestFocus();
                          }
                          if (i == 5 && _code.length == 6) {
                            _submit();
                          }
                        },
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 12),

              if (_error != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.error.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.error.withOpacity(0.3)),
                  ),
                  child: Text(
                    _error!,
                    style: const TextStyle(color: AppColors.error, fontSize: 13),
                  ),
                ),

              const Spacer(),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _loading ? null : _submit,
                  child: _loading
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: AppColors.black,
                          ),
                        )
                      : const Text('Vérifier et activer →'),
                ),
              ),
              const SizedBox(height: 12),
              const Center(
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
