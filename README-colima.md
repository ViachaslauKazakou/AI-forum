# Colima Docker Setup Guide

This document provides instructions for setting up and using Colima as a lightweight Docker Desktop alternative on macOS.

## What is Colima?

Colima is a container runtime on macOS (and Linux) with minimal setup. It provides Docker functionality without the overhead of Docker Desktop, making it a popular choice for developers who want a simpler, more resource-efficient solution.

## Installation

### Prerequisites

Make sure you have Homebrew installed on your macOS system.

### Install Colima and Docker CLI

```bash
# Install Colima
brew install colima

# Install Docker CLI (if not already installed)
brew install docker

# Optional: Install Docker Compose
brew install docker-compose
```

## Basic Usage

### Start Colima

```bash
# Start with default settings (2 CPUs, 2GB RAM)
colima start

# Start with custom resources
colima start --cpu 4 --memory 8 --disk 60

# Start with specific VM type (default is QEMU)
colima start --vm-type vz --cpu 4 --memory 8
```

### Check Status

```bash
# Check if Colima is running
colima status

# List all Colima instances
colima list
```

### Stop Colima

```bash
# Stop the default instance
colima stop

# Stop and delete the instance
colima delete
```

## Configuration Options

### Resource Configuration

When starting Colima, you can specify various resources:

```bash
colima start \
  --cpu 4 \
  --memory 8 \
  --disk 100 \
  --arch x86_64 \
  --vm-type vz
```

**Parameters:**
- `--cpu`: Number of CPUs (default: 2)
- `--memory`: Memory in GB (default: 2)
- `--disk`: Disk size in GB (default: 60)
- `--arch`: Architecture (x86_64, aarch64)
- `--vm-type`: VM type (qemu, vz - Virtualization.framework)

### VM Types

- **QEMU** (default): More compatible, works on Intel and Apple Silicon
- **VZ** (Virtualization.framework): Faster on Apple Silicon, requires macOS 13+

## Docker Commands

Once Colima is running, you can use standard Docker commands:

```bash
# Check Docker version
docker version

# Run a test container
docker run hello-world

# Build an image
docker build -t my-app .

# Run a container
docker run -p 8080:80 nginx

# Use Docker Compose
docker-compose up -d
```

## Project-Specific Setup

For the AI-forum project, here's how to use Colima:

### 1. Start Colima with Adequate Resources

```bash
# Start with enough resources for the AI-forum project
colima start --cpu 4 --memory 6 --disk 80
```

### 2. Build and Run the Project

```bash
# Navigate to project directory
cd /path/to/AI-forum

# Build the Docker image
docker build -t ai-forum .

# Or use Docker Compose
docker-compose up -d
```

### 3. Check Running Containers

```bash
# List running containers
docker ps

# Check logs
docker logs <container-name>
```

## Advanced Configuration

### Custom Colima Configuration

Create a configuration file at `~/.colima/default/colima.yaml`:

```yaml
# Colima configuration
cpu: 4
memory: 6
disk: 80
arch: aarch64
runtime: docker
kubernetes:
  enabled: false
  version: v1.25.4+k3s1
network:
  address: true
  dns: []
  dnsHosts: {}
vmType: vz
rosetta: false
mountType: sshfs
provision: []
sshConfig: true
mounts: []
env: {}
```

### Port Forwarding

Colima automatically handles port forwarding for Docker containers. If you need custom port forwarding:

```bash
# Start with port forwarding
colima start --network-address
```

### Volume Mounts

By default, Colima mounts your home directory. For custom mounts:

```bash
# Mount additional directories
colima start --mount /custom/path:/vm/path:w
```

## Troubleshooting

### Common Issues

#### Issue: Docker command not found after Colima start

**Solution:**
```bash
# Make sure Docker CLI is installed
brew install docker

# Check if Docker context is set correctly
docker context ls
docker context use colima
```

#### Issue: Performance issues

**Solution:**
```bash
# Stop current instance
colima stop

# Start with more resources
colima start --cpu 4 --memory 8 --vm-type vz
```

#### Issue: Port binding problems

**Solution:**
```bash
# Start Colima with network address
colima start --network-address

# Check if ports are properly exposed
docker port <container-name>
```

#### Issue: Volume mounting not working

**Solution:**
```bash
# Check mount configuration
colima status

# Restart with proper mounts
colima stop
colima start --mount /your/local/path:/container/path:w
```

#### Issue: Docker Buildx plugin missing (fork/exec error)

**Problem:** 
```
fork/exec /Users/username/.docker/cli-plugins/docker-buildx: no such file or directory
```

**Solution:**
```bash
# Install missing Docker Buildx plugin
brew install docker-buildx

# Configure Docker to find CLI plugins
mkdir -p ~/.docker
jq '. + {"cliPluginsExtraDirs": ["/usr/local/lib/docker/cli-plugins"]}' ~/.docker/config.json > ~/.docker/config.json.tmp && mv ~/.docker/config.json.tmp ~/.docker/config.json

# If jq is not installed, manually edit ~/.docker/config.json and add:
# "cliPluginsExtraDirs": ["/usr/local/lib/docker/cli-plugins"]
```

#### Issue: Docker-compose version warning

**Problem:**
```
WARN: the attribute `version` is obsolete, it will be ignored
```

**Solution:**
Remove the `version: '3.8'` line from your docker-compose.yml file. Modern Docker Compose doesn't require version specification.

### Reset Colima

If you encounter persistent issues:

```bash
# Stop and delete current instance
colima stop
colima delete

# Start fresh
colima start --cpu 4 --memory 6
```

## Performance Tips

### Optimize for Development

```bash
# Use VZ for better performance on Apple Silicon
colima start --vm-type vz --cpu 4 --memory 6

# Enable Rosetta for x86 compatibility (Apple Silicon only)
colima start --vm-type vz --arch x86_64 --cpu 4 --memory 6
```

### Resource Monitoring

```bash
# Check resource usage
colima status

# Monitor Docker resource usage
docker stats
```

## Comparison with Docker Desktop

| Feature | Colima | Docker Desktop |
|---------|---------|----------------|
| Resource Usage | Lightweight | Heavy |
| Startup Time | Fast | Slow |
| Cost | Free | Free/Paid |
| GUI | CLI only | GUI + CLI |
| Kubernetes | Optional | Built-in |
| Updates | Manual | Automatic |

## Integration with IDEs

### VS Code

Colima works seamlessly with VS Code Docker extension. Make sure Docker context is set to `colima`:

```bash
docker context use colima
```

### JetBrains IDEs

Configure Docker settings to use the Colima socket:
- Docker socket: `unix:///Users/$USER/.colima/default/docker.sock`

## Useful Commands

```bash
# Quick status check
colima status

# View Colima logs
colima logs

# SSH into Colima VM
colima ssh

# Edit Colima VM
colima edit

# Get VM IP address
colima ssh -- ip addr show eth0

# Check available templates
colima template
```

## Environment Variables

Set these in your shell configuration:

```bash
# For Colima Docker socket
export DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock"

# For Docker Compose
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1
```

## Additional Resources

- [Colima GitHub Repository](https://github.com/abiosoft/colima)
- [Colima Documentation](https://github.com/abiosoft/colima/blob/main/docs/FAQ.md)
- [Docker CLI Documentation](https://docs.docker.com/engine/reference/commandline/cli/)

---

## Project Context

This guide is specifically tailored for the AI-forum project to provide a lightweight Docker alternative to Docker Desktop on macOS systems.
