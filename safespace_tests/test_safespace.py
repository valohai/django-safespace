import json

import pytest
from django.db.utils import DatabaseError


@pytest.mark.parametrize('code', (False, True))
@pytest.mark.parametrize('ajax', (False, True))
def test_basic_usage(client, code, ajax):
    response = client.get(
        '/problem/',
        {'code': ('oops' if code else '')},
        HTTP_X_REQUESTED_WITH=('XMLHttpRequest' if ajax else 'An Unicorn'),
    )
    assert response.status_code == 406
    assert b'woeful error' in response.content
    assert (b'oops' in response.content) == bool(code)
    if code:
        assert response['X-Error-Code'] == 'oops'
    if ajax:
        data = json.loads(response.content.decode())
        assert data['error'] == 'A woeful error'
        if code:
            assert data['code'] == 'oops'


def test_custom(client):
    response = client.get('/custom/')
    assert response.status_code == 406
    assert b'Oopsy daisy' in response.content


def test_raised_404(client):
    """
    Test that raised Http404s can be caught.
    """
    response = client.get('/404/')
    assert response.status_code == 406


def test_natural_404(client):
    """
    Test that "natural" 404s from the router aren't caught by the middleware.
    """
    response = client.get('/dsfargeg/')
    assert response.status_code == 404


def test_passthrough(client):
    """
    Test that exceptions that we don't want to catch are passed through.
    """
    with pytest.raises(DatabaseError):
        client.get('/db/', {'exc': 'db'})


def test_arbitrary_response(client):
    """
    Test that exceptions may carry `response`s
    """
    response = client.get('/exception-response/')
    assert response.content == b'nice.'


def test_custom_template(client, settings):
    """
    Test that SAFESPACE_TEMPLATE_NAMES can be used for customization.
    """
    response = client.get('/problem/', {'exc': 'problem', 'code': 'foo'})
    assert response.status_code == 406
    assert b'a foo error occurred, boo' in response.content


def test_accept_json(client):
    response = client.get('/problem/', HTTP_ACCEPT=('application/json; text/html'))
    assert response.status_code == 406
    assert json.loads(response.content.decode())['error'] == 'A woeful error'
