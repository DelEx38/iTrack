import 'package:flutter/material.dart';
import '../models/study.dart';
import 'dashboard_screen.dart';
import 'sites_screen.dart';
import 'patients_screen.dart';
import 'visits_screen.dart';
import 'adverse_events_screen.dart';
import 'documents_screen.dart';
import 'queries_screen.dart';
import 'settings_screen.dart';

/// Ecran principal d'une etude avec navigation par onglets
class StudyHomeScreen extends StatefulWidget {
  final Study study;

  const StudyHomeScreen({super.key, required this.study});

  @override
  State<StudyHomeScreen> createState() => _StudyHomeScreenState();
}

class _StudyHomeScreenState extends State<StudyHomeScreen> {
  int _selectedIndex = 0;

  static const List<_NavItem> _navItems = [
    _NavItem(icon: Icons.dashboard_outlined, selectedIcon: Icons.dashboard, label: 'Dashboard'),
    _NavItem(icon: Icons.location_on_outlined, selectedIcon: Icons.location_on, label: 'Sites'),
    _NavItem(icon: Icons.people_outlined, selectedIcon: Icons.people, label: 'Patients'),
    _NavItem(icon: Icons.event_outlined, selectedIcon: Icons.event, label: 'Visits'),
    _NavItem(icon: Icons.warning_outlined, selectedIcon: Icons.warning, label: 'AE'),
    _NavItem(icon: Icons.description_outlined, selectedIcon: Icons.description, label: 'Documents'),
    _NavItem(icon: Icons.help_outline, selectedIcon: Icons.help, label: 'Queries'),
    _NavItem(icon: Icons.settings_outlined, selectedIcon: Icons.settings, label: 'Settings'),
  ];

  Widget _buildPage() {
    switch (_selectedIndex) {
      case 0:
        return DashboardScreen(study: widget.study);
      case 1:
        return SitesScreen(study: widget.study);
      case 2:
        return PatientsScreen(study: widget.study);
      case 3:
        return VisitsScreen(study: widget.study);
      case 4:
        return AdverseEventsScreen(study: widget.study);
      case 5:
        return DocumentsScreen(study: widget.study);
      case 6:
        return QueriesScreen(study: widget.study);
      case 7:
        return SettingsScreen(study: widget.study);
      default:
        return _PlaceholderScreen(title: _navItems[_selectedIndex].label);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Sidebar
          NavigationRail(
            selectedIndex: _selectedIndex,
            onDestinationSelected: (index) {
              setState(() => _selectedIndex = index);
            },
            labelType: NavigationRailLabelType.all,
            leading: Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: Column(
                children: [
                  // Bouton retour
                  IconButton(
                    icon: const Icon(Icons.arrow_back),
                    onPressed: () => Navigator.pop(context),
                    tooltip: 'Back to Studies',
                  ),
                  const SizedBox(height: 16),
                  // Logo
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Color(widget.study.phaseColor),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.science, size: 24, color: Colors.white),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    widget.study.number,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11),
                  ),
                ],
              ),
            ),
            destinations: _navItems
                .map((item) => NavigationRailDestination(
                      icon: Icon(item.icon),
                      selectedIcon: Icon(item.selectedIcon),
                      label: Text(item.label),
                    ))
                .toList(),
          ),

          const VerticalDivider(thickness: 1, width: 1),

          // Contenu principal
          Expanded(child: _buildPage()),
        ],
      ),
    );
  }
}

class _NavItem {
  final IconData icon;
  final IconData selectedIcon;
  final String label;

  const _NavItem({required this.icon, required this.selectedIcon, required this.label});
}

class _PlaceholderScreen extends StatelessWidget {
  final String title;

  const _PlaceholderScreen({required this.title});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.construction, size: 64, color: Colors.grey[600]),
          const SizedBox(height: 16),
          Text(
            title,
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            'Coming soon...',
            style: TextStyle(fontSize: 14, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }
}
