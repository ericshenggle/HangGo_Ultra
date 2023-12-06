import requests
import re
from pyquery import PyQuery as pq

ssoAddr = "https://sso.buaa.edu.cn"
vpnAddr = "https://d.buaa.edu.cn/login?cas_login=true"
bykcAddr = "https://d.buaa.edu.cn/http/77726476706e69737468656265737421f2ee4a9f69327d517f468ca88d1b203b"
inner_ssoAddr = "https://d.buaa.edu.cn/https/77726476706e69737468656265737421e3e44ed225256951300d8db9d6562d"

vpn2Addr = "https://e1.buaa.edu.cn"
bykc2Addr = "https://bykc.e1.buaa.edu.cn/"


def get_token(username, password):
    session = requests.Session()
    login_page = pq(session.get(ssoAddr + "/login").text)
    submit_form = dict((x.name, x.value) for x in login_page("#loginForm").find("input"))
    submit_form['username'] = username
    submit_form['password'] = password
    login_result = session.post(ssoAddr + "/login", allow_redirects=False, data=submit_form,
                                headers={"User-Agent": "Gecko", "Accept-Language": "zh-CN,zh"})
    if login_result.status_code >= 400:
        result_page = pq(login_result.text)
        error_message = result_page("#errorDiv").text()
        if len(error_message) == 0:
            error_message = result_page(".tip-text").text()
        raise RuntimeError(error_message)
    session.get(vpnAddr, allow_redirects=True,
                headers={"User-Agent": "Gecko", "Accept-Language": "zh-CN,zh"})  # 访问vebVpn，得到WebVpn访问权限

    login_page = pq(session.get(inner_ssoAddr + "/login").text)
    submit_form = dict((x.name, x.value) for x in login_page("#loginForm").find("input"))
    submit_form['username'] = username
    submit_form['password'] = password
    login_result = session.post(inner_ssoAddr + "/login", allow_redirects=False, data=submit_form,
                                headers={"User-Agent": "Gecko", "Accept-Language": "zh-CN,zh"})
    if login_result.status_code >= 400:
        result_page = pq(login_result.text)
        error_message = result_page("#errorDiv").text()
        if len(error_message) == 0:
            error_message = result_page(".tip-text").text()
        raise RuntimeError(error_message)

    current_url = bykcAddr + "/sscv/casLogin"

    for i in range(10):
        r = session.get(current_url, allow_redirects=False,
                        headers={"User-Agent": "Gecko", "Accept-Language": "zh-CN,zh"})
        mt = re.search(r'cas-login\?token=([A-F0-9]+)', current_url)
        if mt:
            return mt.group(1), session
        elif r.status_code == 302:
            current_url = r.headers["Location"]
        elif r.status_code == 200:
            raise RuntimeError("e1或者sso登录失败，博雅登录请求被重定向到vpn或sso登录页面")
        else:
            raise RuntimeError("博雅系统返回了状态码：" + str(r.status_code))
    raise RuntimeError("登录失败，重定向次数过多。")


def post_api(session, token, username, password, api, data):
    login_page = pq(session.get(vpn2Addr + "/users/sign_in").text)
    submit_form = dict((x.name, x.value) for x in login_page("#login-form").find("input"))
    submit_form['user[login]'] = username
    submit_form['user[password]'] = password
    login_result = session.post("https://e1.buaa.edu.cn/users/sign_in", allow_redirects=False, data=submit_form,
                                headers={"User-Agent": "Gecko", "Accept-Language": "zh-CN,zh"})
    if login_result.status_code == 200:
        raise RuntimeError("Web vpn1登录失败，请确定sso账号密码正确，且vpn e1没有被锁定")
    if login_result.status_code == 302:
        current_url = login_result.headers["Location"]
        for i in range(10):
            r = session.get(current_url, headers={"User-Agent": "Gecko", "Accept-Language": "zh-CN,zh"})
            if r.status_code != 302:
                break
    resp = session.post(bykc2Addr + "/sscv/" + api,
                        headers={"auth_token": token, "User-Agent": "Gecko", "Accept-Language": "zh-CN,zh"},
                        json=data).json()
    if resp["status"] == "1" and resp["errmsg"] == None:
        raise RuntimeError("博雅系统返回了错误码：1")
    if resp["status"] != "0":
        raise RuntimeError(resp["errmsg"])
    return resp['data']
