// Signup form — phone + nom + grade, appel POST /auth/signup/self.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/api/auth_repository.dart';
import '../../../core/theme/app_theme.dart';

class SignupFormScreen extends ConsumerStatefulWidget {
  const SignupFormScreen({super.key});

  @override
  ConsumerState<SignupFormScreen> createState() => _SignupFormScreenState();
}

class _SignupFormScreenState extends ConsumerState<SignupFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _phoneController = TextEditingController(text: '34 12 567');
  final _nameController = TextEditingController();
  String _grade = 'CM2';
  bool _loading = false;
  String? _error;

  String _formattedPhone() {
    final cleaned = _phoneController.text.replaceAll(RegExp(r'[^0-9]'), '');
    return '+269$cleaned';
  }

  Future<void> _submit() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final repo = ref.read(authRepositoryProvider);
      final result = await repo.selfSignup(
        phone: _formattedPhone(),
        fullName: _nameController.text.trim(),
        hasWhatsapp: true,
        gradeLevel: _grade,
      );
      if (!mounted) return;
      if (result.accepted) {
        context.go('/otp?phone=${Uri.encodeComponent(_formattedPhone())}');
      } else {
        context.go('/whatsapp-guidance', extra: result.nearbyVendors);
      }
    } catch (e) {
      setState(() {
        _error = 'Erreur réseau : $e\nVérifie que le backend tourne sur localhost:8000';
      });
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _phoneController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/whatsapp-check'),
        ),
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Crée ton compte\nen 30 secondes',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
                const SizedBox(height: 24),

                // Nom
                _Label('Ton prénom'),
                TextFormField(
                  controller: _nameController,
                  style: const TextStyle(color: AppColors.textPrimary),
                  decoration: const InputDecoration(
                    hintText: 'Ali',
                  ),
                  validator: (v) {
                    if (v == null || v.trim().length < 2) {
                      return 'Au moins 2 caractères';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 20),

                // Phone
                _Label('Ton numéro WhatsApp'),
                Row(
                  children: [
                    Container(
                      height: 56,
                      padding: const EdgeInsets.symmetric(horizontal: 14),
                      decoration: BoxDecoration(
                        color: AppColors.charcoal,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text('🇰🇲 ', style: TextStyle(fontSize: 18)),
                          Text('+269', style: TextStyle(color: AppColors.textPrimary)),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: TextFormField(
                        controller: _phoneController,
                        style: const TextStyle(color: AppColors.textPrimary),
                        keyboardType: TextInputType.phone,
                        inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[0-9 ]'))],
                        decoration: const InputDecoration(
                          hintText: '3X XX XXX',
                        ),
                        validator: (v) {
                          final cleaned = (v ?? '').replaceAll(RegExp(r'[^0-9]'), '');
                          if (cleaned.length != 7) {
                            return 'Numéro comorien à 7 chiffres (ex : 34 12 567)';
                          }
                          return null;
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                // Grade
                _Label('Ton niveau scolaire'),
                Row(
                  children: [
                    for (final g in const ['CM1', 'CM2', '6E']) ...[
                      _GradeChip(
                        label: g,
                        selected: _grade == g,
                        onTap: () => setState(() => _grade = g),
                      ),
                      const SizedBox(width: 8),
                    ],
                  ],
                ),
                const SizedBox(height: 24),

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

                const SizedBox(height: 32),
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
                        : const Text('Recevoir mon code via WhatsApp →'),
                  ),
                ),
                const SizedBox(height: 12),
                const Text(
                  'En continuant, j\'accepte les CGU et la politique de confidentialité.',
                  style: TextStyle(color: AppColors.textTertiary, fontSize: 12),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _Label extends StatelessWidget {
  const _Label(this.text);
  final String text;
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Text(
          text,
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: AppColors.textSecondary,
          ),
        ),
      );
}

class _GradeChip extends StatelessWidget {
  const _GradeChip({required this.label, required this.selected, required this.onTap});
  final String label;
  final bool selected;
  final VoidCallback onTap;
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        decoration: BoxDecoration(
          color: selected ? AppColors.limeAccent : AppColors.charcoal,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: selected ? AppColors.black : AppColors.textPrimary,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
