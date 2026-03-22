"""
Frames de l'interface graphique.
"""

from .sidebar import SidebarFrame
from .dashboard import DashboardFrame
from .patients import PatientsFrame
from .visits import VisitsFrame
from .adverse_events import AdverseEventsFrame
from .documents import DocumentsFrame
from .queries import QueriesFrame
from .settings import SettingsFrame
from .monitoring import MonitoringFrame

__all__ = [
    "SidebarFrame",
    "DashboardFrame",
    "PatientsFrame",
    "VisitsFrame",
    "AdverseEventsFrame",
    "DocumentsFrame",
    "QueriesFrame",
    "SettingsFrame",
    "MonitoringFrame",
]
