import argparse
import base64
import hashlib
import hmac
from urllib.parse import quote_plus

import pyperclip

# Add argument parser
parser = argparse.ArgumentParser(description='GoodRx API v2 signing script.')
parser.add_argument('--api-key', type=str, required=True, help='GoodRx Public API Key')
parser.add_argument('--api-secret', type=str, required=True, help='GoodRx Public API Secret')
args = parser.parse_args()

class ApiV2RequestParameters:
    def __init__(self, url, api_key, c, name, ndc, form, dosage, quantity, metric_quantity, user_quantity,
                 manufacturer_type, location, exclude_local, ncpdp, expand_chains):
        self.url = url
        self.api_key = api_key
        self.c = c
        self.name = name
        self.ndc = ndc
        self.form = form
        self.dosage = dosage
        self.quantity = quantity
        self.metric_quantity = metric_quantity
        self.user_quantity = user_quantity
        self.manufacturer_type = manufacturer_type
        self.location = location
        self.exclude_local = exclude_local
        self.ncpdp = ncpdp
        self.expand_chains = expand_chains

    # IGNORED_FOR_QUERY_STRING is a set containing just url
    IGNORED_FOR_QUERY_STRING = {"url"}

    def allowed_in_query_string(self):
        return {key: value for key, value in self.__dict__.items() if
                key not in self.IGNORED_FOR_QUERY_STRING and value is not None}

    def build_query_string(self):
        query_string = ""
        for key, value in self.allowed_in_query_string().items():
            if value is not None:
                query_string += f"{key}={quote_plus(value)}&"

        # update query_string to be URL encoded
        return query_string[:-1]

    def signed_query_string(self):
        query_string = self.build_query_string()
        api_secret = args.api_secret.encode("utf-8")
        signature = hmac.new(
            api_secret,
            msg=query_string.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        signature_encoded = base64.b64encode(signature, b"__").decode("utf-8")
        signed_query_string = "?%s&sig=%s" % (query_string, signature_encoded)
        return signed_query_string

    # build_curl_command() is a method that returns a valid curl command to GET the url with the signed_query_string appended
    def build_curl_command(self):
        return f"curl -X GET {self.url}{self.signed_query_string()} | jq ."


V2_PRICE_COMPARE_REQUESTS = dict(
    atorvastatin_by_name=ApiV2RequestParameters(
        url="https://api.goodrx.com/v2/price/compare",
        api_key=args.api_key.encode("utf-8"),
        c="sfeinstein_20240605_test",
        name="atorvastatin",
        ndc=None,
        form=None,
        dosage=None,
        quantity=None,
        metric_quantity="30",
        user_quantity=None,
        manufacturer_type=None,
        location="20850",
        exclude_local="1",
        ncpdp=None,
        expand_chains=None,
    ),
    lipitor_by_name=ApiV2RequestParameters(
        url="https://api.goodrx.com/v2/price/compare",
        api_key=args.api_key.encode("utf-8"),
        c="sfeinstein_20240605_test",
        name="lipitor",
        ndc=None,
        form=None,
        dosage=None,
        quantity=None,
        metric_quantity="30",
        user_quantity=None,
        manufacturer_type=None,
        location=None,
        exclude_local=None,
        ncpdp=None,
        expand_chains=None,
    ),
    lipitor_by_ndc=ApiV2RequestParameters(
        url="https://api.goodrx.com/v2/price/compare",
        api_key=args.api_key.encode("utf-8"),
        c="sfeinstein_20240605_test",
        name=None,
        ndc="55289080030",
        form=None,
        dosage=None,
        quantity=None,
        metric_quantity="30",
        user_quantity=None,
        manufacturer_type=None,
        location=None,
        exclude_local=None,
        ncpdp=None,
        expand_chains=None,
    )
)

request = V2_PRICE_COMPARE_REQUESTS["atorvastatin_by_name"]

print(f"""
curl command
-------------
{request.build_curl_command()}
""")

print(f"""
query string only
----------------------------------------
{request.signed_query_string()}
""")

pyperclip.copy(request.build_curl_command())
