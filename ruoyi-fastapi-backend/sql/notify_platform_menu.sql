-- 平台ID菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('平台ID', 0, 1, 'notify_platform', 'admin/notify_platform/index', 1, 0, 'C', '0', '0', 'admin:notify_platform:list', '#', 'admin', NOW(), '', NULL, '平台ID菜单');

-- 按钮权限
SET @parentId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('平台ID查询', @parentId, 1, '', '', 1, 0, 'F', '0', '0', 'admin:notify_platform:query', '#', 'admin', NOW(), '', NULL, ''),
('平台ID新增', @parentId, 2, '', '', 1, 0, 'F', '0', '0', 'admin:notify_platform:add', '#', 'admin', NOW(), '', NULL, ''),
('平台ID修改', @parentId, 3, '', '', 1, 0, 'F', '0', '0', 'admin:notify_platform:edit', '#', 'admin', NOW(), '', NULL, ''),
('平台ID删除', @parentId, 4, '', '', 1, 0, 'F', '0', '0', 'admin:notify_platform:remove', '#', 'admin', NOW(), '', NULL, ''),
('平台ID导出', @parentId, 5, '', '', 1, 0, 'F', '0', '0', 'admin:notify_platform:export', '#', 'admin', NOW(), '', NULL, '');
