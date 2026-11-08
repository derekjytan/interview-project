from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import text


def create_conversation(client, headers):
    response = client.post("/api/conversation", headers=headers)
    assert response.status_code == 201
    return response.json()["id"]


def completion_body(client):
    models = client.get("/api/models").json()
    return {
        "content": "Hello",
        "model": next(m["id"] for m in models if m["is_default"]),
    }


def stub_model(client, *, failure=False):
    from api.dependencies import get_chat_service
    from app import app
    from service.openai import ModelServiceError

    calls = []

    def complete(turns, model):
        # A model request must not hold a read transaction or DB connection.
        assert not client.db_sessions[-1].in_transaction()
        calls.append(turns)
        if failure:
            raise ModelServiceError(502, "Model unavailable")
        return SimpleNamespace(content="Hello from the assistant")

    app.dependency_overrides[get_chat_service] = lambda: SimpleNamespace(
        complete=complete
    )
    return calls


def test_health_and_seeded_history(client, alice):
    assert client.get("/api/health").json() == {"ok": True}
    response = client.get("/api/conversations", headers=alice)
    assert response.status_code == 200
    conversations = response.json()
    assert conversations
    for conversation in conversations:
        messages = conversation["messages"]
        assert [m["created_at"] for m in messages] == sorted(
            m["created_at"] for m in messages
        )
        assert (
            client.get(f"/api/conversation/{conversation['id']}", headers=alice).json()
            == conversation
        )


def test_auth_persistence_and_duplicate_signup(client):
    credentials = {"name": "new-user", "password": "test-password"}
    response = client.post("/api/auth/signup", json=credentials)
    assert response.status_code == 201
    assert set(response.json()["user"]) == {"id", "name"}
    assert client.post("/api/auth/signup", json=credentials).status_code == 409
    assert (
        client.post(
            "/api/auth/login", json={**credentials, "password": "wrong"}
        ).status_code
        == 401
    )
    login = client.post("/api/auth/login", json=credentials)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['token']}"}
    assert client.get("/api/conversations", headers=headers).json() == []
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/conversations", headers=headers).status_code == 401
    assert client.get("/api/conversations").status_code == 401


def test_conversation_ownership(client, alice):
    conversation_id = create_conversation(client, alice)
    bob = client.post(
        "/api/auth/login", json={"name": "bob", "password": "bob-password"}
    )
    headers = {"Authorization": f"Bearer {bob.json()['token']}"}
    assert (
        client.get(f"/api/conversation/{conversation_id}", headers=headers).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/conversation/{conversation_id}/archive", headers=headers
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/api/chat/completion/{conversation_id}",
            headers=headers,
            json=completion_body(client),
        ).status_code
        == 404
    )
    assert conversation_id not in [
        c["id"] for c in client.get("/api/conversations", headers=headers).json()
    ]
    assert client.get(f"/api/conversation/{uuid4()}", headers=alice).status_code == 404
    assert client.get("/api/conversation/not-a-uuid", headers=alice).status_code == 422


def test_archive_is_idempotent_and_prevents_completion(client, alice):
    conversation_id = create_conversation(client, alice)
    url = f"/api/conversation/{conversation_id}/archive"
    first = client.post(url, headers=alice)
    second = client.post(url, headers=alice)
    assert first.status_code == second.status_code == 200
    assert first.json()["archived_at"] is not None
    assert first.json()["archived_at"] == second.json()["archived_at"]
    calls = stub_model(client)
    response = client.post(
        f"/api/chat/completion/{conversation_id}",
        headers=alice,
        json=completion_body(client),
    )
    assert response.status_code == 409
    assert calls == []


def test_exchange_persistence_order_history_and_title(client, alice):
    conversation_id = create_conversation(client, alice)
    calls = stub_model(client)
    url = f"/api/chat/completion/{conversation_id}"
    body = {**completion_body(client), "content": "x" * 100}
    first = client.post(url, headers=alice, json=body)
    assert first.status_code == 200
    messages = first.json()
    assert [m["role"] for m in messages] == ["HUMAN", "AI"]
    assert messages[0]["created_at"] < messages[1]["created_at"]
    conversation = client.get(
        f"/api/conversation/{conversation_id}", headers=alice
    ).json()
    assert conversation["messages"] == messages
    assert conversation["title"] == "x" * 80
    assert conversation["updated_at"] >= conversation["created_at"]
    second = client.post(url, headers=alice, json=completion_body(client))
    assert second.status_code == 200
    assert [turn.content for turn in calls[1]] == [
        "x" * 100,
        "Hello from the assistant",
        "Hello",
    ]
    conversation = client.get(
        f"/api/conversation/{conversation_id}", headers=alice
    ).json()
    assert conversation["title"] == "x" * 80
    assert len(conversation["messages"]) == 4


def test_model_failure_does_not_persist(client, alice):
    conversation_id = create_conversation(client, alice)
    before = client.get(f"/api/conversation/{conversation_id}", headers=alice).json()
    stub_model(client, failure=True)
    response = client.post(
        f"/api/chat/completion/{conversation_id}",
        headers=alice,
        json=completion_body(client),
    )
    assert response.status_code == 502
    assert (
        client.get(f"/api/conversation/{conversation_id}", headers=alice).json()
        == before
    )


def test_second_insert_failure_rolls_back_entire_exchange(client, database, alice):
    conversation_id = create_conversation(client, alice)
    before = client.get(f"/api/conversation/{conversation_id}", headers=alice).json()
    # Fail the second insert after the HUMAN row has been flushed to Postgres.
    with database.begin() as connection:
        connection.execute(
            text("""
            CREATE FUNCTION reject_ai() RETURNS trigger LANGUAGE plpgsql AS $$
            BEGIN
                IF NEW.role = 'AI' THEN RAISE EXCEPTION 'injected write failure'; END IF;
                RETURN NEW;
            END $$;
            CREATE TRIGGER reject_ai BEFORE INSERT ON conversation_messages
            FOR EACH ROW EXECUTE FUNCTION reject_ai();
        """)
        )
    stub_model(client)
    response = client.post(
        f"/api/chat/completion/{conversation_id}",
        headers=alice,
        json=completion_body(client),
    )
    assert response.status_code == 500
    assert (
        client.get(f"/api/conversation/{conversation_id}", headers=alice).json()
        == before
    )
