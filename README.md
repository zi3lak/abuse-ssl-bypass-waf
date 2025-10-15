# abuse-ssl-bypass-waf

**Helping you find the SSL/TLS Cipher that WAF cannot decrypt and Server can decrypt same time**



Referer article: [Bypassing Web-Application Firewalls by abusing SSL/TLS](https://0x09al.github.io/waf/bypass/ssl/2018/07/02/web-application-firewall-bypass.html)



#### Idea

![](pictures/mind.png)



#### Usage

`python abuse-ssl-bypass-waf.py --help`



If you can find keyword or regex when hit the WAF page, you can use:

`python abuse-ssl-bypass-waf.py -regex "regex" -target https://target.com`

or you cannot find keyword or regex when filter by WAF,you can use:

`python abuse-ssl-bypass-waf.py -thread 4 -target https://target.com`



**Notice**: If you are worry about WAF drop the connection, you have better not use `-thread` option.



#### Thirdparty

**curl**

**sslcan**

**Notice**: If your operation system is not Windows, you should be modify `config.py` ，adjust `curl`  and `sslscan` path & command values.



#### Running

**If you don't know what the type of the WAF, you can compare the html response content length and try to find the bypassing WAF ciphers**

![](pictures/example.png)



**knowing the hit WAF page keyword or regex:**

![](pictures/example-regex.png)



**When using some SSL/TLS ciphers request the payload URL, If WAF keyword or regex not in html page, there is a way bypassing WAF using Cipher!**

![](pictures/example-regex-success.png)

## AI server dashboard

The repository also contains a lightweight panel do monitorowania serwera AI i kontroli kosztów tokenów.

### Instalacja

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Uruchomienie

```bash
python -m dashboard
```

Domyślnie serwer startuje na porcie `8000`. W razie potrzeby możesz ustawić zmienne środowiskowe:

| Zmienna | Opis |
| --- | --- |
| `DASHBOARD_HOST` | Adres interfejsu (domyślnie `0.0.0.0`). |
| `DASHBOARD_PORT` | Port HTTP (domyślnie `8000`). |
| `DASHBOARD_METRICS_REFRESH_SECONDS` | Odstęp odświeżania metryk (sekundy). |
| `TOKEN_COST_PROMPT` | Koszt 1000 tokenów promptu. |
| `TOKEN_COST_COMPLETION` | Koszt 1000 tokenów odpowiedzi. |
| `TOKEN_COST_CURRENCY` | Waluta wyświetlana w panelu. |
| `AI_SERVER_ENDPOINT` | Opcjonalny endpoint webhooka odpowiadającego za generowanie odpowiedzi. |
| `AI_SERVER_API_KEY` | Klucz API przekazywany w nagłówku `Authorization`. |
| `AI_SERVER_MODEL` | Nazwa modelu przekazywana do endpointu. |

Bez konfiguracji endpointu panel pracuje w trybie demonstracyjnym i zwraca komunikaty echo.