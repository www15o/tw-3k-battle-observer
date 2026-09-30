# 全面战争：三国（3K）官方 Lua 脚本库 API 参考

> 本文档从游戏提取的官方 Lua 脚本库中逐库取证整理（函数名/签名取自源文件，未臆测）。
> 格式：中文说明 + API 函数名/签名（照录）。**官方注解原文与官方文件内容不入库**，本仓库只保留我们自己的说明与 API 事实。

---

## 0. 数据来源

| 项目 | 值 |
|---|---|
| 游戏 | 全面战争：三国（Total War: THREE KINGDOMS，3K） |
| 提取时间 | 2026-08-15 15:19（源目录文件 mtime） |
| 提取工具 | `pfh5_extract.py`（`../extract/tools/pfh5_extract.py`，PFH5 包通用提取器，试探性逆向产物 2026-08，不依赖 RPFM） |
| 源路径 | `../extract/3k/script/_lib/`（15 个核心库 + `mod/` 子目录） |
| 取证方法 | `read`/`grep` 直接读取 `.lua` 源文件：`--- @c`（类）、`--- @function`（方法）、`function xxx:`（定义行）、`--- @desc`（说明） |

**3K 注释风格**：`--- @loaded_in_battle` / `--- @c <name> <标题>` / `--- @section <段名>` / `--- @function <名>` / `--- @desc <说明>` / `--- @p`（参数）/ `--- @r`（返回值）。与 WH3 的 `--- @set_environment` / `--- @a` 风格不同。

---

## 1. 核心库总览（15 个）

| # | 文件名 | 大小(B) | 一行职责 |
|---|---|---|---|
| 1 | `lib_battle_manager.lua` | 134,682 | **battle_manager**：battle 对象 的 Lua 包装，战斗脚本中枢（阶段/单位选择/指令/时间/watches/顾问/相机/UI） |
| 2 | `lib_battle_script_ai_planner.lua` | 45,175 | **script_ai_planner**：脚本 AI 编组——把一队单位交给 AI 半自主执行高层命令（移动/防御/攻击/巡逻） |
| 3 | `lib_battle_script_unit.lua` | 115,295 | **script_unit / script_units / unitcontroller**：脚本单位封装（unit+unitcontroller 组合），单位级移动/士气/弹药/控制权 |
| 4 | `lib_generated_battle.lua` | 163,017 | **generated_battle / generated_army**：生成式战斗系统，消息驱动的军级指令（用于任务战） |
| 5 | `lib_campaign_pending_battle_cache.lua` | 19,244 | **pending_battle_cache**：战役层待定战斗快照缓存（可存档序列化），包装 `query_model:pending_battle()` 查询 |
| 6 | `lib_battle_misc.lua` | 51,734 | 战斗杂项全局工具：向量 `v()`、音效、unitcontroller 创建、溃败/接战/位置判定 |
| 7 | `lib_battle_ui.lua` | 46,490 | **battle_ui_manager**：战斗 UI 高亮/脉冲面板（单位卡、按钮、雷达等 30+ 高亮函数） |
| 8 | `lib_battle_advice.lua` | 58,243 | **advice_manager / advice_monitor**：战斗顾问（advice）播放调度与监视器条件触发 |
| 9 | `lib_battle_cutscene.lua` | 71,092 | **cutscene**：战斗过场（动作队列、cinematic 相机、跳过/恢复相机、字幕） |
| 10 | `lib_battle_patrol_manager.lua` | 37,337 | **patrol_manager / waypoint**：巡逻管理器（waypoint 路径、截击、放弃/完成回调） |
| 11 | `lib_campaign_string_mission.lua` | 9,189 | **string_mission**：战役字符串任务构造（任务文本/目标/触发） |
| 12 | `lib_fe_sequence.lua` | 11,298 | **fe_hb_sequence**：史实战役前端（frontend）序列——图形/顾问演出编排 |
| 13 | `lib_lua_extensions.lua` | 68,382 | Lua 语言参考与扩展：`string.split/trim`、`table.copy/filter/tostring` 等（含 Lua 语法文档） |
| 14 | `lib_mod_loader.lua` | 4,622 | **mod 加载器**：`ModLog()` + `core:load_mods()`/`execute_mods()` 挂载 `mod/` 目录脚本 |
| 15 | `lib_state_machine.lua` | 18,841 | **state_machine**：状态机（add_state/change_to/state_change_listener，供战斗/战役脚本组织流程） |

> 注：`lib_header.lua`（库加载入口）在 3K 中位于 `../extract/3k/script/` 根，不在 `_lib/`；`_lib/` 下另有 `mod/` 目录存放 mod 自定义库。

---

## 2. 重点库详解

### 2.1 lib_battle_manager.lua — battle_manager（战斗管理器）


**创建**：`battle_manager:new(b)`（参数为 `empire_battle:new()` 创建的 battle 代码对象；全程只允许一个实例）；另有全局便捷函数 `get_bm()` 从任意位置取回战斗管理器。

**关键方法（`function battle_manager:` 签名照录）**：

