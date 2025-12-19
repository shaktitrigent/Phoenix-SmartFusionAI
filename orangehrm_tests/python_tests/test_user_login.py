"""Test file that loads scenarios from feature file."""

from pytest_bdd import scenarios

# Import step definitions so pytest-bdd can find them
import test_user_login_steps  # noqa: F401

# Load scenarios from the feature file
scenarios('../merged_feature_files/user_login.feature')

