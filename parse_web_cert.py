# -*- coding:UTF-8 -*-

"""
    该模块用于提取网站证书信息, 并解析需要的字段
"""

import ssl
import re
import socket
from cryptography import x509
import sys
from cryptography.hazmat.backends import default_backend
from urllib.parse import urlparse

# 检查传入的字符串是否为合法的域名格式
def is_valid_domain(domain):
    pattern = r'^(?:\*\.)?(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    if re.match(pattern, domain):
        return True
    else:
        return False

# 将证书字段信息以字符串形式返回
def parse_certificate(cert):
    cert_fields = {
        "subject": cert.subject,
        "issuer": cert.issuer,
        "version": cert.version,
        "san_names": cert.extensions.get_extension_for_class(x509.SubjectAlternativeName),
        "common_name": cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    }

    # 对证书字段信息进行字符串格式化
    fields_str = '\n'.join([f"{field}: {value}" for field, value in cert_fields.items()])


    return fields_str

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

        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # 获取 DER 编码的证书
                cert_der = ssock.getpeercert(binary_form=True)
                # 将 DER 编码的证书转换为 x509.Certificate 对象
                cert = x509.load_der_x509_certificate(cert_der, default_backend())

                # 解析所有字段信息
                cert_info = parse_certificate(cert)
                return cert_info

    except Exception as e:
        print(e)
        return ""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 poc.py <url>")
        sys.exit(1)

    # 命令行参数
    target_url = sys.argv[1]

    certificate_info = get_certificate_info(target_url)
    print(certificate_info)