| 分类 | API 原文（签名） | 中文说明 |
|---|---|---|
| 创建 | `function battle_manager:new(b)` | 创建 battle_manager；已存在则返回首个实例 |
| 全局取用 | `function get_bm()`（`--- @function get_bm`） | 全局函数，战斗环境内任意位置获取 battle manager |
| 输出 | `function battle_manager:out(msg)` | 带时间戳向控制台打印调试字符串 |
| 杂项查询 | `function battle_manager:get_tm()` | 直接访问内部 timer_manager |
| | `function battle_manager:get_battle_ui_manager()` | 取 @battle_ui_manager 句柄（未建则创建） |
| | `function battle_manager:get_battle_folder()` | 返回战斗脚本文件夹路径 |
| | `function battle_manager:get_origin()` | 返回世界原点向量 |
| | `function battle_manager:ui_component(component_name)` | 包装 ui_component，返回 UIComponent 对象 |
| | `function battle_manager:is_any_cutscene_running()` | 是否有过场正在播放 |
| | `function battle_manager:is_any_unit_selected()` / `are_all_units_selected()` / `num_units_selected()` | 查询 UI 当前单位选中状态/数量 |
| | `function battle_manager:get_player_alliance_num()` / `get_non_player_alliance_num()` | 玩家/敌方同盟编号 |
| | `function battle_manager:get_player_alliance()` / `get_non_player_alliance()` | 玩家/敌方同盟对象 |
| | `function battle_manager:player_is_attacker()` | 本地玩家是否为进攻方 |
| | `function battle_manager:get_player_army()` / `get_first_non_player_army()` | 玩家军队 / 首个敌方军队 |
| 随机 | `function battle_manager:random_number(max_value)` | 安全（多人可用）随机数：无参返回 0~1 浮点，有参返回 1..max 整数 |
| | `function battle_manager:random_sort(t)` | 随机重排数值索引表（不修改原表，多人安全） |
| 开局/阶段 | `function battle_manager:setup_battle(new_deployment_end_callback)` | 打包的开局设置：抑制单位音效、锁输入焦点，部署阶段结束回调 |
| | `function battle_manager:end_deployment()` | 结束部署阶段 |
| | `function battle_manager:register_phase_change_callback(new_event, new_callback)` | 注册阶段变更回调（Deployment→Deployed→VictoryCountdown→Complete） |
| 单位选择回调 | `function battle_manager:force_unit_selection_handler_active(value)` | 强制单位选择处理器常驻激活 |
| | `function battle_manager:register_unit_selection_callback(unit, callback)` / `unregister_unit_selection_callback(unit)` | 注册/注销单位被选中回调 |
| | `function battle_manager:register_default_unit_selection_handler()` / `unregister_default_unit_selection_handler()` | 注册/注销默认单位选择处理器 |
| 指令回调 | `function battle_manager:register_command_handler_callback(command_name, callback, callback_name)` / `unregister_command_handler_callback(command_name, callback_name)` | 注册/注销指令事件回调 |
| 输入回调 | `function battle_manager:register_input_handler_callback(input_name, callback, callback_name)` / `unregister_input_handler_callback(input_name, callback_name)` | 注册/注销输入事件回调 |
| ESC 键 | `function battle_manager:steal_escape_key_with_callback(name, callback)` | 劫持 ESC 键并注册回调（可多个，后注册者优先） |
| | `function battle_manager:release_escape_key_with_callback(name)` | 按名取消 ESC 回调 |
| 胜利 | `function battle_manager:setup_victory_callback(callback)` | 设置胜利回调并把胜利倒计时设为无限（配合 `end_battle` 手动收尾） |
| | `function battle_manager:end_battle()` | 立即结束战斗 |
| | `function battle_manager:register_results_callbacks(player_victory_callback, player_defeat_callback)` | 旧式战斗结果回调 |
| 时间 | `function battle_manager:slow_game_over_time(start_game_speed, target_game_speed, total_time, steps)` | 游戏速度渐变 |
| | `function battle_manager:pause()` | 暂停战斗 |
| | `function battle_manager:is_historical_mode()` / `is_romance_mode()` | 历史/演义模式判定（3K 特有） |
| 定时器 | `function battle_manager:callback(new_callback, new_time_offset, new_entryname)` | 单次延时回调（推荐） |
| | `function battle_manager:repeat_callback(new_callback, new_time_offset, new_entryname)` | 循环延时回调（推荐） |
| | `function battle_manager:register_singleshot_timer(name, t)` / `register_repeating_timer(name, t)` / `unregister_timer(name)` | 旧式定时器接口（兼容） |
| Watches | `function battle_manager:watch(new_condition, new_time_offset, new_callback, new_entryname)` | 轮询条件监视：条件为真→等待→调用回调 |
| | `function battle_manager:remove_process(key)` | 按名停止/移除 watch 或 callback |
| | `function battle_manager:remove_process_from_watch_list(key)` / `print_watch_list()` / `clear_watches_and_callbacks()` / `set_load_balancing(value)` | watch 维护工具 |
| 顾问 | `function battle_manager:queue_advisor(new_advisor_string, ...)` | 排队顾问台词 |
| | `function battle_manager:stop_advisor_queue(should_close, force_immediate_stop)` / `advice_cease()` / `advice_resume()` / `has_advice_played_this_battle()` / `modify_advice(progress_button, highlight)` | 顾问队列控制 |
| 目标 | `function battle_manager:set_objective(...)` / `complete_objective(...)` / `fail_objective(...)` / `remove_objective(...)` / `activate_objective_chain(...)` / `update_objective_chain(...)` / `end_objective_chain(...)` / `reset_objective_chain(...)` | objectives_manager 透传：脚本化目标/目标链 |
| | `function battle_manager:set_locatable_objective(obj_key, cam_pos, cam_targ, duration)` | 可定位目标：目标列表 + 缩放至战场位置按钮 |
| 信息文本 | `function battle_manager:add_infotext(...)` / `remove_infotext(...)` / `clear_infotext(...)` | infotext 面板透传 |
| 字幕 | `function battle_manager:show_subtitle(key, full_key_supplied, should_force)` / `hide_subtitles()` | 过场字幕显示/隐藏 |
| 帮助消息 | `function battle_manager:queue_help_message(key, duration, fade_time, high_priority, play_after_battle_victory, callback)` | 排队帮助消息（任务战常用） |
| **相机** | `function battle_manager:enable_camera_movement(value)` | **允许/禁止玩家移动相机**（不劫持输入，其他交互仍可用；传 false 禁用） |
| | `function battle_manager:cache_camera()` | 缓存当前相机位置/目标 |
| | `function battle_manager:get_cached_camera_pos()` / `get_cached_camera_targ()` | 取缓存相机位置/目标（须先 cache_camera） |
| 相机跟踪 | `function battle_manager:start_camera_movement_tracker()` / `stop_camera_movement_tracker()` | 相机移动跟踪器启停（教程脚本用） |
| | `function battle_manager:get_camera_altitude_change()` / `get_camera_distance_travelled()` | 相机高度变化 / 总移动距离 |
| Ping 图标 | `function battle_manager:add_ping_icon(pos_x, pos_y, pos_z, ping_type, is_waypoint, rotation, optional_ring_radius)` / `remove_ping_icon(pos_x, pos_y, pos_z)` | 地图 ping 图标增删 |
| | `function battle_manager:add_named_ping_icon(...)` / `add_named_terrain_offset_ping_icon(...)` / `remove_named_ping_icon(name)` / `int_register_ping_data(...)` / `int_deregister_ping_data(name)` / `int_get_ping_data(name, suppress_errors)` | 命名 ping 图标/数据（3K 特有） |
| UI 显隐 | `function battle_manager:show_ui(value)` | 显隐战斗 UI |
| | `function battle_manager:show_army_panel(value, immediate)` / `show_winds_of_magic_panel(value, immediate)` / `show_portrait_panel(value, immediate)` / `show_top_bar(value, immediate)` / `show_radar_frame(value, immediate)` / `show_start_battle_button(value, is_multiplayer)` / `show_ui_options_panel(value)` / `enable_spell_browser_button(value)` / `enable_ui_hiding(value)` / `is_ui_hiding_enabled()` | 各 UI 部件显隐/禁用 |
| 接战监视 | `function battle_manager:start_engagement_monitor()` / `stop_engagement_monitor()` / `engagement_monitor_battle_starts()` | 接战监视器（双方距离/接战比例/火力下比例） |
| | `function battle_manager:get_distance_between_forces()` / `get_num_units_engaged()` / `get_proportion_engaged()` / `get_num_units_under_fire()` / `get_proportion_under_fire()` / `get_player_army_altitude()` / `get_enemy_army_altitude()` | 接战数据查询 |
| 其他 | `function battle_manager:is_land_ambush()` | 是否陆地伏击战 |
| | `function battle_manager:progress_on_loading_screen_dismissed(callback)` | 加载画面关闭回调 |
| | `function battle_manager:enable_cinematic_ui(enable_cinematic_ui, enable_cursor, enable_cinematic_bars)` | 电影式 UI 开关 |

