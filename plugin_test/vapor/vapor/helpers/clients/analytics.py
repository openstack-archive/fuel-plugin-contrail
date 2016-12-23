from . import base


class ContrailAnalyticsClient(base.ContrailBaseClient):
    """Contrail analytics client."""

    def get_alarms(self):
        """Get alarms."""
        return self._get('/analytics/alarms')
