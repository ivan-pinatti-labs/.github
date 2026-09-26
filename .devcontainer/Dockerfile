# Development container for this repository: everything its hooks need, on
# top of the organization's shared base image. See .devcontainer/README.md for
# how to start it and why each run argument is there.
#
# The base image is pinned by digest. BASE_IMAGE is a build argument only so a
# change to the base image can be tested against this repository before it is
# published.
ARG BASE_IMAGE=ghcr.io/ivan-pinatti-labs/devcontainer-base@sha256:79139cb9b646e8a3f8e18ac466f44afdd88c87d30422baa15d16a125a66d755e
FROM ${BASE_IMAGE}

USER 0:0

# pre-commit from Ubuntu's own archive. This repository's hooks need nothing
# else: it holds the organization profile and shared configuration, not code.
#
# Versions are deliberately unpinned, which makes this layer rolling rather
# than reproducible: the digest above fixes what this builds on and says
# nothing about what apt resolves on top. See the base image's
# docs/TOOL_SOURCES.md.
# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get install -y --no-install-recommends pre-commit \
  && rm -rf /var/lib/apt/lists/*

USER 1000:1000

WORKDIR /workspace