### 2.2 lib_battle_script_ai_planner.lua — script_ai_planner（脚本 AI 编组）


**核心 API（签名照录）**：

| 分类 | API 原文 | 中文说明 |
|---|---|---|
| 创建 | `function script_ai_planner:new(new_name, new_sunits, is_debug)` | 创建编组，传入名称与 @script_units/@script_unit/表；单位随即纳入 AI 控制 |
| 调试 | `function script_ai_planner:set_debug(value)` | 开启/关闭调试输出 |
| 增删单位 | `function script_ai_planner:add_sunits(input)` | 添加单位（须与编组同盟一致） |
| | `function script_ai_planner:remove_sunits(input)` | 移除单位 |
| | `function script_ai_planner:release()` | **移除全部单位并释放控制权给 AI/玩家** |
| 测试 | `function script_ai_planner:any_controlled_sunit_standing()` | 是否有受控单位仍存活/未溃败 |
| | `function script_ai_planner:get_centre_point()` | 所有受控单位的平均中心点向量 |
| **移动** | `function script_ai_planner:move_to_position(pos)` | **命令编组移动到某位置**（取代之前命令） |
| | `function script_ai_planner:move_to_position_of_sunit(sunit, end_callback, reorder, internal)` | 移动到某 @script_unit 位置并跟踪其移动 |
| | `function script_ai_planner:move_to_force(enemy_force, reorder, defend_radius)` | 移动到某军队位置并跟踪 |
| **防御** | `function script_ai_planner:defend_position(pos, radius, reorder)` | **命令编组防御某位置**（radius 决定阵型松紧） |
| | `function script_ai_planner:defend_position_of_sunit(sunit, radius, end_callback, internal)` | 防御某单位位置并跟踪 |
| | `function script_ai_planner:defend_force(enemy_force, radius)` | 防御某军队位置并跟踪 |
| | `function script_ai_planner:set_should_reorder(value)` | 每 30 秒重发防御/移动命令（默认开启，传 false 关闭） |
| **攻击** | `function script_ai_planner:attack_unit(unit, reorder)` | **命令编组攻击某单位**（须为敌军） |
| | `function script_ai_planner:attack_force(enemy_force, reorder)` | **命令编组攻击某军队**（@script_units 或表，须为敌军） |
| 合并 | `function script_ai_planner:merge_into(planner, reorder)` | 编组合并：接近目标编组后移交单位（阈值 120m） |
| **巡逻** | `function script_ai_planner:patrol(waypoint_list, enemy_force, completion_callback, reorder)` | **沿 waypoint 列表巡逻**，沿途发现敌人即接战，敌人远离则恢复巡逻 |
| | `function script_ai_planner:set_patrol_defend_radius(value)` | 每个 waypoint 的防御半径（默认 100m） |
| | `function script_ai_planner:set_patrol_enemy_distance(value)` | 巡逻截击敌人距离阈值（默认 100m） |
| | `function script_ai_planner:set_patrol_waypoint_distance(value)` | 判定抵达 waypoint 的距离（默认 75） |
| | `function script_ai_planner:set_perform_patrol_prox_test(value)` | 巡逻时是否执行敌人邻近测试（默认开启） |

