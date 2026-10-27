# Phân loại rủi ro quyền

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud duy trì dữ liệu mức độ nghiêm trọng của quyền dùng chung, được [CloudPEASS](https://github.com/peass-ng/CloudPEASS) và [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) sử dụng. Hãy chỉnh sửa tệp nền tảng chuẩn tại đây, thay vì các bản sao được tạo trong một trong hai consumer.

- **Critical**: các quyền trực tiếp hoặc gần như độc lập cấp đặc quyền mạnh, tạo danh tính hoặc cho phép thực thi với đặc quyền.
- **High**: quyền truy cập thông tin nhạy cảm, thông tin xác thực hoặc một đường dẫn leo thang đặc quyền có điều kiện.
- **Medium**: DoS/Break, gián đoạn hoạt động, các thay đổi thông thường hoặc khả năng có điều kiện nhưng chưa chứng minh được đường dẫn đến dữ liệu nhạy cảm hay đặc quyền.
- **Low**: khả năng khám phá thông thường và quyền truy cập siêu dữ liệu.

Mỗi nền tảng có một tệp YAML chuẩn: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) và [Kubernetes](k8s.yaml). Đây là các tệp máy có thể đọc; các trang nền tảng hiển thị toàn bộ YAML trong trình duyệt và giải thích cách chỉnh sửa. Trình xem nội tuyến sử dụng bản trong sách, còn quy trình PEASS lấy các tệp chuẩn từ GitHub.

## Tệp nhà cung cấp cloud

`version` và `provider` xác định schema. `permission_categories` chứa bốn danh sách quyền riêng biệt. Chuyển một quyền giữa các danh sách để thay đổi mức đánh giá. Việc khớp của AWS và Azure không phân biệt chữ hoa chữ thường; việc khớp của GCP có phân biệt. Các bí danh khác nhau về chữ hoa chữ thường có thể lặp lại trong cùng mức độ nghiêm trọng, nhưng các mức đánh giá xung đột sẽ bị từ chối.

`severity_overrides` chứa các ngoại lệ đã được kiểm tra đối với quy tắc chung. Nếu một ngoại lệ cũng xuất hiện trong danh mục, cả hai mục phải thống nhất. `severity_caps` ngăn tổ hợp nâng mức đánh giá của các quyền được chọn. `non_permission_identifiers` loại trừ tên phương thức API, khóa điều kiện và các chuỗi khác đã được ghi nhận nhưng không phải quyền ủy quyền thực tế.

`combinations.critical` và `combinations.high` là danh sách các danh sách quyền: mọi phần tử trong một danh sách con đều phải được cấp thì tổ hợp đó mới áp dụng. Hãy giữ nguyên các tổ hợp; tách chúng thành các quyền riêng lẻ sẽ phóng đại rủi ro. Các trường chính xác và biểu thức chính quy hiện có vẫn là phương án dự phòng cho những quyền không có trong danh mục. Việc viết lại toàn bộ bộ phân loại hoặc thêm hành vi khớp mới vẫn cần thay đổi mã trong các consumer.

## Tệp Kubernetes

`rules` được sắp xếp theo thứ tự: quy tắc khớp đầu tiên sẽ được áp dụng. Mỗi quy tắc có một `id` duy nhất, một `match`, một `severity` và một `description` bằng ngôn ngữ thông thường. Thêm quy tắc cụ thể hơn trước quy tắc tổng quát hơn, hoặc thay đổi mức độ nghiêm trọng của quy tắc hiện có. Giữ nguyên quy tắc dự phòng cuối cùng không có điều kiện.

Điều kiện khớp dùng `all`, `any` và `not` để kết hợp, hoặc dùng phép so sánh `field`, `op` và `value`. Các trường hiện có là `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL không phải resource viết thường), `non_resource_url`, `mode` và `delegated_verb`. Các phép toán là `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` và `truthy` (không cần value). `always: true` khớp mọi trường hợp. Giá trị group, resource, subresource và verb được viết thường. Wildcard dạng ký tự cố định được viết là `'*'`; việc khớp một quyền cấp wildcard được nêu tường minh trong quy tắc, thay vì mở rộng theo mẫu shell.

`severity_when` có thể chọn một mức độ nghiêm trọng khác cho điều kiện khớp. `severity: delegated` được dành riêng cho hành vi impersonation bị giới hạn: bản đồ `delegated_severities` chuyển phân loại của hành động được ủy quyền thành mức đánh giá có điều kiện. Các placeholder trong description có thể tham chiếu đến những trường hiện có, chẳng hạn `{full}` và `{verb}`. Các quy tắc là dữ liệu và không bao giờ được đánh giá như mã Python hay shell.

## Xác thực và đồng bộ hóa

Trước khi gửi thay đổi, hãy chạy `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` khi đã cài PyYAML. Quy trình pull request của sách chạy cùng bước xác thực này.

Mỗi thứ Hai, cả hai repository consumer đều checkout `master` hiện tại của sách, xác thực cả bốn tệp, so sánh mã băm SHA-256 và cập nhật các tệp YAML đi kèm cùng các danh sách legacy được tạo. Tệp manifest nguồn ghi lại revision của sách và mã băm của từng tệp. Các thay đổi không liên quan trong sách sẽ không tạo commit ở consumer. Mỗi workflow cũng hỗ trợ chạy thủ công. Các bài kiểm thử chạy trước khi workflow commit dữ liệu đã thay đổi vào nhánh mặc định của consumer; nếu thất bại, nhánh đó sẽ không thay đổi. Consumer tiếp tục sử dụng các bản sao đi kèm khi offline giữa các lần cập nhật.

Để cập nhật cục bộ trong một consumer, hãy chạy `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Thêm `--check` để phát hiện các bản sao lỗi thời mà không ghi thay đổi.

Việc tải mã nguồn trong cả hai consumer thử lại năm lần, với thời hạn checkout có giới hạn và thời gian chờ tăng dần. Các lượt tải chưa hoàn tất được giữ trong thư mục tạm; nếu hết số lần thử, dữ liệu đi kèm hiện có sẽ không thay đổi.
{{#include ../banners/hacktricks-training.md}}
