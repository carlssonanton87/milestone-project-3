# 🧪 Testing - TradeTracker

This document outlines the testing strategy for the TradeTracker Django project.

---

## Automated Testing

### Python Unit Tests
Comprehensive unit tests were developed for the Django application to verify the functionality of individual components. These tests focus on:

We use Django’s built-in `TestCase` class to validate core functionality.

### ✅ To run tests:

python manage.py test

## ✅ What is Tested

### `trades/tests.py`

| Test Name                     | Purpose |
|------------------------------|---------|
| `test_return_percent`        | Ensures return percentage is correctly calculated |
| `test_holding_days`          | Ensures holding duration (in days) is correct |
| `test_trade_str_representation` | Ensures `__str__` returns expected format |
| `test_trade_outcome_choices` | Verifies valid outcome values (`win`, `loss`, `open`) |
| `test_open_trade_return_none` | Ensures open trades return `None` for return and holding time |

---

## 👤 Manual User Testing

### User Flows Tested
| Action | Verified Behavior |
|--------|-------------------|
| Register new account | Redirects to dashboard |
| Log in with existing user | Grants access to dashboard |
| Add a new trade | Form validates & saves correctly |
| Edit trade | Fields update and save successfully |
| Delete trade | Removes trade from list |
| View dashboard stats | Metrics update in real time |
| Use date filters | Filters dashboard correctly |
| Logout | Redirects to landing page |
| Unauthorized access | Redirects to login page |

---

## 🖥️ Browser Compatibility

Tested manually on:

- Chrome (latest)
- Firefox (latest)
- Safari (Mac)
- Edge

All layouts tested on mobile and desktop screens (responsive design).

---
.

## 🧪 Optional: Run with coverage
pip install coverage
coverage run manage.py test
coverage report


## 🧹 TODO (Future)
- Add Automated test part
- Add integration tests
- Add form validation tests
- Add Performance Testing
- Setup GitHub Actions for CI test runs
