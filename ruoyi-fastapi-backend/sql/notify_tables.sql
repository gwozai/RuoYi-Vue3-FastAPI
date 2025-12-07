-- 通知服务数据库表
-- 执行此SQL创建通知服务所需的表

-- 1. 通知平台表
CREATE TABLE IF NOT EXISTS notify_platform (
    platform_id     BIGINT          NOT NULL AUTO_INCREMENT    COMMENT '平台ID',
    platform_name   VARCHAR(50)     NOT NULL                   COMMENT '平台名称',
    platform_code   VARCHAR(50)     NOT NULL                   COMMENT '平台编码',
    platform_icon   VARCHAR(255)    DEFAULT ''                 COMMENT '平台图标',
    webhook_template VARCHAR(500)   NOT NULL                   COMMENT 'Webhook模板',
    request_method  VARCHAR(10)     DEFAULT 'POST'             COMMENT '请求方式',
    content_type    VARCHAR(50)     DEFAULT 'application/json' COMMENT '内容类型',
    body_template   TEXT                                       COMMENT '请求体模板',
    status          CHAR(1)         DEFAULT '0'                COMMENT '状态(0正常 1停用)',
    order_num       INT             DEFAULT 0                  COMMENT '排序',
    create_by       VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
    create_time     DATETIME                                   COMMENT '创建时间',
    update_by       VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
    update_time     DATETIME                                   COMMENT '更新时间',
    remark          VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
    PRIMARY KEY (platform_id),
    UNIQUE KEY uk_platform_code (platform_code)
) ENGINE=InnoDB AUTO_INCREMENT=1 COMMENT='通知平台表';

