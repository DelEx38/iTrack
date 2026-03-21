import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/site.dart';
import '../models/patient.dart';
import '../models/staff.dart';
import '../widgets/status_badge.dart';

class SiteDetailScreen extends StatefulWidget {
  final StudySite site;

  const SiteDetailScreen({super.key, required this.site});

  @override
  State<SiteDetailScreen> createState() => _SiteDetailScreenState();
}

class _SiteDetailScreenState extends State<SiteDetailScreen> {
  late List<StaffMember> _staffList;
  final _dateFormat = DateFormat('yyyy-MM-dd');

  @override
  void initState() {
    super.initState();
    _staffList = List.from(demoStaffBySite[widget.site.id] ?? []);
  }

  void _showStaffDialog([StaffMember? staff]) {
    showDialog(
      context: context,
      builder: (context) => _StaffDialog(
        staff: staff,
        studySiteId: widget.site.id ?? 0,
        onSave: (newStaff) {
          setState(() {
            if (staff != null) {
              final index = _staffList.indexWhere((s) => s.id == staff.id);
              if (index >= 0) {
                _staffList[index] = newStaff;
              }
            } else {
              _staffList.add(newStaff);
            }
          });
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(staff == null ? 'Staff added!' : 'Staff updated!')),
          );
        },
      ),
    );
  }

  void _deleteStaff(StaffMember staff) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Staff Member'),
        content: Text('Are you sure you want to delete ${staff.fullName}?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () {
              setState(() {
                _staffList.removeWhere((s) => s.id == staff.id);
              });
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Staff deleted!')),
              );
            },
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final site = widget.site;

    // Patients de ce site
    final sitePatients = demoPatients.where((p) => p.siteId == site.siteNumber).toList();

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            IconButton(
              icon: const Icon(Icons.arrow_back),
              onPressed: () => Navigator.pop(context),
            ),
            const SizedBox(width: 8),
            const Text('Retour à la liste des centres'),
          ],
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Bandeau Site Information
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.grey[900],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey[800]!),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Titre avec statut à droite
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        site.siteName ?? 'Site ${site.siteNumber}',
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      StatusBadge(status: site.status),
                    ],
                  ),
                  const Divider(height: 24),
                  // Infos sur 2 colonnes x 3 lignes
                  Row(
                    children: [
                      Expanded(
                        child: _InfoRow(label: 'Site Number', value: site.siteNumber ?? '-'),
                      ),
                      Expanded(
                        child: _InfoRow(label: 'Site Name', value: site.siteName ?? '-'),
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      Expanded(
                        child: _InfoRow(label: 'Principal Investigator', value: site.principalInvestigator ?? '-'),
                      ),
                      Expanded(
                        child: _InfoRow(label: 'Target Patients', value: '${site.targetPatients}'),
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      Expanded(
                        child: _InfoRow(
                          label: 'Activation Date',
                          value: site.activationDate != null
                              ? _dateFormat.format(site.activationDate!)
                              : '-',
                        ),
                      ),
                      Expanded(
                        child: _InfoRow(
                          label: 'First Patient In',
                          value: site.firstPatientDate != null
                              ? _dateFormat.format(site.firstPatientDate!)
                              : '-',
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Staff et Patients côte à côte
            IntrinsicHeight(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Staff
                  Expanded(
                    child: _StaffCard(
                      staffList: _staffList,
                      dateFormat: _dateFormat,
                      onAdd: () => _showStaffDialog(),
                      onEdit: _showStaffDialog,
                      onDelete: _deleteStaff,
                    ),
                  ),
                  const SizedBox(width: 24),
                  // Patients
                  Expanded(
                    child: _InfoCard(
                      title: 'Patients (${sitePatients.length})',
                      action: TextButton(
                        onPressed: () {},
                        child: const Text('View All'),
                      ),
                      children: [
                        if (sitePatients.isEmpty)
                          Padding(
                            padding: const EdgeInsets.all(16),
                            child: Text(
                              'No patients yet',
                              style: TextStyle(color: Colors.grey[500]),
                            ),
                          )
                        else
                          ...sitePatients.map((patient) => _PatientRow(
                                patient: patient,
                                dateFormat: _dateFormat,
                              )),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String title;
  final List<Widget> children;
  final Widget? action;

  const _InfoCard({required this.title, required this.children, this.action});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              if (action != null) action!,
            ],
          ),
          const Divider(height: 24),
          ...children,
        ],
      ),
    );
  }
}

class _StaffCard extends StatelessWidget {
  final List<StaffMember> staffList;
  final DateFormat dateFormat;
  final VoidCallback onAdd;
  final Function(StaffMember) onEdit;
  final Function(StaffMember) onDelete;

  const _StaffCard({
    required this.staffList,
    required this.dateFormat,
    required this.onAdd,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[900],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[800]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Staff (${staffList.length})',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              FilledButton.icon(
                onPressed: onAdd,
                icon: const Icon(Icons.add, size: 18),
                label: const Text('Add Staff'),
              ),
            ],
          ),
          const Divider(height: 24),
          if (staffList.isEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'No staff members yet',
                style: TextStyle(color: Colors.grey[500]),
              ),
            )
          else
            ...staffList.map((staff) => _StaffRow(
                  staff: staff,
                  dateFormat: dateFormat,
                  onEdit: () => onEdit(staff),
                  onDelete: () => onDelete(staff),
                )),
        ],
      ),
    );
  }
}

