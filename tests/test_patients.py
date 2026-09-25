from fastapi import status


def test_create_patient_valid(client, admin_headers):
    payload = {
        "name": "Jane Patient",
        "age": 28,
        "phone": "+12345678901",
    }
    response = client.post("/patients", json=payload, headers=admin_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Jane Patient"
    assert data["age"] == 28
    assert data["phone"] == "+12345678901"
    assert "id" in data


def test_patient_age_validation(client, admin_headers):
    res_zero = client.post(
        "/patients",
        json={"name": "Baby", "age": 0, "phone": "+12345678901"},
        headers=admin_headers,
    )
    assert res_zero.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    res_neg = client.post(
        "/patients",
        json={"name": "Time Traveler", "age": -5, "phone": "+12345678901"},
        headers=admin_headers,
    )
    assert res_neg.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_patient_phone_validation(client, admin_headers):
    res_short = client.post(
        "/patients",
        json={"name": "Short Phone", "age": 30, "phone": "12345"},
        headers=admin_headers,
    )
    assert res_short.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    res_long = client.post(
        "/patients",
        json={"name": "Long Phone", "age": 30, "phone": "12345678901234567"},
        headers=admin_headers,
    )
    assert res_long.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    res_invalid = client.post(
        "/patients",
        json={"name": "Letters Phone", "age": 30, "phone": "abcdef12345"},
        headers=admin_headers,
    )
    assert res_invalid.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    res_10 = client.post(
        "/patients",
        json={"name": "Valid 10", "age": 30, "phone": "9876543210"},
        headers=admin_headers,
    )
    assert res_10.status_code == status.HTTP_201_CREATED

    res_15 = client.post(
        "/patients",
        json={"name": "Valid 15", "age": 30, "phone": "+123456789012345"},
        headers=admin_headers,
    )
    assert res_15.status_code == status.HTTP_201_CREATED


def test_doctor_sees_only_assigned_patients(client, admin_headers, doctor1_fixture, doctor2_fixture):
    p1 = client.post(
        "/patients",
        json={"name": "Patient For Doc1", "age": 40, "phone": "1111111111"},
        headers=admin_headers,
    ).json()

    p2 = client.post(
        "/patients",
        json={"name": "Patient For Doc2", "age": 50, "phone": "2222222222"},
        headers=admin_headers,
    ).json()

    doc1_id = doctor1_fixture["doctor"].id
    doc2_id = doctor2_fixture["doctor"].id

    client.post(f"/doctors/{doc1_id}/patients/{p1['id']}", headers=admin_headers)
    client.post(f"/doctors/{doc2_id}/patients/{p2['id']}", headers=admin_headers)

    doc1_list = client.get("/patients", headers=doctor1_fixture["headers"]).json()
    assert doc1_list["meta"]["total_items"] == 1
    assert doc1_list["items"][0]["id"] == p1["id"]

    doc1_p2_res = client.get(f"/patients/{p2['id']}", headers=doctor1_fixture["headers"])
    assert doc1_p2_res.status_code == status.HTTP_403_FORBIDDEN

    doc1_p1_res = client.get(f"/patients/{p1['id']}", headers=doctor1_fixture["headers"])
    assert doc1_p1_res.status_code == status.HTTP_200_OK
    assert doc1_p1_res.json()["name"] == "Patient For Doc1"

    admin_list = client.get("/patients", headers=admin_headers).json()
    assert admin_list["meta"]["total_items"] >= 2
    admin_p2_res = client.get(f"/patients/{p2['id']}", headers=admin_headers)
    assert admin_p2_res.status_code == status.HTTP_200_OK
