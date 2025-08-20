# user (用户)
- int id
- str name (用户名称)
- str email (邮箱)
- str phone (电话)
- str passwd (用户密码)
- is_active (是否激活)
- is_admin (是否为管理员)
- datetime created_at 
- datetime updated_at
- datetime last_login 
# customer(客户)
- int id
- str name
- str email
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