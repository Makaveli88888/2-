class OrderExecutor:
    """Permanent fail-closed stub. This class cannot submit or cancel live orders."""

    def __init__(self, *args, **kwargs):
        self._enabled = False

    async def place_order(self, *args, **kwargs):
        raise RuntimeError("OrderExecutor is disabled. JOKERAl has no live execution capability.")

    async def cancel_order(self, *args, **kwargs):
        raise RuntimeError("OrderExecutor is disabled. JOKERAl has no live execution capability.")