### 2.3 lib_campaign_pending_battle_cache.lua — pending battle 缓存（重点）


**注意**：该库**消费**（而非定义）`query_model:pending_battle()` 上的查询方法；缓存对象把这些查询结果快照并序列化进存档。`pending_battle` 查询原文（源文件内调用取证）：

```lua
local pending_battle = query_model:pending_battle();   -- 取当前待定战斗
o.human_involved = pending_battle:human_involved();    -- 玩家是否参战
pending_battle:attacker_is_stronger()                  -- 攻方是否更强
pending_battle:has_attacker() / pending_battle:attacker():military_force()
pending_battle:secondary_attackers()                   -- 次攻方（list，is_empty()/num_items()/item_at(i)）
pending_battle:has_defender() / pending_battle:defender():military_force()
pending_battle:secondary_defenders()
```

**缓存对象**（`function xxx:` 签名照录）：

| 对象 | API 原文 | 中文说明 |
|---|---|---|
| 顶层 | `function pending_battle_cache:cache_last_pending_battle(query_model)` | 缓存最近一次待定战斗 |
| | `function pending_battle_cache:get_pending_battle_cache()` | 取回缓存 |
| | `function pending_battle_cache:post_load_fixup(saved_cached_battle)` | 读档后重连对象引用 |
| 战斗 | `function pending_battle_cached_battle:new(query_model)` | 从 query_model 构建战斗快照 |
| | `function pending_battle_cached_battle:attacker_commander()` / `defender_commander()` | 攻/防方指挥官 |
| | `function pending_battle_cached_battle:num_attackers()` / `num_defenders()` | 攻/防方军队数 |
| | `function pending_battle_cached_battle:num_attacker_units(exclude_characters)` / `num_defender_units(exclude_characters)` | 攻/防方单位数 |
| | `function pending_battle_cached_battle:num_attacker_unit_key(unit_key)` / `num_defender_unit_key(unit_key)` / `num_faction_unit_key(faction_key, unit_key)` | 按单位 key 计数 |
| | `function pending_battle_cached_battle:num_attacker_unit_class(unit_class)` / `num_defender_unit_class(unit_class)` / `num_faction_unit_class(faction_key, unit_class)` | 按单位类别计数 |
| | `function pending_battle_cached_battle:num_attacker_unit_category(unit_category)` / `num_defender_unit_category(unit_category)` / `num_faction_unit_category(faction_key, unit_category)` | 按单位类型计数 |
| | `function pending_battle_cached_battle:faction_was_involved(faction_key)` / `faction_was_attacker(faction_key)` / `faction_was_defender(faction_key)` | 派系是否参战/攻/防 |
| | `function pending_battle_cached_battle:was_character_in_battle(query_character)` / `was_character_attacker_in_battle(query_character)` / `was_character_defender_in_battle(query_character)` | 人物是否参战/攻/防 |
| 军队 | `function pending_battle_cached_force:new(military_force, is_attacker)` | 军队快照 |
| | `function pending_battle_cached_force:units()` / `characters()` | 单位/人物列表 |
| | `function pending_battle_cached_force:num_units(exclude_characters)` / `num_characters()` / `num_unit_key(unit_key)` / `num_unit_class(unit_class)` / `num_unit_category(unit_category)` | 计数查询 |
| 部曲 | `function pending_battle_retinue:new(query_retinue)` | 部曲快照；`num_units(exclude_characters)` / `num_characters()` / `num_unit_key/class/category` | 计数查询 |
| 人物 | `function pending_battle_cached_character:new(query_character)` | 人物快照 |
| 单位 | `function pending_battle_unit:new(query_unit)` | 单位快照 |

