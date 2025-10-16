# BAIHOCDAUTIEN

Ứng dụng dòng lệnh nhỏ giúp bạn theo dõi công việc hằng ngày. Nhiệm vụ
được lưu trong file `tasks.json` và có thể được thêm, liệt kê, đánh dấu
hoàn thành hoặc xoá bỏ.

## Cài đặt

Không cần cài đặt đặc biệt, chỉ cần Python 3.8 trở lên.

## Cách sử dụng

Thêm nhiệm vụ mới (mặc định ngày là hôm nay):

```bash
python daily_tracker.py add "Đọc sách 30 phút"
```

Liệt kê nhiệm vụ của hôm nay:

```bash
python daily_tracker.py list
```

Liệt kê toàn bộ nhiệm vụ:

```bash
python daily_tracker.py list --all
```

Đánh dấu hoàn thành:

```bash
python daily_tracker.py done 1
```

Bỏ đánh dấu hoàn thành:

```bash
python daily_tracker.py done 1 --undone
```

Xoá nhiệm vụ:

```bash
python daily_tracker.py remove 1
```

Có thể chỉ định ngày khác khi thêm hoặc liệt kê bằng định dạng
`YYYY-MM-DD` hoặc từ khoá `today`.
