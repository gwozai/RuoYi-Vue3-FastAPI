-- 渠道ID菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('渠道ID', 0, 1, 'notify_channel', 'admin/notify_channel/index', 1, 0, 'C', '0', '0', 'admin:notify_channel:list', '#', 'admin', NOW(), '', NULL, '渠道ID菜单');

-- 按钮权限
SET @parentId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('渠道ID查询', @parentId, 1, '', '', 1, 0, 'F', '0', '0', 'admin:notify_channel:query', '#', 'admin', NOW(), '', NULL, ''),
('渠道ID新增', @parentId, 2, '', '', 1, 0, 'F', '0', '0', 'admin:notify_channel:add', '#', 'admin', NOW(), '', NULL, ''),
('渠道ID修改', @parentId, 3, '', '', 1, 0, 'F', '0', '0', 'admin:notify_channel:edit', '#', 'admin', NOW(), '', NULL, ''),
('渠道ID删除', @parentId, 4, '', '', 1, 0, 'F', '0', '0', 'admin:notify_channel:remove', '#', 'admin', NOW(), '', NULL, ''),
('渠道ID导出', @parentId, 5, '', '', 1, 0, 'F', '0', '0', 'admin:notify_channel:export', '#', 'admin', NOW(), '', NULL, '');