### 2.4 lib_battle_script_unit.lua — script_unit / script_units / unitcontroller


**script_unit 关键方法（签名照录）**：

| 分类 | API 原文 | 中文说明 |
|---|---|---|
| 创建 | `function script_unit:new(new_army, new_ref)` | 新脚本单位；new_ref 为军队内序号（1=将军）或脚本名 |
| 移动 | `function script_unit:goto_start_location(should_run)` / `teleport_to_start_location()` | 前往/传送至初始位置 |
| | `function script_unit:goto_location_offset(x_offset, z_offset, should_run, bearing_deg, should_release)` / `teleport_to_location_offset(x_offset, z_offset, bearing_deg, should_release)` | 前往/传送到偏移位置 |
| | `function script_unit:goto_location_offset_when_deployed(x_offset, z_offset, should_run, bearing, should_release)` | 部署后前往偏移位置 |
| | `function script_unit:turn_to_face(pos)` | 转向面对某位置 |
| | `function script_unit:teleport_to_location(position, bearing, width)` | 传送到绝对位置 |
| 缓存 | `function script_unit:cache_location()` / `get_cached_position()` / `get_cached_bearing()` / `get_cached_width()` / `goto_cached_location(should_run)` / `teleport_to_cached_location()` | 缓存位置及回放 |
| | `function script_unit:cache_destination()` / `cache_destination_and_halt()` / `get_cached_destination_position()` / `get_cached_destination_bearing()` / `get_cached_destination_width()` / `goto_cached_destination(should_release)` | 缓存目的地及回放 |
| 状态 | `function script_unit:has_moved(pos, dist)` / `cache_health(under_attack_check)` / `has_taken_casualties(tolerance, under_attack_check)` / `is_under_attack()` / `is_in_melee()` | 移动/伤亡/受击/近战判定 |
| 指令 | `function script_unit:halt()` / `celebrate()` / `taunt()` / `play_sound_charge()` / `play_sound_taunt()` / `play_vo(sound)` | 单位行为/音效 |
| 行为 | `function script_unit:deploy_reinforcement(value)` | 部署增援 |
| | `function script_unit:change_behaviour_active(behaviour, value, should_release)` | 切换行为（如防御模式） |
| | `function script_unit:withdraw(should_run)` / `set_melee_mode(value, should_release)` | 撤退 / 近战模式 |
| 可见性 | `function script_unit:set_enabled(value)` / `set_always_visible(value)` / `mark_as_ally(value)` / `is_hidden()` / `set_invisible_to_all(visible, update_ui)` / `is_visible_to_enemy()` / `is_active_on_battlefield()` | 启用/可见性/友军标记 |
| **控制权** | `function script_unit:take_control()` | **夺取该单位控制权（脚本接管）** |
| | `function script_unit:release_control()` | **释放控制权（交还 AI/玩家）** |
| 弹药 | `function script_unit:modify_ammo(value)` / `refill_ammo(value)` / `grant_infinite_ammo()` / `cache_ammo()` / `restore_cached_ammo()` | 弹药修改/无限/缓存恢复 |
| 血量 | `function script_unit:unary_hitpoints()` / `max_casualties(proportion, should_release, exception_sunits, silent)` / `fearless_until_casualties(proportion, should_release)` / `rout_on_casualties(unary_proportion)` / `invincible_if_standing(should_release)` / `set_invincible(value)` | 伤亡/士气/无敌操控 |
| | `function script_unit:prevent_rallying_if_routing(perpetual)` / `stop_prevent_rallying_if_routing()` / `morale_behavior_fearless()` / `morale_behavior_rout()` / `morale_behavior_default()` | 士气行为强制 |
| 击杀 | `function script_unit:kill(should_disappear, killer_alliance)` / `kill_proportion(proportion, preserve, hide_bodies)` / `kill_proportion_over_time(proportion, duration, stop_on_rout)` / `stop_kill_proportion_over_time()` | 击杀单位/比例/持续击杀 |
| 其他 | `function script_unit:get_enemy_alliance_num()` / `get_retinue_number()` / `monitor_sunit_selection(selected_callback, deselected_callback)` / `highlight_unit_card(value, pulse_strength, force_highlight)` / `add_ping_icon(icon_type, duration)` / `remove_ping_icon()` | 杂项 |

**script_units 集合**（同文件第二部分，`--- @c script_units`）：`new` / `set_debug` / `add_sunits` / `remove_sunit` / `remove_sunits` / `contains_sunit` / `contains_type` / `count` / `item` / `get_sunit_table` / `filter` / `out` / `duplicate` / **`get_unitcontroller`** / 位置测试（`centre_point` / `radius` / `get_northernmost` / `get_southernmost` / `get_westernmost` / `get_easternmost` / `get_closest` / `get_outlying`）/ 移动与战斗测试（`have_any_moved` / `have_all_moved` / `are_any_running` / `are_all_running` / `is_under_attack` / `is_in_melee` / `unary_hitpoints`）/ `change_formation` / `is_hidden` / `is_visible_to_enemy` / `deploy_at_random_intervals` / `cancel_deploy_at_random_intervals` / `start_kill_aura` / `stop_kill_aura` / `attack_enemy_scriptunits` / `stop_attack_enemy_scriptunits` / `rout_over_time` / `max_casualties` / `have_any_deployed` / `have_all_deployed` / `are_any_active_on_battlefield`。

