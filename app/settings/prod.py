from .base import *

import os
if "SENTRY_SDK" in os.environ:

    import sentry_sdk

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_SDK"),

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,
        traces_sample_rate=1.0,
    )
