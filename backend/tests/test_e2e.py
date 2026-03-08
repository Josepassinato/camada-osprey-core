"""
End-to-end tests for Imigrai B2B platform.
Tests against the running server at localhost:8001.
"""

import time
import pytest
import httpx

BASE = "http://localhost:8001"

# Unique test data
_ts = str(int(time.time()))
FIRM = "Test Law Firm E2E"
EMAIL = f"test_e2e_{_ts}@imigrai.app"
PASSWORD = "TestPass123!"

# Shared state across tests
_state = {}


@pytest.mark.asyncio
async def test_01_register():
    """Register a new office."""
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{BASE}/api/auth/b2b/register", json={
            "firm_name": FIRM,
            "owner_name": "Test Owner",
            "email": EMAIL,
            "password": PASSWORD,
        })
    assert r.status_code == 200, r.text
    data = r.json()
    assert "token" in data
    assert data["user"]["role"] == "owner"
    _state["token"] = data["token"]
    _state["office_id"] = data["user"]["office_id"]


@pytest.mark.asyncio
async def test_02_login():
    """Login with created credentials."""
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{BASE}/api/auth/b2b/login", json={
            "email": EMAIL,
            "password": PASSWORD,
        })
    assert r.status_code == 200, r.text
    assert "token" in r.json()


@pytest.mark.asyncio
async def test_03_me():
    """Validate JWT returns correct data."""
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/api/auth/b2b/me",
            headers={"Authorization": f"Bearer {_state['token']}"})
    assert r.status_code == 200, r.text
    assert r.json()["office_id"] == _state["office_id"]


@pytest.mark.asyncio
async def test_04_create_case():
    """Create a case and validate office isolation."""
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{BASE}/api/cases", json={
            "client_name": "João Silva",
            "visa_type": "H-1B",
            "notes": "Software engineer, offer from Acme Corp",
        }, headers={"Authorization": f"Bearer {_state['token']}"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["status"] == "intake"
    _state["case_id"] = data["case_id"]


@pytest.mark.asyncio
async def test_05_list_cases():
    """List cases — should return the created case."""
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/api/cases",
            headers={"Authorization": f"Bearer {_state['token']}"})
    assert r.status_code == 200, r.text
    cases = r.json()
    assert any(c["case_id"] == _state["case_id"] for c in cases)


@pytest.mark.asyncio
async def test_06_chat_message():
    """Send a message to the Chief of Staff."""
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(f"{BASE}/api/osprey-chat/chat", json={
            "message": "What documents do I need for the H-1B petition for João Silva?",
            "channel": "web",
        }, headers={"Authorization": f"Bearer {_state['token']}"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "response" in data
    assert len(data["response"]) > 50  # Substantive response


@pytest.mark.asyncio
async def test_07_generate_letter():
    """Generate a cover letter for the case."""
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{BASE}/api/letters/generate", json={
            "case_id": _state["case_id"],
            "letter_type": "initial_filing",
        }, headers={"Authorization": f"Bearer {_state['token']}"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "content" in data
    assert len(data["content"]) > 200  # Substantive letter
    assert "USCIS" in data["content"]
    _state["letter_id"] = data["letter_id"]


@pytest.mark.asyncio
async def test_08_dashboard_stats():
    """Dashboard returns correct metrics."""
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/api/cases/stats",
            headers={"Authorization": f"Bearer {_state['token']}"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["total"] >= 1
    assert "active" in data
    assert "critical" in data


@pytest.mark.asyncio
async def test_09_multi_tenant_isolation():
    """Create second office and verify isolation."""
    async with httpx.AsyncClient() as c:
        # Create second office
        r2 = await c.post(f"{BASE}/api/auth/b2b/register", json={
            "firm_name": "Other Firm",
            "owner_name": "Other Owner",
            "email": f"other_{_ts}@imigrai.app",
            "password": "OtherPass123!",
        })
        assert r2.status_code == 200
        token2 = r2.json()["token"]

        # Try accessing case from office 1 with token from office 2
        r = await c.get(f"{BASE}/api/cases/{_state['case_id']}",
            headers={"Authorization": f"Bearer {token2}"})
    # Should return 404 (not found for this office) or 403
    assert r.status_code in [403, 404], f"Expected 403/404, got {r.status_code}"


@pytest.mark.asyncio
async def test_10_rate_limit():
    """Rate limiting blocks after limit."""
    async with httpx.AsyncClient(timeout=30) as c:
        responses = []
        for i in range(25):  # Limit is 20/min for /chat
            r = await c.post(f"{BASE}/api/osprey-chat/chat",
                json={"message": f"test {i}", "channel": "web"},
                headers={"Authorization": f"Bearer {_state['token']}"})
            responses.append(r.status_code)
            if r.status_code == 429:
                break
    # At least one response should be 429
    assert 429 in responses, f"Expected 429 in responses, got: {set(responses)}"


@pytest.mark.asyncio
async def test_11_invite_user():
    """Invite a user to the office."""
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{BASE}/api/settings/users/invite", json={
            "email": f"paralegal_{_ts}@imigrai.app",
            "name": "Maria Paralegal",
            "role": "paralegal",
        }, headers={"Authorization": f"Bearer {_state['token']}"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "temp_password" in data
    assert len(data["temp_password"]) >= 6


@pytest.mark.asyncio
async def test_12_settings_office():
    """Office settings are accessible."""
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{BASE}/api/settings/office",
            headers={"Authorization": f"Bearer {_state['token']}"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["name"] == FIRM
