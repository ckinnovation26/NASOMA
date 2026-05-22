import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../data/providers/auth_provider.dart';

class PhoneScreen extends ConsumerStatefulWidget {
  const PhoneScreen({super.key});

  @override
  ConsumerState<PhoneScreen> createState() => _PhoneScreenState();
}

class _PhoneScreenState extends ConsumerState<PhoneScreen> {
  final _controller = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _loading = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String get _phone {
    final raw = _controller.text.trim().replaceAll(' ', '');
    // Normalise en +269XXXXXXXX si l'utilisateur entre juste les chiffres
    if (raw.startsWith('0')) return '+269${raw.substring(1)}';
    if (!raw.startsWith('+')) return '+269$raw';
    return raw;
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() => _loading = true);

    final notifier = ref.read(authProvider.notifier);
    await notifier.startOtpFlow(_phone);

    if (!mounted) return;
    setState(() => _loading = false);

    final authState = ref.read(authProvider);
    if (authState == AuthState.error) return; // L'UI affiche l'erreur via listener
    context.push('/otp?phone=${Uri.encodeComponent(_phone)}');
  }

  @override
  Widget build(BuildContext context) {
    ref.listen<AuthState>(authProvider, (_, next) {
      if (next == AuthState.error) {
        final msg = ref.read(authProvider.notifier).errorMessage ?? 'Erreur inconnue';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(msg),
            backgroundColor: AppColors.error,
          ),
        );
      }
    });

    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: () => context.go('/onboarding'),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Ton numéro\nde téléphone',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: AppColors.textPrimary,
                        height: 1.3,
                      ),
                ),
                const SizedBox(height: 10),
                Text(
                  'Tu recevras un code à 6 chiffres sur WhatsApp.',
                  style: TextStyle(color: AppColors.textSecondary, fontSize: 14, height: 1.5),
                ),
                const SizedBox(height: 36),

                // Input numéro
                TextFormField(
                  controller: _controller,
                  autofocus: true,
                  keyboardType: TextInputType.phone,
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'[\d\s+]')),
                    LengthLimitingTextInputFormatter(16),
                  ],
                  style: const TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 20,
                    fontWeight: FontWeight.w500,
                    letterSpacing: 1,
                  ),
                  decoration: InputDecoration(
                    hintText: '322 XX XX',
                    prefixText: '+269  ',
                    prefixStyle: TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 20,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  validator: (v) {
                    final stripped = (v ?? '').trim().replaceAll(' ', '');
                    if (stripped.isEmpty) return 'Entre ton numéro';
                    if (stripped.replaceAll(RegExp(r'[^\d]'), '').length < 7) {
                      return 'Numéro trop court';
                    }
                    return null;
                  },
                  onFieldSubmitted: (_) => _submit(),
                ),
                const SizedBox(height: 8),
                Text(
                  'Exemple : 322 XX XX (Comores)',
                  style: TextStyle(color: AppColors.textTertiary, fontSize: 12),
                ),

                const Spacer(),

                SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _submit,
                    child: _loading
                        ? const SizedBox(
                            width: 22,
                            height: 22,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              color: AppColors.black,
                            ),
                          )
                        : const Text(
                            'Recevoir mon code →',
                            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                          ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
