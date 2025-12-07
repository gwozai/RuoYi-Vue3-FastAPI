-- 日志ID菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('日志ID', 0, 1, 'notify_log', 'admin/notify_log/index', 1, 0, 'C', '0', '0', 'admin:notify_log:list', '#', 'admin', NOW(), '', NULL, '日志ID菜单');

-- 按钮权限
SET @parentId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('日志ID查询', @parentId, 1, '', '', 1, 0, 'F', '0', '0', 'admin:notify_log:query', '#', 'admin', NOW(), '', NULL, ''),
('日志ID新增', @parentId, 2, '', '', 1, 0, 'F', '0', '0', 'admin:notify_log:add', '#', 'admin', NOW(), '', NULL, ''),
('日志ID修改', @parentId, 3, '', '', 1, 0, 'F', '0', '0', 'admin:notify_log:edit', '#', 'admin', NOW(), '', NULL, ''),
('日志ID删除', @parentId, 4, '', '', 1, 0, 'F', '0', '0', 'admin:notify_log:remove', '#', 'admin', NOW(), '', NULL, ''),
('日志ID导出', @parentId, 5, '', '', 1, 0, 'F', '0', '0', 'admin:notify_log:export', '#', 'admin', NOW(), '', NULL, '');
