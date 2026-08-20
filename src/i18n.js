/* Tu dien song ngu — nhung thang vao index.html luc build.
   Moi chuoi hien ra man hinh deu phai co o CA HAI ngon ngu. */
const T={
en:{
 title:"HCMC Rental Yield", src:"Chợ Tốt · 15 Aug 2026",
 s_clean:"listings analysed", s_raw:"raw listings", s_cells:"ward cells",
 h_cmp:"Net rental yield vs 12-month bank deposit",
 h_rent:"letting, after all costs", h_dep:"bank deposit, state banks",
 h_gap:(g,m)=>"A deposit pays <b>"+m+"×</b> more — a gap of <b>"+g+"</b> every year, "
   +"before the property has appreciated a single dong.",
 s_gross:"Gross yield", s_gross_s:"before tax, fees and vacancy",
 s_pay:"Payback", s_pay_s:"years of rent to repay the price",
 s_rng:"Across districts", s_rng_s:n=>"not one of "+n+" reaches the deposit rate",
 
 dep_short:"Deposit",
 unit_yr:"%/yr", unit_pp:"pp", unit_years:"yrs",
 p_map:"Net yield by district", h_map:"drag · scroll to zoom · click to fly",
 p_rank:"District ranking", h_rank:"whiskers show the 95% confidence interval",
 p_scat:"Price versus yield", h_scat:"one dot = district × size cell",
 p_hist:"Distribution across wards",
 p_calc:"Investment calculator",
 h_calc:"pick a market cell or type your own — every assumption is adjustable",
 p_tbl:"Ward-level data", h_tbl:"click a header to sort · thin-sample cells are dimmed",
 p_meth:"Method", p_lim:"Limitations", h_lim:"read before citing",
 b_vn:"All Vietnam", b_hcm:"Back to HCMC", lg_t:"Net yield %/yr",
 m_sat:"Satellite", m_str:"Street", m_dark:"Dark",
 f_all:"All", f_apt:"Apartment", f_house:"House", lg_size:"dot size ∝ listing count",
 f_cell:"Market cell", f_price:"Purchase price", f_rent:"Monthly rent",
 f_ltv:"Loan-to-value", f_mrate:"Mortgage rate", f_drate:"Deposit rate",
 f_vac:"Vacancy", f_maint:"Management + maintenance",
 r_gross:"Gross yield", r_net:"Net yield", r_pay:"Payback period",
 r_cf:"Monthly cash flow if financed", r_dep:"Same money in the bank",
 r_appr:"Price growth needed to break even",
 ax_price:"Sale price, million ₫ per m²", ax_ward:"Net yield per ward cell",
 own:"— type your own —", mo:"months", yrs:"yrs", never:"never",
 nodata:"insufficient data", nomap:"The map needs a network connection to load tiles.",
 th:["Ward","District","Type","Sale<span>M₫/m²</span>","Rent<span>k₫/m²/mo</span>",
     "Gross<span>%/yr</span>","Net<span>%/yr</span>","95% CI",
     "Listings<span>sale/rent</span>"],
 vd1:(a,b,c)=>"A bank deposit beats this by <b>"+a+"</b> a year. The monthly cash-flow gap "
   +"between the two options is <b>"+b+"</b>. For buying to come out ahead, the property "
   +"price must rise <b>"+c+"</b> every year, year after year.",
 vd2:a=>"Under these assumptions, letting the property edges out a deposit by <b>"+a+"</b> a year.",
 foot:"High-school project · data collected from Chợ Tốt on 15 Aug 2026 · only ward-level "
   +"aggregates are published, never the original listing text · base maps by Esri and CARTO · "
   +"<b>not investment advice</b>.",
 meth:d=>`
  <h3>Matched cells, never district averages</h3>
  <p>Dividing a district's average sale price by its average rent is wrong: for-sale listings skew
  toward large townhouses while rentals skew toward small apartments, so the ratio compares a villa
  price against a room rent. Every comparison here happens <b>inside a single cell</b> — same ward
  (or district), same property type, same size band — using the <b>median price per m²</b> on each
  side. A cell needs at least 10 listings on <i>both</i> sides or it is dropped rather than guessed.</p>

  <h3>Confidence intervals</h3>
  <p>Each cell holds only tens of listings, so the yield <b>carries sampling error</b>. The 95%
  interval is estimated by <b>bootstrap</b>: resample the cell's own listings with replacement,
  recompute the yield, repeat 600 times. At district level that interval spans a median of
  <b>${d.n.ciw} percentage points</b>. Consequently <b>ranks in the middle of the table are not
  statistically distinguishable</b> — only the two ends separate cleanly.</p>

  <h3>Cross-check</h3>
  <p>Gross yield was computed two independent ways: by <i>ward × type</i> it comes to 2.57%/yr, by
  <i>district × type × size band</i> to 2.61%/yr. The near-agreement means the result is not an
  artefact of differing size mixes between the two sides.</p>

  <h3>Cleaning</h3>
  <p>${d.n.raw.toLocaleString('en-US')} raw listings → ${d.n.clean.toLocaleString('en-US')} kept
  (${d.n.pct}%). Dropped:</p>
  <table class="kv"><tbody>
  <tr><td>Missing price, size or ward</td><td>${d.rej['1_thieu_truong_bat_buoc'].toLocaleString('en-US')}</td></tr>
  <tr><td>Size outside 10–1,000 m²</td><td>${d.rej['2_dien_tich_vo_ly'].toLocaleString('en-US')}</td></tr>
  <tr><td>Price outside a plausible range</td><td>${d.rej['3_gia_vo_ly'].toLocaleString('en-US')}</td></tr>
  <tr><td>Implausible price per m² (posted in the wrong category)</td><td>${d.rej['4_gia_tren_m2_vo_ly'].toLocaleString('en-US')}</td></tr>
  <tr><td>Duplicate: same poster, size and price</td><td>${d.rej['5_trung_mem'].toLocaleString('en-US')}</td></tr>
  </tbody></table>

  <h3>Default assumptions</h3>
  <table class="kv"><tbody>
  <tr><td>12-month deposit rate</td><td>6.0%/yr</td></tr>
  <tr><td>Floating mortgage rate</td><td>12.0%/yr</td></tr>
  <tr><td>Loan-to-value</td><td>70%</td></tr>
  <tr><td>Vacancy</td><td>1 month/yr</td></tr>
  <tr><td>Rental income tax</td><td>10% of revenue</td></tr>
  <tr><td>Building management fee</td><td>15,000 ₫/m²/month</td></tr>
  <tr><td>Maintenance</td><td>0.5% of value/yr</td></tr>
  </tbody></table>`,
 lim:`
  <details open><summary>These are asking prices, not transaction prices</summary>
  <p>Sellers typically ask 5–15% above the closing price while rents are negotiated less, so the
  true yield is <b>higher</b> than shown here. But for the gross yield to reach the 6% deposit rate,
  asking prices would have to exceed transaction prices by <b>53%</b> — no market negotiates that
  far. The conclusion survives its own biggest weakness.</p></details>

  <details><summary>Transaction costs are not yet modelled</summary>
  <p>Registration tax, notarisation, agency fees and the 2% transfer tax add roughly 5–7% for a
  round trip. Over a five-year hold that is about 1.2%/yr not deducted here, so the
  <b>required price growth shown is understated</b>.</p></details>

  <details><summary>A single-period comparison, not an IRR</summary>
  <p>This is a static one-year comparison. The industry-standard frame is an IRR over a 5–10 year
  hold with amortising debt, entry costs and a terminal sale. A deposit rate is also a soft hurdle:
  an illiquid, levered, undiversified asset should have to clear a higher bar.</p></details>

  <details><summary>One source, and only freshly posted listings</summary>
  <p>Everything comes from Chợ Tốt. Median listing age is just <b>6 days</b> — the API returns
  recent posts rather than standing inventory, so stale listings (typically the most overpriced)
  may be under-represented. The 3.4%/yr apartment figure also sits below the 4–5% published by CBRE
  and Savills; that gap is not yet fully explained.</p></details>

  <details><summary>The two sides may not be the same asset</summary>
  <p>Within one cell, for-sale listings may skew toward newly completed towers while rentals skew
  toward older stock. If so, this divides new-build prices by old-building rents and the yield is
  systematically depressed.</p></details>

  <details><summary>Ward names are unstable after the mergers</summary>
  <p>Many carry a "(former District 2)" suffix and 17 names map to more than one code. All
  computation keys on the <b>ward code</b>; names are for display only.</p></details>

  <details><summary>A snapshot, not a time series</summary>
  <p>Data captured on 15 Aug 2026. Whether prices actually rise fast enough for a buyer to break
  even <b>cannot</b> be answered with this dataset.</p></details>`
},

vi:{
 title:"Tỉ suất cho thuê bất động sản TP.HCM", src:"Chợ Tốt · 15/08/2026",
 s_clean:"tin sau lọc", s_raw:"tin thô", s_cells:"ô phường",
 h_cmp:"Tỉ suất cho thuê ròng so với gửi tiết kiệm 12 tháng",
 h_rent:"cho thuê, sau mọi chi phí", h_dep:"gửi tiết kiệm, Big4 tại quầy",
 h_gap:(g,m)=>"Gửi ngân hàng lời gấp <b>"+m+" lần</b> — chênh <b>"+g+"</b> mỗi năm, "
   +"khi giá nhà còn chưa tăng đồng nào.",
 s_gross:"Tỉ suất gộp", s_gross_s:"trước thuế, phí và bỏ trống",
 s_pay:"Hoàn vốn", s_pay_s:"số năm tiền thuê trả hết giá mua",
 s_rng:"Giữa các quận", s_rng_s:n=>"không quận nào trong "+n+" chạm mức tiết kiệm",
 
 dep_short:"Tiết kiệm",
 unit_yr:"%/năm", unit_pp:"điểm %", unit_years:"năm",
 p_map:"Tỉ suất ròng theo quận", h_map:"kéo · lăn để phóng · bấm để nhảy tới",
 p_rank:"Xếp hạng quận", h_rank:"vạch ngang là khoảng tin cậy 95%",
 p_scat:"Giá bán và tỉ suất", h_scat:"mỗi điểm là một ô quận × diện tích",
 p_hist:"Phân bố theo phường",
 p_calc:"Máy tính đầu tư",
 h_calc:"chọn một ô thị trường hoặc tự nhập — mọi giả định đều chỉnh được",
 p_tbl:"Dữ liệu theo phường", h_tbl:"bấm tiêu đề cột để sắp xếp · ô ít tin được làm mờ",
 p_meth:"Phương pháp", p_lim:"Giới hạn", h_lim:"đọc trước khi trích dẫn",
 b_vn:"Toàn Việt Nam", b_hcm:"Về TP.HCM", lg_t:"Tỉ suất ròng %/năm",
 m_sat:"Vệ tinh", m_str:"Bản đồ", m_dark:"Nền tối",
 f_all:"Tất cả", f_apt:"Căn hộ", f_house:"Nhà ở", lg_size:"kích thước điểm ∝ số tin",
 f_cell:"Ô thị trường", f_price:"Giá mua", f_rent:"Tiền thuê mỗi tháng",
 f_ltv:"Tỉ lệ vay", f_mrate:"Lãi suất vay", f_drate:"Lãi tiết kiệm",
 f_vac:"Bỏ trống", f_maint:"Phí quản lý + bảo trì",
 r_gross:"Tỉ suất gộp", r_net:"Tỉ suất ròng", r_pay:"Số năm hoàn vốn",
 r_cf:"Dòng tiền mỗi tháng khi vay", r_dep:"Nếu gửi số tiền đó vào ngân hàng",
 r_appr:"Giá phải tăng mỗi năm để hòa vốn",
 ax_price:"Giá bán, triệu ₫ mỗi m²", ax_ward:"Tỉ suất ròng của ô phường",
 own:"— tự nhập —", mo:"tháng", yrs:"năm", never:"không bao giờ",
 nodata:"không đủ dữ liệu", nomap:"Bản đồ cần kết nối mạng để tải ảnh nền.",
 th:["Phường","Quận","Loại hình","Giá bán<span>tr₫/m²</span>","Giá thuê<span>ngh₫/m²/th</span>",
     "Gộp<span>%/năm</span>","Ròng<span>%/năm</span>","KTC 95%",
     "Số tin<span>bán/thuê</span>"],
 vd1:(a,b,c)=>"Gửi ngân hàng hơn <b>"+a+"</b> mỗi năm. Chênh lệch dòng tiền giữa hai lựa chọn là "
   +"<b>"+b+"</b> mỗi tháng. Để mua nhà có lợi hơn, giá nhà phải tăng đều <b>"+c+"</b> mỗi năm, "
   +"năm này qua năm khác.",
 vd2:a=>"Với các giả định này, cho thuê nhỉnh hơn gửi tiết kiệm <b>"+a+"</b> mỗi năm.",
 foot:"Dự án học sinh · dữ liệu Chợ Tốt thu thập ngày 15/08/2026 · chỉ công bố số liệu đã tổng hợp "
   +"theo phường, không đăng lại nội dung tin gốc · bản đồ nền Esri và CARTO · "
   +"<b>không phải lời khuyên đầu tư</b>.",
 meth:d=>`
  <h3>Ghép theo ô, không lấy trung bình cả quận</h3>
  <p>Lấy giá bán trung bình một quận chia cho tiền thuê trung bình quận đó là sai: tin rao bán
  nghiêng về nhà phố lớn, tin cho thuê nghiêng về căn hộ nhỏ, nên phép chia đó đem giá biệt thự so
  với tiền thuê một phòng. Mọi so sánh ở đây chỉ thực hiện <b>trong cùng một ô</b> — cùng phường
  (hoặc quận), cùng loại hình, cùng tầm diện tích — và dùng <b>trung vị giá trên mỗi m²</b> của
  từng bên. Ô nào không đủ 10 tin ở <i>cả hai</i> phía thì bị loại chứ không đoán.</p>

  <h3>Khoảng tin cậy</h3>
  <p>Mỗi ô chỉ có vài chục tin, nên tỉ suất tính ra <b>có sai số lấy mẫu</b>. Khoảng tin cậy 95%
  được ước lượng bằng <b>bootstrap</b>: lấy mẫu có hoàn lại từ chính danh sách tin của ô, tính lại
  tỉ suất, lặp 600 lần. Ở cấp quận, khoảng này rộng trung vị <b>${d.n.ciw} điểm phần trăm</b>.
  Vì vậy <b>thứ hạng ở nhóm giữa bảng không tách bạch về mặt thống kê</b> — chỉ hai đầu là phân
  biệt được rõ.</p>

  <h3>Tự kiểm tra chéo</h3>
  <p>Tỉ suất gộp được tính độc lập theo hai cách: theo <i>phường × loại hình</i> ra 2,57%/năm, theo
  <i>quận × loại hình × nhóm diện tích</i> ra 2,61%/năm. Hai con số gần trùng nhau, nghĩa là kết quả
  không đến từ chênh lệch cơ cấu diện tích giữa hai phía.</p>

  <h3>Làm sạch</h3>
  <p>${d.n.raw.toLocaleString('vi-VN')} tin thô → giữ ${d.n.clean.toLocaleString('vi-VN')} tin
  (${String(d.n.pct).replace('.',',')}%). Bị loại:</p>
  <table class="kv"><tbody>
  <tr><td>Thiếu giá, diện tích hoặc phường</td><td>${d.rej['1_thieu_truong_bat_buoc'].toLocaleString('vi-VN')}</td></tr>
  <tr><td>Diện tích ngoài 10–1.000 m²</td><td>${d.rej['2_dien_tich_vo_ly'].toLocaleString('vi-VN')}</td></tr>
  <tr><td>Giá ngoài khoảng hợp lý</td><td>${d.rej['3_gia_vo_ly'].toLocaleString('vi-VN')}</td></tr>
  <tr><td>Giá trên m² vô lý (đăng nhầm mục)</td><td>${d.rej['4_gia_tren_m2_vo_ly'].toLocaleString('vi-VN')}</td></tr>
  <tr><td>Trùng: cùng người đăng, cùng m², cùng giá</td><td>${d.rej['5_trung_mem'].toLocaleString('vi-VN')}</td></tr>
  </tbody></table>

  <h3>Giả định mặc định</h3>
  <table class="kv"><tbody>
  <tr><td>Lãi tiết kiệm 12 tháng</td><td>6,0%/năm</td></tr>
  <tr><td>Lãi vay thả nổi</td><td>12,0%/năm</td></tr>
  <tr><td>Tỉ lệ vay</td><td>70%</td></tr>
  <tr><td>Bỏ trống</td><td>1 tháng/năm</td></tr>
  <tr><td>Thuế cho thuê</td><td>10% doanh thu</td></tr>
  <tr><td>Phí quản lý chung cư</td><td>15.000 ₫/m²/tháng</td></tr>
  <tr><td>Bảo trì</td><td>0,5% giá trị/năm</td></tr>
  </tbody></table>`,
 lim:`
  <details open><summary>Đây là giá rao, không phải giá giao dịch</summary>
  <p>Người bán thường hét cao hơn giá chốt 5–15%, giá thuê ít mặc cả hơn, nên tỉ suất thật
  <b>cao hơn</b> con số ở đây. Nhưng để tỉ suất gộp chạm mức tiết kiệm 6%, giá rao phải cao hơn giá
  bán thật tới <b>53%</b> — không thị trường nào mặc cả ở mức đó. Kết luận đứng vững trước chính
  điểm yếu lớn nhất của nó.</p></details>

  <details><summary>Chưa tính chi phí giao dịch</summary>
  <p>Lệ phí trước bạ, công chứng, môi giới và thuế chuyển nhượng 2% cộng lại khoảng 5–7% cho một
  vòng mua–bán. Với kỳ nắm giữ 5 năm đó là khoảng 1,2%/năm chưa được trừ, nên <b>mức tăng giá cần
  thiết hiển thị ở đây đang bị tính thấp</b>.</p></details>

  <details><summary>So sánh một kỳ, chưa phải IRR</summary>
  <p>Đây là so sánh tĩnh một năm. Khung đúng của ngành là IRR trên kỳ nắm giữ 5–10 năm, có trả gốc
  dần, chi phí mua vào và bán ra ở cuối kỳ. Lãi tiết kiệm cũng là mốc dễ dãi — tài sản kém thanh
  khoản, có đòn bẩy, không phân tán thì phải vượt một mốc cao hơn.</p></details>

  <details><summary>Một nguồn, và chỉ là tin mới đăng</summary>
  <p>Toàn bộ từ Chợ Tốt. Tuổi tin trung vị chỉ <b>6 ngày</b> — API trả về tin mới đăng chứ không
  phải toàn bộ hàng đang chào bán, nên hàng ế nằm lâu (thường bị hét giá cao nhất) có thể thiếu đại
  diện. Con số căn hộ 3,4%/năm cũng thấp hơn mức 4–5% mà CBRE và Savills công bố; phần chênh này
  chưa được giải thích đầy đủ.</p></details>

  <details><summary>Chưa kiểm tra hai phía có cùng loại tài sản</summary>
  <p>Trong cùng một ô, tin bán có thể nghiêng về căn hộ mới bàn giao còn tin thuê nghiêng về chung
  cư cũ. Nếu vậy thì đang lấy giá nhà mới chia cho tiền thuê nhà cũ, và tỉ suất bị kéo xuống một
  cách hệ thống.</p></details>

  <details><summary>Tên phường loạn vì sáp nhập</summary>
  <p>Nhiều phường có đuôi "(Quận 2 cũ)", 17 tên ứng với nhiều hơn một mã. Mọi tính toán dùng
  <b>mã phường</b> làm khóa, tên chỉ để hiển thị.</p></details>

  <details><summary>Một lát cắt, không phải chuỗi thời gian</summary>
  <p>Dữ liệu chụp ngày 15/08/2026. Câu hỏi "giá nhà có thật sự tăng đủ để người mua hòa vốn không"
  <b>không</b> trả lời được bằng bộ dữ liệu này.</p></details>`
}};
