# -*- coding:UTF-8 -*-

"""
    该模块用于提取网站证书信息, 并打印出解析的字段
"""

import ssl
import socket
from cryptography import x509
import sys
from cryptography.hazmat.backends import default_backend
from urllib.parse import urlparse

# 将证书字段信息以字符串形式返回
def parse_certificate(cert):
    cert_fields = {}
    
    # 主题(subject)字段
    try:
        cert_fields["subject"] = cert.subject
    except Exception as e:
        cert_fields["subject"] = ""

    # 证书的颁发者(issuer)字段
    try:
        cert_fields["issuer"] = cert.issuer
    except Exception as e:
        cert_fields["issuer"] = ""

    # 证书的版本(version)信息
    try:
        cert_fields["version"] = cert.version
    except Exception as e:
        cert_fields["version"] = ""

    # Subject备用名称(Subject Alternative Name, SAN)
    try:
        san_extension = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        cert_fields["san_names"] = san_extension.value.get_values_for_type(x509.DNSName)
    except Exception as e:
        cert_fields["san_names"] = ""

    # 证书的通用名称(Common Name, CN)
    try:
        common_name_attr = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        cert_fields["common_name"] = common_name_attr[0].value if common_name_attr else ""
    except Exception as e:
        cert_fields["common_name"] = ""
    
    return cert_fields

# 请求URL, 提取出证书信息
def get_certificate_info(url):
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        port = parsed_url.port or 443

        # 获取证书
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((hostname, port), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # 获取 DER 编码的证书
                cert_der = ssock.getpeercert(binary_form=True)
                # 将 DER 编码的证书转换为 x509.Certificate 对象
                cert = x509.load_der_x509_certificate(cert_der, default_backend())

                # 解析所有字段信息
                cert_info = parse_certificate(cert)
                return cert_info

    except Exception as e:
        print(f"request cert Error : {str(e)}")
        return {}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parse_web_cert.py <url>")
        sys.exit(1)

    # 命令行参数
    target_url = sys.argv[1]
    if '://' not in target_url:
        target_url = 'https://' + target_url

    certificate_info = get_certificate_info(target_url)

    if certificate_info != {}:
        max_key_length = max(len(key) for key in certificate_info.keys())

        for key, value in certificate_info.items():
            print(f"{key.ljust(max_key_length)}:   {value}")
    else:
        print("No certificate information found")