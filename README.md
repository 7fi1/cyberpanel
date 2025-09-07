# 🛠️ CyberPanel

Web Hosting Control Panel powered by OpenLiteSpeed, designed to simplify hosting management.

---

## 🔧 Features & Services

- 🔐 **Different User Access Levels** (via ACLs).
- 🌌 **Auto SSL** for secure websites.
- 💻 **FTP Server** for file transfers.
- 🕒 **Light-weight DNS Server** (PowerDNS).
- 🔐 **phpMyAdmin** to manage databases (MariaDB).
- 📧 **Email Support** (SnappyMail).
- 🕌 **File Manager** for quick file access.
- 🌐 **PHP Management** made easy.
- 🔒 **Firewall** (FirewallD & ConfigServer Firewall Integration).
- 📀 **One-click Backups and Restores**.
- 🐳 **Docker Management** with command execution capabilities.
- 🤖 **AI-Powered Security Scanner** for enhanced protection.

---

## 📖 **Documentation & Guides**

CyberPanel comes with comprehensive documentation and step-by-step guides:

- 📚 **[Complete Guides Index](guides/INDEX.md)** - All available documentation in one place
- 🐳 **[Docker Command Execution](guides/Docker_Command_Execution_Guide.md)** - Execute commands in Docker containers
- 🤖 **[AI Scanner Setup](guides/AIScannerDocs.md)** - Configure AI-powered security scanning
- 📧 **[Mautic Installation](guides/MAUTIC_INSTALLATION_GUIDE.md)** - Email marketing platform setup

---

## 🔢 Supported PHP Versions

CyberPanel supports a wide range of PHP versions across different operating systems:

### ☑️ **Currently Supported PHP Versions**

- **PHP 8.5** - Latest stable version (EOL: Dec 2028)
- **PHP 8.4** - Stable version (EOL: Dec 2027)
- **PHP 8.3** - Stable version (EOL: Dec 2027)
- **PHP 8.2** - Stable version (EOL: Dec 2026)
- **PHP 8.1** - Stable version (EOL: Dec 2025)
- **PHP 8.0** - Legacy support (EOL: Nov 2023)
- **PHP 7.4** - Legacy support (EOL: Nov 2022)

### 🔧 **Third-Party PHP Add-ons**

For additional PHP versions or specific requirements, you can install third-party packages:

#### **Ubuntu/Debian**

- **Ondrej's PPA**: Provides PHP 5.6 to 8.5
- **Sury's PPA**: Alternative repository with latest PHP versions

#### **RHEL-based Systems** (AlmaLinux, RockyLinux, CentOS, RHEL)

- **Remi Repository**: Comprehensive PHP package collection
- **EPEL Repository**: Additional packages for enterprise Linux

#### **CloudLinux**

- **CloudLinux PHP Selector**: Built-in tool for managing multiple PHP versions
- **Remi Repository**: Additional PHP versions and extensions

> **Note**: Third-party repositories may provide additional PHP versions beyond what's available in default repositories. Always verify compatibility with your specific use case.

---

## 🌐 Supported Operating Systems

CyberPanel runs on x86_64 architecture and supports the following operating systems:

### **✅ Currently Supported**

- **Ubuntu 22.04** - Supported until April 2027
- **Ubuntu 20.04** - Supported until April 2025
- **AlmaLinux 10** - Active support until May 2030, security support until May 2035
- **AlmaLinux 9** - Supported until May 2032
- **AlmaLinux 8** - Supported until May 2029
- **RockyLinux 9** - Supported until May 2032
- **RockyLinux 8** - Supported until May 2029
- **RHEL 9** - Supported until May 2032
- **RHEL 8** - Supported until May 2029
- **CloudLinux 8** - Supported until May 2029
- **CentOS 9** - Supported until May 2027

### **🔧 Third-Party OS Support**

Additional operating systems may be supported through third-party repositories or community efforts:

- **Debian** - May work with Ubuntu-compatible packages
- **openEuler** - Community-supported with limited testing
- **Other RHEL derivatives** - May work with AlmaLinux/RockyLinux packages

> **Note**: For unsupported operating systems, compatibility is not guaranteed. Always test in a non-production environment first.

---

## ⚙️ Installation Instructions

Install CyberPanel easily with the following command:

```bash
sh <(curl https://cyberpanel.net/install.sh || wget -O - https://cyberpanel.net/install.sh)
```

---

## 📊 Upgrading CyberPanel

Upgrade your CyberPanel installation using:

```bash
sh <(curl https://raw.githubusercontent.com/usmannasir/cyberpanel/stable/preUpgrade.sh || wget -O - https://raw.githubusercontent.com/usmannasir/cyberpanel/stable/preUpgrade.sh)
```

---

## 📚 Resources

- 🌐 [Official Site](https://cyberpanel.net)
- ✏️ [Docs (Old)](https://docs.cyberpanel.net)
- 🎓 [Docs (New)](https://community.cyberpanel.net/docs)
- 📖 [Additional Guides](guides/INDEX.md) - Detailed guides for Docker, AI Scanner, Mautic, and more
- 📚 [Local Documentation](guides/) - All guides available in this repository
- ✅ [Changelog](https://community.cyberpanel.net/t/change-logs/161)
- 💬 [Forums](https://community.cyberpanel.net)
- 📢 [Discord](https://discord.gg/g8k8Db3)
- 📵 [Facebook Group](https://www.facebook.com/groups/cyberpanel)
- 🎥 [YouTube Channel](https://www.youtube.com/@Cyber-Panel)

### 📖 **Quick Start Guides**

- 🐳 [Docker Command Execution](guides/Docker_Command_Execution_Guide.md) - Execute commands in Docker containers
- 🤖 [AI Scanner Setup](guides/AIScannerDocs.md) - Configure AI-powered security scanning
- 📧 [Mautic Installation](guides/MAUTIC_INSTALLATION_GUIDE.md) - Email marketing platform setup
- 📚 [All Guides Index](guides/INDEX.md) - Complete documentation hub

### 🔗 **Direct Guide Links**

| Feature     | Guide                                                      | Description                    |
| ----------- | ---------------------------------------------------------- | ------------------------------ |
| 🐳 Docker   | [Command Execution](guides/Docker_Command_Execution_Guide.md) | Execute commands in containers |
| 🤖 Security | [AI Scanner](guides/AIScannerDocs.md)                         | AI-powered security scanning   |
| 📧 Email    | [Mautic Setup](guides/MAUTIC_INSTALLATION_GUIDE.md)           | Email marketing platform       |
| 📚 All      | [Complete Index](guides/INDEX.md)                             | Browse all available guides    |
