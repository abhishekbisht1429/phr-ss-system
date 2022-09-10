import hashlib

ACTION_SET = 'set'
ACTION_SEARCH = 'search'
TXN_FAMILY_NAME = 'thesis'
TXN_FAMILY_VERSION = '1.0'
TXN_NAMESPACE = hashlib.sha512(TXN_FAMILY_NAME.encode('utf-8')).hexdigest()[:6]

STORE_KEY_EC_PRIVATE = 'ec_private_key'
STORE_KEY_EC_PUBLIC = 'ec_public_key'

