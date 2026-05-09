# tests/e2e/test_e2e.py

import pytest  # Import the pytest framework for writing and running tests
import requests
from faker import Faker

fake = Faker()

# The following decorators and functions define E2E tests for the FastAPI calculator application.

@pytest.mark.e2e
def test_calculator_add(page, fastapi_server):
    """
    Test the addition functionality of the calculator.

    This test simulates a user performing an addition operation using the calculator
    on the frontend. It fills in two numbers, clicks the "Add" button, and verifies
    that the result displayed is correct.
    """
    # Navigate the browser to the homepage URL of the FastAPI application.
    page.goto('http://localhost:8000')
    
    # Fill in the first number input field (with id 'a') with the value '10'.
    page.fill('#a', '10')
    
    # Fill in the second number input field (with id 'b') with the value '5'.
    page.fill('#b', '5')
    
    # Click the button that has the exact text "Add". This triggers the addition operation.
    page.click('button:text("Add")')

    page.wait_for_function("document.getElementById('result').innerText !== ''")
    assert page.inner_text('#result') == 'Result: 15'

@pytest.mark.e2e
def test_calculator_divide_by_zero(page, fastapi_server):
    """
    Test the divide by zero functionality of the calculator.

    This test simulates a user attempting to divide a number by zero using the calculator.
    It fills in the numbers, clicks the "Divide" button, and verifies that the appropriate
    error message is displayed. This ensures that the application correctly handles invalid
    operations and provides meaningful feedback to the user.
    """
    # Navigate the browser to the homepage URL of the FastAPI application.
    page.goto('http://localhost:8000')
    
    # Fill in the first number input field (with id 'a') with the value '10'.
    page.fill('#a', '10')
    
    # Fill in the second number input field (with id 'b') with the value '0', attempting to divide by zero.
    page.fill('#b', '0')
    
    # Click the button that has the exact text "Divide". This triggers the division operation.
    page.click('button:text("Divide")')

    page.wait_for_function("document.getElementById('result').innerText !== ''")
    assert page.inner_text('#result') == 'Error: Cannot divide by zero!'

@pytest.mark.e2e                                                                                                                                            
def test_calculator_power(page, fastapi_server):                                                                                                            
    """                                                                                                                                                     
    Test the power functionality of the calculator.                                                                                                       
                                                                                                                                                            
    This test simulates a user performing an exponentiation operation using the                                                                           
    calculator on the frontend. It fills in two numbers, clicks the "Power" button,                                                                         
    and verifies that the result displayed is correct.                                                                                                      
    """                                                                                                                                                     
    page.goto('http://localhost:8000')                                                                                                                      
    page.fill('#a', '2')                                                                                                                                    
    page.fill('#b', '3')                                                                                                                                    
    page.click('button:text("Power")')
                                                                                                                                                            
    page.wait_for_function("document.getElementById('result').innerText !== ''")                                                                            
    assert page.inner_text('#result') == 'Result: 8'  

@pytest.mark.e2e
def test_register_success(page, fastapi_server):
    """
    Test that a user can successfully register with valid data.

    This test navigates to the registration page, fills in all required fields
    with valid data, submits the form, and verifies that the success message
    is displayed to the user.
    """
    page.goto('http://localhost:8000/register')

    page.fill('#username', fake.user_name())
    page.fill('#email', fake.email())
    page.fill('#first_name', fake.first_name())
    page.fill('#last_name', fake.last_name())
    page.fill('#password', 'Password1!')
    page.fill('#confirm_password', 'Password1!')

    page.click('button[type="submit"]')

    page.wait_for_selector('#successAlert:not(.hidden)')
    assert 'Registration successful' in page.inner_text('#successAlert')

@pytest.mark.e2e
def test_login_success(page, fastapi_server):
    """
    Test that a user can successfully log in with valid credentials.

    This test registers a user directly via the API to avoid depending on
    the registration UI, then navigates to the login page, fills in the
    credentials, submits the form, and verifies that the success message
    is displayed.
    """
    username = fake.user_name()
    password = 'Password1!'

    requests.post('http://localhost:8000/auth/register', json={
        'username': username,
        'email': fake.email(),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'password': password,
        'confirm_password': password,
    })

    page.goto('http://localhost:8000/login')

    page.fill('#username', username)
    page.fill('#password', password)

    page.click('button[type="submit"]')

    page.wait_for_selector('#successAlert:not(.hidden)')
    assert 'Login successful' in page.inner_text('#successAlert')

@pytest.mark.e2e
def test_register_short_password(page, fastapi_server):
    """
    Test that registering with a short password shows a client-side error.

    This test navigates to the registration page, fills in all fields but
    provides a password that is too short, submits the form, and verifies
    that the error message is displayed without the form being submitted
    to the server.
    """
    page.goto('http://localhost:8000/register')

    page.fill('#username', fake.user_name())
    page.fill('#email', fake.email())
    page.fill('#first_name', fake.first_name())
    page.fill('#last_name', fake.last_name())
    page.fill('#password', 'short')
    page.fill('#confirm_password', 'short')

    page.click('button[type="submit"]')

    page.wait_for_selector('#errorAlert:not(.hidden)')
    assert 'Password must be at least 8 characters' in page.inner_text('#errorAlert')

@pytest.mark.e2e
def test_login_wrong_password(page, fastapi_server):
    """
    Test that logging in with an incorrect password shows an error message.

    This test registers a user directly via the API, then navigates to the
    login page, submits with the wrong password, and verifies that the server's
    401 response causes the UI to display an error message.
    """
    username = fake.user_name()

    requests.post('http://localhost:8000/auth/register', json={
        'username': username,
        'email': fake.email(),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'password': 'Password1!',
        'confirm_password': 'Password1!',
    })

    page.goto('http://localhost:8000/login')

    page.fill('#username', username)
    page.fill('#password', 'WrongPassword1!')

    page.click('button[type="submit"]')

    page.wait_for_selector('#errorAlert:not(.hidden)')
    assert 'Login failed' in page.inner_text('#errorAlert')
