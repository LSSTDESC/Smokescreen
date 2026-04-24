## Building the JOSS paper PDF locally

Requires Docker. From the repo root:

```bash
docker run --rm \
    --platform linux/amd64 \
    --volume $PWD/paper:/data \
    --user $(id -u):$(id -g) \
    --env JOURNAL=joss \
    openjournals/inara
```

> **ARM64 users (Apple Silicon, AWS Graviton, etc.):** the `openjournals/inara` image is AMD64-only. The `--platform linux/amd64` flag enables emulation via Docker's QEMU layer. The build will succeed but will be slower than on a native AMD64 host.

The compiled `paper.pdf` will appear in `./paper/`.