**unitcontroller 创建工具**（在 `lib_battle_misc.lua`）：`create_unitcontroller(army, ...)` / `unitcontroller_from_army(army)`。

### 2.5 lib_generated_battle.lua — generated_battle / generated_army


**generated_battle**：`new(...)`（screen_starts_black / prevent_deployment_for_player / prevent_deployment_for_ai / intro_cutscene / is_debug）、`set_cutscene_during_deployment`、`has_battle_started`、`get_player_alliance_num`、`get_non_player_alliance_num`、`get_army(script_name, sub_army_num, sunits, is_debug)`（创建 generated_army）、`remove_listener`、`set_victory_countdown_on_message`、`block_message_on_message`。自动发送消息：`deployment_started` / `battle_started` / `battle_ending` / `cutscene_ended` / `generated_custscene_ended` / `outro_camera_finished`。

**generated_army 关键方法（签名照录）**：

| 分类 | API 原文 | 中文说明 |
|---|---|---|
| 创建 | `function generated_army:new(script_name, sub_army_num, sunits, generated_battle, is_debug)` | 创建生成军队 |
| **规划器** | `function generated_army:set_up_script_planner()` | **为军队建立 script_ai_planner**（此后 move/advance/attack/defend 才可用） |
| | `function generated_army:release_control_of_all_sunits()` | **释放全部单位的脚本控制权** |
| 查询 | `function generated_army:get_script_name()` / `get_unitcontroller()` / `get_handicap()` / `get_first_scriptunit()` / `get_first_active_scriptunit()` / `get_most_westerly/easterly/northerly/southerly_scriptunit()` / `get_casualty_rate()` / `get_rout_proportion()` / `get_shattered_proportion()` / `are_unit_types_in_army(...)` | 军队查询 |
| 指令 | `function generated_army:set_visible_to_all(value)` / `set_enabled(value)` / `halt()` / `hold_fire()` / `celebrate()` / `taunt()` / `play_sound_charge()` / `play_sound_taunt()` / `add_ping_icon(icon_type, unit_index, duration)` / `remove_ping_icon(unit_index)` | 行为指令 |
| 移动 | `function generated_army:teleport_to_start_location_offset(x_offset, z_offset)` / `goto_start_location(should_run)` / `goto_location_offset(x_offset, z_offset, should_run)` / `move_to_position(position, no_debug_output)` / `advance(no_debug_output)` | 移动（自动 set_up_script_planner） |
| 战斗 | `function generated_army:attack(no_debug_output)` / `attack_force(enemy_force)` / `defend(x, y, radius, no_debug_output)` / `release(no_debug_output)` | 攻击/防御/释放 |
| 消息监听 | `function generated_army:<xxx>_on_message(message, ...)` | 全套消息监听：`teleport_to_start_location_offset` / `goto_start_location` / `goto_location_offset` / `set_enabled` / `set_formation` / `move_to_position` / `advance` / `attack` / `attack_force` / `defend` / `release` / `reinforce` / `rout_over_time` / `withdraw` / `set_melee_mode` / `change_behaviour_active` / `set_invincible` / `deploy_at_random_intervals` / `grant_infinite_ammo` / `add_ping_icon` / `remove_ping_icon` / `add_winds_of_magic` / `set_always_visible` / `force_victory` / `remove` / `take_control` |
| 消息产生 | `function generated_army:message_on_<条件>(message, ...)` | 条件触发消息：`casualties` / `proximity_to_enemy` / `proximity_to_ally` / `proximity_to_position` / `rout_proportion` / `shattered_proportion` / `deployed` / `any_deployed` / `seen_by_enemy` / `commander_death` / `commander_dead_or_routing` / `commander_dead_or_shattered` / `under_attack` / `alliance_not_active_on_battlefield` / `victory` / `defeat` |

---

## 3. 其余库 API 摘要

### 3.1 lib_battle_misc.lua（全局工具函数）
- 向量：`function v(x, y, z)`（向量构造）
- 音效：`new_sfx(soundfile)` / `play_sound(position, sound)` / `play_sound_2D(sound)` / `stop_sound(sound)`
- Unitcontroller：`create_unitcontroller(army, ...)` / `unitcontroller_from_army(army)`
- 溃败/接战测试：`is_routing_or_dead(obj, shattered_only, permit_rampaging)` / `is_shattered_or_dead(obj, permit_rampaging)` / `num_units_routing(obj, shattered_only, permit_rampaging)` / `num_units_shattered(obj, permit_rampaging)` / `num_units_engaged(obj)` / `num_units_under_fire(obj)` / `rout_all_units(obj)`
- 位置测试：`number_close_to_position(obj, pos, range, two_d, standing_only, return_bool)` / `standing_number_close_to_position(obj, pos, range, two_d)` / `is_close_to_position(obj, pos, range, two_d, standing_only)` / `standing_is_close_to_position(obj, pos, range, two_d)` / `distance_between_forces(a, b, standing_only)` / `get_closest_unit(obj, pos, standing_only, test)` / `get_closest_standing_unit(obj, pos, test)` / `get_average_altitude(obj)`
- 集合测试：`num_units_in_collection(obj)` / `contains_unit(obj, unit)` / `num_units_passing_test(obj, test)` / `get_all_matching_units(obj, test, starting_table)` / `number_alive(obj)` / `is_visible(obj, alliance)` / `has_deployed(obj)`
- 建筑：`print_buildings(start_index, end_index)` / `print_buildings_near(x, y, range)` / `get_building_near(x, y)`

