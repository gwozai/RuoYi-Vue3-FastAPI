-- 密钥ID菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('密钥ID', 0, 1, 'notify_key', 'admin/notify_key/index', 1, 0, 'C', '0', '0', 'admin:notify_key:list', '#', 'admin', NOW(), '', NULL, '密钥ID菜单');

-- 按钮权限
SET @parentId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('密钥ID查询', @parentId, 1, '', '', 1, 0, 'F', '0', '0', 'admin:notify_key:query', '#', 'admin', NOW(), '', NULL, ''),
('密钥ID新增', @parentId, 2, '', '', 1, 0, 'F', '0', '0', 'admin:notify_key:add', '#', 'admin', NOW(), '', NULL, ''),
('密钥ID修改', @parentId, 3, '', '', 1, 0, 'F', '0', '0', 'admin:notify_key:edit', '#', 'admin', NOW(), '', NULL, ''),
('密钥ID删除', @parentId, 4, '', '', 1, 0, 'F', '0', '0', 'admin:notify_key:remove', '#', 'admin', NOW(), '', NULL, ''),
('密钥ID导出', @parentId, 5, '', '', 1, 0, 'F', '0', '0', 'admin:notify_key:export', '#', 'admin', NOW(), '', NULL, '');
