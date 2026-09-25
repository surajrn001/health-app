from fastapi import status


def test_admin_can_create_doctor(client, admin_headers):
    payload = {
        "name": "Dr. Gregory House",
        "specialization": "Diagnostic Medicine",
        "email": "dr.house@princeton.edu",
    }
    response = client.post("/doctors", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["specialization"] == payload["specialization"]
    assert data["email"] == payload["email"]
    assert data["is_active"] is True
    assert "id" in data


def test_doctor_cannot_create_doctor(client, doctor1_fixture):
    payload = {
        "name": "Dr. Unauthorized",
        "specialization": "Pediatrics",
        "email": "unauth_doc@example.com",
    }
    response = client.post("/doctors", json=payload, headers=doctor1_fixture["headers"])
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_doctor_duplicate_email(client, admin_headers):
    payload = {
        "name": "Dr. First",
        "specialization": "Cardiology",
        "email": "unique_doc@example.com",
    }
    res1 = client.post("/doctors", json=payload, headers=admin_headers)
    assert res1.status_code == status.HTTP_201_CREATED

    res2 = client.post("/doctors", json=payload, headers=admin_headers)
    assert res2.status_code == status.HTTP_400_BAD_REQUEST


def test_list_doctors_with_pagination_and_search(client, admin_headers):
    client.post(
        "/doctors",
        json={"name": "Dr. Alice Smith", "specialization": "Cardiology", "email": "alice@hospital.com"},
        headers=admin_headers,
    )
    client.post(
        "/doctors",
        json={"name": "Dr. Bob Jones", "specialization": "Neurology", "email": "bob@hospital.com"},
        headers=admin_headers,
    )

    res = client.get("/doctors", headers=admin_headers)
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["meta"]["total_items"] >= 2
    assert len(data["items"]) >= 2

    search_res = client.get("/doctors?search=Alice", headers=admin_headers)
    search_data = search_res.json()
    assert search_data["meta"]["total_items"] == 1
    assert search_data["items"][0]["name"] == "Dr. Alice Smith"


def test_get_doctor_details(client, doctor1_fixture):
    doc_id = doctor1_fixture["doctor"].id
    res = client.get(f"/doctors/{doc_id}", headers=doctor1_fixture["headers"])
    assert res.status_code == status.HTTP_200_OK
    data = res.json()
    assert data["id"] == doc_id
    assert data["name"] == doctor1_fixture["doctor"].name
    assert "patients" in data


def test_update_doctor_self(client, doctor1_fixture):
    doc_id = doctor1_fixture["doctor"].id
    update_payload = {"name": "Dr. Stephen Strange, MD, PhD"}
    res = client.put(f"/doctors/{doc_id}", json=update_payload, headers=doctor1_fixture["headers"])
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["name"] == "Dr. Stephen Strange, MD, PhD"


def test_doctor_cannot_update_other_doctor(client, doctor1_fixture, doctor2_fixture):
    target_id = doctor2_fixture["doctor"].id
    res = client.put(
        f"/doctors/{target_id}",
        json={"name": "Hacked Name"},
        headers=doctor1_fixture["headers"],
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_soft_delete_doctor(client, admin_headers):
    create_res = client.post(
        "/doctors",
        json={"name": "Dr. To Delete", "specialization": "General", "email": "delete_me@doc.com"},
        headers=admin_headers,
    )
    doc_id = create_res.json()["id"]

    del_res = client.delete(f"/doctors/{doc_id}", headers=admin_headers)
    assert del_res.status_code == status.HTTP_200_OK
    assert del_res.json()["is_active"] is False

    del_res_again = client.delete(f"/doctors/{doc_id}", headers=admin_headers)
    assert del_res_again.status_code == status.HTTP_400_BAD_REQUEST
