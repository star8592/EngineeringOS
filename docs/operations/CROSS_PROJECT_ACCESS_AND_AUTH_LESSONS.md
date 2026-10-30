# 跨项目访问、登录与远程操作：唯一经验手册（v1.0）

**状态：跨项目通用规范；2026-10-30 建立。维护仓库：EngineeringOS。**

> 这不是凭据库。**不保存任何密码、私钥、商户密钥、Cookie、OAuth Token、完整连接串、个人身份信息或内部生产机清单。** 项目自己的授权清单、环境配置及实际证据保留在其受控位置。此文档是操作方法的唯一权威来源；项目根 `AGENTS.md` 只放链接、当地补充约束和已验证的入口，禁止复制完整手册产生冲突。

## 0. 必须执行的启动协议（所有工程、所有会话）

任何涉及 SSH、DevControl/Zoria/Next 设备、生产部署、Chrome、第三方登录、Google/微信 OAuth、支付或带权限的数据写入，在尝试登录/修复之前都按下表执行：

| 步骤 | 必须回答 | 证据/产物 |
| --- | --- | --- |
| **A. 明确对象** | 是哪个 **产品**、哪个 **环境**、哪个 **服务器/设备**、哪个 **账号或授权主体**？历史服务与新服务是否共用域名？ | 项目仓库 + 运行/发布文档，记录目标来源与核对时间 |
| **B. 查历史成功路径** | 项目 `AGENTS.md`/部署手册/已有 GitHub issue 中最后一次成功的登录是什么方式？现在的主分支与生产 SHA 是什么？ | **已验证目标**、SSH alias、工具 channel，不猜 IP/端口 |
| **C. 判身份与授权** | SSH 免密？OAuth 用户授权？设备已审批？Agent 在线？工具执行可用？这些彼此不是同一个状态 | 明确 `authorized / online / execution_ready` 等独立事实 |
| **D. 先只读试探** | 现成连接器的 `check_ssh`、`list_devices`、只读状态/API/健康检查能否成功？ | 返回原始状态、时间、限制；**不碰生产密钥** |
| **E. 分类失败** | 错误来自 SSH identity、Host alias、执行 sandbox、OAuth、域名 DNS、应用登录态、API 许可，还是业务代码？ | 错误码 + 针对性假设 + **一次**最短无副作用复验 |
| **F. 有证据再写入** | 是否拥有目标上的写权限及用户授权？是否已有备份/回滚？变更真的针对根因吗？ | 隔离分支、测试、实际服务端或平台回执、回滚凭证 |
| **G. 经验闭环** | 发现了什么新规律？此前哪些结论已经过时？能否写成回归测试？ | 更新本手册或项目补充，关联 issue/PR 与证据 |

**默认策略：最短有效路径 = 查历史成功配置 → 只读原路复验 → 定点排错 → 如确有必要再变更。** 不因为某一次连接失败重新设计身份认证、安装工具、改服务器权限或新建平行系统。

## 1. SSH 免密登录事故：`Too many authentication failures`

**已发生的真实事故模式（2026-10-30，SOCTHINK）**：

- 历史 ThinkAI 部署代码和 SSH 配置存在**已配置的主机别名**。但先前操作根据另一个项目中出现的裸 IP 去尝试，得到 `Too many authentication failures`，错误地被当成整个项目无法免密访问的阻塞。
- 后续在**同一台已授权的 Z890 设备**、通过原有连接器，用历史主机别名执行 `check_ssh`，得到了 **connected=true**；直接使用后端 IP 仍失败。
- **结论**：目标误归属 / SSH Host 匹配与身份选择错误，比“服务器根本没配免密”更有证据。**成功的免密握手不等于已经执行了远程命令，也不等于登录到了正确的业务容器/生产环境。**
- 后续远程执行工具单独返回安全阻断，不代表 SSH 连接失败；属于另一层授权或执行限制，不能用绕过保护来“修 SSH”。

**配套只读预检**（可选、不是新发布门禁）：`python3 scripts/ssh_alias_safe_preflight.py <项目已验证的Host别名> --project-root <项目根目录>`。工具只运行本地 `ssh -G` 并输出匿名化诊断结果，不发起 SSH 连接、不展示用户名/IP/IdentityFile 路径/私钥内容；它只能诊断配置，不能代替实际握手、主机校验或业务验收。**注意：OpenSSH 读取受信任 SSH config 时可能执行已有的 `Match exec` 条件，不能对未经信任的外部配置运行预检。**

**以后唯一正确排查顺序：**

