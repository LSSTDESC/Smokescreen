## Building the JOSS paper PDF locally

Requires Docker. From the repo root:

**Step 1 — register QEMU emulation (required on ARM64 hosts; one-time setup):**

```bash
docker run --privileged --rm tonistiigi/binfmt --install x86_64
```

**Step 2 — build the PDF:**

```bash
docker run --rm \
    --platform linux/amd64 \
    --volume $PWD/paper:/data \
    --user $(id -u):$(id -g) \
    --env JOURNAL=joss \
    openjournals/inara
```

The compiled `paper.pdf` will appear in `./paper/`.

> **Note:** the `openjournals/inara` image is AMD64-only. Step 1 registers QEMU x86_64 emulation so Docker can run it on ARM64 hosts (Apple Silicon, AWS Graviton, etc.). The build will succeed but run slower than on a native AMD64 host. On AMD64 hosts Step 1 is not needed.
