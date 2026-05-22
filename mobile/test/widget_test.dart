// Smoke test — vérifie que l'app démarre sans crash.

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nasoma/main.dart';

void main() {
  testWidgets('App launches and shows Nasoma branding', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: NasomaApp()));
    await tester.pump();

    expect(find.text('Nasoma'), findsOneWidget);
  });
}
