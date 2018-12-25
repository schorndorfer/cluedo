
import logging
import pytest
from .context import *
import shutil
import os

# @pytest.fixture(scope="session",
#                 params=[pytest.mark.spark_local('local'),
#                         pytest.mark.spark_yarn('yarn')])
# pylint: disable=redefined-outer-name
@pytest.fixture(scope="module")
def cluedo_solver(request):
    return Cluedo([('Will', 6), ('Julie', 6), ('Laura', 6)])

