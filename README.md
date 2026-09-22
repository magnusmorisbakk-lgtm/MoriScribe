

# Homelab Server (`moris`) Architecture & Services

## Navigation

* [Tailscale & Networking](docs/tailscale-setup.md): Remote access, exit node setup, and UFW subnet routing configuration.
* [Storage Layout](docs/storage-layout.md): Partition breakdown across NVMe SSD (`/`) and 4TB HDD (`/mnt/hdd`).
* [Infrastructure Overview](docs/infrastructure-overview.md): Global server specs, full port matrix, and system health commands.
*  [Ollama LLM Setup](docs/ollama.md): GPU-accelerated Ollama deployment guide and model management commands.
* [Faster-Whisper STT Setup](docs/whisper.md): OpenAI-compatible speech-to-text API service documentation.

---

##  System Hardware

| Component | Specification |
| :--- | :--- |
| **Host Name** | `moris` |
| **OS / Kernel** | Ubuntu Server (`7.0.0-31-generic`) |
| **GPU Acceleration** | NVIDIA GeForce RTX 2060 (Driver `595.91.07`, CUDA `13.2`) |
|**CPU** | Ryzen 5 3600, 6 cores 12 threads
|**RAM**| 16GB DDR4
| **Tailscale Address** | `100.70.56.80`
| **Local LAN IP** | `192.168.0.179` |

---

## Repository Structure

```text
.
├── README.md
├── docs/
│   ├── infrastructure-overview.md
│   ├── storage-layout.md
│   ├── tailscale-setup.md
│   ├── ollama.md
│   └── whisper.md
└── services/
    ├── ollama/
    │   └── docker-compose.yml
    └── whisper/
        └── docker-compose.yml