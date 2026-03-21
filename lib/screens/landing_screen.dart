import 'package:flutter/material.dart';
import '../models/study.dart';
import '../widgets/study_card.dart';
import '../services/database_service.dart';
import 'study_home_screen.dart';

/// Page d'accueil avec la liste des études
class LandingScreen extends StatefulWidget {
  const LandingScreen({super.key});

  @override
  State<LandingScreen> createState() => _LandingScreenState();
}

class _LandingScreenState extends State<LandingScreen> {
  final TextEditingController _searchController = TextEditingController();
  List<Study> _studies = [];
  List<Study> _filteredStudies = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadStudies();
  }

  Future<void> _loadStudies() async {
    setState(() => _isLoading = true);
    try {
      final studies = await DatabaseService.getStudies();
      setState(() {
        _studies = studies;
        _filteredStudies = studies;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading studies: $e')),
        );
      }
    }
  }

  void _onSearch(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredStudies = _studies;
      } else {
        _filteredStudies = _studies.where((study) {
          final searchLower = query.toLowerCase();
          return study.name.toLowerCase().contains(searchLower) ||
              study.number.toLowerCase().contains(searchLower) ||
              (study.sponsor?.toLowerCase().contains(searchLower) ?? false);
        }).toList();
      }
    });
  }

  void _navigateToStudy(Study study) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => StudyHomeScreen(study: study),
      ),
    ).then((_) => _loadStudies()); // Refresh on return
  }

  void _showNewStudyDialog() {
    showDialog(
      context: context,
      builder: (context) => _NewStudyDialog(
        onSave: (study) async {
          Navigator.pop(context);
          await DatabaseService.createStudy(study);
          _loadStudies();
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Study created!')),
            );
          }
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Studies',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                FilledButton.icon(
                  onPressed: _showNewStudyDialog,
                  icon: const Icon(Icons.add),
                  label: const Text('New Study'),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Barre de recherche
            SizedBox(
              width: 300,
              child: TextField(
                controller: _searchController,
                onChanged: _onSearch,
                decoration: InputDecoration(
                  hintText: 'Search studies...',
                  prefixIcon: const Icon(Icons.search),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                ),
              ),
            ),

            const SizedBox(height: 32),

            // Grille d'études
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _filteredStudies.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.science_outlined, size: 64, color: Colors.grey[600]),
                              const SizedBox(height: 16),
                              Text(
                                'No studies found',
                                style: TextStyle(color: Colors.grey[400], fontSize: 16),
                              ),
                              const SizedBox(height: 8),
                              TextButton.icon(
                                onPressed: _showNewStudyDialog,
                                icon: const Icon(Icons.add),
                                label: const Text('Create your first study'),
                              ),
                            ],
                          ),
                        )
                      : RefreshIndicator(
                          onRefresh: _loadStudies,
                          child: SingleChildScrollView(
                            physics: const AlwaysScrollableScrollPhysics(),
                            child: Wrap(
                              spacing: 20,
                              runSpacing: 20,
                              children: _filteredStudies.map((study) {
                                return StudyCard(
                                  study: study,
                                  onTap: () => _navigateToStudy(study),
                                );
                              }).toList(),
                            ),
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }
}

class _NewStudyDialog extends StatefulWidget {
  final Function(Study) onSave;

  const _NewStudyDialog({required this.onSave});

  @override
  State<_NewStudyDialog> createState() => _NewStudyDialogState();
}

class _NewStudyDialogState extends State<_NewStudyDialog> {
  final _numberController = TextEditingController();
  final _nameController = TextEditingController();
  final _sponsorController = TextEditingController();
  final _pathologyController = TextEditingController();
  String _phase = 'II';

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('New Study'),
      content: SizedBox(
        width: 400,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _numberController,
              decoration: const InputDecoration(labelText: 'Study Number *'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: 'Study Name'),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _phase,
              decoration: const InputDecoration(labelText: 'Phase'),
              items: ['I', 'II', 'III', 'IV'].map((p) {
                return DropdownMenuItem(value: p, child: Text('Phase $p'));
              }).toList(),
              onChanged: (value) {
                if (value != null) setState(() => _phase = value);
              },
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _sponsorController,
              decoration: const InputDecoration(labelText: 'Sponsor'),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _pathologyController,
              decoration: const InputDecoration(labelText: 'Pathology'),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        FilledButton(
          onPressed: _numberController.text.isNotEmpty
              ? () {
                  final study = Study(
                    studyNumber: _numberController.text,
                    studyName: _nameController.text.isEmpty ? null : _nameController.text,
                    phase: _phase,
                    sponsor: _sponsorController.text.isEmpty ? null : _sponsorController.text,
                    pathology: _pathologyController.text.isEmpty ? null : _pathologyController.text,
                  );
                  widget.onSave(study);
                }
              : null,
          child: const Text('Create'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _numberController.dispose();
    _nameController.dispose();
    _sponsorController.dispose();
    _pathologyController.dispose();
    super.dispose();
  }
}
