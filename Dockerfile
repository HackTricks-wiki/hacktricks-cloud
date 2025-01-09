# Use the official Python 3.12 Bullseye image as the base
FROM python:3.12-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    sudo \
    build-essential \
    awscli

# Install Python libraries
RUN pip install --upgrade pip && \
    pip install openai tqdm tiktoken

# Install Rust & Cargo
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install mdBook & plugins
RUN cargo install mdbook
RUN cargo install mdbook-alerts
RUN cargo install mdbook-reading-time
RUN cargo install mdbook-pagetoc
RUN cargo install mdbook-tabs
RUN cargo install mdbook-codename

# Set the working directory
WORKDIR /app

