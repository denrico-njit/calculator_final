# tests/e2e/test_dashboard_e2e.py

import pytest
import requests
from faker import Faker

fake = Faker()

BASE_URL = 'http://localhost:8000'


# ── Helpers ───────────────────────────────────────────────────────────────────

def register_user(password='Password1!'):
    username = fake.unique.user_name()
    requests.post(f'{BASE_URL}/auth/register', json={
        'username': username,
        'email': fake.unique.email(),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'password': password,
        'confirm_password': password,
    })
    return username


def get_token(username, password='Password1!'):
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'username': username,
        'password': password,
    })
    return response.json()['access_token']


def login(page, username, password='Password1!'):
    page.goto(f'{BASE_URL}/login')
    page.fill('#username', username)
    page.fill('#password', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f'{BASE_URL}/dashboard', timeout=5000)


def create_calculation(token, a=10, b=5, operation='add'):
    response = requests.post(
        f'{BASE_URL}/calculations',
        json={'a': a, 'b': b, 'operation': operation},
        headers={'Authorization': f'Bearer {token}'},
    )
    return response.json()


# ── Positive Scenarios ────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_dashboard_add_calculation(page, fastapi_server):
    """User submits the form; a new row appears in the table."""
    username = register_user()
    login(page, username)

    page.fill('#calcA', '10')
    page.select_option('#calcOperation', 'add')
    page.fill('#calcB', '5')
    page.click('#calculationForm button[type="submit"]')

    page.wait_for_selector('#successAlert:not(.hidden)')
    assert 'created' in page.inner_text('#successAlert').lower()

    page.wait_for_selector('#calculationsTable tr')
    table = page.inner_text('#calculationsTable')
    assert '10' in table
    assert '+' in table
    assert '5' in table
    assert '15' in table


@pytest.mark.e2e
def test_dashboard_browse_calculations(page, fastapi_server):
    """Calculations created via the API appear in the table on page load."""
    username = register_user()
    token = get_token(username)
    create_calculation(token, a=7, b=3, operation='multiply')

    login(page, username)

    page.wait_for_selector('#calculationsTable tr')
    table = page.inner_text('#calculationsTable')
    assert '7' in table
    assert 'x' in table
    assert '3' in table
    assert '21' in table


@pytest.mark.e2e
def test_dashboard_view_calculation(page, fastapi_server):
    """User clicks View; the modal shows the correct calculation details."""
    username = register_user()
    token = get_token(username)
    create_calculation(token, a=10, b=5, operation='add')

    login(page, username)
    page.wait_for_selector('#calculationsTable tr')

    page.click('.view-calc')
    page.wait_for_selector('#viewModal:not(.hidden)')

    modal = page.inner_text('#viewModal')
    assert '10' in modal
    assert '+' in modal
    assert '5' in modal
    assert '15' in modal

    page.click('#closeView')
    page.wait_for_selector('#viewModal.hidden')


@pytest.mark.e2e
def test_dashboard_edit_calculation(page, fastapi_server):
    """User edits a calculation via the modal; the row updates."""
    username = register_user()
    token = get_token(username)
    create_calculation(token, a=10, b=5, operation='add')

    login(page, username)
    page.wait_for_selector('#calculationsTable tr')

    page.click('.edit-calc')
    page.wait_for_selector('#editModal:not(.hidden)')

    page.fill('#editA', '20')
    page.select_option('#editOperation', 'subtract')
    page.fill('#editB', '4')
    page.click('#editForm button[type="submit"]')

    page.wait_for_selector('#successAlert:not(.hidden)')
    assert 'updated' in page.inner_text('#successAlert').lower()

    table = page.inner_text('#calculationsTable')
    assert '20' in table
    assert '-' in table
    assert '4' in table
    assert '16' in table


@pytest.mark.e2e
def test_dashboard_delete_calculation(page, fastapi_server):
    """User deletes a calculation; the row disappears."""
    username = register_user()
    token = get_token(username)
    create_calculation(token, a=10, b=5, operation='add')

    login(page, username)
    page.wait_for_selector('#calculationsTable tr')

    page.on('dialog', lambda dialog: dialog.accept())
    page.click('.delete-calc')

    page.wait_for_selector('#successAlert:not(.hidden)')
    assert 'deleted' in page.inner_text('#successAlert').lower()

    page.wait_for_selector('#calculationsTable tr')
    assert 'No calculations' in page.inner_text('#calculationsTable')


# ── Negative Scenarios ────────────────────────────────────────────────────────

@pytest.mark.e2e
def test_dashboard_unauthenticated(page, fastapi_server):
    """Visiting /dashboard without a token redirects to /login."""
    page.goto(f'{BASE_URL}/dashboard')
    page.wait_for_url(f'{BASE_URL}/login', timeout=3000)


@pytest.mark.e2e
def test_dashboard_add_divide_by_zero(page, fastapi_server):
    """Client-side validation blocks divide-by-zero before submission."""
    username = register_user()
    login(page, username)

    page.fill('#calcA', '10')
    page.select_option('#calcOperation', 'divide')
    page.fill('#calcB', '0')
    page.click('#calculationForm button[type="submit"]')

    page.wait_for_selector('#errorAlert:not(.hidden)')
    assert 'divide by zero' in page.inner_text('#errorAlert').lower()


@pytest.mark.e2e
def test_dashboard_edit_divide_by_zero(page, fastapi_server):
    """Client-side validation blocks divide-by-zero in the edit modal."""
    username = register_user()
    token = get_token(username)
    create_calculation(token, a=10, b=5, operation='add')

    login(page, username)
    page.wait_for_selector('#calculationsTable tr')

    page.click('.edit-calc')
    page.wait_for_selector('#editModal:not(.hidden)')

    page.select_option('#editOperation', 'divide')
    page.fill('#editB', '0')
    page.click('#editForm button[type="submit"]')

    page.wait_for_selector('#errorAlert:not(.hidden)')
    assert 'divide by zero' in page.inner_text('#errorAlert').lower()