import hashlib

ACTION_SET = 'set'
TXN_FAMILY_NAME = 'thesis'
TXN_FAMILY_VERSION = '1.0'
TXN_NAMESPACE = hashlib.sha512(TXN_FAMILY_NAME.encode('utf-8')).hexdigest()[:6]