-- 2. 通知渠道表（用户的Webhook配置）
CREATE TABLE IF NOT EXISTS notify_channel (
    channel_id      BIGINT          NOT NULL AUTO_INCREMENT    COMMENT '渠道ID',
    user_id         BIGINT          NOT NULL                   COMMENT '用户ID',
    platform_id     BIGINT          NOT NULL                   COMMENT '平台ID',
    channel_name    VARCHAR(100)    NOT NULL                   COMMENT '渠道名称',
    webhook_key     VARCHAR(255)    NOT NULL                   COMMENT 'Webhook密钥',
    webhook_url     VARCHAR(500)    DEFAULT ''                 COMMENT '完整Webhook地址',
    is_default      CHAR(1)         DEFAULT '0'                COMMENT '是否默认(0否 1是)',
    status          CHAR(1)         DEFAULT '0'                COMMENT '状态(0正常 1停用)',
    last_used_time  DATETIME                                   COMMENT '最后使用时间',
    use_count       INT             DEFAULT 0                  COMMENT '使用次数',
    create_by       VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
    create_time     DATETIME                                   COMMENT '创建时间',
    update_by       VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
    update_time     DATETIME                                   COMMENT '更新时间',
    remark          VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
    PRIMARY KEY (channel_id),
    KEY idx_user_id (user_id),
    KEY idx_platform_id (platform_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 COMMENT='通知渠道表';

-- 3. 通知API密钥表（用户调用密钥，类似Server酱的SCKEY）
CREATE TABLE IF NOT EXISTS notify_key (
    key_id          BIGINT          NOT NULL AUTO_INCREMENT    COMMENT '密钥ID',
    user_id         BIGINT          NOT NULL                   COMMENT '用户ID',
    key_name        VARCHAR(100)    NOT NULL                   COMMENT '密钥名称',
    api_key         VARCHAR(64)     NOT NULL                   COMMENT 'API密钥',
    channel_ids     VARCHAR(500)    DEFAULT ''                 COMMENT '绑定渠道ID(逗号分隔)',
    daily_limit     INT             DEFAULT 100                COMMENT '每日限额',
    daily_used      INT             DEFAULT 0                  COMMENT '今日已用',
    total_count     INT             DEFAULT 0                  COMMENT '总调用次数',
    last_used_time  DATETIME                                   COMMENT '最后使用时间',
    last_reset_date DATE                                       COMMENT '最后重置日期',
    status          CHAR(1)         DEFAULT '0'                COMMENT '状态(0正常 1停用)',
    expire_time     DATETIME                                   COMMENT '过期时间',
    create_by       VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
    create_time     DATETIME                                   COMMENT '创建时间',
    update_by       VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
    update_time     DATETIME                                   COMMENT '更新时间',
    remark          VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
    PRIMARY KEY (key_id),
    UNIQUE KEY uk_api_key (api_key),
    KEY idx_user_id (user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 COMMENT='通知API密钥表';

-- 4. 通知发送记录表
CREATE TABLE IF NOT EXISTS notify_log (
    log_id          BIGINT          NOT NULL AUTO_INCREMENT    COMMENT '日志ID',
    user_id         BIGINT                                     COMMENT '用户ID',
    key_id          BIGINT                                     COMMENT 'API密钥ID',
    channel_id      BIGINT                                     COMMENT '渠道ID',
    platform_id     BIGINT                                     COMMENT '平台ID',
    title           VARCHAR(200)    DEFAULT ''                 COMMENT '消息标题',
    content         TEXT                                       COMMENT '消息内容',
    msg_type        VARCHAR(20)     DEFAULT 'text'             COMMENT '消息类型',
    request_data    TEXT                                       COMMENT '请求数据',
    response_data   TEXT                                       COMMENT '响应数据',
    status          CHAR(1)         DEFAULT '0'                COMMENT '状态(0成功 1失败)',
    error_msg       VARCHAR(500)    DEFAULT ''                 COMMENT '错误信息',
    ip_address      VARCHAR(50)     DEFAULT ''                 COMMENT 'IP地址',
    send_time       DATETIME                                   COMMENT '发送时间',
    cost_time       INT             DEFAULT 0                  COMMENT '耗时(毫秒)',
    create_time     DATETIME                                   COMMENT '创建时间',
    PRIMARY KEY (log_id),
    KEY idx_user_id (user_id),
    KEY idx_key_id (key_id),
    KEY idx_send_time (send_time)
) ENGINE=InnoDB AUTO_INCREMENT=1 COMMENT='通知发送记录表';

-- 5. 初始化平台数据
INSERT INTO notify_platform (platform_name, platform_code, platform_icon, webhook_template, request_method, content_type, body_template, status, order_num, create_by, create_time, remark) VALUES
('飞书', 'feishu', 'feishu', 'https://open.feishu.cn/open-apis/bot/v2/hook/{key}', 'POST', 'application/json', '{"msg_type":"text","content":{"text":"{content}"}}', '0', 1, 'admin', NOW(), '飞书机器人Webhook'),
('企业微信', 'wecom', 'wecom', 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}', 'POST', 'application/json', '{"msgtype":"text","text":{"content":"{content}"}}', '0', 2, 'admin', NOW(), '企业微信机器人Webhook'),
('钉钉', 'dingtalk', 'dingtalk', 'https://oapi.dingtalk.com/robot/send?access_token={key}', 'POST', 'application/json', '{"msgtype":"text","text":{"content":"{content}"}}', '0', 3, 'admin', NOW(), '钉钉机器人Webhook');

-- 6. 通知服务菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('通知服务', 0, 10, 'notify', '', 1, 0, 'M', '0', '0', '', 'message', 'admin', NOW(), '', NULL, '通知服务目录');

SET @notifyDirId = LAST_INSERT_ID();

-- 通知平台菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('通知平台', @notifyDirId, 1, 'platform', 'notify/platform/index', 1, 0, 'C', '0', '0', 'notify:platform:list', '#', 'admin', NOW(), '', NULL, '通知平台菜单');

SET @platformMenuId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('通知平台查询', @platformMenuId, 1, '', '', 1, 0, 'F', '0', '0', 'notify:platform:query', '#', 'admin', NOW(), '', NULL, ''),
('通知平台新增', @platformMenuId, 2, '', '', 1, 0, 'F', '0', '0', 'notify:platform:add', '#', 'admin', NOW(), '', NULL, ''),
('通知平台修改', @platformMenuId, 3, '', '', 1, 0, 'F', '0', '0', 'notify:platform:edit', '#', 'admin', NOW(), '', NULL, ''),
('通知平台删除', @platformMenuId, 4, '', '', 1, 0, 'F', '0', '0', 'notify:platform:remove', '#', 'admin', NOW(), '', NULL, '');

-- 通知渠道菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('我的渠道', @notifyDirId, 2, 'channel', 'notify/channel/index', 1, 0, 'C', '0', '0', 'notify:channel:list', '#', 'admin', NOW(), '', NULL, '通知渠道菜单');

SET @channelMenuId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('通知渠道查询', @channelMenuId, 1, '', '', 1, 0, 'F', '0', '0', 'notify:channel:query', '#', 'admin', NOW(), '', NULL, ''),
('通知渠道新增', @channelMenuId, 2, '', '', 1, 0, 'F', '0', '0', 'notify:channel:add', '#', 'admin', NOW(), '', NULL, ''),
('通知渠道修改', @channelMenuId, 3, '', '', 1, 0, 'F', '0', '0', 'notify:channel:edit', '#', 'admin', NOW(), '', NULL, ''),
('通知渠道删除', @channelMenuId, 4, '', '', 1, 0, 'F', '0', '0', 'notify:channel:remove', '#', 'admin', NOW(), '', NULL, ''),
('通知渠道测试', @channelMenuId, 5, '', '', 1, 0, 'F', '0', '0', 'notify:channel:test', '#', 'admin', NOW(), '', NULL, '');

-- API密钥菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('API密钥', @notifyDirId, 3, 'key', 'notify/key/index', 1, 0, 'C', '0', '0', 'notify:key:list', '#', 'admin', NOW(), '', NULL, 'API密钥菜单');

SET @keyMenuId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('API密钥查询', @keyMenuId, 1, '', '', 1, 0, 'F', '0', '0', 'notify:key:query', '#', 'admin', NOW(), '', NULL, ''),
('API密钥新增', @keyMenuId, 2, '', '', 1, 0, 'F', '0', '0', 'notify:key:add', '#', 'admin', NOW(), '', NULL, ''),
('API密钥修改', @keyMenuId, 3, '', '', 1, 0, 'F', '0', '0', 'notify:key:edit', '#', 'admin', NOW(), '', NULL, ''),
('API密钥删除', @keyMenuId, 4, '', '', 1, 0, 'F', '0', '0', 'notify:key:remove', '#', 'admin', NOW(), '', NULL, ''),
('API密钥重置', @keyMenuId, 5, '', '', 1, 0, 'F', '0', '0', 'notify:key:reset', '#', 'admin', NOW(), '', NULL, '');

-- 发送记录菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('发送记录', @notifyDirId, 4, 'log', 'notify/log/index', 1, 0, 'C', '0', '0', 'notify:log:list', '#', 'admin', NOW(), '', NULL, '发送记录菜单');

SET @logMenuId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('发送记录查询', @logMenuId, 1, '', '', 1, 0, 'F', '0', '0', 'notify:log:query', '#', 'admin', NOW(), '', NULL, ''),
('发送记录删除', @logMenuId, 2, '', '', 1, 0, 'F', '0', '0', 'notify:log:remove', '#', 'admin', NOW(), '', NULL, '');
