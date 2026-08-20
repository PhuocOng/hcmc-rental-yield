# Tỉ suất cho thuê BĐS: Hà Nội & TP.HCM

**Luận điểm:** Mua nhà cho thuê ở hai thành phố lớn nhất Việt Nam sinh lời ít hơn gửi tiết
kiệm ngân hàng — và đây là bản đồ chỗ nào tệ nhất.

**Sản phẩm cuối:** website có bản đồ theo quận/phường + máy tính đầu tư cá nhân + dữ liệu mở.

---

## Giai đoạn 0 — Khảo sát nguồn dữ liệu ← ĐANG Ở ĐÂY

Chấm mỗi trang theo 6 tiêu chí trước khi viết bất kỳ scraper thật nào.

| Tiêu chí | Vì sao quan trọng |
|---|---|
| Lấy được dữ liệu không? | Có API JSON hay phải bóc HTML? Có bị Cloudflare chặn? |
| Có CẢ bán và cho thuê? | Không có cả hai thì không tính được tỉ suất |
| Có diện tích m²? | Không có m² thì không chuẩn hóa được, vô dụng |
| Có địa bàn tới cấp phường? | Cấp quận là quá thô để ghép bán ↔ thuê |
| Lọc/chia nhỏ được không? | Cần để né trần phân trang |
| Có khóa lọc trùng? | ID người đăng / SĐT — nếu không có thì thống kê bị bóp méo |

### Kết quả khảo sát

#### ✅ Chợ Tốt (nhatot.com) — ĐẠT, nguồn tốt nhất hiện tại

API JSON công khai: `https://gateway.chotot.com/v1/public/ad-listing`
Không cần đăng nhập, không bị chặn, trả về sạch.

| Tiêu chí | Kết quả |
|---|---|
| Lấy được | ✅ API JSON, ổn định |
| Bán & thuê | ✅ `st=s` = bán, `st=u` = cho thuê — lọc chuẩn 100% |
| Diện tích | ✅ `area` (m²), có sẵn cả `price_million_per_m2` |
| Địa bàn | ✅ `area_v2` = quận, `ward` = phường |
| Chia nhỏ | ✅ lọc được theo quận và theo phường |
| Lọc trùng | ✅ `account_oid` (ID người đăng) |

**Mã cần dùng**

- Vùng: Hà Nội = `12000`, TP.HCM = `13000`
- Danh mục: `1010` Căn hộ/Chung cư · `1020` Nhà ở · `1030` Văn phòng, MBKD ·
  `1040` Đất · `1050` Phòng trọ

**Cảnh báo đã phát hiện**

1. **Tin bán và tin thuê nằm CHUNG một danh mục.** cg=1010 chứa cả "6 tỷ" lẫn
   "6,3 triệu/tháng". Bắt buộc lọc bằng `st`, nếu không tỉ suất sai hoàn toàn.
   *(Tham số `type` truyền vào bị API bỏ qua — đừng dùng.)*
2. **`total` chặn cứng ở 10000** dù thực tế nhiều hơn. Offset sâu vẫn trả tin thật
   (kiểm tra 120 tin ở 6 mức offset → 120 ID khác nhau, không trùng), nhưng `o=20000`
   thì lỗi. → **Phải chia truy vấn theo từng quận/phường**, đừng quét cả thành phố một lần.
3. Trường `type` của tin: `s` = bán, `u` = cho thuê.

**Trữ lượng mẫu (TP.HCM):** căn hộ bán ~4.081 tin · căn hộ thuê 10.000+ tin ·
nhà ở Quận 1 ~494 tin · một phường ở Thủ Đức ~89 tin.

#### ⬜ Chưa khảo sát

- batdongsan.com.vn — trữ lượng lớn nhất, nhưng nghi bị Cloudflare chặn mạnh
- guland.vn — mạnh về đất, nghi ít tin cho thuê
- alonhadat.com.vn / nhadat24h — trang cũ, HTML đơn giản, có thể dễ bóc
- mogi.vn — chưa đánh giá

---

## Giai đoạn 1 — Thu thập (~1 tuần)

Quét theo vòng lặp: `mỗi thành phố × mỗi quận × mỗi danh mục × (bán, thuê)`.
Chia theo quận để né trần 10.000. Chạy chậm, có nghỉ giữa các lần gọi, ghi log số
tin thu được mỗi lần để phát hiện khi trang đổi cấu trúc.

Lưu thô dạng JSON theo ngày, không sửa gì — mọi xử lý làm ở bước sau.

## Giai đoạn 2 — Làm sạch & lọc trùng (~1 tuần)

- Lọc trùng theo `account_oid` + diện tích + giá lệch < 5%
- Loại tin rác: giá quá thấp/cao bất thường, diện tích vô lý, tin mồi
- Chuẩn hóa tên phường/quận (nhiều tên có hậu tố "Quận X cũ" do sáp nhập)
- Ghi lại **đã loại bao nhiêu tin và vì sao** → đưa vào trang Phương pháp

## Giai đoạn 3 — Tính tỉ suất (~3 ngày)

Tính theo **ô**: `phường × loại hình × khoảng diện tích`.
Trong mỗi ô lấy **trung vị** giá bán/m² và giá thuê/m².

```
tỉ suất thô = (giá thuê/m²/tháng × 12) / (giá bán/m²)
```

**Ô nào có dưới 10 tin ở một trong hai phía thì để trống** — thà bản đồ có lỗ còn hơn sai.

## Giai đoạn 4 — Tầng tài chính (~4 ngày)

1. Tỉ suất **ròng** = trừ thuế cho thuê, phí quản lý, sửa chữa, tỉ lệ bỏ trống
2. So với **lãi suất tiết kiệm** → bản đồ chính tô theo phần chênh lệch
3. Kịch bản **đi vay**: lãi vay > tỉ suất ⇒ mỗi tháng bù lỗ bao nhiêu
4. Câu hỏi chốt: **giá nhà phải tăng bao nhiêu %/năm thì người mua mới hòa vốn?**

## Giai đoạn 5 — Website (~1–2 tuần)

1. Một câu + một con số ở đầu trang
2. Bản đồ quận/phường tô theo chênh lệch so với gửi tiết kiệm
3. **Máy tính đầu tư** — nhập giá nhà, tiền thuê, % vay, lãi suất → dòng tiền/tháng,
   số năm hòa vốn, mức tăng giá cần thiết
4. Bảng xếp hạng quận, kèm cột số tin để thấy độ tin cậy
5. Phương pháp · Giới hạn · Tải dữ liệu **đã tổng hợp** (không đăng lại tin thô)

## Giai đoạn 6 — Viết (~3 ngày)

Báo cáo 10–15 trang. Gửi xin nhận xét từ một giảng viên tài chính.

---

## Giới hạn phải nói thẳng trên web

- Giá **rao** không phải giá **giao dịch**; người bán thường hét cao hơn 5–15%
  ⇒ tỉ suất tính ra bị **thấp hơn thực tế**. Cần đưa kịch bản chiết khấu 10%.
- Chỉ phản ánh phân khúc có rao trên mạng, không phải toàn thị trường.
- Đất nền không có thị trường cho thuê ⇒ không tính được tỉ suất.
- Dữ liệu là **một lát cắt tại thời điểm quét**, không phải chuỗi thời gian.

## Nguyên tắc thu thập

Quét chậm, tôn trọng robots.txt, không đăng nhập chui, không đăng lại nội dung tin gốc —
chỉ công bố số liệu đã tổng hợp theo phường.
