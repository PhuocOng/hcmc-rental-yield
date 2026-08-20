# Rental Yield — Tỉ suất cho thuê bất động sản TP.HCM

**Trang chạy tại: https://peter208.com/hcmc-rental-yield/**

> Mua nhà cho thuê ở TP.HCM sinh lời ít hơn gửi tiết kiệm ngân hàng —
> và đây là bản đồ chỗ nào tệ nhất.

**Phạm vi: chỉ TP.HCM, chỉ nguồn Chợ Tốt.** Hà Nội và các nguồn đối chứng đã bị
loại khỏi phạm vi — làm sâu một thành phố thay vì nông hai thành phố. Mọi kết luận
phải nói rõ là về TP.HCM, không được viết thành "Việt Nam".

Dự án data science + tài chính: cào tin rao bán và rao cho thuê, ghép lại theo từng
phường để tính **tỉ suất cho thuê** (tiền thuê một năm chia cho giá mua), rồi đem so
với lãi suất tiết kiệm và lãi suất vay mua nhà.

Sản phẩm cuối là một website có bản đồ theo quận/phường, một máy tính đầu tư cho
người dùng tự nhập số của mình, và bộ dữ liệu tổng hợp mở.

Kế hoạch chi tiết: [PLAN.md](PLAN.md)

---

## Trạng thái

Giai đoạn 0–4 **XONG**. Còn lại: bản đồ địa lý (v2) và báo cáo viết.

| GĐ | Việc | Trạng thái | Chạy bằng |
|---|---|---|---|
| 0 | Khảo sát nguồn | ✅ chọn Chợ Tốt | `probe/*.py` |
| 1 | Thu thập | ✅ 48.018 tin | `src/collect_chotot.py` |
| 2 | Làm sạch | ✅ giữ 45.084 (93,9%) | `src/clean.py` |
| 3 | Tính tỉ suất | ✅ 298 ô phường | `src/compute_yield.py` |
| 4 | Tầng tài chính | ✅ | `src/financial_layer.py` |
| 5 | Website + bản đồ | ✅ | `src/prep_map.py` → `src/build_site.py` |
| 6 | Báo cáo viết | ⬜ | |

Còn lại ngoài báo cáo: đưa trang lên mạng, hẹn giờ cào lại hằng tháng, đối chiếu
số liệu với báo cáo quý của CBRE/Savills.

### Bản đồ

