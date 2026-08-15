#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="/home/ubuntu/edemocracy-hu-merge-ready"
WORK_ROOT="/home/ubuntu/edemocracy-hu-local-test"
BRANCH="feature/hu-localisation-ux-verification"

sudo apt-get install -y ruby3.2 ruby3.2-dev ruby-bundler
sudo pg_ctlcluster 16 main start || true
sudo -u postgres createuser --superuser ubuntu 2>/dev/null || true

rm -rf "${WORK_ROOT}"
git clone --branch "${BRANCH}" --single-branch "${SOURCE_ROOT}" "${WORK_ROOT}"
cd "${WORK_ROOT}"

# Local compatibility overlay only: it is never committed or pushed to the review branch.
sed -i 's/ruby file: ".ruby-version"/ruby ">= 3.2.0", "< 3.4"/' Gemfile
for template in config/*.example; do
  cp "${template}" "${template/.example}"
done

bundle config set --local path vendor/bundle
bundle install
npm clean-install

createdb consul_development 2>/dev/null || true
RAILS_ENV=development bundle exec rails db:setup

echo "Compatibility preview setup completed at ${WORK_ROOT}."
ruby --version
bundle --version
