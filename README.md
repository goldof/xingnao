# 醒脑 Xingnao

<img src="xingnao-logo-brain-512.png" width="128" alt="醒脑 logo" />

每天一段大白话思维训练：基于行为经济学、博弈论与演化心理学的 30 条科学机制（每条带出处），日积月累强化思维；附 6 大决策框架（博弈锚定、说服框架、沉没成本止损、认知摩擦跨越、反刍打断、反共识引擎）供随时调用。纯科学，不搞心灵鸡汤。

## 仓库内容

- `SKILL.md` — skill 本体（6 大模块、晨间段子模式、用户设置、改版与免责）
- `references/TOPICS.md` — 30 条主题库，每条带科学机制出处
- `references/INSTALL.md` — 安装说明
- `templates/` — `sent_log.json` / `user_prefs.json` 初始模板
- `LICENSE` — MIT

## 安装

1. 把本仓库放入你的 AI 智能体的 skills 目录；
2. 初始化 `~/.xingnao/`：把 `templates/` 下的两个 json 复制过去（已有历史的不覆盖；运行时状态只读写 `~/.xingnao/`，永不写 skill 目录）；
3. 建一个每日定时任务：按 `SKILL.md`「晨间段子模式」生成今日段子，追加 sent_log，并推送给用户。

详见 `references/INSTALL.md`。

## 版本

- v0.2.0（当前）— 30 条全科学主题库、6 模块轮换、每日流程防重样、内容安全 6 条

历史版本见 [Releases](../../releases)。WorkBuddy SkillHub：v0.2.0 审核中。

## 许可与署名

MIT 许可（见 LICENSE）。转发每篇段子时请保留末尾署名行"——醒脑 · goldof 的思维训练"。
