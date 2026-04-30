"""
ACEest Fitness & Gym - Pytest Test Suite
Task 3: Unit Testing and Test Automation
Tests cover: health check, client CRUD, workouts, metrics, programs, login
"""

import pytest
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, init_db, DB_NAME
