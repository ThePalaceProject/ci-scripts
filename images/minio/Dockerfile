# syntax=docker/dockerfile:1.7
#
# Mirror of the upstream MinIO server image, published as
# ghcr.io/thepalaceproject/palace-ci-minio.
#
# Why this exists
# ---------------
# MinIO withdrew anonymous public access to its server image: first from Docker Hub
# (~13 Sept 2026), then from quay.io (~24 Sept 2026). Both registries now answer 401 to
# anonymous manifest requests for every tag, and the binary download host (dl.min.io) answers
# 410. Every Palace repo that ran `FROM <registry>/minio/minio` in its test setup therefore
# fails before its test suite starts. Pinning an older tag or relying on a local Docker cache
# does not help: the whole repository is gated, and tox-docker passes `pull=True` on every
# build, forcing a fresh pull.
#
# The one channel MinIO still serves anonymously is GitHub release assets, so this image is
# assembled from the official release binaries rather than pulled and re-tagged. The binaries
# below are byte-for-byte identical to the ones inside the last upstream image CI used
# (quay.io/minio/minio:latest, labelled RELEASE.2025-09-07T16-13-09Z) — verified by comparing
# their sha256 against /usr/bin/minio and /usr/bin/mc extracted from that image. The same holds
# for the license files in /licenses.
#
# Note that RELEASE.2025-09-07T16-13-09Z is the last MinIO release to publish binaries at all;
# later tags ship no assets. There is no newer version to move to.
#
# Scope
# -----
# This is a bare passthrough. It contains no Palace configuration: no credentials, no buckets,
# no entrypoint script. The repos that consume it (circulation, library-registry,
# virtual-library-card) each configure MinIO differently and keep doing so in their own
# Dockerfiles — they change only their `FROM` line. Baking configuration in here would fork
# the image between repos immediately.
#
# This mirror is a bridge, not a destination. PP-5245 tracks replacing MinIO outright:
# https://ebce-lyrasis.atlassian.net/browse/PP-5245
# Do not add features to it. Retiring it gets harder the longer it lives: GitHub does not allow
# self-service deletion of a public package once any version passes 5,000 downloads, after which
# it becomes a Support request.
#
# Updating
# --------
# Every downloaded artifact is pinned by sha256. The release strings and their checksums are a
# matched set: if you bump a version you MUST also replace the matching `--checksum=` values, or
# the build will fail (by design). Checksums come from the `.sha256sum` asset published
# alongside each binary. The base image is pinned by digest so that a rebuild reproduces the
# same image rather than picking up whatever `9.6` points at that day.

# Declared once here and inherited by every stage below with a bare `ARG`. Keeping a single
# definition means the tag the workflow publishes, the binaries the checksums cover and the
# labels on the image cannot drift apart in a version bump.
ARG BASE_IMAGE=registry.access.redhat.com/ubi9/ubi-minimal:9.6@sha256:34880b64c07f28f64d95737f82f891516de9a3b43583f39970f7bf8e4cfa48b7
ARG MINIO_RELEASE=RELEASE.2025-09-07T16-13-09Z
ARG MC_RELEASE=RELEASE.2025-08-13T08-35-41Z

# MinIO publishes one binary per platform rather than a multi-arch artifact, and each has its
# own checksum, so the download is split into a per-architecture stage that `fetch` selects
# from using TARGETARCH. This keeps checksum verification native to BuildKit's ADD.
FROM ${BASE_IMAGE} AS fetch-amd64
ARG MINIO_RELEASE
ARG MC_RELEASE
ADD --chmod=755 --checksum=sha256:7c5bd8512c6e966455b1d198209358b2d191c77a83ab377c4073281065fb855f \
    https://github.com/minio/minio/releases/download/${MINIO_RELEASE}/minio.linux-amd64.${MINIO_RELEASE} \
    /staging/minio
