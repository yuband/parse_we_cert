import requests
import re
import urllib3
from urllib.parse import urljoin
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 获取一个URL的Response对象
def get_http_response(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'close'
    }
    try:
        # 爬虫允许跳转
        response = requests.get(url, timeout=3, headers=headers, verify=False, allow_redirects=True)

        # URL跳转跟随
        if "top.location.href" in response.text:
            # 提取重定向URL
            new_url = response.text.split("'")[1]
            # 使用urljoin自动处理相对路径和绝对路径的问题
            new_full_url = urljoin(url, new_url)
            # 递归处理重定向
            return get_http_response(new_full_url)
        return response
    except Exception as e:
        return None

def fetch_icp_number(url):
    try:
        response = get_http_response(url)
        # 设置编码为`UTF-8`, 防止乱码导致的匹配失败
        response.encoding = 'utf-8'
        response.raise_for_status()  # 检查请求是否成功

        text = response.text
        # 正则匹配备案号的格式, 备案号中间可能会出现空格, 同样需要进行匹配
        match = re.findall(r'([\u4e00-\u9fa5]{1,1}\s{0,2}ICP\s{0,2}备\s{0,2}\d+\s{0,2}号\s{0,2}-?\s{0,2}\d*)', text, re.IGNORECASE)
        # 清理字符串并去重， 移除所有空白字符
        cleaned_matches = {re.sub(r'\s+', '', m) for m in match}
        # 转换为大写并去重
        cleaned_matches = {m.upper() for m in cleaned_matches}
        # 重新编号
        cleaned_matches = {i: match for i, match in enumerate(cleaned_matches)}
        
        icp_list = []
        for number, icp in cleaned_matches.items():
            icp_list.append(icp)

        return icp_list

    except Exception as e:
        return None

def main():
    parser = argparse.ArgumentParser(description='Extract ICP number from a website.')
    parser.add_argument('-u', '--url', type=str, required=True, help='Target URL to fetch ICP number.')
    args = parser.parse_args()

    icp_number = fetch_icp_number(args.url)
    if icp_number:
        print(f"Found {len(icp_number)} ICP number(s):")
        for icp in icp_number:
            print(icp)

if __name__ == "__main__":
    main()