### 3.2 lib_battle_ui.lua — battle_ui_manager（战斗 UI 高亮）
- `battle_ui_manager:new()` / `is_panel_open(panel_name)` / `get_panel_pulse_strength()` / `get_button_pulse_strength()` / `register_unhighlight_callback(callback)` / `unhighlight_all_for_tooltips()` / `set_help_page_link_highlighting_permitted(value)` / `get_help_page_link_highlighting_permitted()` / `highlight_unit_card(uic_card, value, pulse_strength)` / `highlight_retinue(value, index)`
- 30+ 部件高亮（`highlight_xxx(value, pulse_strength, force_highlight)`）：`advice_history_buttons` / `advisor_button` / `advisor` / `army_abilities` / `army_panel` / `balance_of_power` / `drop_equipment_button` / `fire_at_will_button` / `formations_button` / `game_guide_button` / `group_button` / `guard_button` / `lore_panel` / `melee_mode_button` / `power_reserve_bar` / `radar_map` / `realm_of_souls` / `skirmish_button` / `spells` / `tactical_map_button` / `time_controls` / `time_limit` / `unit_abilities` / `unit_cards` / `unit_details_button` / `unit_details_panel` / `unit_portrait_panel` / `winds_of_magic_panel`

### 3.3 lib_battle_advice.lua — advice_manager / advice_monitor
- `advice_manager:new(is_debug, ignore_advice_history)` / `get_advice_manager()` / `set_debug(value)` / `set_advice_enabled(value)` / `register_advice_monitor(advice_monitor)` / `get_advice_monitor(name)`
- `advice_monitor:new(name, priority, advice_key, infotext, duration)` / `set_advice_level(value)` / `set_can_interrupt_other_advice(value)` / `set_can_trigger_on_esc_menu(value)` / `set_delay_before_triggering(value)` / `set_trigger_callback(callback, do_not_trigger_advice)` / `set_halt_callback(callback)` / `set_halt_advice_on_battle_end(value)` / `add_start_condition(condition, event)` / `add_trigger_condition(condition, event)` / `add_halt_condition(condition, event)` / `add_advice_location(vector)` / `get_advice_location()` / `add_context_object(object)` / `get_context_object()` / `add_halt_on_advice_monitor_triggering(monitor_name)` / `add_halt_advice_monitor_on_trigger(monitor_name)` / `start()`

### 3.4 lib_battle_cutscene.lua — cutscene（战斗过场）
- `cutscene:new(name, players_army, cutscene_length, end_callback)` / `new_from_cindyscene(name, players_army, end_callback, cindy_scene, blend_in_duration, blend_out_duration)`
- `set_debug(is_debug, hide_ui_in_debug)` / `enable_debug_timestamps(value)` / `action(new_callback, new_delay, new_is_terminator)` / `cindy_action(xml_path, delay, blend_in_duration, blend_out_duration)` / `add_cinematic_trigger_listener(id, callback)`
- `play_sound(sound)` / `play_vo(sound, sunit)` / `wait_for_advisor()` / `wait_for_vo()` / `subtitles()` / `camera()` / `length()` / `is_playing_sound()` / `is_playing_camera()` / `is_any_cutscene_running()` / `is_active()`
- `set_skippable(skippable, skip_callback)` / `set_skip_camera(skip_cam_pos, skip_cam_target)` / `set_restore_cam(new_time, new_pos, new_targ)` / `set_post_cutscene_fade_time(fade_in_time, fade_in_time_delay)` / `set_post_skip_cutscene_fade_time(...)` / `set_music(music_event, fade_in, fade_out)` / `set_music_resume_auto_playback(new_value)` / `set_relative_mode()` / `set_is_ambush(value, teleport_on_end)` / `set_do_not_end(value)` / `set_should_disable_unit_ids(value)` / `suppress_unit_voices(value)` / `set_should_enable_cinematic_camera(value)` / `set_wait_for_advisor_on_end(value)` / `set_wait_for_vo_on_end(value)` / `set_close_advisor_on_end(value)` / `set_close_advisor_on_start(value)` / `enable_ui_on_end(value)` / `set_call_end_callback_when_skipped(new_value)` / `set_should_release_players_army(new_value)` / `set_show_cinematic_bars(new_value)` / `set_should_hide_ui(new_value)` / `set_steal_input_focus(new_value)` / `set_should_stop_cindy_playback(new_value)`
- `start()` / `show_custom_cutscene_subtitle(key, style, duration, force_display)` / `hide_custom_cutscene_subtitles(immediately)` / `show_esc_prompt(value)` / `skip()` / `finish()` / `restore_camera_and_release(should_cut)` / `release()`
- 全局辅助：`track_unit_commander(unit, movement_speed, tracking_angle_h, tracking_angle_v, tracking_distance, tracking_height, t)` / `predict_commander_position(...)` / `get_tracking_offset(...)` / `get_track_commander_positions(...)`

