// Quand l'utilisateur n'a pas WhatsApp — orientation vendeur ou install.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class WhatsAppGuidanceScreen extends ConsumerWidget {
  const WhatsAppGuidanceScreen({super.key, required this.nearbyVendors});

  final List<Map<String, dynamic>> nearbyVendors;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/whatsapp-check'),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Tu as besoin de\nWhatsApp d\'abord',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 12),
              Text(
                'Pour activer Nasoma, il faut WhatsApp installé sur ton téléphone. '
                'Sans WhatsApp, tu ne peux pas recevoir ton code d\'activation.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: AppColors.textSecondary,
                      height: 1.5,
                    ),
              ),
              const SizedBox(height: 24),

              // Option 1 : installer WhatsApp
              _OptionCard(
                icon: '📱',
                title: 'Installe WhatsApp',
                body: 'Va dans Play Store, télécharge WhatsApp, puis reviens nous voir.',
                cta: 'Ouvrir Play Store',
                onTap: () {
                  // TODO Sprint Mobile 2 : url_launcher
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'Lien Play Store WhatsApp (à brancher Sprint Mobile 2)',
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 12),

              // Option 2 : visite vendeur
              if (nearbyVendors.isNotEmpty) ...[
                _OptionCard(
                  icon: '🏪',
                  title: 'Demande à ton vendeur Nasoma',
                  body: nearbyVendors.first['name']?.toString() ??
                      'Le vendeur le plus proche peut t\'aider à installer WhatsApp + activer ton compte en 5 minutes.',
                  cta: 'Voir ${nearbyVendors.length} vendeur(s)',
                  onTap: () {},
                ),
              ] else
                const _OptionCard(
                  icon: '🏪',
                  title: 'Demande à ton vendeur Nasoma',
                  body: 'Le vendeur le plus proche peut t\'aider à installer '
                      'WhatsApp et activer ton compte en 5 minutes.',
                  cta: 'Pas de vendeur enregistré',
                  onTap: null,
                ),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                child: TextButton(
                  onPressed: () => context.go('/whatsapp-check'),
                  child: const Text(
                    'J\'ai installé WhatsApp, je continue →',
                    style: TextStyle(color: AppColors.limeAccent),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _OptionCard extends StatelessWidget {
  const _OptionCard({
    required this.icon,
    required this.title,
    required this.body,
    required this.cta,
    required this.onTap,
  });

  final String icon;
  final String title;
  final String body;
  final String cta;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.charcoal,
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.borderSubtle),
          ),
          child: Row(
            children: [
              Text(icon, style: const TextStyle(fontSize: 32)),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      body,
                      style: const TextStyle(
                        fontSize: 13,
                        color: AppColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      cta,
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.limeAccent,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
