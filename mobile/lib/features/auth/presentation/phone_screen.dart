// Phone — utilisé pour login existant (futur sprint).

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';

class PhoneScreen extends ConsumerWidget {
  const PhoneScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppColors.black,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/'),
        ),
      ),
      body: const Center(
        child: Text(
          'Login existant — à coder Sprint Mobile 2',
          style: TextStyle(color: AppColors.textSecondary),
        ),
      ),
    );
  }
}