1. 在**目标项目**的发布手册、历史验收和 SSH config 中定位 **上次成功的主机别名**（`Host`），不要从相邻项目抄裸 IP。辨别网页生产主机、License 主机、代理主机及边缘节点。
2. 用 `ssh -G <alias>` 在**原执行身份与权限上下文**中本地检查最终解析出的 `hostname`、`user`、`identityfile`、`identitiesonly`、`proxyjump`、`port` 和 config/include 链。过滤任何不应进入日志的信息，不将该输出上传公开仓库。
3. 通过已经授权的 DevControl/Zoria **SSH 检查能力**优先 `check_ssh(target=<alias>)`，比较结果与同 IP 直连。保留标准的 host key 验证。
4. 如果确实是 SSH 客户端向服务器提交了过多身份，应在**现有正确 Host stanza 或已批准调用参数**中选择正确已有 IdentityFile + `IdentitiesOnly yes`，而不是新造私钥、重置口令、清空 `~/.ssh`、关闭 StrictHostKeyChecking 或频繁重试。
5. 连接成功后先确认返回的是**目标服务**而非仅 `hostname`：服务名、反向代理路由、发布 SHA、运行目录和只读健康端点必须相互印证。
6. 若 `check_ssh` 成功但 `execute_ssh` 被授权/安全策略阻止：记录 `SSH_CONNECTED / EXECUTION_NOT_AUTHORIZED`，停止越权替代方法；不把它写成“服务器故障”。

**一条铁则：先问“我用的是不是这个项目上次成功的 Host alias 和身份？”再问“SSH 要不要修”。**

## 2. 执行上下文 ≠ 宿主机上下文

