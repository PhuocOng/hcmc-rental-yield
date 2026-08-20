/* Chuoi cua TRANG CHU. Tach rieng khoi i18n.js (cua bang dieu khien) de moi trang
   chi mang theo dung phan chu cua no. */
const H={
en:{
 title:"HCMC Rental Yield",
 sc1:"45,084 listings.", sc1b:"20 districts. One question.",
 sc2:"What does a landlord actually keep?",
 sc2b:"Every for-sale and for-rent listing on Vietnam's largest classifieds site, matched ward by ward, size band by size band.",
 sc3:"This is what they keep.",
 loading:"Loading", scroll:"Scroll",
 nav_dash:"Data explorer",
 cta_sub:"Interactive map · district ranking · run your own numbers",
 kick:"Ho Chi Minh City · 45,084 listings · August 2026",
 h1a:"Buying to let in HCMC", h1b:"earns less than a bank deposit",
 lede:"I collected every for-sale and for-rent listing on Vietnam's largest classifieds site, "
   +"matched them ward by ward, and worked out what a landlord actually keeps. "
   +"Across all 20 districts, not one clears the rate a bank pays for doing nothing.",
 bar_rent:"letting, after tax, fees and vacancy", bar_dep:"12-month deposit, state banks",
 cta:"Open the data explorer", cta2:"How it was done",
 f_title:"What the numbers say",
 f1n:"66", f1u:"years", f1:"Payback period",
 f1t:"At a net yield of 1.51%, rent alone needs sixty-six years to repay the purchase price. "
   +"Buy today and the rent finishes paying for the flat in 2092.",
 f2n:"−6.9", f2u:"% a year", f2:"Cash flow when financed",
 f2t:"Borrow 70% at the 12% floating rate most buyers end up on and the property bleeds money "
   +"every single month. The rent covers barely a fifth of the interest.",
 f3n:"8.7", f3u:"% a year", f3:"Price growth needed",
 f3t:"For a leveraged buyer to merely match a savings account, HCMC property prices must rise "
   +"8.7% every year, forever. That is the bet the whole market is making.",
 h_title:"How it was done", h_sub:"Four steps, all reproducible from the code in this repo.",
 h1:"Collect", h1t:"48,018 listings pulled from Chợ Tốt's public API, split by district to dodge "
   +"the 10,000-row pagination ceiling. Sale and rent listings share one category, so they must be "
   +"separated by an explicit flag — miss that and every number is silently wrong.",
 h2:"Clean", h2t:"45,084 kept (93.9%). Dropped: impossible sizes (one listing claimed 64 billion m²), "
   +"prices posted in the wrong category, and 2,292 duplicates from brokers reposting the same flat.",
 h3:"Match", h3t:"Never district averages — sale listings skew to large townhouses, rentals to small "
   +"flats. Every comparison happens inside one cell: same ward, same property type, same size band, "
   +"median price per m² on each side, minimum 10 listings per side or the cell is dropped.",
 h4:"Compare", h4t:"Gross yield becomes net after tax, vacancy, management and maintenance. Then it "
   +"is set against the deposit rate, the mortgage rate, and the price growth a buyer would need to "
   +"break even.",
 w_title:"What is in the explorer",
 w1:"Interactive map", w1t:"20 districts over satellite imagery, coloured by net yield.",
 w2:"Ranked comparison", w2t:"Every district with its 95% confidence interval, so you can see which "
   +"ranks are real and which are noise.",
 w3:"Your own numbers", w3t:"A calculator pre-loaded with any of 170 market cells. Every assumption "
   +"is a slider.",
 l_title:"What this cannot tell you",
 l_t:"These are asking prices, not transaction prices, so the true yield is somewhat higher than "
   +"shown. Transaction costs are not yet modelled, which means the required price growth is "
   +"understated. It is one source and a single snapshot, so it says nothing about trend. Every "
   +"limitation is spelled out in full on the explorer page — read them before quoting any number.",
 l_link:"Read the full limitations",
 d_title:"Data and code",
 d_t:"Only ward-level aggregates are published, never the original listing text. Everything below "
   +"is the exact data behind the charts.",
 d1:"Yield by ward cell", d2:"Yield by district and size", d3:"District ranking with intervals",
 d4:"Financial summary", d5:"Cleaning log",
 foot:"High-school project · data from Chợ Tốt, 15 August 2026 · base maps by Esri and CARTO · "
   +"<b>not investment advice</b>."
},
vi:{
 title:"Tỉ suất cho thuê bất động sản TP.HCM",
 sc1:"45.084 tin rao.", sc1b:"20 quận. Một câu hỏi.",
 sc2:"Người cho thuê thực sự giữ được bao nhiêu?",
 sc2b:"Toàn bộ tin rao bán và rao cho thuê trên sàn rao vặt lớn nhất Việt Nam, ghép theo từng phường, từng tầm diện tích.",
 sc3:"Đây là con số họ giữ được.",
 loading:"Đang tải", scroll:"Cuộn xuống",
 nav_dash:"Bảng dữ liệu",
 cta_sub:"Bản đồ tương tác · xếp hạng quận · nhập số của chính bạn",
 kick:"TP. Hồ Chí Minh · 45.084 tin rao · Tháng 8/2026",
 h1a:"Mua nhà cho thuê ở TP.HCM", h1b:"lời ít hơn gửi tiết kiệm",
 lede:"Mình thu thập toàn bộ tin rao bán và rao cho thuê trên sàn rao vặt lớn nhất Việt Nam, "
   +"ghép lại theo từng phường, rồi tính xem người cho thuê thực sự giữ được bao nhiêu. "
   +"Cả 20 quận, không một quận nào đuổi kịp mức lãi ngân hàng trả cho việc không làm gì.",
 bar_rent:"cho thuê, sau thuế, phí và bỏ trống", bar_dep:"gửi tiết kiệm 12 tháng, Big4",
 cta:"Mở bảng dữ liệu", cta2:"Cách làm",
 f_title:"Những con số nói gì",
 f1n:"66", f1u:"năm", f1:"Số năm hoàn vốn",
 f1t:"Với tỉ suất ròng 1,51%, riêng tiền thuê cần sáu mươi sáu năm mới trả hết giá mua. "
   +"Mua hôm nay thì tới năm 2092 tiền thuê mới trả xong căn nhà.",
 f2n:"−6,9", f2u:"% mỗi năm", f2:"Dòng tiền khi vay",
 f2t:"Vay 70% ở mức thả nổi 12% mà hầu hết người mua rơi vào, căn nhà rỉ máu mỗi tháng. "
   +"Tiền thuê chỉ bù nổi khoảng một phần năm tiền lãi.",
 f3n:"8,7", f3u:"% mỗi năm", f3:"Mức tăng giá cần có",
 f3t:"Để người vay chỉ vừa bằng gửi tiết kiệm, giá nhà TP.HCM phải tăng 8,7% mỗi năm, mãi mãi. "
   +"Đó là canh bạc mà cả thị trường đang đặt cược.",
 h_title:"Cách làm", h_sub:"Bốn bước, đều chạy lại được từ mã nguồn trong dự án.",
 h1:"Thu thập", h1t:"48.018 tin lấy từ API công khai của Chợ Tốt, chia theo từng quận để né trần "
   +"phân trang 10.000 dòng. Tin bán và tin thuê nằm chung một danh mục nên bắt buộc phải tách bằng "
   +"tham số riêng — bỏ sót chỗ này là mọi con số sai mà nhìn vẫn thấy hợp lý.",
 h2:"Làm sạch", h2t:"Giữ lại 45.084 tin (93,9%). Loại: diện tích vô lý (có tin khai 64 tỷ m²), "
   +"giá đăng nhầm mục, và 2.292 tin trùng do môi giới đăng lại cùng một căn.",
 h3:"Ghép cặp", h3t:"Tuyệt đối không lấy trung bình cả quận — tin bán nghiêng về nhà phố lớn, tin "
   +"thuê nghiêng về căn hộ nhỏ. Mọi so sánh chỉ diễn ra trong một ô: cùng phường, cùng loại hình, "
   +"cùng tầm diện tích, lấy trung vị giá mỗi m² của từng bên, tối thiểu 10 tin mỗi phía nếu không "
   +"thì bỏ ô đó.",
 h4:"So sánh", h4t:"Tỉ suất gộp thành tỉ suất ròng sau thuế, bỏ trống, phí quản lý và bảo trì. Rồi "
   +"đem đặt cạnh lãi tiết kiệm, lãi vay, và mức tăng giá mà người mua cần để hòa vốn.",
 w_title:"Trong bảng dữ liệu có gì",
 w1:"Bản đồ tương tác", w1t:"20 quận phủ lên ảnh vệ tinh, tô màu theo tỉ suất ròng.",
 w2:"Xếp hạng có sai số", w2t:"Từng quận kèm khoảng tin cậy 95%, để thấy thứ hạng nào là thật và "
   +"thứ hạng nào chỉ là nhiễu.",
 w3:"Số của chính bạn", w3t:"Máy tính điền sẵn theo 170 ô thị trường. Mọi giả định đều là thanh trượt.",
 l_title:"Những gì trang này không trả lời được",
 l_t:"Đây là giá rao chứ không phải giá giao dịch, nên tỉ suất thật cao hơn con số hiển thị đôi chút. "
   +"Chi phí giao dịch chưa được đưa vào mô hình, nghĩa là mức tăng giá cần có đang bị tính thấp. "
   +"Chỉ một nguồn và chỉ một lát cắt thời gian, nên không nói được gì về xu hướng. Toàn bộ giới hạn "
   +"được ghi đầy đủ trong bảng dữ liệu — đọc trước khi trích bất kỳ con số nào.",
 l_link:"Đọc đầy đủ phần giới hạn",
 d_title:"Dữ liệu và mã nguồn",
 d_t:"Chỉ công bố số liệu đã tổng hợp theo phường, không đăng lại nội dung tin gốc. Bên dưới là đúng "
   +"bộ dữ liệu đứng sau các biểu đồ.",
 d1:"Tỉ suất theo ô phường", d2:"Tỉ suất theo quận và diện tích", d3:"Xếp hạng quận kèm khoảng tin cậy",
 d4:"Tổng hợp tài chính", d5:"Nhật ký làm sạch",
 foot:"Dự án học sinh · dữ liệu từ Chợ Tốt, ngày 15/08/2026 · bản đồ nền Esri và CARTO · "
   +"<b>không phải lời khuyên đầu tư</b>."
}};
