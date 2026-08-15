#!/usr/bin/env bash
set -euo pipefail

RUBY_VERSION="3.3.11"
RUBY_PREFIX="${HOME}/.local/ruby-${RUBY_VERSION}"
RUBY_TARBALL="/tmp/ruby-${RUBY_VERSION}.tar.gz"
RUBY_SOURCE="/tmp/ruby-${RUBY_VERSION}"

sudo apt-get install -y \
  autoconf bison build-essential libdb-dev libffi-dev libgmp-dev libpq-dev \
  libreadline-dev libssl-dev libyaml-dev pkg-config postgresql postgresql-client \
  zlib1g-dev

sudo service postgresql start || true

if [[ ! -x "${RUBY_PREFIX}/bin/ruby" ]]; then
  rm -rf "${RUBY_SOURCE}" "${RUBY_TARBALL}"
  curl -fL --connect-timeout 20 --max-time 300 --retry 3 --retry-delay 2 \
    "https://cache.ruby-lang.org/pub/ruby/3.3/ruby-${RUBY_VERSION}.tar.gz" -o "${RUBY_TARBALL}"
  tar -xzf "${RUBY_TARBALL}" -C /tmp
  cd "${RUBY_SOURCE}"
  ./configure --prefix="${RUBY_PREFIX}" --disable-install-doc
  make -j"$(nproc)"
  make install
fi

"${RUBY_PREFIX}/bin/gem" install bundler --no-document
"${RUBY_PREFIX}/bin/ruby" --version
"${RUBY_PREFIX}/bin/bundle" --version
sudo service postgresql status || true