Ranh giới 22 quận/huyện lấy từ [tphcm_district_boundaries](https://github.com/nguyencaonhan271201/tphcm_district_boundaries),
tự chiếu sang SVG nhúng thẳng vào trang — không dùng Leaflet/Mapbox để trang vẫn
tự chứa và chạy được offline.

> **Bẫy đã dính:** phép chiếu Mercator phải để **cả hai trục cùng đơn vị radian**.
> Ban đầu mình để kinh độ ở đơn vị độ còn vĩ độ ở radian rồi dùng chung hệ số co
> giãn — trục ngang bị kéo giãn ~57 lần và bản đồ bẹp thành một vệt ngang.

### Kết quả chính

| | %/năm |
|---|---|
| Tỉ suất **gộp** | 2,61 |
| Tỉ suất **ròng** (sau thuế, phí, bỏ trống, bảo trì) | **1,51** |
| Lãi tiết kiệm 12 tháng (Big4 tại quầy, 8/2026) | 6,00 |

- Thu hồi vốn bằng tiền thuê: **66 năm**
- Vay 70% ở lãi 12% → dòng tiền **−6,89%** giá trị nhà mỗi năm
- Giá nhà phải tăng **8,69%/năm** thì người vay mới bằng gửi tiết kiệm
- **Không một quận nào** trong 20 quận đuổi kịp lãi tiết kiệm

Kiểm tra chéo: tính theo *phường × loại hình* ra 2,57%, theo *quận × loại hình ×
diện tích* ra 2,61% — hai cách độc lập gần như trùng nhau, nên kết quả không đến từ
lệch cơ cấu diện tích.

### Xem website

Bản đã đưa lên: **https://peter208.com/hcmc-rental-yield/**

Chạy tại máy:

```bash
python -m http.server 8765 --directory docs
```

### Đưa lên mạng

GitHub Pages, nguồn là nhánh `main` thư mục `/docs`. Đẩy code lên là tự cập nhật,
không cần CI.

```bash
python src/build_home.py && python src/build_site.py
git add -A && git commit -m "..." && git push
```

**Vì sao là `docs/` chứ không phải `web/`:** GitHub Pages chỉ phục vụ được từ thư
mục gốc hoặc `/docs`. Đổi tên thư mục đơn giản hơn dựng một quy trình CI. Báo cáo
viết để ở `report/`.

**Không bao giờ commit `data/raw/`** — 274 MB, và đó là nội dung tin rao gốc.
`.gitignore` đã chặn sẵn, cùng với các file HTML lưu lúc dò cấu trúc trang bên khác.

> **Bẫy:** `og:image` phải là **đường dẫn tuyệt đối**. Tài khoản này còn có tên
> miền riêng gắn ở cấp user nên Pages phục vụ tại `peter208.com/<repo>/` chứ không
> phải `phuocong.github.io`. Đổi tên miền thì phải sửa lại chỗ đó trong
> `src/build_home.py` và `src/build_site.py`.

| Nguồn | Kết quả |
|---|---|
| Chợ Tốt (nhatot.com) | ✅ **Nguồn duy nhất** — API JSON công khai, đủ 6 tiêu chí |
| mogi.vn | ⚠️ Bóc được, nhưng **đã loại**. Bộ lọc quận của họ im lặng bỏ qua tên quận, và trang có khối "Tin TOP" quảng cáo lẫn tin từ tỉnh khác (Hà Đông, Biên Hòa). Mẻ thu được 16.500 dòng nhưng chỉ 750 ID duy nhất → đã cách ly, xem `data/raw/*.INVALID-do-not-use` |
| alonhadat.com.vn | ❌ Chỉ trả khung trang, 0 link tin — listings do JavaScript nạp |
| homedy.com | ❌ Cũng do JavaScript nạp |
| batdongsan.com.vn · guland.vn · nhadat24h.net · muaban.net · bds123.vn | ❌ Cloudflare chặn |

> **Bẫy khi khảo sát:** đừng đánh giá một trang bằng cách đếm chuỗi "tỷ / triệu / m²"
> trong HTML — chúng khớp phải các `<option>` của form lọc giá và làm trang rỗng
> trông như trang đầy tin. Phải **đếm link chi tiết của tin** mới đúng. Mình đã dính
> bẫy này và kết luận nhầm alonhadat là "dễ cào".

**Dữ liệu đã có:** `data/raw/chotot_hcm_20260815.jsonl` — 48.018 tin, 280 MB
(căn hộ bán 4.078 · căn hộ thuê 14.381 · nhà ở bán 19.971 · nhà ở thuê 9.588).
Số thu được khớp gần như tuyệt đối với số `total` API báo trước khi cào (48.019)
→ không có ô nào bị cắt cụt vì trần phân trang.

---

## Cấu trúc thư mục

```
rental_yield/
├── README.md        # file này
├── PLAN.md          # kế hoạch 6 giai đoạn + kết quả khảo sát chi tiết
├── probe/           # script khảo sát nguồn (giai đoạn 0)
├── src/             # code chính: cào, làm sạch, tính toán
├── data/
│   ├── raw/         # JSON thô theo ngày — KHÔNG sửa tay, không commit
│   ├── interim/     # đã lọc trùng và làm sạch
│   └── output/      # số liệu tổng hợp theo phường (thứ đem công bố)
├── web/             # website
└── docs/            # báo cáo, ghi chú
```

## Chạy các script khảo sát

```bash
python probe/probe_chotot.py
```

| Script | Trả lời câu hỏi gì |
|---|---|
| `probe_chotot.py` | API có sống không, mỗi tin có những trường nào, mã vùng và mã danh mục là gì |
| `probe_rent_and_limits.py` | Có những danh mục BĐS nào, `total` có bị chặn không |
| `probe_split_and_paging.py` | Tách tin bán khỏi tin thuê bằng cách nào, phân trang sâu có đáng tin không |

## Những gì đã biết chắc về API Chợ Tốt

Endpoint: `https://gateway.chotot.com/v1/public/ad-listing` (JSON, không cần đăng nhập)

| Tham số | Ý nghĩa |
|---|---|
| `region_v2` | `12000` Hà Nội · `13000` TP.HCM |
| `cg` | `1010` Căn hộ · `1020` Nhà ở · `1030` Văn phòng/MBKD · `1040` Đất · `1050` Phòng trọ |
| `st` | **`s` = bán · `u` = cho thuê** — tách sạch 100% |
| `area_v2` | lọc theo quận |
| `ward` | lọc theo phường |
| `limit`, `o` | số tin mỗi lần, vị trí bắt đầu |

**Ba điều phải nhớ:**

1. Tin bán và tin cho thuê **nằm chung một danh mục** — bắt buộc lọc bằng `st`,
   nếu không tỉ suất sai hoàn toàn mà nhìn số vẫn thấy hợp lý.
2. Tham số `type` truyền vào **bị API bỏ qua**. Đừng dùng. (Nhưng trường `type`
   *của tin trả về* thì có nghĩa: `s` bán, `u` thuê.)
3. `total` chặn cứng ở `10000` dù thực tế nhiều hơn → **quét theo từng quận**,
   đừng quét cả thành phố một lần.

## Nguyên tắc

- Cào chậm, có nghỉ giữa các lần gọi, tôn trọng robots.txt, không đăng nhập chui
- Chỉ công bố **số liệu đã tổng hợp** theo phường — không đăng lại nội dung tin gốc
- Ô nào dưới 10 tin ở một trong hai phía (bán/thuê) thì **để trống**, không đoán

---

## Website — hai trang

| Trang | File | Dựng bằng | Chuỗi hiển thị |
|---|---|---|---|
| Trang chủ | `web/index.html` | `src/build_home.py` | `src/i18n_home.js` |
| Bảng dữ liệu | `web/dashboard.html` | `src/build_site.py` | `src/i18n.js` |

Dựng lại cả hai:

```bash
python src/build_home.py && python src/build_site.py
```

Trang chủ mở bằng **hero cuộn-tua**: một video flycam TP.HCM dán cứng toàn màn,
cuộn tới đâu video tua tới đó, bốn khối chữ hiện/ẩn theo từng khoảng cuộn. Bên dưới
là ba con số chính kèm diễn giải, bốn bước phương pháp, mục giới hạn, và khu tải
dữ liệu. Nó **không** lặp lại bảng điều khiển, chỉ dẫn vào đó.

### Video nền chạy suốt trang

Video **cố định sau toàn bộ trang**, không phải một hero riêng. Tiến độ cuộn của
cả tài liệu (0 → 1) ánh xạ thẳng sang thời điểm video (0 → 26,5s), nên kéo tới
đâu cũng có chuyển động. Nội dung nổi bên trên trên những tấm kính tối
(`backdrop-filter: blur`). Nền video còn được đẩy vào từ `scale(1)` tới
`scale(1.07)` theo tiến độ cuộn, tạo cảm giác chiều sâu.

**Hành trình 6 chặng**: mây → vén mây lộ châu thổ → chợ nổi miền Tây → TP.HCM →
luồn giữa cao ốc → vòng xoay đường phố.

| # | Chặng | Nguồn |
|---|---|---|
| 1 | Vén mây, sông và đồng bằng hiện ra | **AI** (fal.ai, Seedance v1 lite) |
| 2 | Chợ nổi miền Tây | Quay thật |
| 3 | TP.HCM nhìn rộng | Quay thật |
| 4 | Cao ốc lúc hoàng hôn | Quay thật |
| 5 | Luồn giữa cao ốc | Quay thật |
| 6 | Vòng xoay nhìn thẳng xuống | Quay thật |

27,5 giây · 1152px · **5,11 MB** · hòa tan 1,1 giây giữa các chặng.

Cách làm rẻ: **sinh ảnh khung đầu trước rồi mới sinh video.** Trên fal, ảnh rẻ
hơn video khoảng 40 lần (~$0,003 với FLUX schnell so với ~$3 một video Seedance).
Sinh 8 ảnh nháp, chọn 2 cái ưng, rồi mới tiêu tiền vào video — thay vì sinh video
mù và mất $3 mỗi lần hỏng.

Ghép bằng `src/make_journey.py`:

```bash
python src/make_journey.py            # can 6 clip nguon trong scratchpad
python src/make_hero_video.py raw.mp4 --ss 31 --t 9    # hoac mot clip don
```

`web/assets/hero-scrub.mp4` — 26,5 giây, 1280×720, **7,35 MB**.

Hai việc bắt buộc khi ghép, thiếu cái nào cũng thành trình chiếu ảnh:
**chỉnh cùng một tông** cho cả sáu clip (chúng lệch màu rất xa), và **hòa tan**
giữa các chặng thay vì cắt thẳng.

**Không dùng chuỗi ảnh JPG.** Một file MP4, tải về dạng Blob, kéo
`video.currentTime` theo cuộn. Mấu chốt là `-g 8 -keyint_min 8`: ép keyframe dày
gấp ~15 lần bình thường, nên tua tới đâu cũng tức thì.

Bốn điểm trong `src/build_home.py`:

1. **Tải cả file thành Blob trước** — để trình duyệt tự xin từng đoạn qua HTTP
   Range thì tua qua tua lại sẽ kẹt. Có vòng tròn báo tiến độ.
2. **Nội suy thời gian trong vòng lặp rAF**, không gán thẳng.
3. **Chặn lệnh tua chồng nhau**, kèm hạn 400ms để không kẹt vĩnh viễn.
4. **Chỉ ghi vào DOM khi giá trị thật sự đổi.**

### Tối ưu độ mượt

- **Không dùng `backdrop-filter` trên các tấm panel.** Mỗi khung hình video đổi là
  trình duyệt phải làm mờ lại toàn bộ vùng phía sau từng tấm; năm tấm × mỗi khung
  là rất nặng. Thay bằng nền đục 90% — nhìn gần như y hệt, gần như không tốn gì.
  Chỉ giữ blur cho thanh nav vì nó nhỏ.
- **Bắt đầu tải video ngay trong `<head>`** bằng một dòng `fetch()`, thay vì đợi
  script cuối body chạy. Tiết kiệm cả quãng đọc body và tải CSS font.
- **Hệ số nội suy 0,26** thay vì 0,16. Ở 60fps, 0,16 cần ~220ms mới đuổi kịp 90%
  khoảng cách — đọc ra thành cảm giác trễ. 0,26 còn ~130ms.
- **Nhảy thẳng khi khoảng cách > 2,5 giây** (người dùng kéo thanh cuộn một phát),
  không nội suy, nếu không video sẽ "bơi" theo rất khó chịu.
- Bớt số file font phải tải.

### Bẫy đã dính khi dựng phần này

- **Pexels trả 403 nếu thiếu header `User-Agent`**, kể cả khi key đúng.
  `urllib.urlretrieve` không gửi header nên luôn hỏng — phải dùng `Request`.
  Mình đã tưởng nhầm là key chết.
- **Không dùng `IntersectionObserver` để hiện dần nội dung.** Nếu nó không chạy
  thì nội dung kẹt ở `opacity: 0` vĩnh viễn. Đã chuyển vào chính hàm cuộn.
- **Trùng tên class `.in`** giữa ô chứa của thanh nav và cờ "đã hiện". Đổi thành
  `.seen`.
- **Dấu `#` trong Python nuốt phần còn lại của dòng.** Lúc thêm chú thích vào
  `SCRUB_FLAGS`, cờ `-preset slow` biến mất mà cú pháp vẫn hợp lệ nên
  `ast.parse` không bắt được. Phải nạp module rồi soát từng cờ.
- **Clip nguồn không cùng tỉ lệ** (có cái 2048×1080). Phải
  `scale=...:force_original_aspect_ratio=increase` rồi mới `crop`, không thì
  ffmpeg đổ.

- **Song ngữ EN/VI**, mặc định tiếng Anh, lựa chọn lưu trong `localStorage`.
  Đổi ngôn ngữ thì đổi luôn định dạng số (`1,234,567` ↔ `1.234.567`),
  tên quận (`Thu Duc City` ↔ `Thành phố Thủ Đức`) và cách viết tiền tệ.
- **Chữ:** Inter cho giao diện, IBM Plex Mono cho mọi con số.
- **Màu:** ba sắc có chủ đích, **không dùng cặp đỏ–xanh lá**.
  `--acc` đất nung `#A8432A` = đại lượng đang đo · `--ref` xanh mực `#1F5E5B` = mốc
  so sánh · `--acc2` hoàng thổ `#B07C2B` = nhóm thứ hai. Nền trắng ấm, không xám lạnh.
  Mọi cặp chữ/nền đạt WCAG AA (nhãn mờ nhất 4,66:1).
- **Biểu đồ SVG tự vẽ**, không dùng thư viện: xếp hạng quận có thanh sai số,
  phân tán giá–tỉ suất, phân bố theo phường.
- **Khoảng tin cậy bootstrap** hiện ở biểu đồ, bảng và tooltip bản đồ.
- Bản đồ Leaflet + ảnh vệ tinh Esri (cần mạng; mất mạng thì hiện thông báo).

### Biểu tượng và thẻ chia sẻ

Sinh bằng `python src/make_icons.py` → `favicon.svg` · `favicon.ico` (16–64px)
· `apple-touch-icon.png` · `icon-192.png` · `og.png` (1200×630).

Biểu tượng chính là luận điểm thu gọn: **hai thanh, một ngắn một dài** — đất nung
là tỉ suất cho thuê, xanh mực là lãi tiết kiệm. Tỉ lệ thật 1,51/6,00 = 0,25 bị kéo
lên 0,36 vì ở cỡ 16px thanh ngắn thật sẽ chỉ còn ~2px và biến mất.

> **Khi deploy phải sửa:** `og:image` đang để đường dẫn tương đối `og.png`.
> Facebook và Twitter **không đọc được đường dẫn tương đối** — phải đổi thành URL
> tuyệt đối `https://<tên-miền>/og.png` thì thẻ chia sẻ mới hiện ảnh.

### Bẫy đã dính khi dựng giao diện

1. `svg{height:auto}` cộng `viewBox` → đo sai bề ngang lúc vẽ đầu là chiều cao
   bị phóng gấp 5 lần. Phải đặt `style.height` bằng pixel tuyệt đối.
2. `requestAnimationFrame` **không chạy khi tab đang ẩn** → dùng nó cho lần vẽ
   đầu thì biểu đồ trắng trơn. Phải vẽ đồng bộ.
3. Leaflet ném `"Set map center and zoom first"` nếu thêm lớp trước `fitBounds`.
4. `ResizeObserver` gọi `invalidateSize()` giữa lúc bản đồ đang bay sẽ làm đứt
   hoạt ảnh → chỉ gọi khi khung thật sự đổi kích thước.
5. Ô mặc định của máy tính lấy `findIndex` → trúng Quận 1, đắt và ít đại diện
   nhất. Đổi sang ô nhiều tin nhất.
