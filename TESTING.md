# Testing Guide

This document describes the testing framework and practices for the Neighborhood Food Sharing Platform.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_user_service.py
│   ├── test_food_service.py
│   └── test_exchange_service.py
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   └── test_complete_workflow.py
└── fixtures/                # Test data generators
    ├── __init__.py
    └── sample_data.py
```

## Running Tests

### Quick Start

```bash
# Run all tests
./scripts/test.sh

# Run only unit tests
./scripts/test.sh --unit

# Run only integration tests
./scripts/test.sh --integration

# Run with verbose output
./scripts/test.sh --verbose
```

### Using pytest directly

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_user_service.py

# Run tests matching pattern
pytest -k "test_create_user"

# Run with markers
pytest -m unit
pytest -m integration
```

## Test Categories

### Unit Tests
- Test individual service classes in isolation
- Mock external dependencies (database, Redis, Telegram bot)
- Fast execution (< 1 second per test)
- High code coverage (aim for >90%)

### Integration Tests
- Test complete workflows end-to-end
- Use real database (in-memory SQLite for tests)
- Test API endpoints with actual HTTP requests
- Verify service interactions work correctly

## Test Fixtures

Common fixtures available in all tests:

- `test_db`: In-memory database session
- `sample_building`: Pre-created building
- `sample_user`: Pre-created user
- `sample_user2`: Second user for exchange tests
- `sample_food_post`: Pre-created food post
- `sample_exchange`: Pre-created exchange
- `sample_credit_account`: Pre-created credit account
- `mock_telegram_bot`: Mocked Telegram bot
- `mock_redis`: Mocked Redis client

## Writing Tests

### Unit Test Example

```python
@pytest.mark.asyncio
async def test_create_user(test_db, sample_building):
    """Test user creation."""
    service = UserService(test_db)
    
    user = await service.create_user(
        telegram_id=123456789,
        email="test@example.com",
        display_name="Test User",
        phone_number="+1234567890",
        apartment_number="101",
        building_id=sample_building.id
    )
    
    assert user is not None
    assert user.telegram_id == 123456789
    assert user.email == "test@example.com"
```

### Integration Test Example

```python
def test_create_food_post(client, sample_user):
    """Test creating a food post via API."""
    food_data = {
        "title": "Test Food",
        "description": "A test food item",
        "category": "main_course",
        "serving_size": "serves_2_4",
        # ... other fields
    }
    
    response = client.post("/foods/", json=food_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == "Test Food"
```

## Test Data Generation

Use the `SampleDataGenerator` for creating test data:

```python
from tests.fixtures.sample_data import SampleDataGenerator

# Generate random food data
food_data = SampleDataGenerator.generate_food_data()

# Generate data with overrides
food_data = SampleDataGenerator.generate_food_data(
    title="Custom Title",
    credit_value=15
)

# Generate scenario-specific data
expensive_food = SampleDataGenerator.create_test_scenario_data("expensive_item")
```

## Mocking External Services

### Telegram Bot

```python
@pytest.mark.asyncio
@patch('src.services.notification_service.NotificationService.send_message')
async def test_with_telegram_mock(mock_send_message):
    mock_send_message.return_value = True
    
    # Your test code here
    # Notifications will be mocked
```

### Redis

```python
@patch('src.core.redis.get_redis_client')
async def test_with_redis_mock(mock_redis_client):
    mock_redis_client.return_value.get.return_value = None
    
    # Your test code here
```

## Coverage Requirements

- **Overall Coverage**: Minimum 80%
- **Service Classes**: Minimum 90%
- **API Endpoints**: Minimum 85%
- **Critical Paths**: 100% (user creation, food claiming, credit transfers)

### Viewing Coverage

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Database

Tests use an in-memory SQLite database:

- Fresh database for each test function
- No persistent state between tests
- Fast setup and teardown
- Supports all SQLAlchemy operations

## Continuous Integration

Tests run automatically on:

- Pull request creation
- Push to main branch
- Manual trigger

### CI Requirements

- All tests must pass
- Coverage must meet minimum thresholds
- No test should take longer than 30 seconds
- Integration tests must be stable

## Performance Testing

For performance testing (not included in regular test suite):

```bash
# Run performance tests
pytest tests/performance/ -m slow

# Profile slow tests
pytest --profile --profile-svg
```

## Debugging Tests

### Running Single Test with Debug

```bash
# Run with debug output
pytest tests/unit/test_user_service.py::TestUserService::test_create_user -v -s

# Run with pdb debugger
pytest tests/unit/test_user_service.py::TestUserService::test_create_user --pdb
```

### Common Debugging Issues

1. **Database State**: Ensure test database is clean
2. **Async Issues**: Use `pytest-asyncio` properly
3. **Mock Configuration**: Verify mocks are set up correctly
4. **Fixture Dependencies**: Check fixture dependency order

## Best Practices

### Test Naming

```python
def test_create_user_success():           # ✅ Clear intent
def test_create_user_with_invalid_email(): # ✅ Specific case
def test_user_creation():                 # ❌ Too generic
```

### Test Organization

- One test class per service class
- Group related tests together
- Use descriptive docstrings
- Keep tests focused and atomic

### Assertions

```python
# ✅ Good assertions
assert user.email == "test@example.com"
assert len(foods) == 3
assert exchange.status == ExchangeStatus.CONFIRMED

# ❌ Weak assertions
assert user is not None
assert response.status_code != 500
```

### Test Independence

- Each test should be independent
- No shared state between tests
- Clean database for each test
- Mock external dependencies

## Adding New Tests

1. **Unit Tests**: Add to appropriate service test file
2. **Integration Tests**: Add to workflow or endpoint test file
3. **Fixtures**: Add reusable fixtures to `conftest.py`
4. **Test Data**: Add generators to `sample_data.py`

### Checklist for New Features

- [ ] Unit tests for all service methods
- [ ] Integration tests for API endpoints
- [ ] Error case testing
- [ ] Edge case validation
- [ ] Mock external dependencies
- [ ] Update coverage thresholds if needed