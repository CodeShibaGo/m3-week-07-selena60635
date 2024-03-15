### 什麼是 CSRF Token 與如何使用

- 什麼是 CSRF 攻擊，該如何預防？

  跨站請求偽造（CSRF），攻擊者會利用使用者對網站的信任，使用認證過的身分，執行未經授權的動作，例如：使用者已經通過驗證登入銀行，攻擊者透過偽裝成可能是銀行的網頁、可能是一張透明的圖片等，發送惡意請求，此時攻擊者就能夠利用使用者的身分憑證做一些壞壞的事情，像是更改使用者密碼、發送惡意電子郵件等…

  - 要預防 CSRF 攻擊，可以採取以下措施
    - 使用 CSRF 令牌(Token)
    - 在伺服器檢查請求來源是否與網站域名一致。
    - 要求使用者使用驗證碼做驗證
    - 限制敏感操作，若需要執行敏感操作需要提供額外身分驗證

- 說明如何在 flask 專案中使用以下 `csrf_token()`語法。
  - 使用 Flask-WTF
    - 安裝 Flask-WTF - `pip install flask-wtf`
    - Flask-WTF 初始設定
      ```python
      from flask_wtf.csrfimport CSRFProtect
      ...
      csrf = CSRFProtect(app)
      ```
    - 生成一個隱藏的 CSRF Token
      ```html
      <form action="" method="post">{{form.hidden_tag() }} ...</form>
      ```
  - 使用 HTML 表單
    - 使用<input>生成一個隱藏的 CSRF Token
      ```html
      <form method="post">
        <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
      </form>
      ```
- ajax 需不需要使用 csrf token 進行防禦？該如何使用？
  ```jsx
  <script type="text/javascript">
      var csrf_token = "{{ csrf_token() }}";

      $.ajaxSetup({
          beforeSend: function(xhr, settings) {
              if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                  xhr.setRequestHeader("X-CSRFToken", csrf_token);
              }
          }
      });
  </script>
  ```

### VS Code + VirtualEnv 組合技

- **如何使用 Virtualenv 建立環境**
  安裝 virtualenv - `pip install virtualenv`，解除安裝`pip uninstall virtualenv`。
  建立 virtualenv 環境 - `virtualenv 環境名稱`。
  啟動虛擬環境 - `source 環境名稱/bin/activate`，執行.venv/bin/activate；停用環境請執行`deactivate`。
  - **使用 WSL 系統(Ubuntu)安裝**
    安裝 virtualenv - `sudo apt-get install python3-virtualenv`；解除安裝`sudo apt-get remove python3-virtualenv`，刪除所有設定文件`sudo apt-get purge python3-virtualenv`。
- **如何測試環境使否有載入成功**
  查看  pip 版本 - `pip --version`，查看已安裝的套件，確認是否安裝成功。
  查看現在使用的  pip 路徑 - `which pip`，應該要是虛擬環境中的路徑。
  查看現在使用的 python 路徑 - `which python`，應該要是虛擬環境中的路徑。
- **如何判斷套件是否安裝成功**
  查看  pip 版本 - `pip --version`，查看已安裝的套件，確認是否安裝成功。
  查看 virtualenv 版本 - `virtualenv --version`，查看版本號，確認是否安裝成功。
