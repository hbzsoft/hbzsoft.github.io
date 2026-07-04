> 从 v2.2 到 v3.0，我们带来了 **TLS 传输加密**、**X25519 密钥自动轮换**、**不可逆账户冻结**、**流量混淆** 和 **现代气泡 UI**。隐私，更进一步。

---

## 引言

你是否想过，你和朋友在微信、QQ 上的聊天内容，理论上可以被平台随时查看？端到端加密（E2EE）正是为了解决这个问题而存在的 —— 只有通信的双方能够解密消息，即使是服务器也无法读取。

出于对隐私保护的执着，我开发了 **KaleidoTalk** —— 一款完全开源的端到端加密聊天软件。V3.0 版本在安全性和可用性上实现了飞跃，新增多项关键防护机制。

项目官网：[https://kaleidotalk.hanbangze.tech](https://kaleidotalk.hanbangze.tech)  
GitHub 仓库：[https://github.com/hbzsoft/KaleidoTalk](https://github.com/hbzsoft/KaleidoTalk)

---

## ⚠️ 法律提示及免责声明

KaleidoTalk 是一个开源的端到端加密聊天软件，**仅供技术学习和合法用途**。作者不运营任何公开的 KaleidoTalk 服务器。如果您计划在公网部署本软件，请自行确保符合所在地法律法规。详细的合规声明请参阅 [COMPLIANCE.md](https://kaleidotalk.hanbangze.tech/COMPLIANCE.md)。

---

## ✨ V3.0 新增亮点（基于真实代码对比）

| 特性 | V2.2（基线） | V3.0（新增强） |
| :--- | :--- | :--- |
| **传输加密** | 明文 TCP + JSON 长度头 | **TLS 1.2+ 自签名证书** + TOFU 信任 |
| **密钥轮换** | 固定 X25519 密钥（生命周期内不变） | X25519 密钥每 **24 小时自动轮换**，支持多版本共存 |
| **账户冻结** | 无 | **不可逆冻结**（凭恢复密钥），被盗后永久锁定 |
| **流量混淆** | 固定大小 JSON 包（长度头） | 所有包固定 **2048 字节** + 随机填充 + 随机心跳（3.3–6.7s） |
| **GUI 界面** | 传统 Ctk 文本框聊天 | **现代气泡聊天 UI**（头像、未读红点、深色主题、托盘闪烁） |
| **配置管理** | 硬编码参数 | 服务端 `config.json` + 客户端持久化配置 |
| **管理员工具** | `admin.py`（邀请码/封禁） | 新增 `freeze_account.py` 独立冻结工具 |
| **测试覆盖** | 无集成测试 | 包含端到端集成测试（密钥轮换、冻结流程） |

> **注意**：V2.2 已具备 **Ed25519+X25519+AES-GCM 加密**、**双模式私钥存储**（服务器托管 / 本地）、**BIP39 指纹单词验证**、**离线消息**、**DoS 防护** 和 **邀请码注册**，这些基础能力在 V3.0 中保留并增强。

---

## 🧩 功能概览（V3.0）

| 功能 | 说明 |
| :--- | :--- |
| **端到端加密** | Ed25519 + X25519 + AES-256-GCM，消息仅收发双方可解密 |
| **密钥自动轮换** | 每天生成新的 X25519 密钥，历史消息不受未来密钥泄露影响 |
| **不可逆账户冻结** | 注册时生成恢复密钥，账户被盗后可永久冻结，任何人无法解冻 |
| **双模式私钥存储** | 服务器加密托管（跨设备登录）或完全本地存储（永不离开设备） |
| **TLS + TOFU 信任** | 传输层 TLS 加密，首次连接时显示 BIP39 单词验证证书指纹，无 CA 依赖 |
| **流量混淆** | 固定包长 + 随机填充 + 随机心跳，抵抗流量分析 |
| **用户指纹验证** | 通过 BIP39 单词核对好友身份，防止中间人攻击 |
| **离线消息队列** | 用户上线后自动接收离线期间的消息 |
| **IP / 用户封禁** | 管理员可封禁恶意 IP 或用户，支持临时 / 永久 |
| **DoS 防护** | 注册 / 登录频率限制，自动封禁异常 IP |
| **现代 GUI** | 基于 CustomTkinter 的气泡聊天界面，支持深色主题、系统托盘、任务栏闪烁 |

---

## 🔐 核心加密协议（V3.0 增强）

V3.0 在原有加密体系上加入了 **密钥轮换** 和 **TLS**：

| 组件 | 算法 | 用途 |
| :--- | :--- | :--- |
| 身份密钥 | Ed25519 | 数字签名，验证消息发送者身份 |
| 密钥交换 | X25519 | ECDH 协商共享密钥（支持多版本） |
| 对称加密 | AES-256-GCM | 消息加密，同时提供认证 |
| 密钥派生 | HKDF-SHA256 | 从 ECDH 共享密钥派生 AES key 和 nonce |
| 密码存储 | PBKDF2-SHA256 (600k 迭代) | 服务端存储密码哈希 |
| 传输层 | TLS 1.2+（自签名证书） | 保护客户端与服务器之间的通信，防止窃听 |

### 消息加密流程（V3.0）

1. **发送方**生成临时 X25519 密钥对
2. ECDH 与**接收方最新公钥**（根据 `key_id` 选择）协商共享密钥
3. HKDF 派生 AES key 和 nonce
4. AES-256-GCM 加密消息
5. 使用发送方的 Ed25519 私钥对（临时公钥 + 密文 + tag）签名
6. 将加密包（携带 `key_id`）通过 TLS 发送给服务器
7. 服务器转发给接收方（TLS 加密通道）
8. **接收方**根据 `key_id` 找到对应的历史 X25519 私钥，验证签名并解密

### 密钥轮换机制

- 客户端启动后检查上次轮换时间，若超过 24 小时则自动生成新 X25519 密钥对。
- 新密钥加密后上传服务器，并用 Ed25519 签名认证。
- 服务器保留最近多个密钥版本，确保旧消息仍可解密。
- 轮换过程对用户完全透明。

### 账户冻结机制

- 注册时生成 Ed25519 恢复密钥对（私钥保存在本地 `local_keys/<username>_recovery.priv`）。
- 若账户被盗，用户可使用恢复密钥签名一条冻结指令发送给服务器。
- 服务器验证签名后，将账户标记为 `frozen`，并强制踢出所有在线会话。
- **该操作不可逆**，服务器管理员也无法解冻。

---

## 🏗️ 工程实现与架构解析（V3.0）

### 整体架构

仍采用经典的 C/S 模型，但 V3.0 增加了 **TLS 传输加密** 和 **覆盖流量** 模块：

```
[客户端A] <--TLS + 固定包--> [服务器] <--TLS + 固定包--> [客户端B]
```

- **服务器**：用户认证、消息转发、离线存储，无法解密消息内容
- **客户端**：密钥管理、加密/解密、信任库、自动轮换

### 模块划分（V3.0 新增）

```
KaleidoTalk/
├── run_client.py          # 客户端入口
├── run_server.py          # 服务端入口
├── admin.py               # 管理员脚本（邀请码、封禁）
├── freeze_account.py      # 独立账户冻结工具  ← 新增
├── reset.bat              # 重置脚本
├── src/
│   ├── client/
│   │   ├── chat_client.py  # 客户端核心逻辑（含轮换、冻结）
│   │   └── chat_gui.py     # 现代气泡 UI
│   ├── server/
│   │   ├── config.py       # 配置文件加载  ← 新增
│   │   ├── server.py       # 服务器主循环（TLS + 覆盖流量）
│   │   ├── server_commands.py  # 命令处理（含 rotate_key, freeze_account）
│   │   ├── server_session.py   # 会话管理、DoS
│   │   └── server_storage.py   # 数据持久化
│   ├── common/
│   │   ├── crypto_utils.py     # 加密原语
│   │   ├── padding.py          # 固定包协议（分片、重组、心跳）← 新增
│   │   └── network.py          # 旧版长度头协议（兼容）
├── test/                  # 集成测试  ← 新增
└── requirements.txt
```

### 通信协议（V3.0 升级：覆盖流量）

V3.0 引入 `padding.py`，所有数据包封装为 **2048 字节** 固定长度：

- **包格式**：`[1字节类型][2字节长度][2字节序号][2字节总数][变长数据][随机填充]`
- **分片与重组**：支持大数据分片发送和接收端重组
- **心跳**：每隔 3.3~6.7 秒发送纯填充包，保持流量模式恒定
- **目的**：有效抵抗基于包大小和发送时序的流量分析

### 服务端新增特性

- **TLS 自签名证书**：启动时自动生成，TOFU 信任模型
- **配置文件**：`config.json` 可设置主机、端口、安全参数、日志级别等
- **密钥轮换支持**：处理 `rotate_key` 命令，存储多版本密钥
- **账户冻结**：处理 `freeze_account` 命令，验证恢复签名并冻结

### 客户端新增特性

- **自动密钥轮换**：定时任务检查并执行轮换
- **恢复密钥保存**：注册时生成 `.priv` 文件并提示备份
- **现代 GUI**：气泡消息、头像、未读红点、右键菜单、托盘闪烁

---

## 🚀 快速上手指南（V3.0）

### 环境要求

- Python 3.8+
- 依赖：`cryptography`, `pystray`, `Pillow`, `customtkinter`

### 下载与安装

```bash
git clone https://github.com/hbzsoft/KaleidoTalk.git
cd KaleidoTalk
pip install -r requirements.txt
```

### 启动服务器

```bash
python run_server.py
```

首次启动设置管理员密码（用于保护服务器私钥）。启动后，TLS 证书自动生成，日志显示服务器指纹。

### 启动客户端

```bash
python run_client.py
```

- 点击「连接」，输入服务器地址（默认 `127.0.0.1:5555`）
- 首次连接会弹出 **TLS 证书的 6 个 BIP39 单词**，请通过安全渠道与管理员确认，然后「信任」
- 注册账号（用户名 3-20 位字母数字，密码至少 8 位含字母数字）
- 注册成功后，系统提示保存恢复密钥（重要！）
- 登录后即可与在线用户聊天

### 管理员命令（V3.0）

```bash
# 邀请码管理
python admin.py invites add --count 5 --uses 1 --length 8
python admin.py invites set-require true
python admin.py invites list

# 封禁管理
python admin.py ban ip 192.168.1.10 --duration 3600
python admin.py unban ip 192.168.1.10
python admin.py ban user alice
python admin.py list-bans

# 用户管理
python admin.py users list
python admin.py users delete alice
```

### 紧急冻结账户

```bash
python freeze_account.py --server 127.0.0.1:5555 --username alice --recovery-key local_keys/alice_recovery.priv
```

**警告**：此操作不可逆，请确认后再执行。

---

## 🧪 技术亮点（V3.0）

1. **传输加密 + 覆盖流量**：TLS 保护信道，固定包和心跳掩盖元数据
2. **密钥生命周期管理**：自动轮换，多版本共存，降低泄露影响
3. **用户自救机制**：不可逆冻结，为极端情况提供最后防线
4. **去中心化信任**：TOFU + BIP39 单词，无需 CA
5. **工程完备性**：配置文件、集成测试、独立冻结工具、完整文档

---

## 📅 未来计划

- [ ] 文件传输（分块加密）
- [ ] 群聊（组密钥分发）
- [ ] 音视频通话（WebRTC）
- [ ] 移动端客户端

---

## 📄 许可证与致谢

KaleidoTalk 采用 **GNU General Public License v3.0** 开源。

第三方库致谢：

- [cryptography](https://cryptography.io/) - 加密算法 (Apache 2.0)
- [pystray](https://github.com/moses-palmer/pystray) - 系统托盘 (LGPLv3)
- [Pillow](https://python-pillow.org/) - 图像处理 (MIT 衍生)
- [CustomTkinter](https://customtkinter.tomschimansky.com/) - 现代 GUI (MIT)

---

**让我们一起，把隐私权还给每个人。**

— Bangze Han, 2026