class _StaffRow extends StatelessWidget {
  final StaffMember staff;
  final DateFormat dateFormat;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _StaffRow({
    required this.staff,
    required this.dateFormat,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          // Role badge
          Container(
            width: 45,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Color(staff.role.color),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              staff.role.label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 11,
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(width: 12),
          // Name and dates
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  staff.fullName,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                Row(
                  children: [
                    Text(
                      staff.startDate != null
                          ? 'From: ${dateFormat.format(staff.startDate!)}'
                          : '-',
                      style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                    ),
                    if (staff.endDate != null) ...[
                      Text(
                        '  -  To: ${dateFormat.format(staff.endDate!)}',
                        style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
          // Status
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: staff.isActive ? Colors.green.withAlpha(50) : Colors.grey.withAlpha(50),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(
                color: staff.isActive ? Colors.green : Colors.grey,
              ),
            ),
            child: Text(
              staff.isActive ? 'Active' : 'Inactive',
              style: TextStyle(
                fontSize: 11,
                color: staff.isActive ? Colors.green : Colors.grey,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
          const SizedBox(width: 8),
          // Actions
          IconButton(
            icon: const Icon(Icons.edit, size: 18),
            onPressed: onEdit,
            tooltip: 'Edit',
          ),
          IconButton(
            icon: const Icon(Icons.delete, size: 18, color: Colors.red),
            onPressed: onDelete,
            tooltip: 'Delete',
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 150,
            child: Text(
              label,
              style: TextStyle(color: Colors.grey[500], fontSize: 13),
            ),
          ),
          Expanded(
            child: Text(value, style: const TextStyle(fontSize: 13)),
          ),
        ],
      ),
    );
  }
}

class _PatientRow extends StatelessWidget {
  final Patient patient;
  final DateFormat dateFormat;

  const _PatientRow({required this.patient, required this.dateFormat});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: Color(patient.status.color).withAlpha(50),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Center(
              child: Text(
                patient.initials ?? '?',
                style: TextStyle(
                  color: Color(patient.status.color),
                  fontWeight: FontWeight.bold,
                  fontSize: 11,
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  patient.patientNumber,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  patient.screeningDate != null
                      ? 'Screening: ${dateFormat.format(patient.screeningDate!)}'
                      : '-',
                  style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                ),
              ],
            ),
          ),
          Container(
            width: 95,
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Color(patient.status.color),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              patient.status.label,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 10,
                color: Colors.white,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _StaffDialog extends StatefulWidget {
  final StaffMember? staff;
  final int studySiteId;
  final Function(StaffMember) onSave;

  const _StaffDialog({
    this.staff,
    required this.studySiteId,
    required this.onSave,
  });

  @override
  State<_StaffDialog> createState() => _StaffDialogState();
}

class _StaffDialogState extends State<_StaffDialog> {
  late TextEditingController _firstNameController;
  late TextEditingController _lastNameController;
  late StaffCredential _credential;
  late StaffRole _role;
  DateTime? _startDate;
  DateTime? _endDate;

  @override
  void initState() {
    super.initState();
    _firstNameController = TextEditingController(text: widget.staff?.firstName ?? '');
    _lastNameController = TextEditingController(text: widget.staff?.lastName ?? '');
    _credential = widget.staff?.credential ?? StaffCredential.m;
    _role = widget.staff?.role ?? StaffRole.oth;
    _startDate = widget.staff?.startDate;
    _endDate = widget.staff?.endDate;
  }

  Future<void> _selectDate(bool isStart) async {
    final initialDate = isStart ? _startDate : _endDate;
    final picked = await showDatePicker(
      context: context,
      initialDate: initialDate ?? DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime(2030),
    );
    if (picked != null) {
      setState(() {
        if (isStart) {
          _startDate = picked;
        } else {
          _endDate = picked;
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isEdit = widget.staff != null;
    final dateFormat = DateFormat('yyyy-MM-dd');

    return AlertDialog(
      title: Text(isEdit ? 'Edit Staff Member' : 'Add Staff Member'),
      content: SizedBox(
        width: 450,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Credential and names row
            Row(
              children: [
                SizedBox(
                  width: 80,
                  child: DropdownButtonFormField<StaffCredential>(
                    value: _credential,
                    decoration: const InputDecoration(labelText: 'Title'),
                    items: StaffCredential.values.map((c) {
                      return DropdownMenuItem(value: c, child: Text(c.label));
                    }).toList(),
                    onChanged: (value) {
                      if (value != null) setState(() => _credential = value);
                    },
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _firstNameController,
                    decoration: const InputDecoration(labelText: 'First Name'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextField(
                    controller: _lastNameController,
                    decoration: const InputDecoration(labelText: 'Last Name'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // Role
            DropdownButtonFormField<StaffRole>(
              value: _role,
              decoration: const InputDecoration(labelText: 'Role'),
              items: StaffRole.values.map((r) {
                return DropdownMenuItem(
                  value: r,
                  child: Text('${r.label} - ${r.fullLabel}'),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) setState(() => _role = value);
              },
            ),
            const SizedBox(height: 16),
            // Dates row
            Row(
              children: [
                Expanded(
                  child: InkWell(
                    onTap: () => _selectDate(true),
                    child: InputDecorator(
                      decoration: const InputDecoration(labelText: 'Start Date'),
                      child: Text(
                        _startDate != null ? dateFormat.format(_startDate!) : 'Select date',
                        style: TextStyle(
                          color: _startDate != null ? null : Colors.grey[500],
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: InkWell(
                    onTap: () => _selectDate(false),
                    child: InputDecorator(
                      decoration: const InputDecoration(labelText: 'End Date'),
                      child: Text(
                        _endDate != null ? dateFormat.format(_endDate!) : 'Select date',
                        style: TextStyle(
                          color: _endDate != null ? null : Colors.grey[500],
                        ),
                      ),
                    ),
                  ),
                ),
              ],
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
          onPressed: () {
            if (_firstNameController.text.isEmpty || _lastNameController.text.isEmpty) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Please fill in first and last name')),
              );
              return;
            }
            final staff = StaffMember(
              id: widget.staff?.id ?? DateTime.now().millisecondsSinceEpoch,
              studySiteId: widget.studySiteId,
              firstName: _firstNameController.text,
              lastName: _lastNameController.text,
              credential: _credential,
              role: _role,
              startDate: _startDate,
              endDate: _endDate,
            );
            widget.onSave(staff);
          },
          child: const Text('Save'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    super.dispose();
  }
}
