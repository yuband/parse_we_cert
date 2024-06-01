# parse_web_info

## 说明

本项目旨在提取网站信息，获取证书，ICP备案等信息

`parse_web_cert.py` : 解析web证书，从中获取到签发该证书的公司信息和域名信息

`fetch_web_icp_number.py` : 从目标URL中提取出备案号信息

## Usage

```bash
python3 parse_web_cert.py https://x.x.x.x:443
```

![1717217628426](Pictures\1717217628426.png)

```bash
python3 fetch_web_icp_number.py -u http://220.249.121.106:7880
```

![1717217720428](Pictures\1717217720428.png)
