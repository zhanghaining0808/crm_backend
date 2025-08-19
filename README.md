# user (用户)
- int id
- str name (普通用户)
- str passwd (用户密码)
- bool is_admin (管理员)
- datetime created_at 
- datetime updated_at
- datetime last_login (最后登录时间)

# customer(客户)
- int id
- str name
- str email
- bool is_email_black(黑名单)
- list[str] tags (客户标签)
- datetime created_at (创建时间)
- datetime updated_at (更新客户时间)

# email(邮件)
- int id
- int user_id
- int customer_id
- str title (主题)
- str content (内容)
- datetime created_at

# email task(邮件任务)
- int id
- list[int] customer_ids(客户id)
- bool status (状态)
- bool is_success(完成情况)
- datetime created_at

# System Settings (系统设置)
- 