### 3.5 lib_battle_patrol_manager.lua — patrol_manager / waypoint
- 设置器：`set_intercept_callback` / `set_abandon_callback` / `set_completion_callback` / `set_walk_speed` / `set_rout_callback` / `set_debug` / `set_debug_all` / `set_naval` / `set_stop_on_rout` / `set_stop_on_intercept` / `set_width` / `set_waypoint_threshold` / `set_intercept_time` / `loop(value)` / `set_force_run`
- `add_waypoint(new_dest, new_should_run, new_delay, new_orientation, new_width)` / `start(reason)` / `resume_patrol(reason)` / `restart()` / `stop()` / `complete(reason)` / `intercept()` / `is_enemy_in_range(range)` / `is_in_range_of_patrol_path_segment(range)`
- `waypoint:new(new_pos, new_speed, new_wait_time, new_orient, new_width)`

### 3.6 lib_campaign_string_mission.lua — string_mission（战役字符串任务）
- `string_mission:new(mission_key)` / `set_issuer(issuer_key)` / `set_turn_limit(turn_limit)` / `set_chapter(chapter)` / `add_primary_objective(objective_key, conditions_table, opt_heading_key, opt_description_key)` / `add_primary_payload(payload_string)` / `add_secondary_objective(objective_key, conditions_table, payloads_table, opt_heading_key, opt_description_key)` / `trigger_mission_for_faction(faction_key, whitelist)` / `construct_mission_string()`

### 3.7 lib_fe_sequence.lua — fe_hb_sequence（史实战役前端序列）
- `fe_hb_sequence:new(new_name, new_eh, new_tm, new_end_callback)` / `add_advice(...)` / `add_graphic(new_component, new_fade_in_anim, new_fade_in_time, new_fade_out_anim, new_fade_out_time)` / `contains_graphic(component)` / `play_graphic(component, start_advice, start_advice_time, end_advice, end_advice_time)` / `play(uic)` / `fade_in_graphic(graphic)` / `fade_out_graphic(graphic)` / `play_next()` / `skip()`

### 3.8 lib_lua_extensions.lua（Lua 语言参考 + 扩展）
- 字符串扩展：`string.split(inputstr, separator)` / `string.trim(input_str)` / `string.trim_start(input_str)` / `string.trim_end(input_str)`
- 表扩展：`table.tostring(t, for_campaign_savegame, max_level, tab_level, prepend_tabs, add_line_break)` / `table.contains(t, obj)` / `table.is_empty(t)` / `table.copy(t, previously_copied_tables)` / `table.mem_address(t, leave_punctuation)` / `table.length(t)` / `table.is_array(t)` / `table.filter(t, filter_function)`
- 其余为 Lua 标准库文档（string/math/table 等）

### 3.9 lib_mod_loader.lua（mod 加载器）
- `function ModLog(text)` —— 写 `lua_mod_log.txt` + 控制台
- 机制：`core:load_mods("/script/_lib/mod/", "/script/campaign/" .. CampaignName .. "/mod/")` → `core:execute_mods(context)` → 触发 `ScriptEventAllModsLoaded`；文件内与文件名同名的函数会被执行（类似构造函数）

### 3.10 lib_state_machine.lua — state_machine（状态机）
- `state_machine:new(machine_name, initial_state_key, is_battle_script, on_start_callback)` / `add_state(name, enter_callback, exit_callback, opt_load_state)` / `start()` / `restart()` / `change_to(new_state_name)` / `destroy()` / `state_change_callback(next_state, duration)` / `state_change_listener(next_state, listener_event, listener_condition)` / `state_change_watch(next_state, condition, opt_update_time)` / `get_state_data(state_name)` / `get_state_index(state_name)` / `state_exists(state_name)` / `save()` / `load()`

---

## 4. 备注

1. 3K 的 `script_unit:take_control()` / `release_control()` 是**单位级**控制权接口；`script_ai_planner:release()` 与 `generated_army:release_control_of_all_sunits()` 是**批量**释放接口。
2. `battle_manager:enable_camera_movement(false)` 禁用玩家相机移动但不劫持输入；过场相机移动走 `cutscene`（`set_restore_cam` / `set_skip_camera` 等）。
3. `query_model:pending_battle()` 是引擎代码对象方法，脚本侧通过 `lib_campaign_pending_battle_cache.lua` 快照使用（`human_involved()` / `attacker()` / `defender()` / `secondary_attackers()` / `secondary_defenders()` / `attacker_is_stronger()` 等已在源文件内取证）。
4. `_lib/mod/` 目录用于 mod 自定义库；`lib_header.lua`（3K 位于 `script/` 根）负责按游戏模式装配库。