- DevControl 或 Zoria 的某些泛用 shell 是单 UID / user namespace 的受限执行环境：`nobody:nogroup`、某个 symlink 看似 `0777`、`sudo` 失败或 Chrome sandbox 报错，**不自动证明宿主机权限坏了**。
- 遵循 [Zoria execution context contract](https://github.com/star8592/zoria-control/blob/main/docs/operations/EXECUTION_CONTEXT_CONTRACT.md) 和该仓的 `AGENTS.md`；通过**专用的、已授权的设备/SSH/浏览器接口**执行对应任务。不得用 `chmod 777`、`chown`、关闭 sandbox、绕过执行安全检查来做“修复”。
- 远程操作渠道的状态需要分开记录：设备 enrolled、owner approved、agent online、execution_ready、tool scope allowed、命令实际完成、业务功能经过独立验证。前面成立不推导后面成立。
- 已被拒绝的工具操作不应通过偷偷换协议或另一台机器绕开限制。需要恢复授权、检查 scope 或使用显式允许的专用能力。

## 3. Web / OAuth / 小程序登录态：不要反复注册或误认登录成功

### 用户登录与设备授权是两个流程

- Google OAuth 的用户身份、开发者的商户后台登录、DevControl 设备审批、Agent 的机器登记、MCP 插件的 OAuth scope、业务角色权限，**必须分别验证**；不要把一个页面显示“Approved”推导为 Agent 在线或可以执行工具。
- `login` 成功要经过**重定向后服务端 session readback**、真正的用户菜单变化、刷新页面保持、跨页面导航、过期后可靠续期；回调仅返回 200 或浏览器显示邮箱不够。
- 出现“已登录但导航仍写登录/注册”或“点击后又要求 Google 登录”：优先核对同一 cookie 域、`SameSite`、`Secure`、跨子域回调、后端 session 持久化、刷新/撤销策略、UI 状态订阅，而非给用户重复创建账号。
- 对微信 Web / 公众号 / 小程序，OpenID 随 AppID 不同，UnionID 也须满足官方关联条件；不能按昵称、手机号局部匹配或客户端回报 OpenID 直接合并身份、家庭学籍或购买权益。
- 认证修复验收需覆盖：首次登录、回调、刷新、关闭重开、重新进入、不同设备、退出、失效、权限不足、离线重试、返回原目标页、多个账号切换，并核对实际 session 生效时长。

### 浏览器控制

- 已有用户浏览器会话/已批准 Chrome CDP/AT-SPI 才是默认路径。若 Chrome 提示授权远程调试，不能把用户必须点击的授权提示当成无人值守成功。
- 使用现有 session 工具及其权限；不要绕过 Chrome remote-debugging consent、启动 `--no-sandbox` 或抢占用户主浏览器。
- 必须记录**在何处用户有实际交互义务**；自动化仅在真验收可执行时宣称全自动。

## 4. 支付与第三方 API：登录成功不等于能够收款

- 商户证书/私钥、平台公钥、APIv3 Key、AppID、商户号、微信/支付宝产品准入、回调 URL、交易账本分别核对；公钥证书不等于商户签名私钥。不要从旧聊天、Google Doc 示例直接复制“看起来可用”的生产密钥。
- 历史某版本真实付款成功，是强证据，但**不等于当前代码/环境还在承接**。先找真实交易（非 mock）和订单状态 `pending→paid` + 权益变更的脱敏回执，再定位当前主机及环境的回调路由。
- 网站微信 Native、微信内 Web JSAPI、微信小程序虚拟支付、支付宝 Page/WAP 是**不同产品权限和交互协议**。一个成功不代表其它自动获批。
- 应用密钥放在访问受控的 secret/环境装载中，**不写到仓库、AGENTS、工作日志、Chat、二维码转发站点或浏览器前端**。需要时仅返回存在性、格式、公私钥匹配/证书序列验证布尔值、有效期分级及官方授权状态；避免打印原始配置值。
- 提供旧支付代码的成功实现供评估，但在新旧系统切换时只允许**一个权威订单/权益结算通道**，不能两套同时扣费、重复发放权益；高风险变更先隔离，强制退款/对账/幂等测试。

## 5. 诊断证据与误判规则

在 issue / 工程记录中使用统一事实标签：

| 状态 | 意义 |
| --- | --- |
| `HISTORIC_SUCCESS` | 旧版本有经验证真实成功证据，但非当前可用证明 |
| `CONFIG_FOUND` | 找到配置项/密钥路径；不是密钥有效或商户授权 |
| `SSH_CONNECTED` | 免密 SSH 握手成功，**不是远程命令已执行** |
| `TARGET_VERIFIED` | SSH 目标与所需业务环境、服务与部署 SHA 一致 |
| `AUTH_GRANTED` | 当前会话/设备/渠道得到实际授权 |
| `EXECUTION_BLOCKED` | 已到工具层，但 scope/安全执行不允许 |
| `TEST_PASS` | 指定测试通过；不是生产可用 |
| `DEPLOYED` | 当前生产发布的工件/版本经独立核实 |
| `E2E_VERIFIED` | 用户完整业务流 + 服务端证据及异常分支通过 |
| `UNKNOWN` | 未查到证据，**不能写成不存在、已坏或已完成** |

**禁止互相替代**：SSH 连通、Nginx 200、回调签名正确、代码合并、真正收款、退款成功和用户可用都是不同维度的事实。

## 6. 故障分类与下一步（一次只试最有根据的一条）

| 现象 | 先查什么 | 绝对不要做什么 |
| --- | --- | --- |
| `Too many authentication failures` | 上次成功 alias、`ssh -G`、有效 IdentityFile 与 `IdentitiesOnly` | 立即归因密码错误、暴力重试、关 host key 校验 |
| `Permission denied (publickey)` | 执行身份、SSH 配置作用域、服务器允许的公钥、授权是否撤销 | 用错项目密钥或将私钥复制进聊天 |
| `nobody:nogroup` / SSH 配置变 `0777` | userns、symlink 目标权限、专用执行通道 | 宿主机 `chown/chmod 777` |
| OAuth 成功后重登 | callback、cookie 域、session persistence、角色权限、UI 状态 | 再建一套登录/永久高权限 token |
| Device approved but agent not ready | enrollment、signed registration、heartbeats、tool grant | 反复让用户批准或修改生产数据库 |
| Chrome remote debugging consent | 现有受控浏览器通道、用户授权窗口 | 禁 sandbox 或跳过人类同意 |
| 支付配置齐全但不能支付 | 商户产品授权、真实签名与查单、notify、订单状态 | mock 成功伪装真支付、客户端 paid=true 授权 |
| 某一个命令被安全阻断 | 精确哪个操作/工具限制、是否可由授权只读接口完成 | 换未获授权方式或放宽安全限制 |
| 公网 404/200 与预期不一致 | 反向代理/域名/环境、实际 SHA、缓存/路由 | 直接重部署到猜测的服务器 |

## 7. 所有项目如何使用本手册

每个仓库根 `AGENTS.md` 必须有**一个**显式锚点：

```markdown
## 跨项目连接与认证强制预检
涉及 SSH、远程执行、浏览器、OAuth、微信/支付宝、部署或凭据前，
先阅读 [EngineeringOS 跨项目访问认证经验手册](https://github.com/star8592/EngineeringOS/blob/main/docs/operations/CROSS_PROJECT_ACCESS_AND_AUTH_LESSONS.md)。
此仓库专属 AGENTS、部署运行手册与真实证据在本项目内保留。中央通用规则不覆盖任何授权与隔离限制。
```

- **读取顺序**：当前项目根 `AGENTS.md` → 中央本文件 → 项目部署/认证/支付 runbook → 最新成功验收/事故证据 → 只读操作。读不到中央文档时标记 `RUNBOOK_UNAVAILABLE`，不要假称读过；可先继续完全无害的离线工作。
- 新项目初始化模板默认加入上述锚点。旧项目只做文档入口增补，不覆盖其已有 `AGENTS.md`、独立主机/Agent 配置、部署门禁或凭据。
- 每次新事件先核对是否已有同类事故。若原因新且可迁移，就更新**同一中央文档**（revision、证据链接、有效性边界、回归步骤）；具体地址/密钥/服务器清单放在各项目的受保护配置，不进入这个公共模板。
- 每次发布/登录失败的复盘要记录：`project / target-environment / symptom / verified cause / successful channel / evidence-state / regression-check / unresolved`，但只记录可安全分享的字段。
- 机器可执行门禁由项目 CI / smoke tests / issue 回执负责；**文档链接不是成功登录或用户真正可用的证据**。
- 每隔一段时间用维护脚本盘点仓库根是否有锚点；盘点输出缺失清单并创建修复事项，不能把盘点完成冒充已部署到每个项目。

## 8. 历史实例索引（不含主机地址或私密凭据）

| 事件 | 真实纠偏 | 复发预防 |
| --- | --- | --- |
| 2026-10-30 SOCTHINK SSH 连接误判 | 用错项目的裸 IP 得失败；原项目别名 `check_ssh` 成功 | 每次先按**项目成功别名**连接；区分 SSH 检查与执行授权 |
| 2026-10-30 微信支付旧代码被忽略 | 2026-06-16 旧 ThinkAI 已有真实扫码/回调修复验收；当前 Next 商业链未必承接 | 查所有历史工作目录和验收，而非仅查当前仓库；历史成功 ≠ 当前上线 |
| 2026-10 中旬 DevControl 授权/设备登记 | Google OAuth 会话与设备 approval、signed Agent registration 不应混为同一步 | OAuth/Agent/Owner 授权分别验收 |
| 2026-10 Zoria 受限运行上下文 | userns 文件权限表象不是宿主机真实损坏 | 先读项目执行上下文 doctor，再决定是否允许 host 修复 |
| Chrome 调试授权频繁出现 | 浏览器会话可能需要明确的人类授权，自动流程不能默默绕过 | 现有授权 session 优先，出现 consent 记录阻断点 |

## 9. CI 通过但生产一直是旧 SHA：不应归因 SSH 或缓存（2026-10-30）

**SOCTHINK 真实根因与验证**：GitHub main 已更新，生产 `git ls-remote origin main` 也确认了新 SHA，但自动发布脚本仍报告 `AUTO_DEPLOY=CURRENT`，继续运行旧版本。生产使用 `git fetch origin main` 并随后读取 `origin/main`；在某些仓库 fetch refspec 配置下，显式 fetch 更新 `FETCH_HEAD`，却**不保证**远程跟踪引用 `origin/main` 同步更新。

**正式规则**：在成功执行 `git fetch origin main` 后，使用 `git rev-parse --verify 'FETCH_HEAD^{commit}'` 作为此次实际 fetch 的目标 SHA，而不是直接读取可能过时的 tracking ref。继续针对该精确 SHA 验证官方 CI-green、不可变构建、smoke、回滚和公网 release 回执。不可为了“赶快上线”跳过 CI 或手工给部署元数据写一个假 SHA。

**可复验回归**：SOCTHINK `scripts/test_git_fetch_head_precedence.py` 用纯本地 bare Git 复现 `origin/main` 仍旧、`FETCH_HEAD` 已新，证明错误判断源头。相关修复 [SOCTHINK PR #161](https://github.com/star8592/Kangaroo-Practice-Simulator/pull/161)。相同故障不仅影响支付，所有自动拉取发布项目都应检查此类 stale-ref 判断。

**SSH 救援关联**：不得以 `-F /dev/null` 绕开上次成功的 SSH Host 配置；显式使用正确项目的 Host alias/身份。凡日常自动发布器自身需要修复，使用项目**已有规范化手动恢复发布入口**来更新正式 runner，不在生产服务器叠补丁或启动平行发布路径。记录目标 `TARGET_SHA`、运行 `deployedSha`、CI SHA 三者分别核对。

## 10. 安全、更新和覆盖范围

- 此中央文档**不授予**访问权、项目读写权、商户后台签约权或生产部署权；不改变用户授权、工具安全规则及项目独立性。
- 更新须经过正常工程流程，并在本文件保持一个当前版本。不要每次事故新开重复手册，也不要让旧聊天概述覆盖经过证据核实的新结论。
- 成功不是“已写文档”：成功 = 所有**活跃仓库入口已关联**、跨项目项目初始化/CI 有可验证覆盖、后续实际登录会读入口，且每次事故的技术检查可复验。
