# Step 1: Add this file to __init__.py
# Step 2: Add your functions below.
# Step 3: Don't forget to fire the task somewhere if that is the intended use of this file.


# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

# Example task
# @shared_task
# def function_title(kwarg):
#       logger.info("Doing something with "+str(kwarg))
#       output = "Success!"
#       return output
