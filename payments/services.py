import hmac
import hashlib
import base64
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_esewa_signature(total_amount, transaction_uuid, product_code=None, secret_key=None):
    """
    Generate eSewa v2 HMAC-SHA256 signature.
    Message format: total_amount={val},transaction_uuid={val},product_code={val}
    """
    if product_code is None:
        product_code = getattr(settings, 'ESEWA_PRODUCT_CODE', 'EPAYTEST')
    if secret_key is None:
        secret_key = getattr(settings, 'ESEWA_SECRET_KEY', '8gBm/:&EnhH.1/q')

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    key = secret_key.encode('utf-8')
    h = hmac.new(key, message.encode('utf-8'), hashlib.sha256)
    signature = base64.b64encode(h.digest()).decode('utf-8')
    return signature


def decode_esewa_response(encoded_data):
    """
    Decode base64 JSON payload returned by eSewa on success callback.
    """
    try:
        decoded_bytes = base64.b64decode(encoded_data)
        data = json.loads(decoded_bytes.decode('utf-8'))
        return data
    except Exception as e:
        logger.error(f"Failed to decode eSewa response: {e}")
        return None


def verify_esewa_transaction(product_code, total_amount, transaction_uuid):
    """
    Query eSewa's transaction status API to securely verify payment completion.
    """
    status_url = getattr(settings, 'ESEWA_STATUS_CHECK_URL', 'https://rc-epay.esewa.com.np/api/epay/transaction/status/')
    params = {
        'product_code': product_code,
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
    }
    try:
        response = requests.get(status_url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        logger.error(f"eSewa status check returned {response.status_code}: {response.text}")
    except Exception as e:
        logger.error(f"Exception during eSewa status verification: {e}")
    return None
