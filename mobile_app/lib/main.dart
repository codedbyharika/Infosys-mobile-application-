import 'package:flutter/material.dart';
import 'config/cpcb_theme.dart';
import 'providers/app_state.dart';
import 'screens/main_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final appState = AppState();
  await appState.init();

  runApp(EcoAirApp(appState: appState));
}

class EcoAirApp extends StatelessWidget {
  final AppState appState;

  const EcoAirApp({super.key, required this.appState});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: appState,
      builder: (context, _) {
        return MaterialApp(
          title: 'EcoAir Intelligence',
          debugShowCheckedModeBanner: false,
          theme: CpcbTheme.lightTheme,
          home: MainScreen(state: appState),
        );
      },
    );
  }
}
