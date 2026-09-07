FROM rust:1.89-bookworm@sha256:948f9b08a66e7fe01b03a98ef1c7568292e07ec2e4fe90d88c07bb14563c84ff AS mdbook-builder

ENV CARGO_TARGET_DIR=/tmp/cargo-target

RUN cargo install --locked mdbook --version 0.5.3 \
    && cargo install --locked mdbook-alerts --version 0.8.0 \
    && cargo install --locked mdbook-reading-time --version 0.2.0 \
    && cargo install --locked mdbook-pagetoc --version 0.3.0 \
    && cargo install --locked mdbook-tabs --version 1.0.4 \
    && cargo install --locked mdbook-codename --version 0.0.1

FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

LABEL org.opencontainers.image.source="https://github.com/HackTricks-wiki/hacktricks-cloud"
LABEL org.opencontainers.image.description="Pinned mdBook translation and deployment environment for HackTricks"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        awscli \
        bash \
        ca-certificates \
        curl \
        gh \
        git \
        gzip \
        jq \
        wget \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --no-cache-dir \
        openai==3.6.0 \
        tiktoken==0.14.0 \
        tqdm==4.70.0

COPY --from=mdbook-builder /usr/local/cargo/bin/mdbook /usr/local/bin/mdbook
COPY --from=mdbook-builder /usr/local/cargo/bin/mdbook-alerts /usr/local/bin/mdbook-alerts
COPY --from=mdbook-builder /usr/local/cargo/bin/mdbook-reading-time /usr/local/bin/mdbook-reading-time
COPY --from=mdbook-builder /usr/local/cargo/bin/mdbook-pagetoc /usr/local/bin/mdbook-pagetoc
COPY --from=mdbook-builder /usr/local/cargo/bin/mdbook-tabs /usr/local/bin/mdbook-tabs
COPY --from=mdbook-builder /usr/local/cargo/bin/mdbook-codename /usr/local/bin/mdbook-codename

RUN python --version \
    && aws --version \
    && gh --version \
    && mdbook --version \
    && mdbook-alerts --version \
    && test -x "$(command -v mdbook-reading-time)" \
    && test -x "$(command -v mdbook-pagetoc)" \
    && test -x "$(command -v mdbook-tabs)" \
    && test -x "$(command -v mdbook-codename)"

WORKDIR /app
