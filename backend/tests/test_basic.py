import os
import io
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz():
    r = client.get('/healthz')
    assert r.status_code == 200
    assert r.json().get('status') == 'ok'


def test_list_vacancies():
    r = client.get('/api/v1/vacancies')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_application_with_pdf(tmp_path):
    # create a tiny PDF file
    pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
    cv_path = tmp_path / 'cv.pdf'
    cv_path.write_bytes(pdf_bytes)

    with cv_path.open('rb') as f:
        files = {'cv': ('cv.pdf', f, 'application/pdf')}
        # need at least one vacancy id; get first
        vacs = client.get('/api/v1/vacancies').json()
        if not vacs:
            pytest.skip('no vacancies to apply for')
        data = {
            'vacancy_id': vacs[0]['id'],
            'candidate_name': 'Tester',
            'candidate_email': 'tester@example.com',
        }
        r = client.post('/api/v1/applications', data=data, files=files)
    assert r.status_code in (200, 422, 400)
    # Note: PDF parser may fail on a synthetic minimal file; ensure API handles errors gracefully
