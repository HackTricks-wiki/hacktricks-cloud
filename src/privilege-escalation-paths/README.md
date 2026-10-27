# Các đường dẫn leo thang đặc quyền

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud duy trì danh mục leo thang đặc quyền có thể đọc bằng máy, được [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) sử dụng. Mỗi kỹ thuật nêu rõ principal cần nắm giữ hiệu quả những quyền nào và trên tài nguyên nào để có được đặc quyền của một tập hợp principal mục tiêu. Blue-CloudPEASS đánh giá các mục này offline dựa trên snapshot kiểm kê chỉ đọc, vẽ các đường tấn công giữa các principal, đồng thời dùng policy hoặc binding cấp quyền làm bằng chứng và đưa ra biện pháp giảm thiểu loại bỏ đường dẫn. Hãy chỉnh sửa các tệp chuẩn tại đây, thay vì các bản sao trong consumer.

Các mục chỉ mô tả điều kiện tiên quyết, mục tiêu có thể tiếp cận và biện pháp giảm thiểu. Chúng không chứa lệnh, payload hay các bước thực thi; trang HackTricks được liên kết giải thích kỹ thuật.

## Bố cục

Mỗi nền tảng có một thư mục riêng (`aws`, `gcp`, `azure`, `k8s`) và mỗi dịch vụ có một tệp `<service>.yaml` chứa danh sách kỹ thuật dạng YAML. Các tệp có tên `_excluded*.yaml` liệt kê những kỹ thuật HackTricks đã được xem xét nhưng cố ý không có mục tương ứng, chẳng hạn như post-exploitation, persistence hoặc kỹ thuật không thể mô hình hóa từ cấu hình, kèm theo lý do. `privesc-technique.schema.json` là JSON Schema được xuất ra để hỗ trợ hoàn thành và xác thực trong editor.

## Các trường kỹ thuật

- `id`: duy nhất trên toàn cục, viết thường theo kebab-case và có tiền tố nền tảng.
- `provider`, `service`, `title` và `summary`: một câu mô tả những gì nguồn có được.
- `source`: trang HackTricks và anchor ghi lại kỹ thuật, tính tương đối với cuốn sách này. `source_revision` là commit của cuốn sách đã được đọc.
- `requires`: các quyền mà nguồn phải nắm giữ. `all_of` liệt kê mọi mục bắt buộc, còn `any_of` liệt kê các lựa chọn thay thế. Các mục AWS và GCP dùng `action` và `resource`; mục Azure dùng `action` (hoặc `data_action`) và `scope`; mục Entra ID dùng `entra_permission` hoặc `entra_role`; mục Kubernetes dùng `verb`, `resource`, `subresource`, `api_group` và `namespace`. Các placeholder như `{target.arn}` liên kết một yêu cầu với mục tiêu.
- `target`: `kind` của mục tiêu, `selector` có các điều kiện đều phải thỏa mãn để principal có thể tiếp cận, và `scope` của mục tiêu.
- `conditions` và `blockers`: những yếu tố có thể ngăn cản đường dẫn trong thực tế, chẳng hạn như condition key, SCP, boundary hoặc admission policy.
- `confidence`, `severity`, `mitigation`, `references` và `notes` (tùy chọn).

Các trường, loại mục tiêu, khóa selector và placeholder không xác định sẽ bị từ chối thay vì bị bỏ qua, để một mục không bao giờ âm thầm mở rộng hoặc thu hẹp tập mục tiêu. Trước tiên, hãy bổ sung hỗ trợ selector mới trong evaluator của consumer.

### Các bổ sung trong Schema v2

Loader v2 bổ sung hai placeholder và một selector AWS, đồng thời cho phép selector K8s dành cho pod đang chạy hiện có được dùng với mục tiêu GCP. Các trường này yêu cầu khớp chính xác với dữ liệu kiểm kê đã thu thập; nếu thiếu dữ liệu kiểm kê, phạm vi bao phủ sẽ không xác định, chứ không được xem là đường dẫn có thể tiếp cận.

| Trường | Cách dùng và cấu trúc bắt buộc |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` và `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Dùng kết hợp trên mục tiêu AWS `aws_account_admin`. Mọi phương án thay thế trong yêu cầu phải bao gồm `iam:CreatePolicyVersion` trên placeholder đó. Policy phải được gắn vào một role mà nguồn có thể assume trong cùng tài khoản; evaluator kiểm tra khả năng tạo phiên bản policy và tính toán lại các quyền hiệu lực của role. Không hỗ trợ `SetDefaultPolicyVersion`. |
| `target.selector.k8s_sa_used_by_running_pod: true` | Dùng trên mục tiêu GCP `k8s_service_account` với `scope: cluster` để chọn các KSA được pod đang chạy sử dụng, có token khả dụng trong GKE cluster tương ứng. Không kết hợp với `k8s_sa_in_cluster` hoặc `k8s_sa_has_token_secret`. Cách dùng hiện có với K8s không thay đổi. |
| `{source_rolebound_clusterrole}` | Dùng làm `resource_name` trong các yêu cầu K8s `clusterroles` với `api_group: rbac.authorization.k8s.io` và `namespace: "*"`. Mỗi phương án thay thế cần có `escalate` và `update` hoặc `patch` trên cùng tên đó. Mục tiêu phải là `k8s_service_account` với `scope: same_namespace` và `selector.k8s_sa_in_namespace: "{target.namespace}"`; RoleBinding phải bind nguồn trong namespace đó. |

## Xác thực và đồng bộ hóa

Trước khi gửi thay đổi, hãy chạy `python scripts/validate_privesc_paths.py --book-root .` khi đã cài PyYAML. Lệnh này kiểm tra bố cục thư mục, mọi mục bằng strict loader của evaluator (`scripts/privesc_paths_schema.py`, bản sao của mô-đun schema Blue-CloudPEASS), các id duy nhất, trang nguồn và heading anchor, đồng thời kiểm tra JSON Schema đã được cập nhật chưa. Dùng `--peaso-root /path/to/Blue-CloudPEASS` để so sánh từng byte của cả hai tệp schema với consumer. Quy trình pull request của cuốn sách cũng chạy cùng bước xác thực này.

Vào mỗi thứ Hai, Blue-CloudPEASS checkout phiên bản `master` hiện tại của cuốn sách, xác thực các tệp này và so sánh SHA-256 hash của từng tệp với hash được ghi nhận trong lần đồng bộ trước. Các tệp được thêm, cập nhật hoặc xóa ở upstream sẽ thay thế bản sao trong consumer nếu bản sao đó chưa bị chỉnh sửa. Tệp bị thay đổi ở cả hai phía sẽ được báo là xung đột, và các id kỹ thuật không bao giờ bị xóa nếu không có ledger được xem xét rõ ràng. Nội dung không hợp lệ hoặc kiểm thử thất bại sẽ khiến nhánh mặc định của consumer không thay đổi. Các thay đổi không liên quan trong cuốn sách sẽ không tạo commit trong consumer.
{{#include ../banners/hacktricks-training.md}}