ADD --chmod=755 --checksum=sha256:01f866e9c5f9b87c2b09116fa5d7c06695b106242d829a8bb32990c00312e891 \
    https://github.com/minio/mc/releases/download/${MC_RELEASE}/mc.linux-amd64.${MC_RELEASE} \
    /staging/mc

FROM ${BASE_IMAGE} AS fetch-arm64
ARG MINIO_RELEASE
ARG MC_RELEASE
ADD --chmod=755 --checksum=sha256:5c83cd2cf151717ba0243f73e1c7802ff36e272b67144bdd7f1f7d684fd6f03d \
    https://github.com/minio/minio/releases/download/${MINIO_RELEASE}/minio.linux-arm64.${MINIO_RELEASE} \
    /staging/minio
ADD --chmod=755 --checksum=sha256:14c8c9616cfce4636add161304353244e8de383b2e2752c0e9dad01d4c27c12c \
    https://github.com/minio/mc/releases/download/${MC_RELEASE}/mc.linux-arm64.${MC_RELEASE} \
    /staging/mc

FROM fetch-${TARGETARCH} AS fetch

FROM ${BASE_IMAGE} AS minio
ARG MINIO_RELEASE
ARG MC_RELEASE

LABEL org.opencontainers.image.title="palace-ci-minio" \
      org.opencontainers.image.description="Unmodified MinIO server build, mirrored for Palace CI because upstream withdrew anonymous registry access." \
      org.opencontainers.image.version="${MINIO_RELEASE}" \
      org.opencontainers.image.source="https://github.com/ThePalaceProject/ci-scripts" \
      org.opencontainers.image.vendor="The Palace Project" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later" \
      io.palace.minio.release="${MINIO_RELEASE}" \
      io.palace.mc.release="${MC_RELEASE}"

COPY --from=fetch /staging/minio /usr/bin/minio
COPY --from=fetch /staging/mc /usr/bin/mc

# MinIO and mc are AGPL-3.0, and this image redistributes them publicly, so it carries the same
# license text and dependency attribution the upstream image shipped in /licenses. Both files
# are byte-identical to the ones in quay.io/minio/minio:latest. `mc` is under the same license,
# and its LICENSE file has the same contents, so one copy covers both.
ADD --chmod=644 --checksum=sha256:0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0 \
    https://raw.githubusercontent.com/minio/minio/${MINIO_RELEASE}/LICENSE \
    /licenses/LICENSE
ADD --chmod=644 --checksum=sha256:113b8c63dfd987d3652950d7c2aecb1c0952b41781e79bcdac6a316418d48542 \
    https://raw.githubusercontent.com/minio/minio/${MINIO_RELEASE}/CREDITS \
    /licenses/CREDITS

# Matches the upstream image: MinIO reads credentials from these files when the corresponding
# environment variables are not set, and `mc` needs a writable config dir.
ENV MINIO_ROOT_USER_FILE=access_key \
    MINIO_ROOT_PASSWORD_FILE=secret_key \
    MINIO_KMS_SECRET_KEY_FILE=kms_master_key \
    MINIO_CONFIG_ENV_FILE=config.env \
    MC_CONFIG_DIR=/tmp/.mc

# Declaring the volume creates the mount point, so no RUN is needed here. Keeping this stage
# free of RUN instructions means the image cross-builds for every architecture without QEMU.
VOLUME ["/data"]
EXPOSE 9000 9001

# A plain, unconfigured server. Consumers override this with their own CMD/ENTRYPOINT.
#
# Note one deliberate difference from the upstream image: it set ENTRYPOINT to a
# docker-entrypoint.sh that supplied the `minio` binary, so `docker run <image> server /data`
# worked. There is no entrypoint here, so the binary has to be named:
# `docker run <image> minio server /data`. The old form fails with
# `exec: "server": executable file not found in $PATH` and the container never starts. The three
# CI Dockerfiles set their own command and are unaffected, but anything invoking the image
# directly -- a README, a docker-compose service, a one-off container -- needs the full command.
CMD ["minio", "server", "/data", "--address", ":9000", "--console-address", ":9001"]
